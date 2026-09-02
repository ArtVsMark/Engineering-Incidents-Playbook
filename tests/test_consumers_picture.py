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
import re
import xml.etree.ElementTree as ET

import consumers_picture as cp
from conftest import write


def срез(repo, consumers, rules=("001", "002")):
    write(repo / "export" / "where.json",
          json.dumps({"consumers": consumers}, ensure_ascii=False))
    write(repo / "export" / "rules.json",
          json.dumps({"rules": [{"id": i} for i in rules]}))
    return repo


def подключён(name, trails=0, born=0, answered=2, **механизмы):
    """Ответ подключённого потребителя. Механизмы — по именам, а не позиции.

    Позиционные `gate, step, none` держались ровно до раскола «шага процесса»:
    словарь вырос, а подпись помощника осталась трёхместной и молча решала за
    случай, каких колонок в картинке нет.
    """
    # ИМЯ, КОТОРОГО НЕТ, — ОТКАЗ, А НЕ ТИХИЙ КЛЮЧ В СЛОВАРЕ. Замер: после
    # перехода на `**механизмы` четыре случая продолжали звать `step=3`, ключ
    # ложился в словарь, картинка рисовала единицу, а набор был зелёным ровно
    # там, где обязан был краснеть.
    чужие = set(механизмы) - set(cp.ALL_KEYS)
    assert not чужие, f"механизма нет в словаре каталога: {sorted(чужие)}"
    mech = {"gate": 1, "process-step": 1, "none": 1}
    mech.update(механизмы)
    return {"repo": f"o/{name}", "state": "подключён", "trails": trails,
            "born": born,
            "rules": {"001": "active"}, "answered": answered,
            "by_mechanism": mech}


def рисуй(repo, dark=False, lang="ru"):
    out = repo / "svg"
    assert cp.main(["--root", str(repo), "--out-dir", str(out)]) == 0
    return (out / cp.NAMES[(lang, dark)]).read_text(encoding="utf-8")


# ── что картинка обязана различать ─────────────────────────────────────────

def test_подключённый_рисуется_тремя_плашками(repo):
    """Плашка отвечает на один вопрос и читается целиком."""
    svg = рисуй(срез(repo, [подключён("a", gate=5, none=2, **{"process-step": 3})]))
    t = cp.THEME[False]

    for key in ("gate", "process-step", "none"):
        assert cp.LANG["ru"][key] in svg
    for цвет in (t["gate"], t["process-step"], t["none"]):
        assert цвет in svg


# ── сколько колонок: канон стоит всегда, устаревшее — пока им отвечают ─────
#
# Набор двусторонний (140). Ноль у канонического механизма — это ОТВЕТ
# («гейтом не держим ни одного»), и колонка обязана стоять. Ноль у
# устаревшего слова — это «им больше не отвечают», и колонка обязана уйти:
# вписанная навсегда, она пережила бы последнего потребителя, и вычеркнуть
# её было бы некому (049).

def test_канонический_механизм_показан_даже_нулём(repo):
    """Ноль у гейта — ответ, а пропуск колонки читается как «не спрашивали»."""
    svg = рисуй(срез(repo, [подключён("a", gate=0, pipeline=0,
                                      document=0, none=7,
                                      **{"process-step": 0})]))

    for key in cp.MECHANISM_ORDER:
        assert cp.LANG["ru"][key] in svg


def test_устаревшее_слово_показано_пока_им_отвечают(repo):
    """Показано при ненулевом ответе — и убрано, когда потребитель перешёл."""
    отвечают = рисуй(срез(repo, [подключён("a", **{"process-step": 4})]))
    assert cp.LANG["ru"]["process-step"] in отвечают

    перешли = рисуй(срез(repo, [подключён("a", **{"process-step": 0})]))
    assert cp.LANG["ru"]["process-step"] not in перешли


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
    данные = [подключён("a", gate=5, **{"process-step": 3}, none=2),
              подключён("b", gate=148, **{"process-step": 99}, none=140)]
    svg = рисуй(срез(repo, данные))
    xs = [(int(r.get("x")), int(r.get("y"))) for r in ET.fromstring(svg).iter()
          if r.tag.endswith("rect") and r.get("height") == str(cp.PILL_H)]
    первая = sorted(x for x, y in xs if y == min(y for _, y in xs))
    вторая = sorted(x for x, y in xs if y == max(y for _, y in xs))

    assert len(первая) == len(cp.shown(cp.rows({"consumers": данные})))
    assert первая == вторая


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
              if e.tag.endswith("text") and e.get("font-size") == str(cp.SIZE["number"])}

    assert ячейки[cp.COL_ANSWERED] == "—"
    assert ячейки[cp.COL_TRAILS] == "—"


def test_измеренный_ноль_остаётся_нулём(repo):
    """Обратная сторона: у подключённого ноль — это ответ, а не пустота."""
    svg = рисуй(срез(repo, [подключён("a", gate=0, none=0, answered=0,
                             **{"process-step": 0},
                                      trails=0)]))
    ячейки = {int(e.get("x")): (e.text or "") for e in ET.fromstring(svg).iter()
              if e.tag.endswith("text") and e.get("font-size") == str(cp.SIZE["number"])}

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
    svg = рисуй(срез(repo, [подключён("a", gate=5, none=2, **{"process-step": 3})]))

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
    svg = рисуй(срез(repo, [подключён("a", gate=5, none=2, **{"process-step": 3})]))
    шапка = [e for e in ET.fromstring(svg).iter()
             if e.tag.endswith("text") and e.text == cp.LANG["ru"]["held"]][0]
    плашки = [(int(r.get("x")), int(r.get("width")))
              for r in ET.fromstring(svg).iter()
              if r.tag.endswith("rect") and r.get("height") == str(cp.PILL_H)]
    слева = min(x for x, _ in плашки)
    справа = max(x + w for x, w in плашки)

    assert шапка.get("text-anchor") == "middle"
    assert abs(int(шапка.get("x")) - (слева + справа) // 2) <= 6


# ── третье число: сколько правил родилось у проекта (задача #192) ──────────

def ячейки_чисел(svg):
    return {int(e.get("x")): (e.text or "") for e in ET.fromstring(svg).iter()
            if e.tag.endswith("text") and e.get("font-size") == str(cp.SIZE["number"])}


def test_rodil_stoit_v_svoey_kolonke(repo):
    """Три числа отвечают на разные вопросы, и путать их колонками нельзя:
    два первых про то, как проект каталог ПОТРЕБЛЯЕТ, третье — чем наполнил."""
    svg = рисуй(срез(repo, [подключён("a", answered=140, trails=9, born=41)]))
    ячейки = ячейки_чисел(svg)

    assert ячейки[cp.COL_ANSWERED] == "140"
    assert ячейки[cp.COL_TRAILS] == "9"
    assert ячейки[cp.COL_BORN] == "41"


def test_rodil_vidno_i_u_nepodklyuchyonnogo(repo):
    """Происхождение записи не зависит от того, ответил ли проект каталогу:
    оно считается по НАШЕМУ корпусу. Прочерк здесь означал бы «не знаем»
    про то, что знаем точно."""
    svg = рисуй(срез(repo, [{"repo": "o/тихий", "state": "не подключён",
                             "trails": 0, "born": 3}]))
    ячейки = ячейки_чисел(svg)

    assert ячейки[cp.COL_ANSWERED] == "—"
    assert ячейки[cp.COL_BORN] == "3"


def test_kolonka_rodil_ne_naezzhaet_na_plashki(repo):
    """Колонка вставлена ПЕРЕД плашками, и место ей отведено, а не отнято у
    соседа: иначе первая плашка легла бы поверх числа."""
    svg = рисуй(срез(repo, [подключён("a", born=127)]))
    p = ET.fromstring(svg)
    плашки = [float(e.get("x")) for e in p.iter()
              if e.tag.endswith("rect") and e.get("rx") == "12"]

    assert плашки, "плашек не нашлось — случай проверяет не то"
    assert min(плашки) >= cp.COL_BORN + 40


# ── длинное имя переносится, а не растягивает картинку ───────────────────
#
# Первая редакция починки двигала колонку по самому длинному имени — картинка
# становилась шире, а значит мельче: витрина показывает её по ширине места.
# Владелец увидел это сразу. Ширина теперь не зависит от имён вовсе.

def первая_колонка(svg: str) -> int:
    # Кегль берётся у скрипта, а не вписан сюда: вписанное здесь число
    # протухает при первой же правке размеров — ровно то, о чём 005.
    m = re.search(rf'<text x="(\d+)" y="\d+"[^>]*font-size="{cp.SIZE["column"]}"', svg)
    assert m, "подписи колонок не нашлись"
    return int(m.group(1))


def имена(svg: str) -> list[str]:
    return re.findall(
        rf'<text x="{cp.PAD}" y="\d+"[^>]*font-size="{cp.SIZE["name"]}"[^>]*>([^<]+)<', svg)


def test_dlinnoe_imya_perenositsya_na_vtoruyu_stroku(repo):
    """Ровно инцидент: `Engineering-Incidents-Playbook` не влезал в просвет."""
    срез(repo, [подключён("Engineering-Incidents-Playbook")])

    куски = имена(рисуй(repo))

    assert len(куски) == 2
    assert "".join(куски) == "Engineering-Incidents-Playbook"


def test_kolonka_ne_dvigaetsya_ot_dliny_imeni(repo):
    """Предмет правила: ширина картинки не зависит от имён."""
    короткие = первая_колонка(рисуй(срез(repo, [подключён("a")])))
    длинные = первая_колонка(рисуй(срез(repo, [подключён("a" * 40)])))

    assert короткие == длинные == cp.COL_MIN


def test_razryv_ishchetsya_po_defisu(repo):
    """Перенос посреди слова читается хуже: разрыв ищется по дефису."""
    assert cp.wrap_name("Engineering-Incidents-Playbook")[0].endswith("-")


def test_bez_defisa_ryvyom_po_mestu(repo):
    """Имя без разрывов рвётся жёстко: это лучше, чем выехать за колонку."""
    куски = cp.wrap_name("a" * 30)

    assert len(куски) == 2 and len(куски[0]) == cp.NAME_LINE


def test_ne_vlezshiy_hvost_obryvaetsya_mnogotochiem(repo):
    """Третьей строки нет, и обрыв НАЗВАН, а не сделан молча (158)."""
    куски = cp.wrap_name("a" * 80)

    assert len(куски) == 2 and куски[1].endswith("…")


def test_perenos_ne_shiryaet_kartinku_a_udlinyaet(repo):
    """Ширина — не рычаг: она у витрины дороже высоты, потому что от неё
    зависит масштаб всего текста."""
    узкое = рисуй(срез(repo, [подключён("a")]))
    широкое = рисуй(срез(repo, [подключён("a" * 40)]))
    ш = lambda s: int(re.search(r'<svg width="(\d+)"', s).group(1))
    в = lambda s: int(re.search(r'height="(\d+)"', s).group(1))

    assert ш(узкое) == ш(широкое)
    assert в(широкое) > в(узкое)


def test_korotkie_imena_vysotu_ne_menyayut(repo):
    """Растёт она только когда перенос действительно случился."""
    svg = рисуй(срез(repo, [подключён("a"), подключён("b")]))
    высота = int(re.search(r'height="(\d+)"', svg).group(1))

    assert высота == cp.TOP + cp.ROW * 2 + cp.PAD - 8
