"""Вписанное рукой: подделка вместо зелени живого корпуса.

Гейт зелен на текущем дереве — сворачиваемых блоков в нём нет, версия в
манифесте заглушка. Зелёный прогон на хорошем входе подтверждает, что скрипт
запускается, и ничего больше (146), поэтому предмет ему подсовывают здесь.

Обе ошибки этого гейта тихи. Пропущенный спойлер уедет в витрину, и читатель
увидит оборванный раздел — ровно то, о чём четыре обзора подряд писали
«недоделан». Ложная находка на записи, которая спойлер ЦИТИРУЕТ, сделала бы
первым нарушителем саму запись 008, а красное на верной работе приучают
пропускать (051).

Сеть не трогается; дерево подделывается временным репозиторием, потому что
список файлов гейт берёт у git — непрослеживаемый мусор проверять незачем.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import check_prose as cp


def repo_with(tmp_path: Path, files: dict[str, str]) -> Path:
    """Временный репозиторий: гейт смотрит только отслеживаемое."""
    for name, body in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return tmp_path


# ── сворачиваемые блоки (008) ──────────────────────────────────────────────

def test_spoyler_v_tekste_nahodka(tmp_path):
    root = repo_with(tmp_path, {"README.md": "# Витрина\n\n<details>\n<summary>что-то</summary>\n"})
    assert cp.main(["--root", str(root)]) == 1


def test_spoyler_v_obratnyh_kavychkah_ne_narushenie(tmp_path):
    """Запись 008 объясняет, чем плох спойлер, и обязана его назвать."""
    root = repo_with(tmp_path, {"r.md": "На странице `<details>` даёт заголовок без содержимого.\n"})
    assert cp.main(["--root", str(root)]) == 0


def test_spoyler_v_bloke_koda_ne_narushenie(tmp_path):
    """Показ внутри ``` — это цитата, а не употребление."""
    root = repo_with(tmp_path, {"r.md": "Так делать нельзя:\n\n```\n<details>\n```\n"})
    assert cp.main(["--root", str(root)]) == 0


def test_nahodka_nazyvaet_fayl_i_stroku(tmp_path, capsys):
    """«Где-то есть спойлер» чинить нельзя: адрес — часть находки."""
    root = repo_with(tmp_path, {"a.md": "первая\nвторая\n<details>\n"})
    assert cp.main(["--root", str(root)]) == 1
    assert "a.md:3" in capsys.readouterr().err


def test_nezakrytyy_blok_koda_ne_glushit_ostalnoy_fayl(tmp_path):
    """Открывающая ``` без закрывающей — это порча файла, но спойлер ПОСЛЕ неё
    внутри блока и есть цитата: гейт не должен додумывать за разметку."""
    lines = cp.details_lines("```\n<details>\n")
    assert lines == []


def test_stroki_schitayutsya_ot_edinitsy():
    assert cp.details_lines("<details>\n") == [1]


# ── версия в манифесте (035) ───────────────────────────────────────────────

def test_vpisannaya_versiya_nahodka(tmp_path):
    root = repo_with(tmp_path, {"a.md": "текст\n",
                                "pyproject.toml": '[project]\nversion = "1.1.0"\n'})
    assert cp.main(["--root", str(root)]) == 1


def test_zaglushka_ne_narushenie(tmp_path):
    """`0.0.0` означает «версия приходит из тега» — это соблюдение, а не обход."""
    root = repo_with(tmp_path, {"a.md": "текст\n",
                                "pyproject.toml": '[project]\nversion = "0.0.0"\n'})
    assert cp.main(["--root", str(root)]) == 0


def test_versiya_v_proze_ne_nahodka(tmp_path):
    """ГРАНИЦА, И ОНА ИЗМЕРЕНА: поиск `X.Y.Z` по дереву каталога даёт
    шестнадцать файлов, и все законны — история выпусков, схема версий, чужие
    версии в инцидентах. Проверяется поле манифеста, а не проза."""
    root = repo_with(tmp_path, {"HISTORY.md": "Тег v1.0.0 поставлен в тот же день.\n"})
    assert cp.main(["--root", str(root)]) == 0


# ── три исхода ─────────────────────────────────────────────────────────────

def test_chisto_eto_nol(tmp_path):
    root = repo_with(tmp_path, {"a.md": "обычный текст\n"})
    assert cp.main(["--root", str(root)]) == 0


def test_net_tekstovyh_faylov_eto_dva_a_ne_chisto(tmp_path):
    """Ноль просмотренных файлов — ошибка входа, и зеленеть на ней нельзя (075)."""
    root = repo_with(tmp_path, {"script.py": "x = 1\n"})
    assert cp.main(["--root", str(root)]) == 2


def test_ne_repozitoriy_eto_dva(tmp_path):
    """Список файлов берётся у git: без него смотреть нечего."""
    (tmp_path / "a.md").write_text("<details>\n", encoding="utf-8")
    assert cp.main(["--root", str(tmp_path)]) == 2


# ── номер задачи в объяснении (025) ────────────────────────────────────────

def запись(тело: str) -> str:
    return "# Заголовок\n\n**Область.** процесс\n\n" + тело


def test_nomer_v_pochemu_nahodka(tmp_path):
    root = repo_with(tmp_path, {"rules/ru/001-x.md": запись(
        "## Почему\n\nМеханизм описан в #123, читайте там.\n")})
    assert cp.main(["--root", str(root)]) == 1


def test_nomer_v_intsidente_ne_narushenie(tmp_path):
    """В инциденте номер — это датировка, и она там на месте."""
    root = repo_with(tmp_path, {"rules/ru/001-x.md": запись(
        "## Инцидент\n\nPR #1294: 16 записей, дублей нет.\n")})
    assert cp.main(["--root", str(root)]) == 0


def test_nomer_v_sledе_ne_narushenie(tmp_path):
    """След обязан быть разрешимым, то есть как раз номером задачи."""
    root = repo_with(tmp_path, {"rules/ru/001-x.md": запись(
        "## След\n\nArtVsMark/Engineering-Incidents-Playbook#213\n")})
    assert cp.main(["--root", str(root)]) == 0


def test_nomer_v_bloke_koda_ne_narushenie(tmp_path):
    """Пример чек-листа цитирует строку с номером — это показ, а не ссылка."""
    root = repo_with(tmp_path, {"rules/ru/001-x.md": запись(
        "## Почему\n\n```\n- [x] Находка A — исправлено в #123\n```\n")})
    assert cp.main(["--root", str(root)]) == 0


def test_reshyotka_zagolovka_ne_schitaetsya_nomerom():
    """`#123` — номер, `## Почему` — заголовок: путать их значит краснеть на
    каждой второй записи."""
    assert cp.issue_numbers("## Почему\n\nпросто текст\n") == []


# ── ссылка из оригинала в копию (089) ──────────────────────────────────────

def test_ssylka_v_ukazatel_nahodka(tmp_path):
    root = repo_with(tmp_path, {"rules/ru/001-x.md": запись(
        "## Почему\n\nСписок — в [указателе](../README.md), см. rules/README.md.\n"
        "Точнее: [тут](../../rules/README.md).\n")})
    assert cp.main(["--root", str(root)]) == 1


def test_ssylka_v_vygruzku_nahodka(tmp_path):
    root = repo_with(tmp_path, {"rules/ru/001-x.md": запись(
        "## Почему\n\nДанные лежат в [выгрузке](../../export/rules.json).\n")})
    assert cp.main(["--root", str(root)]) == 1


def test_ssylka_na_sosednyuyu_zapis_ne_narushenie(tmp_path):
    """Запись на запись — связь оригиналов, и она обязательна: правило без
    соседей обычно либо дубль, либо слишком общее."""
    root = repo_with(tmp_path, {"rules/ru/001-x.md": запись(
        "## Почему\n\nСмежное: [022](022-one-canonical-document.md).\n")})
    assert cp.main(["--root", str(root)]) == 0


def test_dokument_vne_zapisey_ne_proveryaetsya_na_ssylki(tmp_path):
    """ГРАНИЦА: свод ссылается на указатель законно — он не оригинал для него,
    а читатель свода ищет вход в каталог именно там."""
    root = repo_with(tmp_path, {"AGENTS.md": "Указатель — [rules/README.md](rules/README.md).\n"})
    assert cp.main(["--root", str(root)]) == 0


# ── две лицензии, и обе названы витриной ───────────────────────────────────

ВИТРИНА = "# Проект\n\nЗаписи — CC BY 4.0 (LICENSE), скрипты — MIT (LICENSE-CODE).\n"


def test_obe_litsenzii_na_meste_chisto(tmp_path):
    root = repo_with(tmp_path, {"README.md": ВИТРИНА,
                                "LICENSE": "CC BY\n", "LICENSE-CODE": "MIT\n"})
    assert cp.main(["--root", str(root)]) == 0


def test_propavshaya_litsenziya_koda_nahodka(tmp_path):
    root = repo_with(tmp_path, {"README.md": ВИТРИНА, "LICENSE": "CC BY\n"})
    assert cp.main(["--root", str(root)]) == 1


def test_litsenziya_o_kotoroy_vitrina_molchit_nahodka(tmp_path, capsys):
    """Площадка показывает одну лицензию — ту, что в LICENSE. Вторая существует
    ровно настолько, насколько на неё ссылается витрина."""
    root = repo_with(tmp_path, {"README.md": "# Проект\n\nЛицензия: LICENSE.\n",
                                "LICENSE": "CC BY\n", "LICENSE-CODE": "MIT\n"})
    assert cp.main(["--root", str(root)]) == 1
    assert "LICENSE-CODE" in capsys.readouterr().err


def test_angliyskaya_vitrina_tozhe_schitaetsya(tmp_path):
    """Назвать лицензию можно в любой из двух витрин: читатель приходит в свою."""
    root = repo_with(tmp_path, {"README.md": "# Проект\n",
                                "README.en.md": ВИТРИНА,
                                "LICENSE": "CC BY\n", "LICENSE-CODE": "MIT\n"})
    assert cp.main(["--root", str(root)]) == 0


# ── номер формата назван там, где объясняют номера ────────────────────────
#
# У каталога одна версия — тег; всё остальное, что выглядит версией,
# версионирует ФОРМАТ. Замер: вопрос владельца «почему 1.2, если версия 1.1»,
# а следом чужой файл, где номер схемы ВЫГРУЗКИ уехал в поле схемы ОТВЕТА.

def дерево(tmp_path, файл: str, схема: str, versioning: str) -> Path:
    return repo_with(tmp_path, {файл: '{\n  "schema": "%s"\n}\n' % схема,
                                "VERSIONING.md": versioning})


def test_nazvannaya_shema_prohodit(tmp_path):
    root = дерево(tmp_path, "a.json", "1.2", "# Версии\n\n`schema` в a.json — формат.\n")

    assert not cp.schema_unnamed(root)


def test_neназванная_shema_eto_nahodka(tmp_path):
    root = дерево(tmp_path, "a.json", "1.2", "# Версии\n\nтолько про тег.\n")

    out = cp.schema_unnamed(root)
    assert out and "a.json" in out[0]


def test_zagotovka_v_schyot_ne_idyot(tmp_path):
    """Заготовка — образец для ЧУЖОГО проекта: её схема описана в контракте,
    и требовать её здесь значит требовать от каталога отвечать за чужой файл."""
    root = дерево(tmp_path, "templates/bindings.json", "1.1", "# Версии\n\nпро тег.\n")

    assert not cp.schema_unnamed(root)


def test_bez_politiki_versiy_predmeta_net(tmp_path):
    """Проверка ходит и по подделанным деревьям: документ принадлежит каталогу."""
    root = repo_with(tmp_path, {"a.json": '{"schema": "1.0"}'})

    assert not cp.schema_unnamed(root)
