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


def рисуй(repo):
    out = repo / "out.svg"
    assert cp.main(["--root", str(repo), "--out", str(out)]) == 0
    return out.read_text(encoding="utf-8")


# ── что картинка обязана различать ─────────────────────────────────────────

def test_подключённый_рисуется_тремя_долями(repo):
    svg = рисуй(срез(repo, [подключён("a")]))
    цвета = [r.get("fill") for r in ET.fromstring(svg).iter()
             if r.tag.endswith("rect")]

    assert cp.INK["gate"] in цвета
    assert cp.INK["process-step"] in цвета
    assert cp.INK["none"] in цвета


def test_не_подключён_и_неизвестно_рисуются_по_разному(repo):
    """Приватный ответ недоступен по причине; рисовать его как запущенность —
    выдавать незнание за отказ (027)."""
    svg = рисуй(срез(repo, [
        {"repo": "o/тихий", "state": "не подключён", "trails": 0},
        {"repo": "o/закрытый", "state": "неизвестно", "trails": 0}]))

    assert cp.STATE_INK["не подключён"] != cp.STATE_INK["неизвестно"]
    assert cp.STATE_INK["не подключён"] in svg and cp.STATE_INK["неизвестно"] in svg
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

    assert "5 · 3 · 2" in svg


# ── третий исход ───────────────────────────────────────────────────────────

def test_нет_сводки_это_третий_исход(repo, capsys):
    код = cp.main(["--root", str(repo), "--out", str(repo / "out.svg")])

    assert код == 2
    assert "не прочитан" in capsys.readouterr().err


def test_пустой_реестр_это_третий_исход(repo, capsys):
    write(repo / "export" / "where.json", json.dumps({"consumers": []}))
    write(repo / "export" / "rules.json", json.dumps({"rules": []}))

    код = cp.main(["--root", str(repo), "--out", str(repo / "out.svg")])

    assert код == 2
    assert "ни одного потребителя" in capsys.readouterr().err


def test_нет_экспорта_правил_это_третий_исход(repo, capsys):
    write(repo / "export" / "where.json",
          json.dumps({"consumers": [подключён("a")]}, ensure_ascii=False))

    код = cp.main(["--root", str(repo), "--out", str(repo / "out.svg")])

    assert код == 2
    assert "экспорт правил" in capsys.readouterr().err


# ── живой предмет ──────────────────────────────────────────────────────────

def test_настоящая_сводка_рисуется(repo):
    """Гейт, не прогнанный по живому предмету, — обещание (139)."""
    from pathlib import Path
    корень = Path(cp.ROOT)
    out = repo / "живая.svg"

    assert cp.main(["--root", str(корень), "--out", str(out)]) == 0
    ET.parse(out)
