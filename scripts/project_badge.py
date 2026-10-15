#!/usr/bin/env python3
"""Единый значок проекта в две строки: состояние сверху, правила и семья снизу.

РЕШЕНИЕ ВЛАДЕЛЬЦА 14.10 (#816, #842, #844): одна картинка вместо трёх от двух
рисовальщиков. Код рисунка — у каталога, данные — у проекта: действие
запускается в репозитории проекта, на его дереве, и картинку публикует сам
проект на своей ветке `badges`. Чужих чисел каталог не считает.

ЧТО В СТРОКАХ.
  строка 1 — зоны `python.svg`, которые тем же прогоном нарисовал
             `python_badge.py` и положил рядом в `python.zones.json`:
             CI │ Python │ ОС │ наборы │ coverage │ release / PyPI │ version;
  строка 2 — `rules │ machine N/M · P% │ own │ taken` по ответу проекта
             каталогу `.rules/bindings.json` и `family │ сегменты`, `EIP · EPM`
             по разбору `family-check.json` от `family_check.py`.

ПРАВИЛА И МЕХАНИЗМЫ — ОДНА ЗОНА (владелец 15.10): это один вопрос — сколько
правил держится механизмом, и из них сколько своих и сколько взятых.
Знаменатель — все правила каталога в ответе, а не только действующие
(владелец 15.10): доля говорит о всём каталоге. «Машиной» — механизмы из
`answer_form.МАШИННЫЕ`, ровно то, что каталог считает машинным в сверке
ответов. «Взяты» — машинные с объявленным `origin_kind` `called`, `copied` или
`adapted`.

ОДНА СЕТКА НА ДВЕ СТРОКИ (владелец 15.10). Конец каждой зоны второй строки
совпадает с концом какой-то зоны первой: зона берёт ближайшую границу сверху
не левее своего конца, и короткая сторона расширяет свою последнюю часть.
Последние зоны кончаются вместе — картинка ровная справа. Ширины частей — та
же `python_badge._ширина`, то есть общая функция `text_width` (214).

ВТОРОГО РИСОВАЛЬЩИКА НЕТ (214). Обе строки рисует `python_badge.рисунок`,
вторая — со сдвигом вниз, а не трансформацией: вложенные `<svg>` и группа с
`transform` резали вторую строку в Chromium (проба 15.10). Зоны семьи берутся
у `family_check.зоны`, а не собираются второй раз.

НЕТ ДАННЫХ — СЕРАЯ ЧАСТЬ С ПРИЧИНОЙ, А НЕ БИТАЯ КАРТИНКА (находка d7bd1e6
обзора #834).

Реализует правила каталога:
  214 — одна функция рисунка, одна функция ширины, одна сборка зон семьи;
  174 — числа о проекте — из его дерева, а не посчитаны за него;
  039 — три исхода: значок собран · собран с серым · не собран.

Запуск:
  python scripts/project_badge.py --python-zones P --family-json F --out O [--root R]

Исходы:
  0 — значок собран из всех частей;
  1 — значок собран, но часть данных не прочитана: серое с причиной названо;
  2 — значок не собран: не записан файл.
"""

import argparse
import json
import sys
from pathlib import Path

import answer_form
import family_check
import python_badge

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".github" / "badges" / "project.svg"
ОТВЕТ = Path(".rules") / "bindings.json"
#: Вид происхождения, который значит «механизм взят у другого проекта».
ВЗЯТО = {"called", "copied", "adapted"}
#: Высота строки и просвет между строками — тот же, что между зонами.
СТРОКА = 20
ПРОСВЕТ = python_badge.ЗАЗОР
#: Серый «не знаю» — тот же, что у семейного значка.
СЕРЫЙ = family_check.ЦВЕТ["unknown"]

Зоны = list[list[python_badge.Часть]]


def доля(n: int, m: int) -> str:
    """«n/m · p%», а без знаменателя «n/m · —»: процент о пустом утверждал бы неизвестное."""
    return f"{n}/{m} · {round(100 * n / m)}%" if m else f"{n}/{m} · —"


def цвет_доли(n: int, m: int) -> str:
    """Красный ниже трети, жёлтый ниже двух третей, иначе зелёный; без знаменателя — серый."""
    if not m:
        return СЕРЫЙ
    часть = n / m
    return ("#cf222e" if часть < 0.34 else "#bf8700" if часть < 0.67
            else python_badge.ЦВЕТ_ПОКРЫТИЯ["green"])


def серая(подпись: str, почему: str) -> Зоны:
    """Зона «не прочитано»: подпись и серая часть с причиной в подсказке."""
    return [[(подпись, python_badge.ПОДПИСЬ, ""), ("n/a", СЕРЫЙ, почему)]]


def зоны_правил(ответ: object) -> tuple[Зоны, str]:
    """Зона «rules»: сколько правил держится механизмом, из них свои и взятые."""
    if not isinstance(ответ, dict) or not isinstance(ответ.get("rules"), dict):
        почему = f"ответа каталогу {ОТВЕТ} нет или он не той формы"
        return серая("rules", почему), почему
    все = [r for r in ответ["rules"].values() if isinstance(r, dict)]
    машинные = [r for r in все if r.get("mechanism") in answer_form.МАШИННЫЕ]
    взяты = sum(1 for r in машинные if r.get("origin_kind") in ВЗЯТО)
    return [[
        ("rules", python_badge.ПОДПИСЬ, ""),
        (f"machine {доля(len(машинные), len(все))}", цвет_доли(len(машинные), len(все)),
         "правил каталога держится механизмом"),
        (f"own {len(машинные) - взяты}", python_badge.СИНИЙ, "механизм свой"),
        (f"taken {взяты}", python_badge.СИНИЙ, "механизм взят у другого проекта"),
    ]], ""


def зоны_семьи(путь: Path) -> tuple[Зоны, str]:
    """Зоны семьи без просвета между подписью и сегментами (владелец 15.10)."""
    try:
        подпись, сегменты, *хвост = family_check.зоны(
            json.loads(путь.read_text(encoding="utf-8")))
        return [подпись + сегменты, *хвост], ""
    except (OSError, ValueError, KeyError, TypeError) as exc:
        почему = f"разбор семьи {путь.name} не прочитан: {exc}"
        return серая("family", почему), почему


def зоны_состояния(путь: Path) -> tuple[Зоны, str]:
    """Зоны первой строки из `python.zones.json`, положенного `python_badge.py`."""
    try:
        зоны = json.loads(путь.read_text(encoding="utf-8"))
        if not (isinstance(зоны, list) and зоны and all(
                isinstance(з, list) and з and all(
                    isinstance(ч, list) and len(ч) == 3 and all(isinstance(x, str) for x in ч)
                    for ч in з)
                for з in зоны)):
            raise ValueError("не список зон")
        return [[(ч[0], ч[1], ч[2]) for ч in з] for з in зоны], ""
    except (OSError, ValueError) as exc:
        почему = f"зоны строки состояния {путь.name} не прочитаны: {exc}"
        return серая("CI", почему), почему


def ширины(зоны: Зоны) -> list[int]:
    """Ширина каждой зоны без добавок — общей функцией ширины части."""
    return [sum(python_badge._ширина(т) for т, _, _ in з) for з in зоны]


def выровнять(верх: Зоны, низ: Зоны) -> tuple[dict[int, int], dict[int, int]]:
    """Добавки к последним частям зон: концы зон второй строки ложатся на концы первой."""
    w1, w2 = ширины(верх), ширины(низ)
    д1: dict[int, int] = {}
    д2: dict[int, int] = {}

    def конец(w: list[int], д: dict[int, int], i: int) -> int:
        return sum(w[:i + 1]) + sum(д.get(x, 0) for x in range(i + 1)) + i * python_badge.ЗАЗОР

    k = -1
    for j in range(len(w2)):
        if j == len(w2) - 1:
            k_new = len(w1) - 1                     # последние кончаются вместе
        else:
            свободные = range(k + 1, len(w1) - 1)    # последняя верхняя — для последней
            подходят = [i for i in свободные if конец(w1, д1, i) >= конец(w2, д2, j)]
            if подходят:
                k_new = подходят[0]
            elif len(свободные):
                k_new = свободные[-1]
            else:
                continue
        a, b = конец(w1, д1, k_new), конец(w2, д2, j)
        if a > b:
            д2[j] = д2.get(j, 0) + a - b
        elif b > a:
            д1[k_new] = д1.get(k_new, 0) + b - a
        k = k_new
    return д1, д2


def собрать(root: Path, python_zones: Path, family_json: Path) -> tuple[str, list[str]]:
    """Картинка в две строки и причины серого."""
    верх, почему_1 = зоны_состояния(python_zones)
    try:
        ответ: object = json.loads((root / ОТВЕТ).read_text(encoding="utf-8"))
    except OSError, ValueError:
        ответ = None
    правила, почему_2 = зоны_правил(ответ)
    семья, почему_3 = зоны_семьи(family_json)
    низ = правила + семья
    д1, д2 = выровнять(верх, низ)
    тела, подсказки = [], []
    for зоны, сдвиг, д in ((верх, 0, д1), (низ, СТРОКА + ПРОСВЕТ, д2)):
        svg = python_badge.рисунок(зоны, сдвиг, д)
        тела.append(svg[svg.find("</title>") + len("</title>"):svg.rfind("</svg>")])
        подсказки.append(svg[svg.find("<title>") + len("<title>"):svg.find("</title>")])
    ширина = max(sum(ширины(з)) + sum(д.values()) + (len(з) - 1) * python_badge.ЗАЗОР
                 for з, д in ((верх, д1), (низ, д2)))
    подсказка = "; ".join(подсказки)
    # Подсказки уже экранированы для текста; в атрибуте нужна ещё кавычка.
    в_атрибуте = подсказка.replace('"', "&quot;")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ширина}" '
           f'height="{2 * СТРОКА + ПРОСВЕТ}" role="img" aria-label="{в_атрибуте}">'
           f"<title>{подсказка}</title>{тела[0]}{тела[1]}</svg>\n")
    return svg, [п for п in (почему_1, почему_2, почему_3) if п]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--python-zones", type=Path, required=True)
    ap.add_argument("--family-json", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)
    svg, серое = собрать(args.root, args.python_zones, args.family_json)
    try:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(svg, encoding="utf-8")
    except OSError as exc:
        print(f"значок не собран: {args.out} не записан — {exc.strerror}", file=sys.stderr)
        return 2
    for п in серое:
        print(f"серое: {п}", file=sys.stderr)
    print(f"единый значок записан: {args.out}" + (f", серых частей {len(серое)}" if серое else ""))
    return 1 if серое else 0


if __name__ == "__main__":
    sys.exit(main())
