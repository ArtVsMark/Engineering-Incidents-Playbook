#!/usr/bin/env python3
"""Контракт семьи: что проект отдаёт и что берёт — манифестом, и их сбор каталогом.

Семейный значок показывает у каждого проекта, сходится ли он с соседями по
контрактам. Сверку делает САМ проект, а каталог даёт форму и данные (решение
владельца 09.10). Здесь — первая половина: форма и сбор.

МАНИФЕСТ (`.github/badges/contracts.json` на ветке `badges` каждого проекта):

  schema   — номер этого формата, FAMILY_SCHEMA;
  project  — `владелец/имя`;
  release  — последний выпуск: {"tag": "v1.10.0", "sha": "<40 знаков>"}
             или null, пока выпусков нет;
  gives    — что проект ОТДАЁТ: {имя контракта: номер}; у кого контрактов
             нет — пустой объект;
  takes    — ПАРНЫЕ связи, которых не найти автоматически: [{"from":
             "владелец/имя", "contract": имя, "where": путь в своём дереве,
             "field": ключ с номером}]. Семейные (действия каталога, шаги
             механизмов, схемы ответа) и внешние связи сверка находит в дереве
             сама и здесь не объявляются.

СВОДКА (`export/family.json` на ветке `badges` каталога) — манифесты всех
проектов реестра `.rules/consumers.json` одним файлом: свежие версии
издателей, с которыми сверяется каждый проект.

СОСТОЯНИЕ У КАЖДОГО ПРОЕКТА ОДНО ИЗ ТРЁХ, И ОНИ НЕ СКЛАДЫВАЮТСЯ (039):
  published  — манифест прочитан и имеет форму;
  absent     — площадка ответила «файла нет» (404): манифест не заведён;
  unreadable — не прочитан (сеть, 5xx, чужая форма), причина названа.
Непрочитанный проект — данные, а не поломка сборки (004): сводка
собирается, и его сегмент у сверяющего будет серым, а не зелёным.

Реализует правила каталога:
  174 — факты о себе публикует сам проект: манифест пишет его владелец, а
        каталог только собирает написанное, не пересказывая;
  049 — номера отдаваемых контрактов берутся у `contracts_now`, а не
        переписываются второй копией;
  039 — у проекта в сводке три состояния, и «не прочитан» не равно «нет».

Исходы:
  0 — файл записан;
  2 — сводка не записана: реестр не прочитан.
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from collections.abc import Callable
from typing import Any

from aggregate_bindings import fetch
from build_rules_index import CATALOGUE_URL, contracts_now
from version import git, latest_tag

ROOT = Path(__file__).resolve().parent.parent

#: Номер формата манифеста и сводки семьи — один на оба: сводка есть список
#: манифестов, и разойтись им не в чем.
FAMILY_SCHEMA = "1.0"
MANIFEST = Path(".github") / "badges" / "contracts.json"
SUMMARY = Path("export") / "family.json"
REGISTRY = Path(".rules") / "consumers.json"
#: Где манифест соседа: та же ветка и тот же путь, что у каталога.
АДРЕС = "https://raw.githubusercontent.com/{repo}/badges/.github/badges/contracts.json"
#: Ключи манифеста и их тип. Форма проверяется этим, а не схемой JSON:
#: зависимостей набора каталог не заводит (тесты — только от объявленного).
ФОРМА: dict[str, type | tuple[type, ...]] = {
    "schema": str, "project": str, "release": (dict, type(None)),
    "gives": dict, "takes": list,
}


def своё_имя() -> str:
    """`владелец/имя` каталога — из того же адреса, что в выгрузке, а не копией."""
    return CATALOGUE_URL.removeprefix("https://github.com/")


def выпуск(root: Path = ROOT) -> dict[str, str] | None:
    """Последний тег схемы и его коммит в дереве `root`; None, пока тега нет.

    Дерево то же, из которого берутся номера (обзор #801): иначе выпуск и
    номера одного манифеста могли бы прийти из двух разных клонов.
    """
    тег = latest_tag(root)
    if тег is None:
        return None
    коммит = git("rev-list", "-n", "1", тег, root=root)
    return {"tag": тег, "sha": коммит} if коммит else None


def манифест(root: Path | None = None) -> dict[str, Any]:
    """Манифест каталога: отдаёт все свои контракты, парных связей не берёт."""
    return {
        "schema": FAMILY_SCHEMA,
        "project": своё_имя(),
        "release": выпуск(root or ROOT),
        "gives": contracts_now(root),
        "takes": [],
    }


def изъян_формы(doc: Any) -> str | None:
    """Чем манифест не похож на манифест; None — форма верна."""
    if not isinstance(doc, dict):
        return "манифест не объект JSON"
    for ключ, тип in ФОРМА.items():
        if ключ not in doc:
            return f"нет ключа «{ключ}»"
        if not isinstance(doc[ключ], тип):
            return f"«{ключ}» не того типа"
    # не проза: номер формата «мажор.минор», сверяется мажор.
    if doc["schema"].split(".")[0] != FAMILY_SCHEMA.split(".")[0]:
        return f"формат {doc['schema']}, а читается {FAMILY_SCHEMA}"
    return None


def запись(repo: str, doc: Any, err: str | None) -> dict[str, Any]:
    """Строка сводки о проекте: его манифест либо состояние с причиной."""
    if err is not None:
        состояние = "absent" if "HTTP Error 404" in err else "unreadable"
        return {"repo": repo, "state": состояние, "why": err}
    if (изъян := изъян_формы(doc)) is not None:
        return {"repo": repo, "state": "unreadable", "why": изъян}
    if doc["project"] != repo:
        return {"repo": repo, "state": "unreadable",
                "why": f"манифест называет себя {doc['project']}"}
    return {"repo": repo, "state": "published",
            **{k: doc[k] for k in ("schema", "release", "gives", "takes")}}


def сводка(реестр: list[dict], свой: dict[str, Any],
           прочесть: Callable[[str], tuple[Any, str | None]] | None = None,
           ) -> dict[str, Any]:
    """Манифесты всех проектов реестра; свой берётся без сети."""
    прочесть = прочесть or fetch
    проекты = []
    for c in реестр:
        repo = c["repo"]
        if repo == свой["project"]:
            проекты.append(запись(repo, свой, None))
        else:
            проекты.append(запись(repo, *прочесть(АДРЕС.format(repo=repo))))
    return {"schema": FAMILY_SCHEMA,
            "generated": dt.date.today().isoformat(),
            "projects": проекты}


def записать(путь: Path, doc: dict[str, Any]) -> None:
    путь.parent.mkdir(parents=True, exist_ok=True)
    путь.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    что = ap.add_mutually_exclusive_group(required=True)
    что.add_argument("--manifest", action="store_true",
                     help=f"записать свой манифест в {MANIFEST}")
    что.add_argument("--summary", action="store_true",
                     help=f"собрать манифесты реестра в {SUMMARY}")
    args = ap.parse_args(argv)

    # Пустого `gives` не бывает: свой номер выгрузки `contracts_now` берёт из
    # константы, а не с диска (обзор #801 — охрана здесь была недостижима).
    свой = манифест(args.root)
    if args.manifest:
        записать(args.root / MANIFEST, свой)
        print(f"манифест: {args.root / MANIFEST}")
        return 0
    try:
        реестр = json.loads((args.root / REGISTRY).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"сводка не собрана: реестр {args.root / REGISTRY} — {e}",
              file=sys.stderr)
        return 2
    doc = сводка(реестр["consumers"], свой)
    записать(args.root / SUMMARY, doc)
    счёт = {s: sum(p["state"] == s for p in doc["projects"])
            for s in ("published", "absent", "unreadable")}
    print(f"сводка семьи: {args.root / SUMMARY} — " +
          ", ".join(f"{k} {v}" for k, v in счёт.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
