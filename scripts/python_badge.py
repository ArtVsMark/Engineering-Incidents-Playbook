#!/usr/bin/env python3
"""Единый значок «Python 3.14 3.15 │ linux windows mac │ coverage │ release / PyPI │ version».

ЗОНЫ ВЫПУСКА (решение владельца 1 октября). Покрытие и версия берутся из
файлов значков, которые проект уже собирает (`--coverage-json`,
`--version-json`), а не меряются второй раз (214); цвет покрытия — порогами
coverage_badge.COLORS. «release / PyPI» показывает старшие два числа выпуска:
зелёный — номер на PyPI совпадает с последним выпуском, красный — расходится
(тогда видны оба: `2.8 / 2.7`), серый — проект на PyPI не публикуется (`--pypi`
пуст) или выпусков нет. Версия — последней, синим: это счётчик, не проверка.

ЧАСТИ ПРОВЕРОК — у каждой свой цвет и свой прогон.

ЗАЧЕМ ОДНА КАРТИНКА ИЗ ТРЁХ ЧАСТЕЙ, А НЕ ДВА ЗНАЧКА. Решение владельца
1 октября: подпись «Python» одна, версии стоят рядом, и каждая окрашена
исходом своего прогона. Сама подпись «Python» окрашена исходом основного CI
проекта: зелёная — пройден, красная — нет. Два отдельных значка shields этого не дают: у
`workflow/status` один цвет на картинку, а подпись версии там набрана рукой.

ЧАСТИ ПО ОС СТОЯТ ВСЕГДА, ВСЕ ТРИ. Цвет берётся у работ решающего прогона
основного CI: ОС красная, если на ней упала хоть одна работа, зелёная — если
работы на ней прошли, серая — если на ней не проверяли вовсе. Нужна ли проекту
мультиплатформенность, решает сам проект, а значок только показывает это
честно: каталог гоняется на одном Linux, и windows с mac у него серые —
«не проверено», а не «работает». У проекта с матрицей из трёх ОС сразу видно,
на какой упало.

ТРИ ЦВЕТА, И ТРЕТИЙ — НЕ СЕРЕДИНА МЕЖДУ ДВУМЯ:
  • зелёный — последний прогон с вердиктом на `main` прошёл;
  • красный — последний прогон с вердиктом на `main` упал;
  • серый   — прогона с вердиктом на `main` нет вовсе: проверка не
    проводилась. Отменённый или пропущенный прогон вердиктом не считается
    и пропускается к предыдущему (039) — отмена ничего не проверила.

ВЕРСИИ БЕРУТСЯ У ПРОГОНОВ, А НЕ ПИШУТСЯ ЗДЕСЬ (005). Основная — версия
`python-version` в основном прогоне (`build_facts.CI_WORKFLOW` у каталога,
`--ci` у потребителя), а если версия там идёт матрицей — планка из
`requires-python`, которую гейт версий держит равной прогонам; следующие —
прогоны с `allow-prereleases: true`, которые узнаёт check_python_version.py.
Сдвинется планка — подпись сдвинется сама, без правки значка.

Исходы:
  0 — значок собран;
  2 — не собран: версий в прогонах не нашлось или площадка не ответила.
      Серым это НЕ рисуется: «не смогли спросить» и «не проводилась» — разные
      ответы, и подменять один другим значит соврать на картинке (075).

Реализует правила каталога:
  005 — подпись версии ставит сборка, а не автор;
  039 — три исхода у сборки и три цвета у версии;
  075 — отказ разбора не превращается в серый «не проводилась»;
  209 — основной прогон назван константой build_facts, а не вторым литералом.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_facts  # noqa: E402
import check_python_version as cv  # noqa: E402
import coverage_badge  # noqa: E402
import ghcli  # noqa: E402
from aggregate_bindings import fetch  # noqa: E402

OUT = ROOT / ".github" / "badges" / "python.svg"

#: Цвет и слово для каждого состояния. Слово уходит в подсказку картинки:
#: цвет без слова не читается ни скринридером, ни при слабом различении цветов.
#: ПАЛИТРА — GITHUB (решение владельца 1 октября): те же цвета, которыми
#: площадка рисует свои ✓ и ✗ у проверок. Замер контраста белого текста
#: (WCAG): прежний зелёный shields #4c1 — 2,1:1, новый #2da44e — 3,2:1,
#: серый #9f9f9f → #8c959f — 2,7:1 → 3,0:1, красный #e05d44 → #cf222e —
#: 3,6:1 → 5,4:1. Порога 4,5:1 для мелкого текста зелёный и серый не
#: достигают — как и значки shields; выбран вид, а не порог, и это
#: решение, а не недосмотр.
СОСТОЯНИЯ: dict[str, tuple[str, str]] = {
    "pass": ("#2da44e", "CI пройден"),
    "fail": ("#cf222e", "CI не пройден"),
    "none": ("#8c959f", "проверка не проводилась"),
}
#: Исходы прогона, которые вердикт. Прочие (cancelled, skipped, neutral,
#: stale, action_required) ничего не проверили и пропускаются к предыдущему.
ПРОШЁЛ = {"success"}
#: События, прогон по которым говорит об ОБЩЕЙ ветке. `branch=main` у
#: площадки — это `head_branch`, а он равен `main` и у изменения из форка с
#: веткой `main`: его исход задаёт автор чужого изменения, а не общая ветка.
СВОИ_СОБЫТИЯ = {"push", "schedule", "workflow_dispatch"}
УПАЛ = {"failure", "timed_out", "startup_failure"}

#: Префикс метки раннера → имя ОС на значке. Порядок — порядок частей.
ОС: dict[str, str] = {"ubuntu": "linux", "windows": "windows", "macos": "mac"}

Прогоны = Callable[[str], list[dict]]
Работы = Callable[[int], list[dict]]


class НеОтветила(Exception):
    """Площадка не ответила о прогонах — третий исход, а не серый цвет."""


def версии(root: Path = ROOT, ci: str = build_facts.CI_WORKFLOW
           ) -> list[tuple[str, str]]:
    """(подпись версии, файл прогона): основная первой, следующие за ней."""
    основные = [(f"{a}.{b}", f) for f, (a, b) in cv.in_workflows(root) if f == ci]
    манифест = root / "pyproject.toml"
    if not основные and (root / ".github" / "workflows" / ci).is_file() \
            and манифест.is_file():
        планка = cv.floor(манифест.read_text(encoding="utf-8"))
        if планка:
            основные = [(f"{планка[0]}.{планка[1]}", ci)]
    следующие = [(f"{a}.{b}", f) for f, (a, b) in cv.in_workflows(root, preview=True)]
    return основные[:1] + sorted(set(следующие))


def решающий(runs: list[dict]) -> dict | None:
    """Последний прогон С ВЕРДИКТОМ; отменённые и пропущенные — мимо (039)."""
    for run in sorted(runs, key=lambda r: r.get("created_at") or "", reverse=True):
        if run.get("event", "push") not in СВОИ_СОБЫТИЯ:
            continue
        if run.get("conclusion") in ПРОШЁЛ | УПАЛ:
            return run
    return None


def состояние(runs: list[dict]) -> str:
    """Цвет по последнему прогону с вердиктом; без вердикта — серый."""
    run = решающий(runs)
    if run is None:
        return "none"
    return "pass" if run["conclusion"] in ПРОШЁЛ else "fail"


def по_ос(jobs: list[dict]) -> list[tuple[str, str]]:
    """(ОС, состояние) для всех трёх ОС; без работ на ОС — серый.

    Приоритет fail > pass > none и от порядка работ не зависит: пропущенная
    работа (условный шаг, деплой) не делает серой ОС, на которой проверки
    прошли."""
    вес = {"none": 0, "pass": 1, "fail": 2}
    итог: dict[str, str] = {}
    for job in jobs:
        метки = job.get("labels") or []
        ос = next((имя for префикс, имя in ОС.items()
                   if any(str(м).startswith(префикс) for м in метки)), None)
        if ос is None:
            continue
        исход = job.get("conclusion")
        сост = "fail" if исход in УПАЛ else "pass" if исход in ПРОШЁЛ else "none"
        if вес[сост] >= вес[итог.get(ос, "none")]:
            итог[ос] = сост
    return [(имя, итог.get(имя, "none")) for имя in ОС.values()]


#: Сколько прогонов спрашивается одной страницей (.rules/limits.json).
ПРЕДЕЛ = 30


def прогоны_площадки(файл: str) -> list[dict]:
    """Завершённые прогоны файла на `main`, от новых; одна страница —
    предел объявлен в .rules/limits.json."""
    код, вывод = ghcli.run(
        "api", f"repos/{{owner}}/{{repo}}/actions/workflows/{файл}/runs"
        f"?branch=main&status=completed&per_page={ПРЕДЕЛ}")
    if код != 0:
        raise НеОтветила(вывод)
    return json.loads(вывод).get("workflow_runs", [])


def работы_площадки(run_id: int) -> list[dict]:
    """Все работы прогона — постранично (212)."""
    код, работы, почему = ghcli.список(
        f"repos/{{owner}}/{{repo}}/actions/runs/{run_id}/jobs", ".jobs[]")
    if код != 0:
        raise НеОтветила(почему)
    return работы


def _ширина(текст: str) -> int:
    """Ширина надписи шрифтом 11px Verdana — приближение, как у shields."""
    return round(len(текст) * 7.2) + 14


#: Часть значка: надпись, цвет, слово для подсказки.
Часть = tuple[str, str, str]

ПОДПИСЬ = "#444d56"
СИНИЙ = "#0969da"
#: Имена цветов shields у порогов покрытия → цвет на картинке. Пороги берутся
#: у coverage_badge.COLORS, а не набираются второй раз (209).
#: Контраст белого текста (WCAG, замер 1 октября): #1a7f37 5,1:1, #2da44e
#: 3,2:1, #bf8700 3,1:1, #bc4c00 5,0:1, #cf222e 5,4:1. Прежний «green»
#: #4ac26b давал 2,3:1 — хуже, чем #2da44e, и заменён тёмным #1a7f37 у
#: верхнего порога, чтобы два зелёных различались, не теряя текста.
ЦВЕТ_ПОКРЫТИЯ = {"brightgreen": "#1a7f37", "green": "#2da44e", "yellow": "#bf8700",
                 "orange": "#bc4c00", "red": "#cf222e"}
#: Зазор между зонами: внутри зоны части разделены тонкой линией, а зоны —
#: просветом, чтобы «проверки», «покрытие» и «выпуск» читались порознь.
ЗАЗОР = 4


def рисунок(зоны: list[list[Часть]]) -> str:
    """Картинка из зон: каждая зона — скруглённая полоса своих частей."""
    подсказка = "; ".join(f"{т}: {слово}" for зона in зоны for т, _, слово in зона if слово)
    # Имена обрезок уникальны для содержимого: две картинки на одной странице
    # (вставленные в HTML, а не через <img>) иначе делят id и режут друг друга.
    метка = hashlib.sha1(repr(зоны).encode("utf-8")).hexdigest()[:8]
    x = 0
    обрезки, прямоугольники, границы, надписи = [], [], [], []
    for н, зона in enumerate(зоны):
        начало = x
        for к, (текст, цвет, _) in enumerate(зона):
            w = _ширина(текст)
            прямоугольники.append(
                f'<rect x="{x}" width="{w}" height="20" fill="{цвет}" clip-path="url(#z{метка}{н})"/>')
            if к:
                # Разделитель частей: при трёх зелёных цвет их не различает.
                границы.append(f'<rect x="{x - 1}" width="1" height="20" fill="#fff" fill-opacity=".7"/>')
            центр = x + w / 2
            надписи.append(
                f'<text x="{центр}" y="15" fill="#010101" fill-opacity=".3">{escape(текст)}</text>'
                f'<text x="{центр}" y="14">{escape(текст)}</text>')
            x += w
        обрезки.append(f'<clipPath id="z{метка}{н}"><rect width="{x - начало}" height="20" '
                       f'rx="3" x="{начало}"/></clipPath>')
        x += ЗАЗОР
    ширина = x - ЗАЗОР
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ширина}" height="20" '
        f'role="img" aria-label="{escape(подсказка)}">'
        f"<title>{escape(подсказка)}</title>{''.join(обрезки)}"
        f'<g>{"".join(прямоугольники)}{"".join(границы)}</g>'
        '<g fill="#fff" text-anchor="middle" '
        'font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">'
        f'{"".join(надписи)}</g></svg>\n')


def зоны_проверок(части: list[tuple[str, str]], общий: str) -> list[list[Часть]]:
    """Зона «Python и версии» и зона ОС."""
    def часть(подпись: str, сост: str) -> Часть:
        return (подпись, СОСТОЯНИЯ[сост][0], СОСТОЯНИЯ[сост][1])
    версии_ = [часть(п, с) for п, с in части if п not in ОС.values()]
    платформы = [часть(п, с) for п, с in части if п in ОС.values()]
    зоны = [[часть("Python", общий)] + версии_]
    if платформы:
        зоны.append(платформы)
    return зоны


# ── зоны выпуска: покрытие, релиз / PyPI, версия ───────────────────────────

def из_значка(путь: Path | None) -> str | None:
    """`message` из файла значка shields (endpoint): None — вход не задан.

    Покрытие и версию проект уже считает своими значками; второй замер здесь
    разошёлся бы с ними (214). ЗАДАННЫЙ, НО ОТСУТСТВУЮЩИЙ ИЛИ БИТЫЙ файл — не
    «не измерено», а «не прочитали»: упал шаг, который его пишет. Серым это не
    рисуется — третий исход, и на ветке остаётся прежний значок (075)."""
    if путь is None:
        return None
    try:
        return str(json.loads(путь.read_text(encoding="utf-8")).get("message") or "") or None
    except (OSError, ValueError, AttributeError) as e:
        raise НеОтветила(f"файл значка {путь} не прочитан — {e}") from e


def _процент(сообщение: str | None) -> str | None:
    m = re.match(r"\s*(\d+(?:\.\d+)?)", сообщение or "")
    return m.group(1) if m else None


def зона_покрытия(сообщение: str | None, по_всем: str | None = None) -> list[Часть]:
    """Покрытие основного замера и — если проект его отдаёт — второе число:
    покрытие, сведённое по всем ОС (`72% / 85%`), как расхождение у PyPI.

    Второе число нужно проекту, у которого часть кода исполняется только на
    своей ОС: на одном Linux её не покрыть, и полный охват виден лишь по
    сумме ОС. Цвет — по основному замеру: он и есть обещание проекта."""
    основное = _процент(сообщение)
    if основное is None:
        return [("coverage", ПОДПИСЬ, ""), ("—", СОСТОЯНИЯ["none"][0], "покрытие не измерено")]
    имя = coverage_badge.color(float(основное))
    все = _процент(по_всем)
    if все is None or все == основное:
        return [("coverage", ПОДПИСЬ, ""), (f"{основное}%", ЦВЕТ_ПОКРЫТИЯ[имя], f"покрытие {основное}%")]
    return [("coverage / all (os)", ПОДПИСЬ, ""), (f"{основное}% / {все}%", ЦВЕТ_ПОКРЫТИЯ[имя],
                                        f"покрытие {основное}%, по всем ОС {все}%")]


def зона_версии(версия: str | None) -> list[Часть]:
    if not версия:
        return [("version", ПОДПИСЬ, ""), ("—", СОСТОЯНИЯ["none"][0], "версия не собрана")]
    return [("version", ПОДПИСЬ, ""), (версия, СИНИЙ, f"версия {версия}")]


def коротко(версия: str) -> str:
    """`v1.5.0` → `1.5`: на значке хватает старших двух чисел."""
    m = re.match(r"v?(\d+)\.(\d+)", версия)
    return f"{m.group(1)}.{m.group(2)}" if m else версия.lstrip("v")


def зона_выпуска(релиз: str | None, pypi: str | None, объявлен: bool) -> list[Часть]:
    """«release / PyPI»: зелёный — номера совпадают, красный — расходятся,
    серый — PyPI у проекта нет (или нет ни одного выпуска)."""
    серый = СОСТОЯНИЯ["none"][0]
    подпись = ("release / PyPI", ПОДПИСЬ, "")
    if релиз is None:
        return [подпись, ("—", серый, "выпусков нет")]
    if not объявлен:
        return [подпись, (коротко(релиз), серый, f"выпуск {релиз}, на PyPI не публикуется")]
    # Сравниваются те же два числа, что на значке. Выпуск и PyPI по схеме
    # семьи всегда `X.Y.0`: третье число — счётчик версии, не выпуска
    # (docs/VERSIONING.md), и различаться по нему им нечем (решение
    # владельца 1 октября). Сравнение по показанному заодно не даёт красного
    # над двумя одинаковыми числами.
    if pypi is not None and коротко(релиз) == коротко(pypi):
        return [подпись, (коротко(релиз), СОСТОЯНИЯ["pass"][0], f"выпуск {релиз} совпадает с PyPI")]
    на_pypi = коротко(pypi) if pypi else "—"
    return [подпись, (f"{коротко(релиз)} / {на_pypi}", СОСТОЯНИЯ["fail"][0],
                      f"выпуск {релиз}, на PyPI {pypi or 'пакета нет'}")]


def релиз_площадки() -> str | None:
    """Тег последнего выпуска; None — выпусков нет (404 — ответ, а не молчание)."""
    код, вывод = ghcli.run("api", "repos/{owner}/{repo}/releases/latest", "--jq", ".tag_name")
    if код == 0:
        return вывод.strip() or None
    if "HTTP 404" in вывод:
        return None
    raise НеОтветила(вывод)


#: Ответ PyPI «пакета нет». fetch отдаёт отказ строкой с `str(HTTPError)`,
#: а у неё форма `HTTP Error 404: Not Found` — код читается по этой форме,
#: а не подстрокой «404», которая встретилась бы и в порте, и в адресе.
НЕТ_ПАКЕТА = re.compile(r"\bHTTP Error 404\b")


def версия_pypi(пакет: str) -> str | None:
    """Последняя версия пакета на PyPI; None — пакета там нет."""
    данные, ошибка = fetch(f"https://pypi.org/pypi/{пакет}/json")
    if ошибка is None:
        return str((данные or {}).get("info", {}).get("version") or "") or None
    if НЕТ_ПАКЕТА.search(ошибка):
        return None
    raise НеОтветила(f"PyPI: {ошибка}")


def main(argv: list[str] | None = None, прогоны: Прогоны = прогоны_площадки,
         работы: Работы = работы_площадки,
         релиз: Callable[[], str | None] | None = None,
         pypi: Callable[[str], str | None] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--ci", default=build_facts.CI_WORKFLOW,
                    help="файл основного CI в .github/workflows")
    ap.add_argument("--coverage-json", type=Path,
                    help="файл значка покрытия (shields endpoint) — его message")
    ap.add_argument("--coverage-all-json", type=Path,
                    help="файл значка покрытия, сведённого по всем ОС; есть — "
                         "в зоне покрытия появляется второе число")
    ap.add_argument("--version-json", type=Path,
                    help="файл значка версии (shields endpoint) — его message")
    ap.add_argument("--pypi", default="",
                    help="имя пакета на PyPI; пусто — проект на PyPI не публикуется")
    args = ap.parse_args(argv)

    пары = версии(args.root, args.ci)
    if not пары:
        print(f"значок не собран: в {args.root}/.github/workflows нет ни "
              f"{args.ci} с python-version, ни предварительного "
              "прогона — подписывать нечего (075)", file=sys.stderr)
        return 2
    if args.ci not in {файл for _, файл in пары}:
        # Без основного CI «Python» и ОС красить нечем: серый сказал бы «не
        # проводилась» о прогоне, которого не спрашивали (075).
        print(f"значок не собран: у {args.ci} не нашлось версии — ни "
              "python-version числом, ни requires-python в pyproject.toml. "
              "«Python» и ОС красятся основным CI, и без него значок врал бы "
              "серым (075)", file=sys.stderr)
        return 2
    части: list[tuple[str, str]] = []
    платформы = по_ос([])
    общий = "none"
    for подпись, файл in пары:
        try:
            runs = прогоны(файл)
            if решающий(runs) is None and len(runs) >= ПРЕДЕЛ:
                # Страница полна, а вердикта на ней нет: за краем он может
                # быть. Серый здесь сказал бы «не проводилась» о том, чего
                # не спросили, — это третий исход, а не цвет (075).
                raise НеОтветила(f"в последних {ПРЕДЕЛ} прогонах нет вердикта, "
                                 "а глубже не спрашивали")
            части.append((подпись, состояние(runs)))
            if файл == args.ci:
                общий = состояние(runs)
                run = решающий(runs)
                if run is not None:
                    платформы = по_ос(работы(int(run["id"])))
        except (НеОтветила, ValueError, KeyError) as e:
            print(f"значок не собран: прогоны {файл} у площадки не прочитаны — "
                  f"{e}. Серым это не рисуется: «не спросили» не значит «не "
                  "проводилась» (075)", file=sys.stderr)
            return 2
    части += платформы
    релиз = релиз or релиз_площадки
    pypi = pypi or версия_pypi
    try:
        тег = релиз()
        на_pypi = pypi(args.pypi) if args.pypi and тег else None
    except НеОтветила as e:
        print(f"значок не собран: {e}. Серым это не рисуется (075)", file=sys.stderr)
        return 2
    # Порядок зон — решение владельца 1 октября: проверки, ОС, покрытие,
    # выпуск, и версия последней.
    try:
        покрытие = из_значка(args.coverage_json)
        покрытие_всех = из_значка(args.coverage_all_json)
        версия = из_значка(args.version_json)
    except НеОтветила as e:
        print(f"значок не собран: {e}. Серым это не рисуется (075)", file=sys.stderr)
        return 2
    зоны = зоны_проверок(части, общий) + [
        зона_покрытия(покрытие, покрытие_всех),
        зона_выпуска(тег, на_pypi, bool(args.pypi)),
        зона_версии(версия),
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(рисунок(зоны), encoding="utf-8")
    print("значок: " + "; ".join(f"{т} — {слово}" for зона in зоны for т, _, слово in зона if слово))
    return 0


if __name__ == "__main__":
    sys.exit(main())
