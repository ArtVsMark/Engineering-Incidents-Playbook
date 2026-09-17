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


def полоса(consumers, lang="ru"):
    """Полоса колонок того же среза, что рисует картинка.

    КООРДИНАТЫ БЕРУТСЯ У СКРИПТА, А НЕ ВПИСЫВАЮТСЯ СЮДА: вписанное число
    протухает при первой же правке размеров — ровно то, о чём 005. Раньше
    случаи знали `COL_ANSWERED` и `COL_PILLS` в лицо; колонки теперь считаются
    по содержимому, и лицо у них меняется от среза к срезу.
    """
    return cp.полоса(cp.rows({"consumers": consumers}), cp.LANG[lang])


def середина(consumers, key, lang="ru"):
    """Середина колонки: по ней стоят и подпись, и число."""
    return cp.середина(полоса(consumers, lang)[key])


def рисуй(repo, dark=False, lang="ru"):
    out = repo / "svg"
    assert cp.main(["--root", str(repo), "--out-dir", str(out)]) == 0
    return (out / cp.NAMES[(lang, dark)]).read_text(encoding="utf-8")


# ── что картинка обязана различать ─────────────────────────────────────────

def test_подключённый_рисуется_тремя_плашками(repo):
    """Плашка отвечает на один вопрос и читается целиком."""
    svg = рисуй(срез(repo, [подключён("a", gate=5, none=2, **{"process-step": 3})]))
    t = cp.THEME[False]

    for key in ("gate", "process-step", cp.UNVERIFIABLE):
        assert cp.LANG["ru"][key] in svg
    for цвет in (t["gate"], t["process-step"], t[cp.UNVERIFIABLE]):
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

    # `none` своей колонки не имеет: он слагаемое «не проверяется».
    for key in [k for k in cp.MECHANISM_ORDER if k != "none"] + [cp.UNVERIFIABLE]:
        assert cp.LANG["ru"][key] in svg


def test_устаревшее_слово_показано_пока_им_отвечают(repo):
    """Показано при ненулевом ответе — и убрано, когда потребитель перешёл."""
    отвечают = рисуй(срез(repo, [подключён("a", **{"process-step": 4})]))
    assert cp.LANG["ru"]["process-step"] in отвечают

    перешли = рисуй(срез(repo, [подключён("a", **{"process-step": 0})]))
    assert cp.LANG["ru"]["process-step"] not in перешли


def test_nepodklyuchyonnyy_nazyvaet_sostoyanie_a_ne_nol(repo):
    """Данных нет — строка называет СОСТОЯНИЕ, а не пустоту и не ноль.

    Ноль здесь был бы ответом «держит ничем», которого мы не знаем: проект не
    отвечал вовсе. Подписи колонок при этом стоят — они часть шапки, а не
    строки, и их отсутствие читалось бы как «такого вопроса не задавали».
    """
    тихий = [{"repo": "o/тихий", "state": "не подключён", "trails": 0}]
    svg = рисуй(срез(repo, тихий))
    левый = cp.край(полоса(тихий), cp.shown(cp.rows({"consumers": тихий})))[0]
    числа = [e for e in ET.fromstring(svg).iter()
             if e.tag.endswith("text") and int(e.get("x")) >= левый
             and e.get("font-size") == str(cp.SIZE["number"])]

    assert "не подключён" in svg
    assert not числа, "у неотвечавшего проекта появились числа механизмов"
    assert cp.LANG["ru"]["gate"] in svg, "подпись колонки исчезла вместе со строкой"


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
    keys = cp.shown(cp.rows({"consumers": данные}))
    левый = cp.край(полоса(данные), keys)[0]
    # Числа блока стоят правее его левого края — по ним и считаем.
    числа = [(int(e.get("x")), int(e.get("y"))) for e in ET.fromstring(svg).iter()
             if e.tag.endswith("text") and int(e.get("x")) >= левый
             and e.get("font-size") == str(cp.SIZE["number"])]
    ряды = sorted({y for _, y in числа})
    первая = sorted(x for x, y in числа if y == ряды[0])
    вторая = sorted(x for x, y in числа if y == ряды[1])

    assert len(первая) == len(keys)
    assert первая == вторая


def test_ширина_колонки_берётся_по_самой_широкой_строке(repo):
    """Иначе колонка дышала бы от строки к строке."""
    данные = [подключён("a", gate=5), подключён("b", gate=148)]

    # Подпись «гейт» короткая, значит ширину задаёт самое широкое число.
    assert полоса(данные)["gate"][1] == int(len("148") * cp.NUMBER_K)


def test_у_колонок_есть_подписи(repo):
    """Подпись стоит один раз сверху, а не повторяется в каждой строке."""
    svg = рисуй(срез(repo, [подключён("a"), подключён("b")]))

    assert svg.count("разобрано") == 1 and svg.count("связей") == 1


def test_нечего_показать_рисуется_прочерком_а_не_нулём(repo):
    """Ноль — это измеренное значение, прочерк — его отсутствие (027).

    Проверяется САМА ячейка, а не документ: тире есть и в подзаголовке, и
    поиск по всему тексту проходил бы при любой поломке.
    """
    тихий = [{"repo": "o/тихий", "state": "не подключён", "trails": 0}]
    svg = рисуй(срез(repo, тихий))
    ячейки = {int(e.get("x")): (e.text or "") for e in ET.fromstring(svg).iter()
              if e.tag.endswith("text") and e.get("font-size") == str(cp.SIZE["number"])}

    assert ячейки[середина(тихий, "answered")] == "—"
    assert ячейки[середина(тихий, "trails")] == "—"


def test_измеренный_ноль_остаётся_нулём(repo):
    """Обратная сторона: у подключённого ноль — это ответ, а не пустота."""
    данные = [подключён("a", gate=0, none=0, answered=0,
                        **{"process-step": 0}, trails=0)]
    svg = рисуй(срез(repo, данные))
    ячейки = {int(e.get("x")): (e.text or "") for e in ET.fromstring(svg).iter()
              if e.tag.endswith("text") and e.get("font-size") == str(cp.SIZE["number"])}

    assert ячейки[середина(данные, "answered")] == "0"


def test_shirinu_zadayot_to_chto_shire(repo):
    """Колонка шире и подписи, и числа: в край не упирается ни то ни другое.

    Двусторонне (140): у короткой подписи ширину держит число, у длинной —
    сама подпись. Одной стороной проверялось бы полмеханизма.
    """
    w = cp.LANG["ru"]
    кол = {k: v[1] for k, v in
           полоса([подключён("a", gate=148, **{"process-step": 1})]).items()}

    assert кол["gate"] == int(len("148") * cp.NUMBER_K)
    assert кол["process-step"] == int(len(w["process-step"]) * cp.LABEL_K)
    assert кол["process-step"] > кол["gate"]


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
    """Гейт, не прогнанный по живому предмету, — обещание (139).

    СВОДКА СОБИРАЕТСЯ ЗДЕСЬ ЖЕ, потому что в дереве её нет: она живёт на ветке
    `badges` (160). Тот же порядок, что и в прогоне публикации — сперва сводка
    из ответов потребителей, потом картинка из сводки.
    """
    import subprocess
    import sys
    from pathlib import Path
    корень = Path(cp.ROOT)
    out = repo / "живая"
    subprocess.run([sys.executable, str(корень / "scripts" / "aggregate_bindings.py")],
                   check=True, capture_output=True, cwd=корень)

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


def test_u_kazhdogo_mehanizma_svoya_podpis_svoim_tsvetom(repo):
    """Подпись стоит НАД своей колонкой и цветом связана со своим числом.

    Прежде слово жило внутри плашки и повторялось в каждой строке. Убрав
    повтор, связь «подпись — значение» держит цвет: без него шапка читалась бы
    как подпись только первой колонки.
    """
    данные = [подключён("a", gate=5, none=2, **{"process-step": 3})]
    svg = рисуй(срез(repo, данные))
    t, w = cp.THEME[False], cp.LANG["ru"]
    тексты = [e for e in ET.fromstring(svg).iter() if e.tag.endswith("text")]

    for key in cp.shown(cp.rows({"consumers": данные})):
        подписи = [e for e in тексты if e.text == w[key]]
        assert len(подписи) == 1, f"подпись «{w[key]}» встречается {len(подписи)} раз"
        assert подписи[0].get("fill") == t[key]


# ── третье число: сколько правил родилось у проекта (задача #192) ──────────

def ячейки_чисел(svg):
    return {int(e.get("x")): (e.text or "") for e in ET.fromstring(svg).iter()
            if e.tag.endswith("text") and e.get("font-size") == str(cp.SIZE["number"])}


def test_rodil_stoit_v_svoey_kolonke(repo):
    """Три числа отвечают на разные вопросы, и путать их колонками нельзя:
    два первых про то, как проект каталог ПОТРЕБЛЯЕТ, третье — чем наполнил."""
    данные = [подключён("a", answered=140, trails=9, born=41)]
    ячейки = ячейки_чисел(рисуй(срез(repo, данные)))

    assert ячейки[середина(данные, "answered")] == "140"
    assert ячейки[середина(данные, "trails")] == "9"
    assert ячейки[середина(данные, "born")] == "41"


def test_rodil_vidno_i_u_nepodklyuchyonnogo(repo):
    """Происхождение записи не зависит от того, ответил ли проект каталогу:
    оно считается по НАШЕМУ корпусу. Прочерк здесь означал бы «не знаем»
    про то, что знаем точно."""
    тихий = [{"repo": "o/тихий", "state": "не подключён", "trails": 0, "born": 3}]
    ячейки = ячейки_чисел(рисуй(срез(repo, тихий)))

    assert ячейки[середина(тихий, "answered")] == "—"
    assert ячейки[середина(тихий, "born")] == "3"


def test_kolonka_rodil_ne_naezzhaet_na_sosedniy_blok(repo):
    """«Родил» закрывает первый блок, и место второму отведено, а не отнято у
    соседа: иначе первое число «чем держится» легло бы поверх трёхзначного."""
    данные = [подключён("a", born=127)]
    band = полоса(данные)
    x, ш = band["born"]
    левый = cp.край(band, cp.shown(cp.rows({"consumers": данные})))[0]

    assert ш >= int(3 * cp.NUMBER_K), "трёхзначное «родил» не поместилось"
    assert левый - (x + ш) == cp.COL_BETWEEN


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

    assert короткие == длинные == середина([подключён("a")], "answered")
    assert полоса([подключён("a")])["answered"][0] == cp.COL_MIN


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

    assert высота == cp.TOP + cp.ROW * 2 + cp.FOOT


# ── два неизвестных — одна колонка ─────────────────────────────────────────
#
# Набор двусторонний (140): он требует, чтобы сумма была видна, И чтобы
# слагаемые СВОИХ колонок не получали. Второе — тот самый откат прежнего
# решения, и без случая на него картинку расщепили бы обратно молча.

def срез_с(none=0, neprimenimo=0, gate=7):
    return {"consumers": [{"repo": "o/r", "state": "подключён", "answered": 10,
                           "rules": {"001": {}},
                           "by_mechanism": {"gate": gate, "none": none},
                           "by_status": {"not-applicable": neprimenimo}}]}


def test_dva_neizvestnyh_skladyvayutsya_v_odnu_kolonku():
    """«Механизма нет» и «к нам не относится» дают один ответ: свидетеля нет."""
    строки = cp.rows(срез_с(none=2, neprimenimo=3))
    assert строки[0][cp.UNVERIFIABLE] == 5
    assert cp.UNVERIFIABLE in cp.shown(строки)


def test_slagaemye_svoih_kolonok_ne_poluchayut():
    """Порознь они обещают определённость, которой нет: 001, 037, 102 и 137
    ушли из «не применимо» в машину — вердикт был опровергнут четырежды."""
    строки = cp.rows(срез_с(none=2, neprimenimo=3))
    колонки = cp.shown(строки)
    assert "none" not in колонки and "not-applicable" not in колонки


def test_kolonka_nichem_stoit_dazhe_nulyom():
    """Ноль здесь — ответ «слепых мест нет», пропуск читался бы иначе (027)."""
    assert cp.UNVERIFIABLE in cp.shown(cp.rows(срез_с(none=0, neprimenimo=0)))


def test_slagaemye_ostayutsya_v_stroke():
    """Сложена ВИТРИНА, а не данные: различение живёт в сводке (021)."""
    строка = cp.rows(срез_с(none=2, neprimenimo=3))[0]
    assert строка["none"] == 2 and строка["not-applicable"] == 3



# ── проекты разделены линией ───────────────────────────────────────────────
#
# Набор двусторонний (140): линий обязано быть ровно на одну меньше, чем
# проектов, — и ни одной, когда проект один. Черта под нижним рядом читается
# как край таблицы, которого нет: карточка уже обведена рамкой.

def линии(svg: str) -> list[int]:
    """Разделители: тонкие прямоугольники во всю ширину карточки."""
    return [int(r.get("y")) for r in ET.fromstring(svg).iter()
            if r.tag.endswith("rect") and r.get("height") == "1"]


def test_proekty_razdeleny_liniey(repo):
    """Строк много — между ними черта, и она одна на пару соседей."""
    данные = [подключён("a"), подключён("b"), подключён("c")]

    assert len(линии(рисуй(срез(repo, данные)))) == len(данные) - 1


def test_pod_poslednim_proektom_linii_net(repo):
    """Один проект — ни одной черты: делить нечего."""
    assert линии(рисуй(срез(repo, [подключён("a")]))) == []


def test_liniya_idyot_mezhdu_ryadami_a_ne_poperyok_teksta(repo):
    """Черта лежит В ПРОСВЕТЕ между строками, а не по их числам."""
    данные = [подключён("a"), подключён("b")]
    svg = рисуй(срез(repo, данные))
    ряды = sorted({int(e.get("y")) for e in ET.fromstring(svg).iter()
                   if e.tag.endswith("text")
                   and e.get("font-size") == str(cp.SIZE["number"])})

    (черта,) = линии(svg)
    assert ряды[0] < черта < ряды[1], f"черта {черта} вне просвета {ряды}"


# ── два блока: правила и чем держится ──────────────────────────────────────
#
# У картинки два вопроса, и разные: сколько у проекта ПРАВИЛ и ЧЕМ он их
# держит. Прежде оба ряда чисел стояли сплошняком, и граница между вопросами
# была видна только тому, кто её уже знает. Набор двусторонний (140): блок
# обязан быть НАЗВАН подписью и ОТДЕЛЁН просветом — и просвет между блоками
# обязан быть заметно больше внутреннего, иначе делить нечем.

def подписи(svg: str, size) -> list[str]:
    return [e.text or "" for e in ET.fromstring(svg).iter()
            if e.tag.endswith("text") and e.get("font-size") == str(size)]


def test_dva_bloka_nazvany_svoimi_podpisyami(repo):
    """Подпись блока стоит над подписями его колонок и ровно один раз."""
    svg = рисуй(срез(repo, [подключён("a"), подключён("b")]))
    w = cp.LANG["ru"]

    assert подписи(svg, cp.SIZE["group"]) == [w["group_rules"], w["group_held"]]


def test_prosvet_mezhdu_blokami_bolshe_chem_vnutri(repo):
    """Блоки разделены ПРОСВЕТОМ, и это он, а не комментарий о нём.

    Обратная сторона тут же: внутри блока просвет ровный и меньший — иначе
    три колонки «правил» читались бы как три одиночки, а не как блок.
    """
    данные = [подключён("a")]
    band = полоса(данные)
    зазор = lambda a, b: band[b][0] - (band[a][0] + band[a][1])
    первый_держится = cp.shown(cp.rows({"consumers": данные}))[0]

    assert зазор("born", первый_держится) == cp.COL_BETWEEN
    assert зазор("answered", "trails") == зазор("trails", "born") == cp.COL_IN
    assert cp.COL_BETWEEN > cp.COL_IN


def test_vtoroy_blok_vydelen_podlozhkoy(repo):
    """«Чем держится» выделен подложкой: она накрывает блок целиком и НЕ
    залезает на соседний — иначе выделяла бы не то, что названа выделять."""
    данные = [подключён("a")]
    svg = рисуй(срез(repo, данные))
    band = полоса(данные)
    слева, справа = cp.край(band, cp.shown(cp.rows({"consumers": данные})))
    подложка = [r for r in ET.fromstring(svg).iter()
                if r.tag.endswith("rect") and r.get("fill") == cp.THEME[False]["tint"]]

    assert len(подложка) == 1, "подложка блока не одна"
    x, ш = int(подложка[0].get("x")), int(подложка[0].get("width"))
    assert x < слева and x + ш > справа, "подложка не накрыла блок целиком"
    born = band["born"]
    assert x > born[0] + born[1], "подложка залезла на блок «правила»"


def test_chislo_stoit_po_seredine_svoey_kolonki(repo):
    """Число и подпись стоят по одной оси — по середине колонки.

    Выключка влево разводила «9» и «154» на два знака вправо, и глаз читал
    это как сдвиг самой колонки.
    """
    данные = [подключён("a", answered=140)]
    svg = рисуй(срез(repo, данные))
    x = середина(данные, "answered")
    по_оси = [e for e in ET.fromstring(svg).iter()
              if e.tag.endswith("text") and e.get("x") == str(x)]

    assert {e.text for e in по_оси} == {"разобрано", "140"}
    assert all(e.get("text-anchor") == "middle" for e in по_оси)


def test_raznaya_dlina_chisla_kolonku_ne_dvigaet(repo):
    """Обратная сторона середины: однозначное и трёхзначное стоят на одной оси."""
    одно = рисуй(срез(repo, [подключён("a", answered=9)]))
    три = рисуй(срез(repo, [подключён("a", answered=140)]))
    ось = lambda s, t: [int(e.get("x")) for e in ET.fromstring(s).iter()
                        if e.tag.endswith("text") and e.text == t][0]

    assert ось(одно, "разобрано") == ось(одно, "9")
    assert ось(три, "разобрано") == ось(три, "140")


# ── подзаголовок стоит под таблицей, а не над ней ──────────────────────────
#
# Он картинку не представляет, а ОГОВАРИВАЕТ: числа — ответы самих проектов,
# не наша оценка их. Место в шапке он занимал у подписей блоков — у того, без
# чего таблица не читается. Двусторонне (140): оговорка ушла ВНИЗ, заголовок
# остался НАВЕРХУ — уехали бы оба, картинка осталась бы без имени.

def нижняя_линия(svg: str, size) -> int:
    return max(int(e.get("y")) for e in ET.fromstring(svg).iter()
               if e.tag.endswith("text") and e.get("font-size") == str(size))


def test_podzagolovok_stoit_pod_poslednim_proektom(repo):
    svg = рисуй(срез(repo, [подключён("a"), подключён("b")]))
    оговорка = [int(e.get("y")) for e in ET.fromstring(svg).iter()
                if e.tag.endswith("text") and (e.text or "").startswith("ответы самих")]

    assert len(оговорка) == 1, "оговорки не нашлось — случай проверяет не то"
    assert оговорка[0] > нижняя_линия(svg, cp.SIZE["number"])


def test_zagolovok_ostalsya_nad_tablitsey(repo):
    svg = рисуй(срез(repo, [подключён("a")]))
    заголовок = [int(e.get("y")) for e in ET.fromstring(svg).iter()
                 if e.tag.endswith("text") and e.text == cp.LANG["ru"]["title"]]

    assert заголовок and заголовок[0] < cp.TOP


# ── «ничем», а не «не проверяется» ─────────────────────────────────────────

def test_slozhennaya_kolonka_nazyvaetsya_nichem():
    """«Не проверяется» обещало проверку, которой нет вовсе: механизма нет —
    значит нечему и краснеть. Слово взято у самого механизма `none`."""
    for язык in ("ru", "en"):
        assert cp.LANG[язык][cp.UNVERIFIABLE] == cp.LANG[язык]["none"]
