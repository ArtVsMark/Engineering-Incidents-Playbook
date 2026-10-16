#!/usr/bin/env python3
"""Текст, который каталог раздаёт окнам, не несёт невидимых символов (#873).

ПРЕДМЕТ — ТО, ЧТО ЧИТАЮТ ОКНА ПОТРЕБИТЕЛЕЙ: записи правил, кандидаты, выгрузка
и навыки. Символ формата Unicode там человек на обзоре не увидит, а окно
соседа прочитает как часть указания. Разбор один — `invisible.py`; второй его
потребитель — сборщик предложений семьи (214).

Исходы: 0 — чисто · 1 — найдено, названы файл, строка и кодовая точка ·
2 — проверять нечего: ни одного файла в охвате (075).

Реализует правила каталога:
  085 — чужой текст — данные; невидимое в раздаваемом тексте не уезжает;
  075 — ноль файлов в охвате — отказ, а не чисто;
  039 — три исхода.
"""

import argparse
import sys
from pathlib import Path

import invisible

ROOT = Path(__file__).resolve().parent.parent
#: Что раздаётся окнам: путь от корня и маска.
ОХВАТ = (("rules", "**/*.md"), ("candidates", "*.md"), ("export", "**/*.json"),
         (".claude/skills", "**/*.md"))


def main(argv: list[str] | None = None) -> int:
    """Проверить охват и напечатать находки."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    файлы = sorted({p for d, маска in ОХВАТ for p in (args.root / d).glob(маска) if p.is_file()})
    if not файлы:
        охват = ", ".join(f"{args.root / d}/{м}" for d, м in ОХВАТ)
        print(f"проверять нечего: в охвате ни одного файла ({охват}) — зеленеть на "
              "этом нельзя (075)", file=sys.stderr)
        return 2
    находки = []
    for путь in файлы:
        for n, строка in enumerate(путь.read_text(encoding="utf-8").splitlines(), 1):
            for _, c in invisible.невидимые(строка):
                находки.append(f"{путь.relative_to(args.root)}:{n}: {invisible.назвать(c)}")
    if находки:
        print("в тексте, который читают окна, есть невидимые символы — человек их "
              "не видит, а модель читает (085, #873):", file=sys.stderr)
        for н in находки:
            print(f"  • {н}", file=sys.stderr)
        return 1
    print(f"невидимых символов нет: файлов {len(файлы)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
