#!/usr/bin/env python3
"""Рисует картинку «чем держится правило у потребителей» для витрины.

ПОЧЕМУ КАРТИНКА, А НЕ ТАБЛИЦА. `export/where.md` отвечает подробно и на
полторы сотни строк. Его читают те, кто уже пришёл; витрина работает на тех,
кто ещё нет, и им нужен один взгляд, а не обход трёх разделов.

ПОЧЕМУ СВОЙ ГЕНЕРАТОР, А НЕ ЧУЖОЙ СЕРВИС. Картинка на витрине от внешнего
сервиса — это зависимость от чужого сервера в самом видном месте и чужое
«почему» рядом с ней (правило 153). Здесь рисуется SVG: он текстовый, диф
читается глазами, и проверить его можно тем же прогоном, что и всё остальное.

ИСТОЧНИК ОДИН И УЖЕ СОБРАН — `export/where.json`. Считать те же числа заново
значило бы завести вторую классификацию одной территории, и разошлись бы они
молча (правило 022). Отсюда же берётся состав: появление строки в
`.rules/consumers.json` доезжает до картинки БЕЗ правки кода, включая чужой
проект.

ТРИ СОСТОЯНИЯ, А НЕ ДВА. «Подключён» рисуется полосой из трёх долей;
«не подключён» и «неизвестно» — разные, и это не косметика: приватный ответ
недоступен по объявленной причине, и рисовать его как запущенность значит
выдавать незнание за отказ (правило 027).

Запуск:  python scripts/consumers_picture.py [--out ФАЙЛ] [--root КОРЕНЬ]
Коды:    0 нарисовано · 2 рисовать нечем
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = "export/where.json"
OUT = ".github/badges/consumers.svg"

#: Цвета механизмов. Взяты из палитры меток зон, чтобы витрина и трекер
#: говорили об одном одинаково.
INK = {
    "gate": "#1d76db",          # держит машина
    "process-step": "#7057ff",  # держит договорённость
    "none": "#d73a4a",          # не держит ничто
}
STATE_INK = {"не подключён": "#d0d7de", "неизвестно": "#8c959f"}
BG, FG, MUTED, GRID = "#ffffff", "#1f2328", "#656d76", "#d8dee4"
FONT = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"

ROW, PAD, BAR, LABEL_W, TOP = 26, 16, 320, 210, 64


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


def render(data: list[dict], total: int) -> str:
    """Собирает SVG. Ширина полосы — доля правил, а не абсолют.

    ДОЛЯ, А НЕ АБСОЛЮТ, потому что вопрос картинки — «чем держится», а не
    «сколько правил». У проекта, ответившего на сто пятьдесят, и у проекта,
    ответившего на девяносто, одинаково важно, какая часть не держится ничем.
    Абсолютные числа стоят рядом текстом, чтобы доля не выдавала себя за объём.
    """
    height = TOP + ROW * len(data) + PAD
    width = PAD * 2 + LABEL_W + BAR + 120
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Чем держится правило у потребителей каталога">',
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        # БЕЗ БЛОКА <style>, И ЭТО НЕ ВКУС. Картинку показывает витрина, а
        # разметку на пути к читателю чистит площадка; шрифт, заданный
        # атрибутом, переживёт эту чистку, а заданный правилом — не обязан.
        f'<text x="{PAD}" y="26" fill="{FG}" font-family="{FONT}" '
        f'font-size="15" font-weight="600">Чем держится правило '
        f'у потребителей</text>',
        f'<text x="{PAD}" y="44" fill="{MUTED}" font-family="{FONT}" '
        f'font-size="11">правил в каталоге: {total} · синее — гейт, '
        f'фиолетовое — шаг процесса, красное — не держится ничем</text>',
    ]
    y = TOP
    for r in data:
        parts.append(f'<text x="{PAD}" y="{y + 14}" fill="{FG}" '
                     f'font-family="{FONT}" font-size="13">{esc(r["name"])}</text>')
        x = PAD + LABEL_W
        if not r["connected"]:
            # Состояние, а не пустое место: незакрашенная полоса с подписью.
            ink = STATE_INK.get(r["state"], GRID)
            parts.append(f'<rect x="{x}" y="{y + 2}" width="{BAR}" height="14" '
                         f'rx="3" fill="{ink}" fill-opacity="0.35"/>')
            parts.append(f'<text x="{x + 8}" y="{y + 13}" fill="{MUTED}" '
                         f'font-family="{FONT}" font-size="11">'
                         f'{esc(r["state"])} · следов {r["trails"]}</text>')
        else:
            held = r["gate"] + r["process-step"] + r["none"]
            left = x
            for key in ("gate", "process-step", "none"):
                if not r[key]:
                    continue
                w = max(2, round(BAR * r[key] / held)) if held else 0
                parts.append(f'<rect x="{left}" y="{y + 2}" width="{w}" '
                             f'height="14" fill="{INK[key]}"/>')
                left += w
            parts.append(
                f'<text x="{x + BAR + 10}" y="{y + 13}" fill="{MUTED}" '
                f'font-family="{FONT}" font-size="11">'
                f'{r["gate"]} · {r["process-step"]} · {r["none"]}</text>')
        y += ROW
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    root: Path = args.root
    out = args.out or (root / OUT)

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

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data, total), encoding="utf-8")
    live = sum(1 for r in data if r["connected"])
    print(f"нарисовано: потребителей {len(data)}, подключено {live}, "
          f"правил {total} → {out.relative_to(root) if out.is_relative_to(root) else out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
