"""Сторож толчка: отвергается ветка, отличная от текущей, и только она.

Случаи спрашивают САМ ХУК через `main()` — событие подаётся на stdin ровно в
том виде, в каком его подаёт площадка (правило 150). Текущая ветка
подменяется: спрашивать настоящую значило бы проверять состояние машины, а не
решение сторожа.

Сторож живёт вне `scripts/`, потому что запускает его не конвейер, а окно, — и
потому подключается путём, а не импортом из общего каталога.
"""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import pytest

ХУК = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "push_guard.py"
_spec = importlib.util.spec_from_file_location("push_guard", ХУК)
pg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pg)


def событие(command: str, tool: str = "Bash") -> str:
    return json.dumps({"tool_name": tool, "tool_input": {"command": command}})


@pytest.fixture
def окно(monkeypatch):
    """Окно стоит на своей ветке; вход подаётся как площадкой.

    ВТОРОЙ ПРЕДМЕТ ХУКА ЗДЕСЬ ОТКЛЮЧЁН НАМЕРЕННО. Проверка тела спрашивает
    НАСТОЯЩЕЕ дерево — коммиты ветки, на которой идёт работа, — и без этой
    подмены случаи про ветку краснели бы от чужой причины: девять из
    двадцати двух отказали разом, когда в рабочей ветке появился коммит с
    неполным телом. Тело проверяется своими случаями ниже (018).
    """
    def настроить(command: str, branch: str | None = "agent/своя",
                  tool: str = "Bash"):
        monkeypatch.setattr(pg, "current_branch", lambda: branch)
        monkeypatch.setattr(pg, "тело_не_проходит", lambda корень: None)
        monkeypatch.setattr("sys.stdin", io.StringIO(событие(command, tool)))
    return настроить


def test_chuzhaya_vetka_otvergaetsya(окно, capsys):
    """Ровно предмет правила: содержимое уехало бы не туда, куда смотрит окно."""
    окно("git push -u origin agent/чужая")

    assert pg.main() == 2
    err = capsys.readouterr().err
    assert "agent/чужая" in err and "agent/своя" in err


def test_svoya_vetka_prohodit(окно):
    окно("git push -u origin agent/своя")

    assert pg.main() == 0


def test_tolchok_bez_imeni_vetki_prohodit(окно):
    """`git push` без ссылки уезжает по настройке ветки — это не промах."""
    окно("git push")

    assert pg.main() == 0


def test_yavnaya_ssylka_prohodit(окно):
    """`HEAD:main` — цель названа явно и осознанно; запрет на общую ветку
    живёт не здесь, а в правиле 131."""
    окно("git push origin HEAD:main")

    assert pg.main() == 0


def test_perenapravlenie_ne_schitaetsya_vetkoy(окно):
    """Замер на первой же живой пробе: `2>&1` уехало в список веток, и сторож
    назвал предметом отказа то, чего в команде не было (158)."""
    окно("git push -u origin agent/своя 2>&1 | tail -3")

    assert pg.main() == 0


def test_tsepochka_komand_razbiraetsya(окно):
    """Толчок прячется за `&&` чаще, чем стоит первым словом."""
    окно("git add -A && git commit -q -m x && git push origin agent/другая")

    assert pg.main() == 2


def test_ne_bash_ne_trogaetsya(окно):
    """Сторож смотрит на действие, а не на текст: строка в файле — не команда."""
    окно("git push origin agent/чужая", tool="Write")

    assert pg.main() == 0


def test_otdelyonnaya_golova_propuskaetsya(окно):
    """Сравнивать не с чем: у отделённой головы имени ветки нет вовсе, и
    отказ здесь был бы отказом на пустом месте (051)."""
    окно("git push origin agent/чужая", branch=None)

    assert pg.main() == 0


def test_slovo_push_v_chuzhoy_komande_ne_schitaetsya(окно):
    """`npm push`, `echo git push` и прочее сторожа не касаются."""
    окно("echo git push origin agent/чужая")

    assert pg.main() == 0


def test_telo_dokumenta_na_vhode_ne_komanda(окно):
    """Замер живой пробы: окно писало прогон через `cat > … <<'YML'`, и внутри
    файла стоял ПРИМЕР для человека — «переименуйте: git push …». Сторож
    разобрал пример как команду и отверг запись файла.

    Случай «строка в файле не команда» в наборе уже был, но проверял запись
    ЧУЖИМ инструментом; запись через оболочку им не покрывалась (140)."""
    окно("cat > f.yml <<'YML'\n"
         "echo 'переименуйте: git push -u origin agent/чужая'\n"
         "YML\n"
         "echo записано")

    assert pg.main() == 0


def test_tolchok_posle_dokumenta_vidno(окно, capsys):
    """Граница с другой стороны: пропускается ТЕЛО, а не всё остальное."""
    окно("cat > f.txt <<'EOF'\n"
         "git push origin agent/из-текста\n"
         "EOF\n"
         "git push origin agent/настоящая")

    assert pg.main() == 2
    err = capsys.readouterr().err
    assert "agent/настоящая" in err and "из-текста" not in err


def test_dokument_bez_zakryvayushchey_stroki_ne_veshaet_storozha(окно):
    """Незакрытый документ — не наше дело: разбор кончается, а не зацикливается."""
    окно("cat > f.txt <<'EOF'\ngit push origin agent/чужая")

    assert pg.main() == 0


def test_perehod_v_vetku_pered_tolchkom_eto_svoya(окно):
    """Замер: за смену это отвергло верный толчок трижды подряд. Сторож
    спрашивает ветку у git ДО того, как команда выполнится, и `checkout X &&
    push X` выглядел толчком в чужую."""
    окно("git checkout -q agent/другая && git push origin agent/другая")

    assert pg.main() == 0


def test_switch_schitaetsya_naravne_s_checkout(окно):
    окно("git switch agent/другая && git push -u origin agent/другая")

    assert pg.main() == 0


def test_novaya_vetka_klyuchom_tozhe_svoya(окно):
    """`checkout -B имя` заводит ветку и переходит в неё — она уже своя."""
    окно("git checkout -B agent/новая origin/main && git push origin agent/новая")

    assert pg.main() == 0


def test_posle_perehoda_chuzhaya_vsyo_ravno_chuzhaya(окно, capsys):
    """Граница с другой стороны: сторож следует за переходом, а не слепнет."""
    окно("git switch agent/одна && git push origin agent/другая")

    assert pg.main() == 2
    assert "agent/другая" in capsys.readouterr().err


def test_imya_podstanovkoy_ne_ugadyvaetsya(окно):
    """«Неизвестно» и «чужая» — разные ответы (051): значения переменной
    сторож не знает и запрещать по догадке не должен."""
    окно("git push -q origin $b")

    assert pg.main() == 0


# ── ВТОРОЙ ПРЕДМЕТ ХУКА: тело, из которого конвейер соберёт изменение ──────
# Замер 7 сентября: три красных подряд (#372, #373, #376) с находкой гейта тела.
# Гейт верен, но живёт на изменении — к его запуску тело уже уехало, а конвейер
# ставит его ОДИН раз при открытии. Единственное окружение, где проверка ещё
# осмысленна, — между коммитом и толчком (018).


@pytest.mark.parametrize("команда, ждём, что", [
    ("git push -u origin ветка", True, "настоящий толчок"),
    ("/usr/bin/git push origin x", True, "полный путь к git"),
    ('echo "git push origin x" > /tmp/a', False, "слова внутри строки-аргумента"),
    ("git status", False, "не толчок вовсе"),
    ("cat > f <<'EOF'\ngit push origin main\nEOF", False, "внутри heredoc — текст"),
])
def test_tolchok_uznayotsya_razborom(команда, ждём, что):
    """ЛОЖНЫЙ ОТКАЗ ЗДЕСЬ ДОРОЖЕ ПРОПУСКА: он останавливает работу, которая
    ничего не нарушает (051). Первая редакция спрашивала «есть ли слово push
    среди слов» и отвергла собственную команду разработки, где эти два слова
    стояли внутри строки-аргумента, — поймано пробой на самом хуке.
    """
    assert pg.толкает(команда) is ждём, что


def test_telo_beryotsya_u_togo_zhe_vybora_chto_i_u_konveyera(monkeypatch, tmp_path):
    """ОДИН ВОПРОС — ОДИН ОТВЕТ (022). Хук проверяет ТО ЖЕ тело, которое
    поставит конвейер, и потому обязан спрашивать коммит у того же скрипта.
    Свой разбор `origin/main..HEAD` здесь уже стоял и повторял дефект
    конвейера: на ветке поверх соседней первым в диапазоне идёт чужой коммит.
    """
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "pr_source_commit.py").write_text("", encoding="utf-8")
    вызовы: list[list[str]] = []

    class Ответ:
        """Форма ответа снята с `python3 scripts/pr_source_commit.py --base
        origin/main`: отпечаток в stdout, объяснение в stderr, код 0 (170)."""

        returncode = 0
        stdout = "deadbeef\n"
        stderr = "заголовок даёт deadbeef: «feat(rules): своя тема»\n"

    def подмена(args, **kwargs):
        вызовы.append([str(a) for a in args])
        return Ответ()

    monkeypatch.setattr(pg.subprocess, "run", подмена)

    assert pg.первый_коммит_ветки(tmp_path) == "deadbeef\n"
    assert any("pr_source_commit.py" in " ".join(c) for c in вызовы), вызовы
    # ОТПЕЧАТОК ОБЯЗАН ДОЛЕТЕТЬ ДО ВТОРОГО ВЫЗОВА, И ИМЕННО ЭТО ЗДЕСЬ ПРЕДМЕТ.
    # Прежний случай спрашивал лишь «был ли вызов с --format=%B» и остался бы
    # зелёным, уйди туда `названо.stdout` без `.strip()` или чужой коммит
    # вовсе: проверка гоняла предмет, а не то, что обязана отвергнуть (140).
    тело = next((c for c in вызовы if "--format=%B" in c), None)
    assert тело is not None, вызовы
    assert тело[:2] == ["git", "-C"] and тело[2] == str(tmp_path), тело
    assert тело[-1] == "deadbeef", тело


def test_chuzhoe_derevo_bez_vybora_ne_meshaet(tmp_path):
    """Хук запускают и там, где каталога нет вовсе: отказ на пустом месте
    остановил бы верный толчок (051)."""
    assert pg.первый_коммит_ветки(tmp_path) is None
