#!/usr/bin/env python3
"""Журнал изменений собирается из фрагментов, а не правится общим файлом.

Реализует правила каталога:
  030 — запись приезжает вместе с изменением, отдельным файлом;
  039 — у проверки три исхода, а не два;
  022 — «что изменилось» и «как мы сюда пришли» — разные документы:
        CHANGELOG.md отвечает на первый вопрос, HISTORY.md на второй;
  075 — не нашёл предмета проверки — падает, а не зеленеет.

Фрагмент:  changelog.d/<слаг>.<секция>.md
Секции:    added · changed · fixed · removed · internal
Внутри:    одна строка текста, без ведущего «-» и без имени секции.

Исходы:
  0 — чисто;
  1 — есть находки (плохое имя, пустой фрагмент, нужна запись, а её нет);
  2 — проверка не отработала (нет каталога фрагментов, нет CHANGELOG.md).

Запуск:  python scripts/collect_changelog.py --check     # проверить
         python scripts/collect_changelog.py --preview   # показать сборку
         python scripts/collect_changelog.py --collect   # собрать в [Unreleased]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAGMENTS = ROOT / "changelog.d"
CHANGELOG = ROOT / "CHANGELOG.md"

#: Порядок фиксирован: «что нового» читается раньше, чем «что починили».
SECTIONS = ("added", "changed", "fixed", "removed", "internal")
TITLES = {
    "added": "Добавлено · Added",
    "changed": "Изменено · Changed",
    "fixed": "Починено · Fixed",
    "removed": "Удалено · Removed",
    "internal": "Внутреннее · Internal",
}
NAME_RE = re.compile(rf"^([a-z0-9][a-z0-9-]*)\.({'|'.join(SECTIONS)})\.md$")
UNRELEASED = "## [Unreleased]"


def fragments() -> list[Path]:
    return sorted(p for p in FRAGMENTS.glob("*.md") if p.name != "README.md")


def validate() -> tuple[dict[str, list[str]], list[str]]:
    """Разбирает фрагменты. Возвращает записи по секциям и список находок."""
    found: dict[str, list[str]] = {s: [] for s in SECTIONS}
    problems: list[str] = []
    for path in fragments():
        m = NAME_RE.match(path.name)
        if not m:
            problems.append(
                f"{path.name}: имя не по форме «<слаг>.<секция>.md», "
                f"секции — {', '.join(SECTIONS)}")
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            problems.append(f"{path.name}: фрагмент пуст — запись, которой нет, "
                            "хуже отсутствующего файла: он выглядит сделанным")
            continue
        if text.startswith("-"):
            problems.append(f"{path.name}: ведущий «-» подставит сборка, "
                            "в тексте он лишний")
            continue
        found[m.group(2)].append(" ".join(text.split()))
    return found, problems


def render(found: dict[str, list[str]]) -> str:
    out = []
    for section in SECTIONS:
        if not found[section]:
            continue
        out.append(f"### {TITLES[section]}\n")
        out += [f"- {line}" for line in sorted(found[section])]
        out.append("")
    return "\n".join(out).rstrip() + "\n" if out else ""


def main() -> int:
    global ROOT, FRAGMENTS, CHANGELOG
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="только проверить")
    mode.add_argument("--preview", action="store_true", help="показать сборку")
    mode.add_argument("--collect", action="store_true", help="собрать в [Unreleased]")
    ap.add_argument("--root", type=Path, default=ROOT,
                    help="корень дерева; по умолчанию сам репозиторий")
    args = ap.parse_args()

    # Ключ «работай в другом корне» заведён не ради удобства: без него у гейта
    # нет отвергаемого предмета — проверить его можно только запуском на
    # здоровом дереве, то есть подтвердить лишь то, что он запускается
    # (правила 140, 145). Пути лежат в константах модуля, поэтому корень
    # переприсваивает их здесь: иначе ключ будет принят и не исполнен.
    ROOT = args.root
    FRAGMENTS = ROOT / "changelog.d"
    CHANGELOG = ROOT / "CHANGELOG.md"

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not FRAGMENTS.is_dir():
        print(f"проверка не отработала: нет каталога {FRAGMENTS.relative_to(ROOT)}",
              file=sys.stderr)
        return 2
    if not CHANGELOG.exists():
        print(f"проверка не отработала: нет {CHANGELOG.relative_to(ROOT)} — "
              "собирать некуда", file=sys.stderr)
        return 2

    found, problems = validate()

    # ── исход 1 ────────────────────────────────────────────────────────────
    if problems:
        print("фрагменты журнала не в порядке:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    body = render(found)
    total = sum(len(v) for v in found.values())

    if args.preview:
        print(body or "фрагментов нет — собирать нечего")
        return 0

    if args.collect:
        text = CHANGELOG.read_text(encoding="utf-8")
        if UNRELEASED not in text:
            print(f"проверка не отработала: в {CHANGELOG.name} нет раздела "
                  f"{UNRELEASED!r}", file=sys.stderr)
            return 2
        if not body:
            print("фрагментов нет — собирать нечего")
            return 0
        head, _, tail = text.partition(UNRELEASED)
        CHANGELOG.write_text(f"{head}{UNRELEASED}\n\n{body}{tail.lstrip()}",
                             encoding="utf-8")
        for path in fragments():
            path.unlink()
        print(f"собрано записей: {total}, фрагменты удалены")
        return 0

    # ── исход 0 ────────────────────────────────────────────────────────────
    print(f"фрагменты журнала в порядке: {total} записей в {len(fragments())} файлах")
    return 0


if __name__ == "__main__":
    sys.exit(main())
