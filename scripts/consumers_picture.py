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
NAMES = {False: "consumers-light.svg", True: "consumers-dark.svg"}

FONT = "Inter,Segoe UI,Helvetica,Arial,sans-serif"

#: Палитра площадки, тема к теме. Значения те же, что у витрины профиля.
THEME = {
    False: {"card": "#FFFFFF", "stroke": "#D0D7DE", "name": "#1F2328",
            "accent": "#0969DA", "label": "#636C76", "track": "#F6F8FA",
            "gate": "#0969DA", "process-step": "#8250DF", "none": "#CF222E",
            "unknown": "#8C959F", "off": "#D0D7DE"},
    True: {"card": "#0D1117", "stroke": "#30363D", "name": "#F0F6FC",
           "accent": "#58A6FF", "label": "#7D8590", "track": "#161B22",
           "gate": "#58A6FF", "process-step": "#A371F7", "none": "#F85149",
           "unknown": "#8B949E", "off": "#30363D"},
}

WIDTH, PAD, TOP, ROW = 1000, 36, 132, 34
BAR, BAR_H, NAME_W = 520, 18, 250


def rows(doc: dict) -> list[dict]:
    """Строки картинки: имя, состояние и три числа. Порядок — как в реестре."""
    out = []
    for c in doc.get("consumers", []):
        mech = c.get("by_mechanism") or {}
        out.append({
            "name": (c.get("repo") or "?").split("/")[-1],
            "state": c.get("state", ""),
            "connected": bool(c.get("rules")),
            "gate": mech.get("gate", 0),
            "process-step": mech.get("process-step", 0),
            "none": mech.get("none", 0),
            "trails": c.get("trails", 0),
        })
    return out


def esc(text: str) -> str:
    """SVG — это XML: пять знаков в нём значат не то, что кажется."""
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;").replace("'", "&apos;"))


def text(x, y, s, fill, size, weight=500, extra=""):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}"{extra}>{esc(s)}</text>')


def render(data: list[dict], total: int, dark: bool) -> str:
    """Собирает SVG одной темы. Ширина полосы — доля правил, а не абсолют.

    ДОЛЯ, А НЕ АБСОЛЮТ, потому что вопрос картинки — «чем держится», а не
    «сколько правил». У проекта, ответившего на сто пятьдесят, и у проекта,
    ответившего на девяносто, одинаково важно, какая часть не держится ничем.
    Абсолютные числа стоят рядом, чтобы доля не выдавала себя за объём.
    """
    t = THEME[dark]
    height = TOP + ROW * len(data) + PAD - 6
    p = [
        f'<svg width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Чем держится правило у потребителей каталога">',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" '
        f'rx="16" fill="{t["card"]}" stroke="{t["stroke"]}"/>',
        f'<rect x="{PAD}" y="28" width="46" height="4" rx="2" fill="{t["accent"]}"/>',
        text(PAD, 68, "Чем держится правило у потребителей", t["name"], 29, 800,
             ' letter-spacing="-0.6"'),
        text(PAD, 94, f"правил в каталоге: {total} · доля от признанных "
                      f"действующими у каждого проекта", t["label"], 15, 500),
    ]
    # Легенда — теми же цветами, что и полосы: подпись словом рядом со
    # свидетельством, а не в отдельной таблице.
    x = PAD
    for key, word in (("gate", "гейт"), ("process-step", "шаг процесса"),
                      ("none", "не держится ничем")):
        p.append(f'<rect x="{x}" y="108" width="10" height="10" rx="2" '
                 f'fill="{t[key]}"/>')
        p.append(text(x + 16, 117, word, t["label"], 12.5, 600))
        x += 26 + int(len(word) * 6.6)

    y = TOP
    for r in data:
        p.append(text(PAD, y + 13, r["name"], t["name"], 15, 600))
        bx = PAD + NAME_W
        p.append(f'<rect x="{bx}" y="{y}" width="{BAR}" height="{BAR_H}" '
                 f'rx="{BAR_H // 2}" fill="{t["track"]}"/>')
        if not r["connected"]:
            # Состояние, а не пустое место: обведённая дорожка со словом.
            ink = t["unknown"] if r["state"] == "неизвестно" else t["off"]
            p.append(f'<rect x="{bx}.5" y="{y}.5" width="{BAR - 1}" '
                     f'height="{BAR_H - 1}" rx="{BAR_H // 2}" fill="none" '
                     f'stroke="{ink}" stroke-dasharray="4 3"/>')
            p.append(text(bx + 14, y + 13,
                          f'{r["state"]} · следов {r["trails"]}', ink, 12.5, 600))
        else:
            held = r["gate"] + r["process-step"] + r["none"]
            clip = f'clip{r["name"]}{"d" if dark else "l"}'.replace(".", "")
            p.append(f'<clipPath id="{clip}"><rect x="{bx}" y="{y}" '
                     f'width="{BAR}" height="{BAR_H}" rx="{BAR_H // 2}"/></clipPath>')
            p.append(f'<g clip-path="url(#{clip})">')
            left = bx
            for key in ("gate", "process-step", "none"):
                if not r[key]:
                    continue
                w = max(3, round(BAR * r[key] / held)) if held else 0
                p.append(f'<rect x="{left}" y="{y}" width="{w}" '
                         f'height="{BAR_H}" fill="{t[key]}"/>')
                left += w
            p.append("</g>")
            nx = bx + BAR + 18
            for key in ("gate", "process-step", "none"):
                p.append(text(nx, y + 13, str(r[key]), t[key], 14, 700))
                nx += 14 + len(str(r[key])) * 9
                if key != "none":
                    p.append(text(nx - 11, y + 13, "·", t["label"], 14, 500))
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
    for dark, name in NAMES.items():
        (out_dir / name).write_text(render(data, total, dark), encoding="utf-8")
    live = sum(1 for r in data if r["connected"])
    print(f"нарисовано: потребителей {len(data)}, подключено {live}, "
          f"правил {total}; тем {len(NAMES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
