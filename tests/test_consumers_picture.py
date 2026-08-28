"""Картинка «чем держится правило у потребителей»: три состояния, а не два.

Витрина работает на тех, кто ещё не пришёл, и им нужен один взгляд. Но взгляд
врёт легче таблицы: у полосы нет подписи «неизвестно», если её не нарисовать.
Поэтому набор двусторонний (140) и стережёт именно различения, а не то, что
файл получился: подключённый рисуется долями, «не подключён» и «неизвестно» —
разными, а не одним серым (027).

Источник картинки — уже собранный `export/where.json`. Случай на это стоит
отдельно: считать те же числа заново значило бы завести вторую классификацию
одной территории (022), и разошлись бы они молча.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

import consumers_picture as cp
from conftest import write


def срез(repo, consumers, rules=("001", "002")):
    write(repo / "export" / "where.json",
          json.dumps({"consumers": consumers}, ensure_ascii=False))
    write(repo / "export" / "rules.json",
          json.dumps({"rules": [{"id": i} for i in rules]}))
    return repo


def подключён(name, gate=1, step=1, none=1, trails=0):
    return {"repo": f"o/{name}", "state": "подключён", "trails": trails,
            "rules": {"001": "active"},
            "by_mechanism": {"gate": gate, "process-step": step, "none": none}}


def рисуй(repo, dark=False):
    out = repo / "svg"
    assert cp.main(["--root", str(repo), "--out-dir", str(out)]) == 0
    return (out / cp.NAMES[dark]).read_text(encoding="utf-8")


# ── что картинка обязана различать ─────────────────────────────────────────

def test_подключённый_рисуется_тремя_долями(repo):
    svg = рисуй(срез(repo, [подключён("a")]))
    цвета = [r.get("fill") for r in ET.fromstring(svg).iter()
             if r.tag.endswith("rect")]

    assert cp.THEME[False]["gate"] in цвета
    assert cp.THEME[False]["process-step"] in цвета
    assert cp.THEME[False]["none"] in цвета


def test_не_подключён_и_неизвестно_рисуются_по_разному(repo):
    """Приватный ответ недоступен по причине; рисовать его как запущенность —
    выдавать незнание за отказ (027)."""
    svg = рисуй(срез(repo, [
        {"repo": "o/тихий", "state": "не подключён", "trails": 0},
        {"repo": "o/закрытый", "state": "неизвестно", "trails": 0}]))

    t = cp.THEME[False]
    assert t["off"] != t["unknown"]
    assert t["off"] in svg and t["unknown"] in svg
    assert "не подключён" in svg and "неизвестно" in svg


def test_неподключённый_называет_свои_следы(repo):
    """Вклад проекта виден, даже когда канала нет: следы считаются и у него."""
    svg = рисуй(срез(repo, [{"repo": "o/тихий", "state": "не подключён",
                             "trails": 7}]))

    assert "следов 7" in svg


def test_доля_а_не_абсолют(repo):
    """Вопрос картинки — ЧЕМ держится, а не сколько правил.

    У двух проектов с разным объёмом одинаковая раскладка обязана дать
    одинаковые полосы: иначе крупный выглядел бы хуже мелкого при той же доле.
    """
    один = рисуй(срез(repo, [подключён("a", gate=1, step=1, none=2)]))
    два = рисуй(срез(repo, [подключён("a", gate=10, step=10, none=20)]))
    ширины = lambda s: [r.get("width") for r in ET.fromstring(s).iter()
                        if r.tag.endswith("rect")]

    assert ширины(один) == ширины(два)


def test_состав_берётся_из_среза_а_не_из_кода(repo):
    """Новый проект доезжает до картинки без правки кода — включая чужой."""
    svg = рисуй(срез(repo, [подключён("a"), подключён("совершенно-новый")]))

    assert "совершенно-новый" in svg


def test_разметка_экранируется(repo):
    """SVG — это XML: имя с амперсандом не должно ломать документ."""
    svg = рисуй(срез(repo, [{"repo": "o/a&b<c>", "state": "не подключён",
                             "trails": 0}]))
    ET.fromstring(svg)

    assert "a&amp;b&lt;c&gt;" in svg


def test_числа_стоят_рядом_с_полосой(repo):
    """Доля не должна выдавать себя за объём — абсолюты подписаны."""
    svg = рисуй(срез(repo, [подключён("a", gate=5, step=3, none=2)]))

    assert ">5<" in svg and ">3<" in svg and ">2<" in svg


# ── третий исход ───────────────────────────────────────────────────────────

def test_нет_сводки_это_третий_исход(repo, capsys):
    код = cp.main(["--root", str(repo), "--out-dir", str(repo / "svg")])

    assert код == 2
    assert "не прочитан" in capsys.readouterr().err


def test_пустой_реестр_это_третий_исход(repo, capsys):
    write(repo / "export" / "where.json", json.dumps({"consumers": []}))
    write(repo / "export" / "rules.json", json.dumps({"rules": []}))

    код = cp.main(["--root", str(repo), "--out-dir", str(repo / "svg")])

    assert код == 2
    assert "ни одного потребителя" in capsys.readouterr().err


def test_нет_экспорта_правил_это_третий_исход(repo, capsys):
    write(repo / "export" / "where.json",
          json.dumps({"consumers": [подключён("a")]}, ensure_ascii=False))

    код = cp.main(["--root", str(repo), "--out-dir", str(repo / "svg")])

    assert код == 2
    assert "экспорт правил" in capsys.readouterr().err


# ── живой предмет ──────────────────────────────────────────────────────────

def test_настоящая_сводка_рисуется(repo):
    """Гейт, не прогнанный по живому предмету, — обещание (139)."""
    from pathlib import Path
    корень = Path(cp.ROOT)
    out = repo / "живая"

    assert cp.main(["--root", str(корень), "--out-dir", str(out)]) == 0
    for name in cp.NAMES.values():
        ET.parse(out / name)


# ── стиль витрины ──────────────────────────────────────────────────────────
#
# Картинка появляется рядом с баннером и плитками витрины профиля. Своя
# палитра сделала бы её чужой, поэтому значения взяты у неё; случаи ниже
# стерегут ровно то, что делает стиль узнаваемым.

def test_рисуются_обе_темы(repo):
    out = repo / "svg"
    срез(repo, [подключён("a")])

    assert cp.main(["--root", str(repo), "--out-dir", str(out)]) == 0
    assert {p.name for p in out.glob("*.svg")} == set(cp.NAMES.values())


def test_тёмная_и_светлая_отличаются_подложкой(repo):
    срез(repo, [подключён("a")])

    светлая, тёмная = рисуй(repo, dark=False), рисуй(repo, dark=True)

    assert cp.THEME[False]["card"] in светлая
    assert cp.THEME[True]["card"] in тёмная
    assert cp.THEME[True]["card"] not in светлая


def test_карточка_со_скруглением_и_обводкой(repo):
    """Скругление 16 и обводка — то, чем витрина отличается от голого SVG."""
    svg = рисуй(срез(repo, [подключён("a")]))
    карточка = [r for r in ET.fromstring(svg).iter() if r.tag.endswith("rect")][0]

    assert карточка.get("rx") == "16"
    assert карточка.get("stroke") == cp.THEME[False]["stroke"]


def test_шрифт_витрины(repo):
    svg = рисуй(срез(repo, [подключён("a")]))

    assert cp.FONT.startswith("Inter") and f'font-family="{cp.FONT}"' in svg


def test_у_каждой_темы_свои_области_отсечения(repo):
    """Обе темы попадают в один документ витрины: одинаковые id столкнулись бы."""
    срез(repo, [подключён("a")])

    ids = lambda s: {e.get("id") for e in ET.fromstring(s).iter()
                     if e.tag.endswith("clipPath")}

    assert ids(рисуй(repo, dark=False)).isdisjoint(ids(рисуй(repo, dark=True)))
