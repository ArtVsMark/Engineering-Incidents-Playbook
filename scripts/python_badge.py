#!/usr/bin/env python3
"""Значок «Python │ 3.14 │ 3.15 │ linux │ windows │ mac»: цвет каждой части — свой прогон.

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
import json
import sys
from collections.abc import Callable
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_facts  # noqa: E402
import check_python_version as cv  # noqa: E402
import ghcli  # noqa: E402

OUT = ROOT / ".github" / "badges" / "python.svg"

#: Цвет и слово для каждого состояния. Слово уходит в подсказку картинки:
#: цвет без слова не читается ни скринридером, ни при слабом различении цветов.
СОСТОЯНИЯ: dict[str, tuple[str, str]] = {
    "pass": ("#4c1", "CI пройден"),
    "fail": ("#e05d44", "CI не пройден"),
    "none": ("#9f9f9f", "проверка не проводилась"),
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


def svg(части: list[tuple[str, str]], общий: str) -> str:
    """Картинка: «Python» цветом основного CI и по сегменту на версию."""
    сегменты = [("Python", СОСТОЯНИЯ[общий][0], СОСТОЯНИЯ[общий][1])] + [
        (подпись, СОСТОЯНИЯ[сост][0], СОСТОЯНИЯ[сост][1]) for подпись, сост in части]
    подсказка = f"Python — {СОСТОЯНИЯ[общий][1]}; " + "; ".join(
        f"{подпись}: {СОСТОЯНИЯ[сост][1]}" for подпись, сост in части)
    x = 0
    прямоугольники, надписи = [], []
    for текст, цвет, _ in сегменты:
        w = _ширина(текст)
        прямоугольники.append(f'<rect x="{x}" width="{w}" height="20" fill="{цвет}"/>')
        центр = x + w / 2
        надписи.append(
            f'<text x="{центр}" y="15" fill="#010101" fill-opacity=".3">{escape(текст)}</text>'
            f'<text x="{центр}" y="14">{escape(текст)}</text>')
        x += w
    # Разделитель между частями: при трёх зелёных цвет их не различает, а
    # «Python │ 3.14 │ 3.15» должно читаться тремя ответами, а не одним.
    границы = []
    край = 0
    for текст, _, _ in сегменты[:-1]:
        край += _ширина(текст)
        границы.append(f'<rect x="{край - 1}" width="1" height="20" fill="#fff" fill-opacity=".7"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{x}" height="20" '
        f'role="img" aria-label="{escape(подсказка)}">'
        f"<title>{escape(подсказка)}</title>"
        '<linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" '
        'stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>'
        f'<clipPath id="r"><rect width="{x}" height="20" rx="3" fill="#fff"/></clipPath>'
        f'<g clip-path="url(#r)">{"".join(прямоугольники)}'
        f'{"".join(границы)}<rect width="{x}" height="20" fill="url(#s)"/></g>'
        '<g fill="#fff" text-anchor="middle" '
        'font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">'
        f'{"".join(надписи)}</g></svg>\n')


def main(argv: list[str] | None = None, прогоны: Прогоны = прогоны_площадки,
         работы: Работы = работы_площадки) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--ci", default=build_facts.CI_WORKFLOW,
                    help="файл основного CI в .github/workflows")
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
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(svg(части, общий), encoding="utf-8")
    print(f"значок Python: основной CI — {СОСТОЯНИЯ[общий][1]}; " + ", ".join(f"{п} — {СОСТОЯНИЯ[с][1]}" for п, с in части))
    return 0


if __name__ == "__main__":
    sys.exit(main())
