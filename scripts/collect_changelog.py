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
import subprocess
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


#: Строка вердикта. Начинается с «>», в журнал НЕ едет и живёт только во
#: фрагменте: читателю выпуска она не адресована, а автору починки — да.
VERDICT_PREFIX = ">"
#: Ссылка на правило: номер рядом со словом «правил» либо путь в дерево.
RULE_RE = re.compile(r"(?i)правил\w*\s+№?\s*\d{3}|rules/(?:ru|en)/\d{3}-")
#: Заполненный отказ. Причина обязательна: «не правило» без неё — это пустота,
#: которую зададут заново следующей починкой (правило 026).
NOT_A_RULE_RE = re.compile(r"(?i)не\s+(?:станови\w+|стало|тянет|правило)[^.]*?потому что\s+\S+")
VERDICT_HINT = ("> правило NNN — <как связано>   ·   "
                "> правилом не становится, потому что <причина>")


def split_verdict(text: str) -> tuple[str, str]:
    """Делит фрагмент на тело журнала и вердикт о правиле."""
    body, verdict = [], []
    for line in text.splitlines():
        (verdict if line.lstrip().startswith(VERDICT_PREFIX) else body).append(line)
    return ("\n".join(body).strip(),
            " ".join(l.lstrip().lstrip(VERDICT_PREFIX).strip() for l in verdict).strip())


def verdict_problems(paths: list[Path]) -> list[str]:
    """Починка обязана ответить, тянет ли она на правило.

    ГДЕ ЗДЕСЬ МОМЕНТ. Фильтр на входе в каталог есть и работает машинно: запись
    без границы «не работает» отвергает audit_catalogue.py, запись без
    инцидента не принимает документ для участника. Но срабатывает он для того,
    кто УЖЕ решил писать. Момента, в который это решают, не было — и замер по
    корпусу показывает форму пропажи: записи появляются пачками там, где кто-то
    целенаправленно садился их писать, а не по одной вслед за починками.

    Момент выбран здесь потому, что фрагмент журнала пишут ровно тогда, когда
    починка сделана и инцидент ещё цел: известны причина, цена и чем чинили.
    Через сутки остаётся след поломки, а не она сама (правило 138).

    СПРАШИВАЕТСЯ ТОЛЬКО У НОВЫХ ФРАГМЕНТОВ. Спросить со старых задним числом
    значило бы завести два десятка отписок за присест — ровно то, чего не хочет
    026: отказ без причины возвращается следующей ревизией.
    """
    out: list[str] = []
    for path in paths:
        m = NAME_RE.match(path.name)
        if not m or m.group(2) != "fixed" or not path.exists():
            continue
        _, verdict = split_verdict(path.read_text(encoding="utf-8"))
        if not verdict:
            out.append(f"{path.name}: починка не ответила, тянет ли она на "
                       f"правило. Строкой с «>»:\n        {VERDICT_HINT}")
        elif not (RULE_RE.search(verdict) or NOT_A_RULE_RE.search(verdict)):
            out.append(f"{path.name}: вердикт есть, но не разбирается — нужен "
                       f"номер правила либо отказ С ПРИЧИНОЙ.\n        {VERDICT_HINT}")
    return out


def added_since(ref: str) -> tuple[list[Path], str | None]:
    """Фрагменты, ДОБАВЛЕННЫЕ этим изменением. Спрашивать со всех нельзя."""
    try:
        done = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=A", f"{ref}...HEAD",
             "--", FRAGMENTS.name],
            cwd=ROOT, capture_output=True, text=True)
    except FileNotFoundError:
        return [], "нет команды git"
    if done.returncode != 0:
        return [], (done.stderr or done.stdout).strip()
    return [ROOT / line for line in done.stdout.split() if line], None


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
        text, _ = split_verdict(path.read_text(encoding="utf-8"))
        text = text.strip()
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
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="только проверить")
    mode.add_argument("--preview", action="store_true", help="показать сборку")
    mode.add_argument("--collect", action="store_true", help="собрать в [Unreleased]")
    ap.add_argument("--added-since", metavar="REF",
                    help="спросить у ДОБАВЛЕННЫХ с этой точки починок, "
                         "тянут ли они на правило")
    args = ap.parse_args()

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

    if args.added_since:
        paths, err = added_since(args.added_since)
        if err:
            print(f"проверка не отработала: список добавленных фрагментов не "
                  f"получен — {err}", file=sys.stderr)
            return 2
        problems += verdict_problems(paths)

    # ── исход 1 ────────────────────────────────────────────────────────────
    if problems:
        print("фрагменты журнала не в порядке:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        print("\n  Вопрос «тянет ли эта поломка на правило» задаётся здесь "
              "потому, что\n  здесь инцидент ещё цел: известны причина, цена и "
              "чем чинили. Ответ\n  «нет» так же полезен, как «да», — но "
              "только если он записан (026).", file=sys.stderr)
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
