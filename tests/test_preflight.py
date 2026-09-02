"""Прогон перед толчком: план собран из конвейера, и пропуск не молчит.

Скрипт заменяет чек-лист свода, и обе его ошибки тихие. Пропущенный шаг даёт
локальное «чисто» там, где конвейер откажет, — а именно ради этого «чисто»
прогон и запускают. Ложное «чисто» о шаге, которого локально запустить нельзя,
хуже: оно неотличимо от проверенного (правило 075), и отличать их приходится
уже по красному в конвейере.

Отдельно и главное — **разъезд**. Ценность прогона держится ровно на том, что
список шагов он читает из `ci.yml`, а не хранит свой. Второй список устареет
первой же правкой конвейера и разойдётся молча (022), поэтому здесь стоит
случай, который сверяет план с живым `ci.yml` каталога: новый шаг обязан в нём
оказаться, и никто не должен об этом помнить.

Сеть и площадка не трогаются: разбор — чистая функция над текстом работы,
а прогон подделывается собственным скриптом-заглушкой.
"""

from __future__ import annotations

from pathlib import Path

import preflight

ROOT = Path(__file__).resolve().parent.parent

STEP = """\
jobs:
  catalogue:
    steps:
      - uses: actions/checkout@v4
      - name: обычный шаг
        run: python scripts/check_links.py
      - name: шаг только на изменении
        if: github.event_name == 'pull_request'
        run: python scripts/check_attribution.py --range "$BASE..$HEAD"
      - name: шаг с телом
        run: |
          set -euo pipefail
          python scripts/pr_body.py --check --body-file "$RUNNER_TEMP/pr-body.md"
"""


def names(steps: list[preflight.Step]) -> list[str]:
    return [s.name for s in steps]


# ── разбор: что попадает в план, а что называется ──────────────────────────

def test_shag_konveyera_popal_v_plan():
    steps = preflight.parse_steps(STEP)
    runnable = [s for s in steps if not s.skip_why]
    assert names(runnable) == ["обычный шаг"]
    assert runnable[0].command == ["python", "scripts/check_links.py"]


def test_shag_na_izmenenii_nazvan_a_ne_propushchen():
    """Пропустить молча — значит выдать «чисто» за то, чего не проверяли."""
    steps = preflight.parse_steps(STEP)
    skipped = {s.name: s.skip_why for s in steps if s.skip_why}
    assert "шаг только на изменении" in skipped
    assert "pull_request" in skipped["шаг только на изменении"]


def test_shag_s_peremennoy_sobytiya_ne_zapuskaetsya_vhollostuyu():
    """Без `if`, но с `$RUNNER_TEMP`: локально он ответил бы о пустой строке."""
    steps = preflight.parse_steps(STEP)
    skipped = {s.name: s.skip_why for s in steps if s.skip_why}
    assert "шаг с телом" in skipped
    assert "контекст изменения" in skipped["шаг с телом"]


def test_uses_ne_schitaetsya_shagom():
    """`actions/checkout` исполняет площадка — запускать нечего и незачем."""
    assert "actions/checkout@v4" not in " ".join(names(preflight.parse_steps(STEP)))


def test_predel_vremeni_u_testov_svoy():
    """Правило 100: общий предел пришлось бы ставить по самому долгому шагу."""
    long = preflight.Step("тесты", ["python", "-m", "pytest"])
    short = preflight.Step("ссылки", ["python", "scripts/check_links.py"])
    assert long.timeout_s > short.timeout_s


# ── разъезд с конвейером: то, ради чего план не хранится ───────────────────

def test_plan_sobran_iz_zhivogo_konveyera_a_ne_iz_spiska():
    """Каждый шаг `ci.yml`, зовущий python, обязан оказаться в плане.

    Это и есть страховка от 022: свой список тех же шагов разъехался бы с
    конвейером молча, и узналось бы это на красном.
    """
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    in_pipeline = {ln.split("python ", 1)[1].split()[0]
                   for ln in text.splitlines() if "python " in ln}
    in_plan = {s.command[1] if s.command[1] != "-m" else "-m"
               for s in preflight.parse_steps(text) if s.command}
    assert in_pipeline - in_plan == set()


# ── три исхода ─────────────────────────────────────────────────────────────

def stub(tmp_path: Path, body: str, run_line: str) -> Path:
    """Каталог-подделка: свой `ci.yml` и скрипт, отвечающий заданным кодом."""
    (tmp_path / "scripts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "scripts" / "stub.py").write_text(body, encoding="utf-8")
    work = tmp_path / ".github" / "workflows"
    work.mkdir(parents=True, exist_ok=True)
    (work / "ci.yml").write_text(
        "jobs:\n  catalogue:\n    steps:\n"
        f"      - name: подделка\n        run: {run_line}\n", encoding="utf-8")
    return tmp_path


def test_chisto_eto_nol(tmp_path):
    root = stub(tmp_path, "import sys; sys.exit(0)\n", "python scripts/stub.py")
    assert preflight.main(["--root", str(root)]) == 0


def test_nahodka_eto_odin(tmp_path):
    root = stub(tmp_path, "import sys; sys.exit(1)\n", "python scripts/stub.py")
    assert preflight.main(["--root", str(root)]) == 1


def test_shag_ne_otrabotal_eto_dva_a_ne_nahodka(tmp_path):
    """Правило 039: «проверка не состоялась» — третий исход, а не находка.

    Слить его с единицей значит записать несостоявшуюся проверку в найденные
    недостатки и починить не то.
    """
    root = stub(tmp_path, "import sys; sys.exit(2)\n", "python scripts/stub.py")
    assert preflight.main(["--root", str(root)]) == 2


def test_bez_konveyera_eto_dva(tmp_path):
    assert preflight.main(["--root", str(tmp_path)]) == 2


def test_konveyer_bez_shagov_eto_dva_a_ne_chisto(tmp_path):
    """Ноль шагов — ошибка разбора, и зеленеть на ней нельзя (правило 075)."""
    work = tmp_path / ".github" / "workflows"
    work.mkdir(parents=True)
    (work / "ci.yml").write_text("jobs:\n  catalogue:\n    steps: []\n",
                                 encoding="utf-8")
    assert preflight.main(["--root", str(tmp_path)]) == 2


def test_pustaya_vyborka_eto_dva_a_ne_chisto(tmp_path):
    """`--only` без совпадений: выборка пуста, а не чиста."""
    root = stub(tmp_path, "import sys; sys.exit(0)\n", "python scripts/stub.py")
    assert preflight.main(["--root", str(root), "--only", "нетакого"]) == 2


def test_list_nichego_ne_zapuskaet(tmp_path, capsys):
    root = stub(tmp_path, "import sys; sys.exit(1)\n", "python scripts/stub.py")
    assert preflight.main(["--root", str(root), "--list"]) == 0
    assert "подделка" in capsys.readouterr().out


def test_nezapuskaemye_nazvany_v_itoge(tmp_path, capsys):
    """Итог обязан сказать, чего не запускали: иначе «чисто» читается шире."""
    root = stub(tmp_path, "import sys; sys.exit(0)\n", "python scripts/stub.py")
    work = root / ".github" / "workflows" / "ci.yml"
    work.write_text(work.read_text(encoding="utf-8")
                    + "      - name: только на изменении\n"
                      "        if: github.event_name == 'pull_request'\n"
                      "        run: python scripts/stub.py\n", encoding="utf-8")
    assert preflight.main(["--root", str(root)]) == 0
    assert "не запускалось локально" in capsys.readouterr().out


# ── локальная замена входа: тело, которое уедет телом изменения ───────────
#
# Замер, из которого это выросло: три изменения подряд за одно окно уехали без
# строки связи с задачей и вернулись красными. Прогон говорил «предмет
# появляется только на изменении» — и был неправ: предмет появляется в момент
# коммита, а тело изменения собирается из ПЕРВОГО коммита ветки.

import subprocess


def репо(tmp_path: Path, *тела: str) -> Path:
    def git(*args):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True,
                       capture_output=True, text=True)
    git("init", "-q", "-b", "main")
    git("config", "user.name", "Владелец")
    git("config", "user.email", "owner@example.com")
    (tmp_path / "a.txt").write_text("основание", encoding="utf-8")
    git("add", "-A")
    git("-c", "commit.gpgsign=false", "commit", "-q", "-m", "основание")
    git("branch", "-f", "подделка-основания")
    for i, тело in enumerate(тела):
        (tmp_path / f"f{i}.txt").write_text(str(i), encoding="utf-8")
        git("add", "-A")
        git("-c", "commit.gpgsign=false", "commit", "-q", "-m",
            f"работа {i}\n\n{тело}")
    return tmp_path


def test_telo_beryotsya_u_PERVOGO_kommita_vetki(tmp_path):
    """Ровно то, что делает agent-pr.yml: берёт первый, а не последний.

    Случай не косметический: у изменения из двух коммитов строка связи может
    стоять во втором — и уехать в тело всё равно не может."""
    root = репо(tmp_path, "Closes #7", "а тут строки связи нет")

    текст, ошибка = preflight.branch_body(root, base="подделка-основания")

    assert not ошибка and "Closes #7" in текст
    assert "строки связи нет" not in текст


def test_vetka_bez_svoih_kommitov_eto_oshibka_a_ne_pustota(tmp_path):
    """«Тела нет» и «тело пустое» — разные ответы (039): пустое прошло бы
    проверку связи молча."""
    root = репо(tmp_path)

    текст, ошибка = preflight.branch_body(root, base="подделка-основания")

    assert текст == "" and "не несёт своих коммитов" in ошибка


def test_neizvestnoe_osnovanie_eto_oshibka(tmp_path):
    root = репо(tmp_path, "Closes #7")

    _, ошибка = preflight.branch_body(root, base="ветки-такой-нет")

    assert "не спросить коммиты" in ошибка


def test_zamena_nazyvaet_sushchestvuyushchiy_skript():
    """Декларация сверяется с фактом: путь в таблице замен должен быть."""
    корень = Path(preflight.__file__).resolve().parent.parent
    for имя, (скрипт, _) in preflight.STAND_IN.items():
        assert (корень / скрипт).exists(), f"{имя}: нет {скрипт}"


def test_zamena_stoit_na_shage_zhivogo_konveyera():
    """Имя в таблице должно совпадать с шагом ci.yml дословно: разойдясь,
    замена молча перестанет срабатывать (141)."""
    корень = Path(preflight.__file__).resolve().parent.parent
    шаги = preflight.parse_steps(
        (корень / ".github/workflows/ci.yml").read_text(encoding="utf-8"))

    имена = {s.name for s in шаги}
    assert set(preflight.STAND_IN) <= имена
