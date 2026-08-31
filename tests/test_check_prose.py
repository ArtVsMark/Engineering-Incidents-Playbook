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
