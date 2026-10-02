#!/usr/bin/env python3
"""Предрелизная версия прогона python-next сверена с площадкой, а не с памятью.

ПОМЕТКА «ПРЕДРЕЛИЗ» — УТВЕРЖДЕНИЕ О ЧУЖОМ КАЛЕНДАРЕ (203). Прогон
`python-next.yml` гоняет следующую версию с `allow-prereleases: true`. Пометка
перестаёт быть верной от события в CPython, а не от правки здесь: 3.15 выйдет
стабильной, и прогон будет гонять выпущенную версию, называя её следующей, —
а вопрос о действительно следующей не задаст никто. Гейт версий
(check_python_version.py) сверяет предварительную версию только со СВОИМИ
прогонами; чужого события он не видит по построению.

ИСТОЧНИК — МАНИФЕСТ, ИЗ КОТОРОГО setup-python И БЕРЁТ ПРЕДМЕТ. Вопрос не «что
выпустил CPython», а «что сможет поставить наш прогон»: между этими ответами
бывают дни. Тот же источник и тот же приём, что у модуля `drift` соседа,
Engineering-Pipeline-Mechanisms (сверено 02.10).

ПРЕДУПРЕЖДЕНИЕ, А НЕ ОТКАЗ (203, 051). Находка — источник работы, а не
поломка: выход 3.15 ничего у нас не ломает. Поэтому у находки адресат —
одна задача с маркером (142), а не красное на вкладке прогонов, куда не ходят.
Красным становится только третий исход: сверка не отработала.

Исходы (039):
  0 — предрелизная версия прогона и площадки сходятся;
  1 — разошлись: задача заведена или обновлена (с --apply) либо напечатана;
  2 — сверка не отработала: нет прогона, нет манифеста, трекер не ответил.

Реализует правила каталога:
  203 — пометка о чужом календаре сверяется с живым источником, предупреждением;
  142 — у находки по расписанию есть адресат: задача, а не цвет прогона;
  039 — три исхода: сходится · разошлись · сверка не отработала;
  075 — пустой манифест или нет стабильной ветки — отказ, а не «сходится»;
  158 — третий исход называет предмет отказа;
  214 — разбор прогона, чтение по сети и поиск задачи — общие швы, а не копии.
"""


import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import aggregate_bindings
import check_python_version as cv
import ghcli
import main_red

ROOT = Path(__file__).resolve().parent.parent

#: Манифест версий, которые умеет ставить `actions/setup-python`.
MANIFEST_URL = ("https://raw.githubusercontent.com/actions/python-versions/"
                "main/versions-manifest.json")

#: По этой строке задача находится снова; заголовок правят руками.
MARKER = "<!-- python-next: не удаляйте, по этой строке задача находится снова -->"
TITLE = "Предрелизная версия прогона python-next разошлась с площадкой"

MINOR_RE = re.compile(r"^(\d+)\.(\d+)")


def ветки(manifest: list[Any]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Ветки языка из манифеста: со стабильным выпуском и пока только с пробными.

    Непонятная запись пропускается, а не роняет сверку: манифест — чужой файл,
    и одна странная строка в нём не повод молчать об остальных."""
    стабильные: set[tuple[int, int]] = set()
    все: set[tuple[int, int]] = set()
    for запись in manifest:
        if not isinstance(запись, dict):
            continue
        m = MINOR_RE.match(str(запись.get("version") or ""))
        if not m:
            continue
        ветка = (int(m.group(1)), int(m.group(2)))
        все.add(ветка)
        if запись.get("stable") is True:
            стабильные.add(ветка)
    return sorted(стабильные), sorted(все - стабильные)


def расхождения(следующая: tuple[int, int], manifest: list[Any]) -> list[str]:
    """Что разошлось у предрелизной версии прогона с площадкой. Пусто — сходится.

    Исключение ValueError — манифест без стабильных веток: читать нечего (075)."""
    стабильные, пробные = ветки(manifest)
    if not стабильные:
        raise ValueError("в манифесте нет ни одной стабильной ветки — читать нечего")
    имя = f"{следующая[0]}.{следующая[1]}"
    out: list[str] = []
    if следующая in стабильные:
        дальше = [f"{a}.{b}" for a, b in пробные if (a, b) > следующая]
        куда = (f"навести python-next на {дальше[-1]}" if дальше else
                "следующей предрелизной ветки у площадки пока нет — python-next "
                "снять с пометки или ждать её")
        out.append(f"{имя} уже стабильна, а python-next гоняет её как "
                   f"предрелизную: {куда}; {имя} теперь — вопрос планки, а не прогона")
    elif следующая not in пробные:
        out.append(f"python-next гоняет {имя}, а площадка такой ветки не знает — "
                   "setup-python её не поставит")
    else:
        новее = [f"{a}.{b}" for a, b in пробные if (a, b) > следующая]
        if новее:
            out.append(f"предрелизная у площадки уже {новее[-1]}, а python-next "
                       f"держит {имя}")
    return out


def тело(найдено: list[str], run_url: str) -> str:
    """Тело задачи: маркер, находки, что делать, ссылка на прогон."""
    return "\n".join([
        MARKER, "",
        "Сверка прогона `python-next` с манифестом `actions/python-versions` "
        "(правило 203) нашла расхождение:", "",
        *[f"- {н}" for н in найдено], "",
        "Это источник работы, а не поломка: выход версии у CPython ничего не "
        "ломает. Задача закрывается человеком вместе с правкой прогона.", "",
        f"Источник: {MANIFEST_URL}",
        f"Прогон: {run_url}" if run_url else "",
    ]).rstrip() + "\n"


def записать(body: str) -> tuple[int, str]:
    """Одна задача на расхождение: найти по маркеру и обновить, иначе завести."""
    номер, отказ = main_red.find_issue(MARKER)
    if отказ is not None:
        return 2, f"трекер не прочитан — {отказ}"
    if номер is not None:
        code, out = ghcli.run("api", "--method", "PATCH",
                              f"repos/{{owner}}/{{repo}}/issues/{номер}", "-f", f"body={body}")
        что = f"задача #{номер} обновлена"
    else:
        code, out = ghcli.run("api", "repos/{owner}/{repo}/issues",
                              "-f", f"title={TITLE}", "-f", f"body={body}",
                              "-f", "labels[]=area/gates")
        что = "задача заведена"
    if code != 0:
        return 2, f"трекер не принял запись — {out}"
    return 1, что


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--manifest", type=Path, default=None,
                    help="манифест файлом вместо сети — для набора и разбора")
    ap.add_argument("--run-url", default="", help="ссылка на текущий прогон")
    ap.add_argument("--apply", action="store_true", help="писать в трекер, а не только печатать")
    args = ap.parse_args(argv)

    # ── исход 2 ────────────────────────────────────────────────────────────
    предварительные = cv.in_workflows(args.root, preview=True)
    if not предварительные:
        print("сверка не отработала: в .github/workflows нет прогона с "
              "allow-prereleases — предрелизной версии, которую сверять, нет", file=sys.stderr)
        return 2
    if len({в for _, в in предварительные}) > 1:
        print("сверка не отработала: предрелизных версий несколько — "
              + ", ".join(f"{a}.{b} ({ф})" for ф, (a, b) in предварительные), file=sys.stderr)
        return 2
    файл, следующая = предварительные[0]

    if args.manifest is not None:
        try:
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"сверка не отработала: манифест {args.manifest} не прочитан — {e}",
                  file=sys.stderr)
            return 2
    else:
        manifest, отказ = aggregate_bindings.fetch(MANIFEST_URL, timeout=30)
        if отказ is not None:
            print(f"сверка не отработала: манифест {MANIFEST_URL} {отказ}", file=sys.stderr)
            return 2
    источник = args.manifest or MANIFEST_URL
    if not isinstance(manifest, list) or not manifest:
        print(f"сверка не отработала: манифест {источник} пуст или не список — "
              "сверять не с чем (075)", file=sys.stderr)
        return 2
    try:
        найдено = расхождения(следующая, manifest)
    except ValueError as e:
        print(f"сверка не отработала: манифест {источник}: {e} (075)", file=sys.stderr)
        return 2

    стабильные, пробные = ветки(manifest)
    охват = (f"{файл}: {следующая[0]}.{следующая[1]}; у площадки стабильная "
             f"{стабильные[-1][0]}.{стабильные[-1][1]}, предрелизных "
             + (", ".join(f"{a}.{b}" for a, b in пробные) or "нет"))
    if not найдено:
        print(f"предрелизная версия сходится с площадкой — {охват}")
        return 0

    print(f"предрелизная версия разошлась с площадкой — {охват}:")
    for н in найдено:
        print(f"  • {н}")
    if not args.apply:
        print("--apply не задан: в трекер ничего не пишу")
        return 1
    код, что = записать(тело(найдено, args.run_url))
    print(что if код == 1 else f"сверка не отработала: {что}",
          file=sys.stdout if код == 1 else sys.stderr)
    return код


if __name__ == "__main__":
    sys.exit(main())
