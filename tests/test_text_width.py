"""Ширина надписи в SVG: одна функция по таблице знаков, а не «длина × k».

Задача #792: значок `python-badge` выходил на 20–25 % шире текста, потому
что каждому знаку давалась ширина 7,2 px, а у картинки потребителей была
своя такая же формула. Набор держит три вещи: таблица различает узкие и
широкие знаки, текст в части значка не обрезается, и в генераторах картинок
нет второго расчёта ширины «len(...) * k».
"""

import ast
import json
import re
from pathlib import Path

import pytest

import build_text_widths as btw
import consumers_picture as cp
import python_badge as pb
import text_width as tw

SCRIPTS = Path(tw.__file__).resolve().parent

#: Имя коэффициента ширины на знак.
КОЭФФИЦИЕНТ_RE = re.compile(r"(?i)(?:^|_)k(?:$|_)|char|знак|ширин|width|px")


def своя_ширина(исходник: str) -> list[str]:
    """Вторая реализация ширины надписи в модуле (214, обзор #795).

    Ищется не форма записи, а то, чем ширина считается без таблицы: число
    знаков, умноженное на коэффициент ширины, — `len(x) * k` в любом порядке,
    напрямую или через имя, которому присвоен `len(...)`; и своя таблица
    ширин — словарь, где больше десяти ключей-знаков. Коэффициент ширины —
    дробное число (px на знак) или имя, которое так и называется (`K`,
    `CHAR`, `ширина`, `px`): `row * len(data)` — высота по числу строк, и
    находкой она не является (051). ГРАНИЦА: коэффициент под другим именем
    и сумма по знакам без словаря разбором не видны.
    """
    дерево = ast.parse(исходник)

    def длина(узел: ast.AST) -> bool:
        return (isinstance(узел, ast.Call) and isinstance(узел.func, ast.Name)
                and узел.func.id == "len")

    из_длины = {ц.id for у in ast.walk(дерево) if isinstance(у, ast.Assign)
                and длина(у.value) for ц in у.targets if isinstance(ц, ast.Name)}
    def знаков(узел: ast.AST) -> bool:
        return длина(узел) or (isinstance(узел, ast.Name) and узел.id in из_длины)

    def коэффициент(узел: ast.AST) -> bool:
        if isinstance(узел, ast.Constant):
            return isinstance(узел.value, float)
        имя = getattr(узел, "id", None) or getattr(узел, "attr", None) or ""
        return bool(КОЭФФИЦИЕНТ_RE.search(имя))

    находки = []
    for у in ast.walk(дерево):
        if isinstance(у, ast.BinOp) and isinstance(у.op, ast.Mult) and (
                знаков(у.left) and коэффициент(у.right)
                or знаков(у.right) and коэффициент(у.left)):
            находки.append(f"строка {у.lineno}: ширина по числу знаков")
        if isinstance(у, ast.Dict) and sum(
                isinstance(к, ast.Constant) and isinstance(к.value, str)
                and len(к.value) == 1 for к in у.keys) > 10:
            находки.append(f"строка {у.lineno}: своя таблица ширин знаков")
    return находки


@pytest.mark.parametrize("исходник", [
    "w = round(len(текст) * 7.2) + 14",
    "n = len(подпись)\nw = n * LABEL_K",
    "w = K * len(t)",
    "ШИРИНЫ = {" + ", ".join(f"'{c}': 7" for c in "abcdefghijkl") + "}",
])
def test_вторая_реализация_ловится(исходник):
    assert своя_ширина(исходник)


@pytest.mark.parametrize("исходник", [
    "x = len(текст) + 1",
    "n = len(строки)\nвысота = 20 + 14",
    "низ = TOP + row * len(data)",
    "цвета = {'ok': 'green', 'bad': 'red'}",
])
def test_не_вторая_реализация_не_ловится(исходник):
    assert not своя_ширина(исходник)


@pytest.mark.parametrize("шрифт, вес", [("Verdana", 400), ("Inter", 800)])
def test_узкая_надпись_уже_широкой_при_равной_длине(шрифт, вес):
    assert tw.ширина("lili", шрифт, вес=вес) < tw.ширина("mwmw", шрифт, вес=вес)


@pytest.mark.parametrize("текст, px", [
    # Сумма advance width из hmtx Verdana 2.35 (sha256 96ed14949ca4) × 11/2048,
    # округлённая, плюс поля 5 + 5. До обзора #795 здесь стояло 113 — число
    # таблицы, подогнанной под эти же надписи, тест её только повторял.
    ("coverage / all (os)", 112), ("windows", 57), ("linux", 36), ("3.14", 35),
])
def test_часть_значка_по_ширине_знаков(текст, px):
    assert pb._ширина(текст) == px


@pytest.mark.parametrize("текст", ["coverage / all (os)", "release / PyPI",
                                   "WWWW", "linux"])
def test_текст_в_части_не_обрезается(текст):
    assert pb._ширина(текст) >= tw.ширина(текст)


def test_знак_вне_таблицы_получает_самую_широкую_ширину():
    """Неизвестный знак не сжимается молча: воздух лучше обрезки (045)."""
    таблица = json.loads(tw.ТАБЛИЦА.read_text(encoding="utf-8"))["fonts"]["Verdana"]
    самый_широкий = max(таблица["weights"]["400"].values()) * 11.0 / таблица["units"]
    assert "中" not in таблица["weights"]["400"]
    assert tw.ширина("中") == pytest.approx(самый_широкий)


def test_таблица_названа_источником_замера():
    """Таблица снята с файлов шрифта, и файл назван так, что замер повторим:
    версия из таблицы имён и начало sha256 (обзор #795)."""
    for имя, шрифт in json.loads(tw.ТАБЛИЦА.read_text(encoding="utf-8"))["fonts"].items():
        assert re.search(r"Version [\d.]+.*sha256:[0-9a-f]{12}", шрифт["source"]), имя


def test_сборщик_берёт_ширину_из_карты_шрифта():
    """Знак есть в карте — ширина его глифа; нет — знак в таблицу не идёт,
    и `text_width` даст ему самую широкую."""
    карта = {ord("a"): "glyph_a", ord("/"): "slash"}
    продвижение = {"glyph_a": 1229, "slash": 930}.__getitem__
    assert btw.ширины(карта, продвижение, "a/中") == {"a": 1229, "/": 930}


def test_начертание_берётся_не_легче_запрошенного():
    assert tw.ширина("abc", "Inter", вес=650) == tw.ширина("abc", "Inter", вес=700)


def test_в_генераторах_картинок_нет_своей_формулы_ширины():
    """Следующий генератор SVG берёт text_width, а не заводит свой k (214)."""
    генераторы = [p for p in SCRIPTS.glob("*.py")
                  if "<svg" in p.read_text(encoding="utf-8")]
    assert {p.name for p in генераторы} >= {"python_badge.py", "consumers_picture.py"}
    for p in генераторы:
        текст = p.read_text(encoding="utf-8")
        assert not своя_ширина(текст), f"{p.name}: {своя_ширина(текст)}"
        assert "text_width" in текст, f"{p.name}: ширина не общей функцией"


def test_имя_переносится_по_ширине_а_не_по_числу_знаков():
    """Узкое имя влезает длиннее широкого — счёт знаков этого не различал."""
    assert cp.влезает("l" * 30) and not cp.влезает("W" * 30)
