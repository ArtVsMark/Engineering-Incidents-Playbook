#!/usr/bin/env python3
"""Таблица ширин знаков `text_widths.json` — замером файлов шрифта, а не рукой.

Реализует правила каталога:
  214 — один вопрос — одна реализация: таблица, которой считает ширину
        `text_width`, собирается этим сборщиком и больше ничем. До него
        таблица Verdana была вписана рукой и «сверена с пятью надписями»:
        25 ширин из 95 расходились с файлом шрифта, `/` — на 28 % (обзор #795).

Файлов шрифта в дереве нет и не будет: Verdana несвободна, и даже Inter
незачем возить ради сотни чисел. Поэтому в таблице записан ИСТОЧНИК —
версия из таблицы имён и начало sha256 файла, — по нему замер повторяется:

  python scripts/build_text_widths.py \\
      --verdana Verdana.TTF \\
      --inter /usr/share/fonts/opentype/inter

Verdana — `Verdana.TTF` из corefonts (`verdan32.exe`, cabextract). Inter —
Inter-{Regular,Medium,SemiBold,Bold,ExtraBold}.otf из пакета fonts-inter.
Нужен fontTools; в зависимости набора он не входит — сборщик зовут руками.

Исходы:
  0 — таблица записана (или совпала с записанной при --check);
  1 — --check: записанная таблица расходится с замером;
  2 — замер не сделан (нет fontTools, нет файла, нет начертания).
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from collections.abc import Callable

ТАБЛИЦА = Path(__file__).resolve().parent / "text_widths.json"

#: Знаки, которые надписи каталога выводят: печатная ASCII, кириллица, кавычки,
#: тире и значки вердиктов. Знак, которого нет в файле шрифта, в таблицу не
#: попадает — `text_width` даст ему ширину самого широкого (045).
ЗНАКИ = ("".join(map(chr, range(0x20, 0x7F)))
         + "ЁАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяё"
         + "«»·×–—…№→✓✗")

#: Файл начертания Inter по весу.
INTER = {400: "Inter-Regular.otf", 500: "Inter-Medium.otf",
         600: "Inter-SemiBold.otf", 700: "Inter-Bold.otf",
         800: "Inter-ExtraBold.otf"}


def ширины(карта: dict[int, str], продвижение: Callable[[str], int],
           знаки: str = ЗНАКИ) -> dict[str, int]:
    """Ширина (advance width, hmtx) каждого знака, который есть в карте шрифта."""
    return {з: продвижение(карта[ord(з)]) for з in знаки if ord(з) in карта}


def замер(путь: Path) -> tuple[dict[str, int], int, str]:
    """Ширины знаков, единицы на кегль и источник одного файла шрифта."""
    from fontTools.ttLib import TTFont
    шрифт = TTFont(путь)
    метрики = шрифт["hmtx"].metrics
    отпечаток = hashlib.sha256(путь.read_bytes()).hexdigest()[:12]
    источник = f"{шрифт['name'].getDebugName(5)} {путь.name} sha256:{отпечаток}"
    return (ширины(шрифт.getBestCmap(), lambda g: метрики[g][0]),
            шрифт["head"].unitsPerEm, источник)


def собрать(verdana: Path, inter: Path) -> dict:
    """Таблица целиком: Verdana 400 и пять начертаний Inter."""
    знаки_v, единицы_v, источник_v = замер(verdana)
    веса, источники, единицы_i = {}, [], set()
    for вес, имя in INTER.items():
        знаки, единицы, источник = замер(inter / имя)
        веса[str(вес)] = знаки
        источники.append(источник)
        единицы_i.add(единицы)
    if len(единицы_i) != 1:
        raise ValueError(f"у начертаний Inter разные единицы: {sorted(единицы_i)}")
    return {
        "about": ("Ширины знаков (advance width) в единицах кегля — источник "
                  "истины для ширины надписей в SVG каталога (#792). Собирается "
                  "scripts/build_text_widths.py замером файлов шрифта, а не "
                  "правится руками."),
        "fonts": {
            "Inter": {"source": "; ".join(источники), "units": единицы_i.pop(),
                      "weights": веса},
            "Verdana": {"source": источник_v, "units": единицы_v,
                        "weights": {"400": знаки_v}},
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--verdana", type=Path, required=True, help="Verdana.TTF")
    ap.add_argument("--inter", type=Path, required=True,
                    help="каталог с Inter-*.otf")
    ap.add_argument("--check", action="store_true",
                    help="сверить записанную таблицу с замером, не записывая")
    args = ap.parse_args(argv)
    try:
        таблица = собрать(args.verdana, args.inter)
    except ImportError:
        print(f"замер не сделан: {Path(__file__).name} нужен fontTools "
              "(pip install fonttools)",
              file=sys.stderr)
        return 2
    except (OSError, KeyError, ValueError) as e:
        print(f"замер не сделан: {e}", file=sys.stderr)
        return 2
    текст = json.dumps(таблица, ensure_ascii=False, indent=1) + "\n"
    if args.check:
        if ТАБЛИЦА.read_text(encoding="utf-8") != текст:
            print(f"{ТАБЛИЦА} расходится с замером шрифтов", file=sys.stderr)
            return 1
        print(f"{ТАБЛИЦА.name} совпадает с замером")
        return 0
    ТАБЛИЦА.write_text(текст, encoding="utf-8")
    print(f"записано: {ТАБЛИЦА.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
