"""Один предмет разбирает одна реализация, а законное совпадение названо.

Держит правило каталога 214. Самопроверка гейта отличает копию от импорта; здесь
— сверка со списком на подделанном дереве: названное совпадение проходит,
неназванная копия краснеет, запись без предмета — отказ, а непрочитанный
список и неразобранный модуль — третий исход, а не зелень.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_copies as cc  # noqa: E402

КОПИЯ = 'import re\nX = re.compile(r"^\\d{3}$")\n'


@pytest.fixture
def дерево(tmp_path: Path) -> Path:
    (tmp_path / "scripts").mkdir()
    (tmp_path / ".rules").mkdir()
    return tmp_path


def модуль(дерево: Path, имя: str, текст: str) -> None:
    (дерево / "scripts" / f"{имя}.py").write_text(текст, encoding="utf-8")


def список(дерево: Path, записи: list[dict]) -> None:
    (дерево / ".rules" / "copies.json").write_text(
        json.dumps({"_": "проба", "allowed": записи}, ensure_ascii=False),
        encoding="utf-8")


def test_kopiya_v_dvukh_modulyakh_otkaz(дерево: Path,
                                        capsys: pytest.CaptureFixture[str]) -> None:
    модуль(дерево, "a", КОПИЯ)
    модуль(дерево, "b", КОПИЯ)
    список(дерево, [])
    assert cc.main(["--root", str(дерево)]) == 1
    вывод = capsys.readouterr().err
    assert "scripts/a.py:2" in вывод and "scripts/b.py:2" in вывод


def test_nazvannoe_sovpadenie_prokhodit(дерево: Path) -> None:
    модуль(дерево, "a", КОПИЯ)
    модуль(дерево, "b", КОПИЯ)
    список(дерево, [{"pattern": "^\\d{3}$", "why": "общая грамматика"}])
    assert cc.main(["--root", str(дерево)]) == 0


def test_import_vmesto_kopii_chisto(дерево: Path) -> None:
    модуль(дерево, "a", КОПИЯ)
    модуль(дерево, "b", "from a import X\n")
    список(дерево, [])
    assert cc.main(["--root", str(дерево)]) == 0


def test_zapis_bez_predmeta_otkaz(дерево: Path,
                                  capsys: pytest.CaptureFixture[str]) -> None:
    модуль(дерево, "a", КОПИЯ)
    список(дерево, [{"pattern": "^\\d{3}$", "why": "было совпадение"}])
    assert cc.main(["--root", str(дерево)]) == 1
    assert "нечего" in capsys.readouterr().err


@pytest.mark.parametrize("содержимое, почему", [
    (None, "не найден"),
    ("{не json", "не разобран"),
    ('{"allowed": [{"pattern": "x"}]}', "нет pattern или why"),
])
def test_spisok_ne_prochitan_tretiy_iskhod(
        дерево: Path, capsys: pytest.CaptureFixture[str],
        содержимое: str | None, почему: str) -> None:
    модуль(дерево, "a", КОПИЯ)
    if содержимое is not None:
        (дерево / ".rules" / "copies.json").write_text(содержимое, encoding="utf-8")
    assert cc.main(["--root", str(дерево)]) == 2
    assert почему in capsys.readouterr().err


def test_nerazobrannyy_modul_tretiy_iskhod(дерево: Path) -> None:
    модуль(дерево, "a", "def f(:\n")
    список(дерево, [])
    assert cc.main(["--root", str(дерево)]) == 2


def test_derevo_kataloga_chisto() -> None:
    assert cc.main([]) == 0
