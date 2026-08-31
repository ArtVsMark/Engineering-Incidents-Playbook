#!/usr/bin/env python3
"""Инструмент, отданный наружу, назван на входе — и вход о нём знает.

Каталог отдаёт потребителю не только текст правил: команду подключения,
действие для прогонов, готовые скрипты. Про них было сказано ровно в одном
месте — в журнале изменений за тот день, когда их построили. Замер 31 августа:
`scripts/onboard_consumer.py` не упомянут ни в README, ни в START, ни в
контракте; `main_red.py` и `link_trails.py` выносились с формулировкой «стал
доступен потребителям» и в потребительских документах не названы; первый день
нового проекта состоял из десяти заготовок и ни одной команды.

ЧТО ПРОВЕРЯЕТСЯ.

  • каждый скрипт с маркером `ОТДАЁТСЯ ПОТРЕБИТЕЛЮ.` назван в CONNECT.md;
  • каждый инструмент из таблицы CONNECT.md существует: скрипт — файлом,
    действие — своим `action.yml`;
  • README и START ведут на CONNECT.md, а не заводят второй список.

ПОЧЕМУ МАРКЕР, А НЕ ДОГАДКА ПО ТЕКСТУ. «Инструмент для потребителя» — решение
автора, а не свойство кода: `check_bindings.py` тоже говорит о потребителях,
оставаясь нашим гейтом. Догадка по словам дала бы ложные отказы, а они
приучают пропускать красное (051). Поэтому маркер объявляется явно и
сверяется целиком, а не началом строки (141).

Догадка при этом не выброшена, а понижена до предупреждения: скрипт, который
говорит «запускается в репозитории потребителя» и маркера не несёт, —
подозрение, и оно печатается. Именно так три инструмента и потерялись.

Реализует правила каталога:
  163 — инструмент, отданный наружу, назван на входе, а не в журнале;
  022 — список инструментов один: README и START ссылаются на него, а не
        заводят второй, который разойдётся молча;
  051 — запрещают достоверное, предупреждают о вероятном;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  075 — нет документа входа или нет таблицы — отказ, а не чистый прогон;
  158 — третий исход называет предмет: какой файл.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONNECT = "CONNECT.md"
#: Маркер объявления. Сверяется целиком и с начала строки: «отдаётся» внутри
#: фразы — это проза, а не декларация (правило 141).
MARK = "ОТДАЁТСЯ ПОТРЕБИТЕЛЮ."
#: Строка таблицы инструментов: первая ячейка — код с путём или с `uses:`.
ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|")
#: Подозрение: скрипт говорит о запуске у потребителя, а маркера не несёт.
HINT_RE = re.compile(r"в репозитории потребителя|Запускается у потребителя")
#: Документы входа обязаны вести сюда. Список короткий и разрешительный:
#: запретительный («все .md») завтра потребует ссылки от чужой страницы.
ENTRY = ("README.md", "START.md")


def tools(text: str) -> list[str]:
    """Первые ячейки таблицы инструментов: пути скриптов и ссылки `uses:`."""
    return [m.group(1) for m in (ROW_RE.match(line) for line in text.splitlines())
            if m and (m.group(1).startswith("scripts/")
                      or m.group(1).startswith("uses: "))]


def action_path(uses: str) -> Path:
    """Локальный путь действия, на которое ссылается `uses:`.

    `uses: владелец/репо@тег` — корневой action.yml; `владелец/репо/путь@тег`
    — action.yml по этому пути. Тег отрезается: он закрепляется сборкой и к
    существованию файла отношения не имеет.
    """
    ref = uses[len("uses: "):].split("@", 1)[0].strip()
    parts = ref.split("/")
    tail = "/".join(parts[2:]) if len(parts) > 2 else ""
    return Path(tail) / "action.yml" if tail else Path("action.yml")


def declared(root: Path) -> tuple[list[str], list[str]]:
    """Скрипты с маркером и скрипты, похожие на него без маркера."""
    marked, suspect = [], []
    for path in sorted((root / "scripts").glob("*.py")):
        # Файл, объявляющий саму догадку, под неё же и попадает: слова
        # «в репозитории потребителя» здесь — определение, а не декларация.
        # Предупреждение о себе печаталось бы каждым прогоном, а шум приучают
        # пропускать (051).
        if path.name == Path(__file__).name:
            continue
        head = path.read_text(encoding="utf-8", errors="replace")[:4000]
        name = f"scripts/{path.name}"
        if any(line.startswith(MARK) for line in head.splitlines()):
            marked.append(name)
        elif HINT_RE.search(head):
            suspect.append(name)
    return marked, suspect


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    args = parser.parse_args(argv)
    root: Path = args.root
    connect = root / CONNECT

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not connect.exists():
        print(f"проверка не отработала: нет {connect} — документа входа, в "
              "котором и живёт список инструментов", file=sys.stderr)
        return 2
    if not (root / "scripts").is_dir():
        print(f"проверка не отработала: нет {root / 'scripts'} — сверять "
              "таблицу не с чем", file=sys.stderr)
        return 2
    text = connect.read_text(encoding="utf-8")
    named = tools(text)
    if not named:
        print(f"проверка не отработала: в {CONNECT} не разобралось ни одной "
              "строки таблицы инструментов. Это ошибка разбора, а не пустой "
              "список: инструменты существуют", file=sys.stderr)
        return 2

    # ── исход 1 ────────────────────────────────────────────────────────────
    problems: list[str] = []
    marked, suspect = declared(root)

    for item in named:
        target = action_path(item) if item.startswith("uses: ") else Path(item)
        if not (root / target).exists():
            problems.append(
                f"{CONNECT} обещает «{item}», а {target} не существует. "
                "Потребитель придёт по названному адресу и не найдёт ничего")

    for script in marked:
        if script not in named:
            problems.append(
                f"{script} объявлен маркером «{MARK}», а в {CONNECT} не назван. "
                "Инструмент, о котором сказано только в коде и журнале, для "
                "новичка не существует")

    for doc in ENTRY:
        path = root / doc
        if not path.exists():
            continue
        if CONNECT not in path.read_text(encoding="utf-8"):
            problems.append(
                f"{doc} не ведёт на {CONNECT}. Вход, не назвавший инструментов, "
                "оставляет читателю единственный путь — копировать руками")

    if problems:
        print("вход в проект разошёлся с инструментами:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    if suspect:
        print("на что стоит посмотреть (не отказ):")
        for script in suspect:
            print(f"  ~ {script}: говорит о запуске у потребителя, а маркера "
                  f"«{MARK}» не несёт — инструмент это или наш гейт, решает автор")

    print(f"вход в порядке: инструментов {len(named)}, объявлено маркером "
          f"{len(marked)}, все названы и все существуют")
    return 0


if __name__ == "__main__":
    sys.exit(main())
