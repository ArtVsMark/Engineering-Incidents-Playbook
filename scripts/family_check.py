#!/usr/bin/env python3
"""Семейный значок: проект сам сверяет, что он отдаёт и что берёт, со свежими версиями семьи.

Вторая ступень семейного значка (решение владельца 09.10). Первая — форма и
данные: манифест `contracts.json` и сводка `export/family.json` (scripts/family.py).
Здесь — сверка, которую проект делает над СВОИМ деревом: какую версию чего он
держит, проект находит сам, а свежие версии издателей берёт из сводки.

СЕГМЕНТЫ, И У КАЖДОГО СВОЙ ЦВЕТ:
  gives    — отдаю: собранный манифест проекта против опубликованного в сводке
             и против последнего тега дерева; у проекта без манифеста — серый;
  family   — беру у семьи: прибитые `uses: <издатель>/…@<ссылка>` в прогонах и
             действиях, номер ответа `.rules/bindings.json` (`schema`,
             `answers_to`), номер фактов `.github/badges/facts.json`;
  pairs    — беру парно: связи `takes` своего манифеста, номер читается из
             названного файла по названному ключу;
  external — внешние зависимости: на этой ступени НЕ сверяются, сегмент серый
             с причиной, а не зелёный.

ЦВЕТ (решение владельца 09.10). Семья и пары: любое отставание — красный,
минор тоже: выпуск минора у издателя и есть смена контракта. Нечего сверять
или не прочитано — серый (039): серый в зелёный не засчитывается.

ГРАНИЦА, И ОНА НАЗВАНА. Ссылка `@<sha>` сверяется только на равенство с
коммитом последнего выпуска: SHA старого выпуска отсюда не отличить от
произвольного коммита, и он идёт в «отстаёт», а не в «неизвестно» — прибито
не к свежему. Диапазон `contract:` в `.pipeline.yml` не сверяется: у механизмов
нет пока манифеста, и сверять его не с чем.

Реализует правила каталога:
  214 — одна реализация на вопрос: картинку рисует `python_badge.рисунок`,
        ширину — `text_width`, форму манифеста судит `family.изъян_формы`;
  039 — у сегмента три исхода: сходится, отстаёт, неизвестно;
  174 — свои версии проект находит в своём дереве, а не объявляет второй
        копией.

Исходы:
  0 — значок и разбор записаны (какого бы цвета ни был значок);
  2 — не записаны: сводка семьи не прочитана либо не той формы.
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import family
import python_badge
from aggregate_bindings import fetch
# Что такое полный SHA, решает одно место каталога (214).
from collect_proposals import SHA_RE
from version import latest_tag

ROOT = Path(__file__).resolve().parent.parent
#: Сводка семьи по умолчанию — там, где её публикует каталог.
СВОДКА = ("https://raw.githubusercontent.com/ArtVsMark/Engineering-Incidents-Playbook"
          "/badges/export/family.json")
SVG = Path(".github") / "badges" / "family.svg"
РАЗБОР = Path(".github") / "badges" / "family-check.json"
ФАКТЫ = Path(".github") / "badges" / "facts.json"
ОТВЕТ = Path(".rules") / "bindings.json"

#: `uses: владелец/репозиторий[/путь]@ссылка` — шаг или вызов прогона.
USES_RE = re.compile(r"^\s*-?\s*uses:\s*([\w.-]+)/([\w.-]+)(?:/[^@\s]*)?@([^\s#]+)", re.M)

СЕГМЕНТЫ = ("gives", "family", "pairs", "external")
#: Состояние сегмента → цвет. Контраст белого текста — тот же, что у значка
#: Python (python_badge.ЦВЕТ_ПОКРЫТИЯ): зелёный 5,1:1, красный 5,4:1.
ЦВЕТ = {"ok": "#1a7f37", "behind": "#cf222e", "unknown": "#6e7781"}
СЛОВО = {"ok": "ok", "behind": "behind", "unknown": "unknown"}


@dataclass(frozen=True)
class Связь:
    """Одна сверка: что, у кого, что держу я, что свежее, где это лежит."""
    segment: str
    publisher: str
    what: str
    mine: str | None
    latest: str | None
    where: str
    state: str          # ok · behind · unknown
    why: str = ""


def сверить(segment: str, publisher: str, what: str, mine: str | None,
            latest: str | None, where: str, sha: str | None = None) -> Связь:
    """Одна связь: равенство — ok; нет одной из сторон — unknown; иначе behind."""
    if mine is None or latest is None:
        почему = "у издателя не опубликовано" if latest is None else "у себя не найдено"
        return Связь(segment, publisher, what, mine, latest, where, "unknown", почему)
    if mine == latest or (sha is not None and mine == sha):
        return Связь(segment, publisher, what, mine, latest, where, "ok")
    return Связь(segment, publisher, what, mine, latest, where, "behind",
                 "прибит не к последнему выпуску" if SHA_RE.match(mine) else "")


def издатели(сводка: dict) -> dict[str, dict]:
    """Опубликованные манифесты сводки по имени проекта в нижнем регистре."""
    return {p["repo"].lower(): p for p in сводка.get("projects", [])
            if p.get("state") == "published"}


def все_проекты(сводка: dict) -> set[str]:
    return {p["repo"].lower() for p in сводка.get("projects", [])}


def прибитые(root: Path) -> list[tuple[str, str, str]]:
    """(владелец/репозиторий, ссылка, файл) для каждого `uses:` в прогонах и действиях."""
    файлы = [*sorted((root / ".github" / "workflows").glob("*.y*ml")),
             *sorted((root / ".github" / "actions").glob("*/action.y*ml"))]
    out = []
    for f in файлы:
        for m in USES_RE.finditer(f.read_text(encoding="utf-8")):
            out.append((f"{m[1]}/{m[2]}", m[3], str(f.relative_to(root))))
    return out


def _json(путь: Path) -> dict | None:
    try:
        return json.loads(путь.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return None


def семья(root: Path, сводка: dict, свой: str) -> list[Связь]:
    """Что проект берёт у семьи — найдено в его дереве."""
    опубликовано, известны = издатели(сводка), все_проекты(сводка)
    связи: list[Связь] = []
    for repo, ссылка, где in прибитые(root):
        ключ = repo.lower()
        if ключ == свой.lower() or ключ not in известны:
            continue                       # своё и чужое вне семьи — не здесь
        выпуск = (опубликовано.get(ключ) or {}).get("release") or {}
        связи.append(сверить("family", repo, "release", ссылка, выпуск.get("tag"),
                             где, выпуск.get("sha")))
    каталог = опубликовано.get(family.своё_имя().lower(), {}).get("gives", {})
    if (ответ := _json(root / ОТВЕТ)) is not None:
        связи.append(сверить("family", family.своё_имя(), "bindings",
                             ответ.get("schema"), каталог.get("bindings"), str(ОТВЕТ)))
        связи.append(сверить("family", family.своё_имя(), "export",
                             ответ.get("answers_to"), каталог.get("export"), str(ОТВЕТ)))
    if (факты := _json(root / ФАКТЫ)) is not None:
        витрина = next((p for p in опубликовано.values() if "facts" in p.get("gives", {})), {})
        связи.append(сверить("family", витрина.get("repo", "издатель фактов"), "facts",
                             факты.get("schema"), витрина.get("gives", {}).get("facts"),
                             str(ФАКТЫ)))
    return связи


def пары(root: Path, сводка: dict, манифест: dict | None) -> list[Связь]:
    """Парные связи, объявленные в `takes` своего манифеста."""
    опубликовано = издатели(сводка)
    связи = []
    for t in (манифест or {}).get("takes", []):
        файл = _json(root / t["where"]) or {}
        latest = (опубликовано.get(t["from"].lower()) or {}).get("gives", {}).get(t["contract"])
        связи.append(сверить("pairs", t["from"], t["contract"], файл.get(t["field"]),
                             latest, f"{t['where']}:{t['field']}"))
    return связи


def отдаю(root: Path, сводка: dict, свой: str, манифест: dict | None) -> list[Связь]:
    """Собранный манифест против опубликованного и против тега дерева."""
    if манифест is None:
        return []                          # не издатель — сегмент серый
    опубликован = издатели(сводка).get(свой.lower())
    связи = [сверить("gives", свой, "release", (манифест.get("release") or {}).get("tag"),
                     latest_tag(root), str(family.MANIFEST))]
    for контракт, номер in sorted(манифест.get("gives", {}).items()):
        связи.append(сверить("gives", свой, контракт,
                             (опубликован or {}).get("gives", {}).get(контракт), номер,
                             "опубликованный манифест"))
    return связи


def итог(связи: list[Связь]) -> str:
    """Цвет сегмента: отстаёт хоть одна — красный; неизвестна хоть одна или
    сверять нечего — серый; иначе зелёный."""
    if any(с.state == "behind" for с in связи):
        return "behind"
    if not связи or any(с.state == "unknown" for с in связи):
        return "unknown"
    return "ok"


def разобрать(root: Path, сводка: dict, свой: str) -> dict[str, Any]:
    """Разбор по сегментам: состояние и связи, из которых оно сложилось."""
    манифест = _json(root / family.MANIFEST)
    по_сегментам = {
        "gives": отдаю(root, сводка, свой, манифест),
        "family": семья(root, сводка, свой),
        "pairs": пары(root, сводка, манифест),
        "external": [],
    }
    причины = {"gives": "манифеста нет — проект не издатель" if манифест is None else "",
               "pairs": "парных связей не объявлено" if not по_сегментам["pairs"] else "",
               "external": "внешние зависимости на этой ступени не сверяются"}
    return {"schema": family.FAMILY_SCHEMA, "project": свой,
            "segments": {с: {"state": итог(по_сегментам[с]),
                             "why": причины.get(с, "") if not по_сегментам[с] else "",
                             "links": [asdict(x) for x in по_сегментам[с]]}
                         for с in СЕГМЕНТЫ}}


def надпись(сегмент: str, данные: dict) -> str:
    отстаёт = sum(x["state"] == "behind" for x in данные["links"])
    if данные["state"] == "behind":
        return f"{сегмент} {отстаёт} behind"
    return f"{сегмент} {СЛОВО[данные['state']]}"


def значок(разбор: dict) -> str:
    """Картинка общей функцией значков каталога, а не своей (214)."""
    зоны = [[("family", python_badge.ПОДПИСЬ, "")],
            [(надпись(с, д), ЦВЕТ[д["state"]], д["why"] or д["state"])
             for с, д in разбор["segments"].items()]]
    return python_badge.рисунок(зоны)


def прочесть_сводку(источник: str) -> tuple[dict | None, str]:
    """Сводка семьи по адресу или пути; форма проверяется у каждого проекта."""
    if источник.startswith("https://"):
        doc, err = fetch(источник)
    else:
        doc, err = _json(Path(источник)), None
        if doc is None:
            err = f"не прочитан файл {источник}"
    if err is not None:
        return None, f"сводка семьи {источник}: {err}"
    if not isinstance(doc, dict) or not isinstance(doc.get("projects"), list):
        return None, f"сводка семьи {источник}: нет списка projects"
    return doc, ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--family", default=СВОДКА, help="адрес или путь сводки семьи")
    ap.add_argument("--repo", default=family.своё_имя(), help="владелец/имя проекта")
    args = ap.parse_args(argv)
    сводка, беда = прочесть_сводку(args.family)
    if сводка is None:
        print(f"значок не собран: {беда}", file=sys.stderr)
        return 2
    разбор = разобрать(args.root, сводка, args.repo)
    family.записать(args.root / РАЗБОР, разбор)
    (args.root / SVG).write_text(значок(разбор), encoding="utf-8")
    for с, д in разбор["segments"].items():
        print(f"{надпись(с, д)}" + (f" — {д['why']}" if д["why"] else ""))
        for x in д["links"]:
            if x["state"] != "ok":
                print(f"  · {x['publisher']} {x['what']}: у себя {x['mine']}, "
                      f"свежее {x['latest']} ({x['where']}) {x['why']}".rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
