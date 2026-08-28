#!/usr/bin/env python3
"""Кандидаты в правила: граница с корпусом держится машинно, а не обещанием.

Кандидат — наблюдение из чужого проекта, у которого НЕТ нашего инцидента.
Каталог такие в `rules/` не принимает (CONTRIBUTING), и это верно: правило без
инцидента через месяц нечем защитить. Но и терять их жаль, поэтому они лежат
в `candidates/` помеченными гипотезами.

ЧЕМ ЭТО ОПАСНО И ЧТО ИМЕННО ЗДЕСЬ ДЕРЖИТСЯ. Папка «почти правил» — готовый
обход требования инцидента. Обход происходит не решением, а сползанием: сперва
на кандидата ссылается правило, потом на него ссылается свод, потом никто уже
не помнит, что это гипотеза. Поэтому главная проверка здесь не про форму файла,
а про ССЫЛКИ: **ни одно правило не ссылается на кандидата**. Ссылка из `rules/`
сюда превращает гипотезу в основание, и происходит это молча.

ПОЧЕМУ У КАНДИДАТА НЕТ НОМЕРА. Номер — место в корпусе, а корпус состоит из
инцидентов. Выдать номер заранее значит занять его под то, что может не
подтвердиться никогда, — при запрете переиспользовать номера это потеря
навсегда.

ПОЧЕМУ ОБЯЗАТЕЛЕН РАЗДЕЛ «ЧЕМ ПОДТВЕРДИТСЯ». Без него кандидат не подтвердится
и не отвергнется: у гипотезы, не назвавшей своего опровержения, нет исхода. Она
просто лежит и придаёт уверенности самим фактом существования.

ПУСТАЯ ПАПКА — ЗАКОННОЕ СОСТОЯНИЕ, и оно объявлено (правило 091). Гейт на ней
не краснеет: кандидатов может не быть.

Запуск:  python scripts/check_candidates.py [--root <корень>]
Коды:    0 чисто · 1 есть находки · 2 проверка не отработала

Реализует правила каталога:
  119 — candidates/README.md кандидатом не считается: свой артефакт держат вне маски входа.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Разделы, без которых кандидат не кандидат. Порядок — порядок чтения.
REQUIRED = ("Источник", "Предполагаемая причина", "Чем подтвердится",
            "Применимость")
#: Раздел правила. Здесь его появление означает, что запись притворяется.
FORBIDDEN = ("След",)

HYPOTHESIS_RE = re.compile(r"(?im)^\*\*Гипотеза\.\*\*\s+\S")
AREA_RE = re.compile(r"(?im)^\*\*Область\.\*\*\s+\S")
#: Разрешимый источник: адрес либо задача `владелец/репозиторий#номер`.
SOURCE_RE = re.compile(r"https?://\S+|[\w.-]+/[\w.-]+#\d+")
#: Имя файла: слаг латиницей, без номера. Номер здесь — попытка занять место
#: в корпусе, и она отвергается по имени, до чтения содержимого.
NAME_RE = re.compile(r"^[a-z][a-z0-9-]*\.md$")
NUMBERED_RE = re.compile(r"^\d")

#: Сколько кандидат живёт, прежде чем о нём напомнят. Не отказ: гипотеза,
#: которую долго не подтвердили, — повод решить её судьбу, а не покрасить
#: чужое изменение (правила 051, 079).
STALE_DAYS = 180


def section(text: str, name: str) -> str | None:
    """Тело раздела `## name` или None, если раздела нет."""
    m = re.search(rf"(?m)^##\s+{re.escape(name)}\s*$", text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"(?m)^##\s+", rest)
    return rest[:nxt.start()] if nxt else rest


def candidates(root: Path) -> list[Path]:
    folder = root / "candidates"
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.glob("*.md") if p.name != "README.md")


def cited_by_rules(root: Path, names: set[str]) -> list[str]:
    """Ссылки из rules/** на кандидатов. Это и есть тихое превращение."""
    out: list[str] = []
    for tree in ("ru", "en"):
        for rule in sorted((root / "rules" / tree).glob("*.md")):
            text = rule.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)\s]+)\)", text):
                tail = target.split("#")[0].rsplit("/", 1)[-1]
                if "candidates/" in target and tail in names:
                    out.append(f"{rule.relative_to(root)} ссылается на "
                               f"кандидата {tail}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT,
                    help="корень дерева; по умолчанию сам репозиторий")
    root = ap.parse_args(argv).root

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not (root / "rules" / "ru").is_dir():
        print("проверка не отработала: нет дерева rules/ru — сверять не с чем",
              file=sys.stderr)
        return 2

    found = candidates(root)
    problems: list[str] = []
    warnings: list[str] = []

    for path in found:
        name = path.name
        if NUMBERED_RE.match(name):
            problems.append(f"{name}: имя начинается с цифры. У кандидата "
                            "номера нет — номер занимает место в корпусе, а "
                            "корпус состоит из инцидентов")
            continue
        if not NAME_RE.match(name):
            problems.append(f"{name}: имя не по форме «слаг-латиницей.md»")
            continue

        text = path.read_text(encoding="utf-8")
        if not HYPOTHESIS_RE.search(text):
            problems.append(f"{name}: нет строки «**Гипотеза.**» с текстом — "
                            "читатель обязан узнать статус из первой строки, "
                            "а не из пути к файлу")
        if not AREA_RE.search(text):
            problems.append(f"{name}: нет строки «**Область.**»")
        for head in REQUIRED:
            body = section(text, head)
            if body is None:
                problems.append(f"{name}: нет раздела «{head}»")
            elif not body.strip():
                problems.append(f"{name}: раздел «{head}» пуст — заголовок без "
                                "содержания выглядит заполненным")
        for head in FORBIDDEN:
            if section(text, head) is not None:
                problems.append(f"{name}: есть раздел «{head}» — он для правил. "
                                "Кандидат с ним притворяется правилом")
        src = section(text, "Источник") or ""
        if src.strip() and not SOURCE_RE.search(src):
            problems.append(f"{name}: источник не разрешается — нужен адрес "
                            "или задача «владелец/репозиторий#номер». Проза "
                            "источником не считается")

        age = (dt.date.today() - dt.date.fromtimestamp(
            path.stat().st_mtime)).days
        if age > STALE_DAYS:
            warnings.append(f"{name}: лежит {age} дн. — пора подтвердить "
                            "инцидентом или отвергнуть с причиной (026)")

    problems += cited_by_rules(root, {p.name for p in found})

    # ── исход 1 ────────────────────────────────────────────────────────────
    if problems:
        print("кандидаты не по форме:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        print("\n  Папка «почти правил» — готовый обход требования инцидента, "
              "и обход\n  происходит сползанием, а не решением. Граница "
              "держится здесь.", file=sys.stderr)
        return 1

    for w in warnings:
        print(f"предупреждение: {w}")

    # ── исход 0 ────────────────────────────────────────────────────────────
    if not found:
        print("кандидатов нет — это объявленное состояние, а не пустая проверка")
        return 0
    print(f"кандидаты в порядке: {len(found)}, ни на одного не ссылается правило")
    return 0


if __name__ == "__main__":
    sys.exit(main())
