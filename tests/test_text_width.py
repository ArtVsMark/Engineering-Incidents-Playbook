"""Ширина надписи в SVG: одна функция по таблице знаков, а не «длина × k».

Задача #792: значок `python-badge` выходил на 20–25 % шире текста, потому
что каждому знаку давалась ширина 7,2 px, а у картинки потребителей была
своя такая же формула. Набор держит три вещи: таблица различает узкие и
широкие знаки, текст в части значка не обрезается, и в генераторах картинок
нет второго расчёта ширины «len(...) * k».
"""

import re
from pathlib import Path

import pytest

import consumers_picture as cp
import python_badge as pb
import text_width as tw

SCRIPTS = Path(tw.__file__).resolve().parent

#: Расчёт ширины по числу знаков: `len(...)`, умноженное на что угодно.
ДЛИНА_НА_K = re.compile(r"len\([^)]*\)\s*\*")


@pytest.mark.parametrize("шрифт, вес", [("Verdana", 400), ("Inter", 800)])
def test_узкая_надпись_уже_широкой_при_равной_длине(шрифт, вес):
    assert tw.ширина("lili", шрифт, вес=вес) < tw.ширина("mwmw", шрифт, вес=вес)


@pytest.mark.parametrize("текст, px", [
    # Замер задачи #792 по таблице Verdana 11px; поля 5 + 5.
    ("coverage / all (os)", 113), ("windows", 57), ("linux", 36), ("3.14", 35),
])
def test_часть_значка_по_ширине_знаков(текст, px):
    assert pb._ширина(текст) == px


@pytest.mark.parametrize("текст", ["coverage / all (os)", "release / PyPI",
                                   "WWWW", "linux"])
def test_текст_в_части_не_обрезается(текст):
    assert pb._ширина(текст) >= tw.ширина(текст)


def test_знак_вне_таблицы_получает_самую_широкую_ширину():
    """Неизвестный знак не сжимается молча: воздух лучше обрезки (045)."""
    assert tw.ширина("中") == tw.ширина("W") or tw.ширина("中") >= tw.ширина("W")


def test_начертание_берётся_не_легче_запрошенного():
    assert tw.ширина("abc", "Inter", вес=650) == tw.ширина("abc", "Inter", вес=700)


def test_длина_на_k_ловится():
    assert ДЛИНА_НА_K.search("return round(len(текст) * 7.2) + 14")
    assert ДЛИНА_НА_K.search("подпись = len(w[key]) * LABEL_K")
    assert not ДЛИНА_НА_K.search("x = len(текст) + 1")


def test_в_генераторах_картинок_нет_своей_формулы_ширины():
    """Следующий генератор SVG берёт text_width, а не заводит свой k (214)."""
    генераторы = [p for p in SCRIPTS.glob("*.py")
                  if "<svg" in p.read_text(encoding="utf-8")]
    assert {p.name for p in генераторы} >= {"python_badge.py", "consumers_picture.py"}
    for p in генераторы:
        текст = p.read_text(encoding="utf-8")
        assert not ДЛИНА_НА_K.search(текст), f"{p.name}: ширина по числу знаков"
        assert "text_width" in текст, f"{p.name}: ширина не общей функцией"


def test_имя_переносится_по_ширине_а_не_по_числу_знаков():
    """Узкое имя влезает длиннее широкого — счёт знаков этого не различал."""
    assert cp.влезает("l" * 30) and not cp.влезает("W" * 30)
