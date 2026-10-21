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

ОДНА ГРАНИЦА, ДАЛЬШЕ СВОБОДНО (владелец 16.10). Зона `rules` кончается там
же, где зона ОС первой строки (`linux windows mac`); правее обе строки идут
обычным просветом. Короткая сторона добирает разницу поровну на все свои
части — не одной последней: на лесенке версий семьи `3.14 3.15 3.16` у всех
разница — единицы точек, и растяжки не видно.
Общая сетка на все зоны пробовалась 15–16.10 на живых данных каталога,
механизмов и грейдера и не годится: растягивание раздувало `taken 7` и
`ext ✗2`, ровнение пустотой рвало строки дырами, а пустота после зоны её
конец не двигает вовсе (проба 16.10). Ширины частей —
та же `python_badge._ширина`, то есть общая функция `text_width` (214).

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
from build_rules_index import действующие_в_выгрузке

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".github" / "badges" / "project.svg"
ОТВЕТ = Path(".rules") / "bindings.json"
#: Выгрузка каталога — из дерева, откуда исполняется скрипт: у соседа это
#: дерево действия на закреплённом теге, у каталога — он сам. Сети не нужно.
ВЫГРУЗКА = ROOT / "export" / "rules.json"
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


def зоны_правил(ответ: object, в_силе: set[str] | None) -> tuple[Зоны, str]:
    """Зона «rules»: сколько правил держится механизмом, из них свои и взятые.

    Знаменатель — действующие правила каталога: ответ о замещённом законен,
    но правилом оно больше не является, и слияние не «строит» механизмов
    (17.10). `в_силе` None — выгрузка не прочитана, и зона серая с причиной.
    """
    if not isinstance(ответ, dict) or not isinstance(ответ.get("rules"), dict):
        почему = f"ответа каталогу {ОТВЕТ} нет или он не той формы"
        return серая("rules", почему), почему
    if в_силе is None:
        почему = f"выгрузка каталога {ВЫГРУЗКА.name} не прочитана — действующих не отличить"
        return серая("rules", почему), почему
    все = [r for rid, r in ответ["rules"].items()
           if isinstance(r, dict) and rid in в_силе]
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


#: Зона первой строки, под концом которой кончается `rules`: ОС, вторая по
#: порядку у `python_badge.зоны_проверок` (CI │ Python, затем linux windows mac).
ЗОНА_ОС = 1


def выровнять(верх: Зоны, низ: Зоны) -> tuple[dict[int, int], dict[int, int]]:
    """Растяжки зон: конец первой зоны второй строки — под концом ОС первой."""
    if len(верх) <= ЗОНА_ОС or not низ:
        return {}, {}
    w1, w2 = ширины(верх), ширины(низ)
    конец_ос = sum(w1[:ЗОНА_ОС + 1]) + ЗОНА_ОС * python_badge.ЗАЗОР
    if w2[0] < конец_ос:
        return {}, {0: конец_ос - w2[0]}
    if w2[0] > конец_ос:
        return {ЗОНА_ОС: w2[0] - конец_ос}, {}
    return {}, {}


def собрать(root: Path, python_zones: Path, family_json: Path) -> tuple[str, list[str]]:
    """Картинка в две строки и причины серого."""
    верх, почему_1 = зоны_состояния(python_zones)
    try:
        ответ: object = json.loads((root / ОТВЕТ).read_text(encoding="utf-8"))
    except OSError, ValueError:
        ответ = None
    try:
        в_силе: set[str] | None = действующие_в_выгрузке(
            json.loads(ВЫГРУЗКА.read_text(encoding="utf-8")))
    except OSError, ValueError, KeyError:
        в_силе = None
    правила, почему_2 = зоны_правил(ответ, в_силе)
    семья, почему_3 = зоны_семьи(family_json)
    низ = правила + семья
    о1, о2 = выровнять(верх, низ)
    тела, подсказки = [], []
    for зоны, сдвиг, о in ((верх, 0, о1), (низ, СТРОКА + ПРОСВЕТ, о2)):
        svg = python_badge.рисунок(зоны, сдвиг, о)
        тела.append(svg[svg.find("</title>") + len("</title>"):svg.rfind("</svg>")])
        подсказки.append(svg[svg.find("<title>") + len("<title>"):svg.find("</title>")])
    ширина = max(sum(ширины(з)) + sum(о.values()) + (len(з) - 1) * python_badge.ЗАЗОР
                 for з, о in ((верх, о1), (низ, о2)))
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
