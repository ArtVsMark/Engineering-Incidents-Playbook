"""Гейт невидимых символов в раздаваемом тексте (#873): отказ, чисто, третий исход."""

from pathlib import Path

import pytest

import check_invisible as ci
import invisible


def дерево(tmp_path: Path, файлы: dict[str, str]) -> Path:
    for имя, текст in файлы.items():
        (tmp_path / имя).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / имя).write_text(текст, encoding="utf-8")
    return tmp_path


# Перечень форм (210): каждое место охвата и каждый род символа — свой случай.
@pytest.mark.parametrize("файлы", [
    {"rules/ru/001-x.md": "Правило\U000E0041.\n"},          # Tag
    {"rules/en/001-x.md": "rule​\n"},                   # нулевая ширина
    {"candidates/x.md": "кандидат‮\n"},                 # двунаправленный
    {"export/rules.json": '{"a": "⁦b"}\n'},             # изоляция направления
    {".claude/skills/s/SKILL.md": "навыкㅤ\n"},          # заполнитель Lo
    {"rules/ru/001-x.md": "мягкий­перенос\n"},          # граница: тоже отказ
])
def test_невидимое_отказ(tmp_path, capsys, файлы):
    assert ci.main(["--root", str(дерево(tmp_path, файлы))]) == 1
    err = capsys.readouterr().err
    assert ":1: U+" in err and "085" in err


def test_видимое_чисто(tmp_path):
    файлы = {"rules/ru/001-x.md": "Обычный текст — с тире, «ёлочками» и 🏛.\n"}
    assert ci.main(["--root", str(дерево(tmp_path, файлы))]) == 0


def test_вне_охвата_не_проверяется(tmp_path):
    файлы = {"rules/ru/001-x.md": "чисто\n", "scripts/x.py": "s = '​'\n"}
    assert ci.main(["--root", str(дерево(tmp_path, файлы))]) == 0


def test_пустой_охват_третий_исход(tmp_path):
    assert ci.main(["--root", str(tmp_path)]) == 2


def test_имя_символа_а_не_сам_символ():
    assert invisible.назвать("\U000E0041") == "U+E0041 TAG LATIN CAPITAL LETTER A"


def test_живое_дерево_чисто():
    assert ci.main([]) == 0
