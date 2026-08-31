#!/usr/bin/env python3
"""Рисует картинку «чем держится правило у потребителей» для витрины.

ПОЧЕМУ КАРТИНКА, А НЕ ТАБЛИЦА. `export/where.md` отвечает подробно и на
полторы сотни строк. Его читают те, кто уже пришёл; витрина работает на тех,
кто ещё нет, и им нужен один взгляд, а не обход трёх разделов.

ПОЧЕМУ СВОЙ ГЕНЕРАТОР, А НЕ ЧУЖОЙ СЕРВИС. Картинка на витрине от внешнего
сервиса — это зависимость от чужого сервера в самом видном месте и чужое
«почему» рядом с ней (правило 153). Здесь рисуется SVG: он текстовый, диф
читается глазами, и проверить его можно тем же прогоном, что и всё остальное.

СТИЛЬ ВЗЯТ У ВИТРИНЫ ПРОФИЛЯ, А НЕ ПРИДУМАН. Карточка со скруглением 16 и
обводкой, шрифт Inter, палитра площадки и две темы — то же, чем нарисованы
её баннер и плитки (`ArtVsMark/ArtVsMark`, `scripts/build_metrics.py`).
Картинка появляется рядом с ними, и своя палитра сделала бы её чужой.

ЧТО ЗДЕСЬ КОПИЯ, А ЧТО ССЫЛКА. Скопированы ЗНАЧЕНИЯ — цвета, размеры,
скругления: они и есть стиль, и без них картинка не нарисуется. Обоснование,
почему витрина выбрала именно их, не копируется: оно принадлежит ей и
устаревает от правки на той стороне (правило 153).

ИСТОЧНИК ОДИН И УЖЕ СОБРАН — `export/where.json`. Считать те же числа заново
значило бы завести вторую классификацию одной территории, и разошлись бы они
молча (правило 022). Отсюда же берётся состав: появление строки в
`.rules/consumers.json` доезжает до картинки БЕЗ правки кода, включая чужой
проект.

ТРИ СОСТОЯНИЯ, А НЕ ДВА. «Подключён» рисуется полосой из трёх долей;
«не подключён» и «неизвестно» — разные, и это не косметика: приватный ответ
недоступен по объявленной причине, и рисовать его как запущенность значит
выдавать незнание за отказ (правило 027).

Запуск:  python scripts/consumers_picture.py [--out-dir КАТАЛОГ] [--root КОРЕНЬ]
Коды:    0 нарисовано · 2 рисовать нечем
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = "export/where.json"
OUT_DIR = ".github/badges"
#: Четыре файла: язык × тема. Английская витрина — не перевод подписей на
#: лету, а свой набор слов: «held by nothing» это не «ничем», и подставлять
#: одно вместо другого значило бы делать вид, что языки совпадают по длине.
NAMES = {("ru", False): "consumers-light.svg", ("ru", True): "consumers-dark.svg",
         ("en", False): "consumers-en-light.svg", ("en", True): "consumers-en-dark.svg"}

FONT = "Inter,Segoe UI,Helvetica,Arial,sans-serif"

# Словарь механизмов — один на весь проект (правило 022). Импорт, а не копия:
# копия молча отстанет, и первым это увидит читатель картинки.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_bindings import MECHANISM_ORDER  # noqa: E402

#: Устаревшие слова, которые ещё отдают потребители. Показываются, пока ими
#: отвечают: подмена устаревшего слова одним из новых была бы догадкой за
#: потребителя, а картинка обещает его собственный ответ.
LEGACY_KEYS = ("process-step",)
ALL_KEYS = tuple(MECHANISM_ORDER) + LEGACY_KEYS

#: Палитра площадки, тема к теме. Значения те же, что у витрины профиля.
THEME = {
    False: {"card": "#FFFFFF", "stroke": "#D0D7DE", "name": "#1F2328",
            "accent": "#0969DA", "label": "#636C76", "pill": "#F6F8FA",
            "gate": "#0969DA", "pipeline": "#1A7F37", "document": "#8250DF",
            "process-step": "#8250DF", "none": "#CF222E",
            "muted": "#8C959F"},
    True: {"card": "#0D1117", "stroke": "#30363D", "name": "#F0F6FC",
           "accent": "#58A6FF", "label": "#7D8590", "pill": "#161B22",
           "gate": "#58A6FF", "pipeline": "#3FB950", "document": "#A371F7",
           "process-step": "#A371F7", "none": "#F85149",
           "muted": "#8B949E"},
}

#: Ширина — не константа, а следствие: колонок «чем держится» столько,
#: сколькими механизмами отвечают потребители, и вписанное число обрезало бы
#: последнюю плашку молча. MIN_WIDTH держит нижнюю границу, чтобы картинка с
#: одним механизмом не съёживалась в полоску.
MIN_WIDTH, PAD, TOP = 1000, 36, 128
#: Строка проекта: одна на всех, чтобы колонки читались сверху вниз.
ROW, PILL_H = 42, 24

#: Колонки. Фиксированные, а не по содержимому: сравнивать глазом можно
#: только то, что стоит друг под другом. Ради этого же ширина каждой
#: плашечной колонки берётся максимальной по всем строкам — иначе числа
#: разной длины сдвигали бы соседнюю колонку у каждого проекта.
# Третья колонка — «родил»: сколько правил каталога РОДИЛОСЬ у проекта.
# Первые две про то, как проект каталог потребляет; эта — про то, чем он
# его наполнил, и стоит она перед плашками, потому что отвечает на вопрос
# о проекте, а не о механизмах (задача #192).
COL_ANSWERED, COL_TRAILS, COL_BORN, COL_PILLS, PILL_GAP = 300, 434, 556, 678, 10

#: Ширина плашки считается по числу знаков, а не измеряется: шрифта у нас
#: нет, и измерить его нечем. Коэффициенты подобраны с запасом — текст,
#: упёршийся в край, хуже лишних трёх точек воздуха.
LABEL_K, VALUE_K = 6.4, 6.9

#: Слова каждой витрины. Состояния приходят из сводки по-русски — она
#: собирается один раз и для обоих языков; сюда они переводятся при
#: рисовании, а не хранятся дважды (022).
LANG = {
    "ru": {
        "title": "Чем держится правило у потребителей",
        "sub": "ответы самих проектов на каждое из {total} правил каталога — "
               "не наша оценка их",
        "answered": "разобрано", "trails": "связей", "born": "родил",
        "held": "чем держится",
        "gate": "гейт", "pipeline": "конвейер", "document": "документ",
        "process-step": "шаг процесса", "none": "ничем",
        "off": "не подключён", "unknown": "неизвестно", "empty": "none",
    },
    "en": {
        "title": "How rules are enforced across consumers",
        "sub": "each project's own answer on all {total} catalogue rules — "
               "not our assessment of them",
        "answered": "answered", "trails": "trails", "born": "born",
        "held": "held by",
        "gate": "gate", "pipeline": "pipeline", "document": "document",
        "process-step": "process step", "none": "nothing",
        "off": "not connected", "unknown": "unknown", "empty": "none",
    },
}
#: Состояние сводки — по-русски; на английской витрине оно называется своим
#: словом, а незнакомое остаётся как есть, а не подменяется догадкой.
STATE = {"не подключён": "off", "неизвестно": "unknown"}


def rows(doc: dict) -> list[dict]:
    """Строки картинки: имя, состояние и три числа. Порядок — как в реестре."""
    out = []
    for c in doc.get("consumers", []):
        mech = c.get("by_mechanism") or {}
        out.append({
            "name": (c.get("repo") or "?").split("/")[-1],
            "state": c.get("state", ""),
            "connected": bool(c.get("rules")),
            **{k: mech.get(k, 0) for k in ALL_KEYS},
            "trails": c.get("trails", 0),
            "born": c.get("born", 0),
            "answered": c.get("answered") or 0,
        })
    return out


def esc(text: str) -> str:
    """SVG — это XML: пять знаков в нём значат не то, что кажется."""
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;").replace("'", "&apos;"))


def text(x, y, s, fill, size, weight=500, extra=""):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}"{extra}>{esc(s)}</text>')


def pill(x: int, y: int, label: str, value: str, ink: str, t: dict) -> tuple[str, int]:
    """Одна плашка: подпись и значение в скруглённой оправе.

    Форма взята у карточки витрины: высота 24, скругление до половины,
    подложка и обводка темы, подпись приглушённая, значение цветное.
    """
    w = int(13 + len(label) * LABEL_K + 7 + len(value) * VALUE_K + 13)
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{PILL_H}" '
           f'rx="{PILL_H // 2}" fill="{t["pill"]}" stroke="{t["stroke"]}"/>'
           f'<text x="{x + 13}" y="{y + 16}" fill="{t["label"]}" '
           f'font-family="{FONT}" font-size="12" font-weight="600">{esc(label)}'
           f'<tspan fill="{ink}" font-weight="700" dx="7">{esc(value)}</tspan></text>')
    return out, w


def shown(data: list[dict]) -> list[str]:
    """Какие механизмы вообще показывать.

    Канонические — всегда: ноль у гейта это ответ, а не пустая клетка.
    Устаревшее слово — только пока им отвечают: вписанная навсегда колонка
    пережила бы последнего потребителя, и вычеркнуть её было бы некому
    (правило 049).
    """
    used = {k for r in data if r["connected"] for k in ALL_KEYS if r.get(k)}
    return list(MECHANISM_ORDER) + [k for k in LEGACY_KEYS if k in used]


def widths(data: list[dict], t: dict, w: dict,
           keys: list[str] | None = None) -> dict[str, int]:
    """Ширина каждой плашечной колонки — максимум по всем строкам."""
    out = {}
    for key in keys if keys is not None else shown(data):
        out[key] = max(
            [pill(0, 0, w[key], str(r[key]), t[key], t)[1]
             for r in data if r["connected"]] or [0])
    return out


def render(data: list[dict], total: int, dark: bool, lang: str = "ru") -> str:
    """Собирает SVG одной темы: строка на проект, колонки друг под другом.

    ПОЧЕМУ КОЛОНКАМИ, А НЕ БЛОКАМИ. Блок на проект читается по одному
    проекту за раз, а вопрос картинки сравнительный: у кого чем держится и
    насколько это отличается от соседа. Сравнивать глазом можно только то,
    что стоит друг под другом, — поэтому колонки фиксированные, а ширина
    плашечной колонки берётся максимальной по всем строкам: иначе число из
    трёх знаков сдвигало бы соседнюю колонку у одного проекта и не сдвигало
    у другого.

    СКОЛЬКО КОЛОНОК — РЕШАЮТ ДАННЫЕ. Канонические механизмы стоят всегда,
    даже нулём: ноль у гейта — это ответ, а пропущенная колонка читается как
    «такого вопроса не задавали». Устаревшее слово держится ровно пока им
    отвечают.

    ПОЧЕМУ ПОЛОС БОЛЬШЕ НЕТ. Полоса показывала долю и молчала об объёме: у
    проекта с сотней правил и у проекта с десятком она выглядела одинаково.
    Плашка отвечает на один вопрос и читается целиком; доля, которую надо
    мерить глазом, не читается никак.
    """
    t = THEME[dark]
    w = LANG[lang]
    keys = shown(data)
    cols = widths(data, t, w, keys)
    span = sum(cols.values()) + PILL_GAP * (len(keys) - 1)
    width = max(MIN_WIDTH, COL_PILLS + span + PAD)
    height = TOP + ROW * len(data) + PAD - 8
    p = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        # Подпись для чтения с экрана — на языке витрины: она и есть то,
        # что услышит читатель вместо картинки.
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{esc(w["title"])}">',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
        f'rx="16" fill="{t["card"]}" stroke="{t["stroke"]}"/>',
        f'<rect x="{PAD}" y="28" width="46" height="4" rx="2" fill="{t["accent"]}"/>',
        text(PAD, 68, w["title"], t["name"], 29, 800, ' letter-spacing="-0.6"'),
        text(PAD, 94, w["sub"].format(total=total), t["label"], 15, 500),
    ]
    # Шапка колонок: подпись стоит один раз сверху, а не повторяется в
    # каждой строке — повтор съедает ту самую ширину, ради которой колонки.
    for x, word in ((COL_ANSWERED, w["answered"]), (COL_TRAILS, w["trails"]),
                    (COL_BORN, w["born"])):
        p.append(text(x, TOP - 14, word, t["label"], 11.5, 600,
                      ' letter-spacing="0.3"'))
    # Подпись плашек — ПО СЕРЕДИНЕ группы, а не над её левым краем: она
    # называет три колонки сразу, и у левого края читается как подпись
    # только первой.
    p.append(text(COL_PILLS + span // 2, TOP - 14, w["held"], t["label"], 11.5,
                  600, ' letter-spacing="0.3" text-anchor="middle"'))

    y = TOP
    for r in data:
        p.append(text(PAD, y + 17, r["name"], t["name"], 18, 800,
                      ' letter-spacing="-0.4"'))
        # «Родил» показывается и у НЕподключённого проекта: происхождение
        # записи не зависит от того, ответил ли проект каталогу, и прочерк
        # здесь означал бы «не знаем», хотя знаем (правило 027).
        for x, value, live in ((COL_ANSWERED, r["answered"], r["connected"]),
                               (COL_TRAILS, r["trails"], r["trails"] > 0),
                               (COL_BORN, r["born"], r["born"] > 0)):
            cell = str(value) if live else "—"
            p.append(text(x, y + 19, cell,
                          t["accent"] if live else t["muted"], 22, 800))
        x = COL_PILLS
        if r["connected"]:
            for key in keys:
                markup, _ = pill(x, y + 2, w[key], str(r[key]), t[key], t)
                p.append(markup)
                x += cols[key] + PILL_GAP
        else:
            # Данных нет — одна плашка, и она называет состояние, а не пустоту.
            state = w.get(STATE.get(r["state"], ""), r["state"])
            markup, _ = pill(x, y + 2, state, w["empty"], t["muted"], t)
            p.append(markup)
        y += ROW
    p.append("</svg>")
    return "\n".join(p) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args(argv)
    root: Path = args.root
    out_dir = args.out_dir or (root / OUT_DIR)

    # ── исход 2: рисовать нечем ────────────────────────────────────────────
    try:
        doc = json.loads((root / SOURCE).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"рисовать нечем: {SOURCE} не прочитан — {e}", file=sys.stderr)
        return 2
    data = rows(doc)
    if not data:
        print(f"рисовать нечем: в {SOURCE} нет ни одного потребителя",
              file=sys.stderr)
        return 2
    try:
        total = len(json.loads(
            (root / "export" / "rules.json").read_text(encoding="utf-8"))["rules"])
    except (OSError, ValueError, KeyError) as e:
        print(f"рисовать нечем: экспорт правил не прочитан — {e}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    for (lang, dark), name in NAMES.items():
        (out_dir / name).write_text(render(data, total, dark, lang),
                                    encoding="utf-8")
    live = sum(1 for r in data if r["connected"])
    print(f"нарисовано: потребителей {len(data)}, подключено {live}, "
          f"правил {total}; файлов {len(NAMES)} (язык × тема)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
