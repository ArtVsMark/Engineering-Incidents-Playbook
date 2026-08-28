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


def подключён(name, gate=1, step=1, none=1, trails=0, answered=2):
    return {"repo": f"o/{name}", "state": "подключён", "trails": trails,
            "rules": {"001": "active"}, "answered": answered,
            "by_mechanism": {"gate": gate, "process-step": step, "none": none}}


def рисуй(repo, dark=False, lang="ru"):
    out = repo / "svg"
    assert cp.main(["--root", str(repo), "--out-dir", str(out)]) == 0
    return (out / cp.NAMES[(lang, dark)]).read_text(encoding="utf-8")


# ── что картинка обязана различать ─────────────────────────────────────────

def test_подключённый_рисуется_тремя_плашками(repo):
    """Плашка отвечает на один вопрос и читается целиком."""
    svg = рисуй(срез(repo, [подключён("a", gate=5, step=3, none=2)]))
    t = cp.THEME[False]

    for key in ("gate", "process-step", "none"):
        assert cp.LANG["ru"][key] in svg
    for цвет in (t["gate"], t["process-step"], t["none"]):
        assert цвет in svg


def test_неподключённый_получает_одну_плашку_none(repo):
    """Данных нет — плашка называет СОСТОЯНИЕ, а не пустоту."""
    svg = рисуй(срез(repo, [{"repo": "o/тихий", "state": "не подключён",
                             "trails": 0}]))

    assert "none" in svg and "не подключён" in svg
    for key in ("gate", "process-step", "none"):
        assert cp.LANG["ru"][key] not in svg


def test_метрики_идут_до_плашек(repo):
    """Сперва объём, потом чем он держится: полоса молчала об объёме."""
    svg = рисуй(срез(repo, [подключён("a", answered=140, trails=9)]))

    assert svg.index("разобрано") < svg.index(cp.LANG["ru"]["gate"])
    assert ">140<" in svg and ">9<" in svg


def test_плашки_стоят_в_одних_колонках(repo):
    """Сравнивать глазом можно только то, что стоит друг под другом.

    Числа разной длины не должны сдвигать соседнюю колонку: у одного
    проекта трёхзначное, у другого однозначное — плашка «ничем» обязана
    начинаться на одном и том же x.
    """
    svg = рисуй(срез(repo, [подключён("a", gate=5, step=3, none=2),
                            подключён("b", gate=148, step=99, none=140)]))
    xs = [(int(r.get("x")), int(r.get("y"))) for r in ET.fromstring(svg).iter()
          if r.tag.endswith("rect") and r.get("height") == str(cp.PILL_H)]
    первая = sorted(x for x, y in xs if y == min(y for _, y in xs))
    вторая = sorted(x for x, y in xs if y == max(y for _, y in xs))

    assert len(первая) == 3 and первая == вторая


def test_ширина_колонки_берётся_по_самой_широкой_строке(repo):
    """Иначе колонка дышала бы от строки к строке."""
    t = cp.THEME[False]
    строки = cp.rows({"consumers": [подключён("a", gate=5),
                                    подключён("b", gate=148)]})
    w = cp.widths(строки, t, cp.LANG["ru"])

    assert w["gate"] == cp.pill(0, 0, cp.LANG["ru"]["gate"], "148", "#000", t)[1]


def test_у_колонок_есть_подписи(repo):
    """Подпись стоит один раз сверху, а не повторяется в каждой строке."""
    svg = рисуй(срез(repo, [подключён("a"), подключён("b")]))

    assert svg.count("разобрано") == 1 and svg.count("связей") == 1


def test_нечего_показать_рисуется_прочерком_а_не_нулём(repo):
    """Ноль — это измеренное значение, прочерк — его отсутствие (027).

    Проверяется САМА ячейка, а не документ: тире есть и в подзаголовке, и
    поиск по всему тексту проходил бы при любой поломке.
    """
    svg = рисуй(срез(repo, [{"repo": "o/тихий", "state": "не подключён",
                             "trails": 0}]))
    ячейки = {int(e.get("x")): (e.text or "") for e in ET.fromstring(svg).iter()
              if e.tag.endswith("text") and e.get("font-size") == "22"}

    assert ячейки[cp.COL_ANSWERED] == "—"
    assert ячейки[cp.COL_TRAILS] == "—"


def test_измеренный_ноль_остаётся_нулём(repo):
    """Обратная сторона: у подключённого ноль — это ответ, а не пустота."""
    svg = рисуй(срез(repo, [подключён("a", gate=0, step=0, none=0, answered=0,
                                      trails=0)]))
    ячейки = {int(e.get("x")): (e.text or "") for e in ET.fromstring(svg).iter()
              if e.tag.endswith("text") and e.get("font-size") == "22"}

    assert ячейки[cp.COL_ANSWERED] == "0"


def test_ширина_плашки_растёт_с_текстом(repo):
    """Шрифта у нас нет: ширина считается по знакам, и текст не должен
    упираться в край."""
    узкая, _ = cp.pill(0, 0, "гейт", "5", "#000", cp.THEME[False])
    широкая, _ = cp.pill(0, 0, "шаг процесса", "148", "#000", cp.THEME[False])
    ширина = lambda m: int(m.split('width="')[1].split('"')[0])

    assert ширина(широкая) > ширина(узкая)


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


def test_числа_стоят_в_плашках(repo):
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


def test_в_документе_нет_общих_идентификаторов(repo):
    """Обе темы попадают в один документ витрины: общий id столкнулся бы."""
    срез(repo, [подключён("a")])

    ids = lambda s: {e.get("id") for e in ET.fromstring(s).iter() if e.get("id")}

    assert ids(рисуй(repo, dark=False)) == set()
    assert ids(рисуй(repo, dark=True)) == set()


# ── две витрины, два языка ─────────────────────────────────────────────────
#
# Каталог двуязычен, и картинка — часть витрины, а не приложение к ней.
# Английская версия написана СВОИМИ словами: «held by nothing» это не
# «ничем», и подставлять одно вместо другого значило бы делать вид, что
# языки совпадают по длине — а по ней считается ширина плашки.

def test_рисуются_четыре_файла_язык_на_тему(repo):
    out = repo / "svg"
    срез(repo, [подключён("a")])

    assert cp.main(["--root", str(repo), "--out-dir", str(out)]) == 0
    assert {p.name for p in out.glob("*.svg")} == set(cp.NAMES.values())


def test_в_английской_витрине_нет_кириллицы(repo):
    import re

    svg = рисуй(срез(repo, [подключён("a"),
                            {"repo": "o/b", "state": "не подключён",
                             "trails": 0}]), lang="en")

    assert not re.search(r"[а-яА-ЯёЁ]", svg)


def test_состояние_переводится_а_не_переносится(repo):
    """Сводка одна и по-русски; на английской витрине состояние — своё слово."""
    срез(repo, [{"repo": "o/тихий", "state": "не подключён", "trails": 0}])

    assert "not connected" in рисуй(repo, lang="en")
    assert "не подключён" in рисуй(repo, lang="ru")


def test_незнакомое_состояние_остаётся_как_есть(repo):
    """Догадка хуже непереведённого: неизвестное слово не подменяется."""
    svg = рисуй(срез(repo, [{"repo": "o/x", "state": "что-то новое",
                             "trails": 0}]), lang="en")

    assert "что-то новое" in svg


def test_подпись_для_чтения_с_экрана_на_языке_витрины(repo):
    import re

    брать = lambda s: re.search(r'aria-label="([^"]+)"', s).group(1)
    срез(repo, [подключён("a")])

    assert брать(рисуй(repo, lang="en")) == cp.LANG["en"]["title"]
    assert брать(рисуй(repo, lang="ru")) == cp.LANG["ru"]["title"]


def test_подпись_плашек_стоит_по_центру_группы(repo):
    """Она называет три колонки сразу; у левого края читается как подпись
    только первой."""
    svg = рисуй(срез(repo, [подключён("a", gate=5, step=3, none=2)]))
    шапка = [e for e in ET.fromstring(svg).iter()
             if e.tag.endswith("text") and e.text == cp.LANG["ru"]["held"]][0]
    плашки = [(int(r.get("x")), int(r.get("width")))
              for r in ET.fromstring(svg).iter()
              if r.tag.endswith("rect") and r.get("height") == str(cp.PILL_H)]
    слева = min(x for x, _ in плашки)
    справа = max(x + w for x, w in плашки)

    assert шапка.get("text-anchor") == "middle"
    assert abs(int(шапка.get("x")) - (слева + справа) // 2) <= 6
