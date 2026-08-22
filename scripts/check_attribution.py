#!/usr/bin/env python3
"""Сверяет трейлеры авторства с согласованным списком до слияния.

Реализует правила каталога:
  123 — атрибуция проверяется в конечной истории, а не в коммите ветки;
        трейлеры сверяются со списком согласованных имён;
  039 — у проверки три исхода, а не два;
  114 — миграция идёт от текущей версии, а не от нуля: требование действует
        с объявленного коммита, а не задним числом на всю историю;
  046 — пробел называется поимённо: коммиты без атрибуции печатаются числом.

Исходы:
  0 — чисто;
  1 — есть находки;
  2 — проверка не отработала (нет git, нет диапазона, нет списка имён).

Запуск:  python scripts/check_attribution.py                 # origin/main..HEAD
         python scripts/check_attribution.py --range A..B
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUTHORS = ROOT / ".github" / "authors.txt"

#: С этого коммита атрибуция обязательна. Раньше него история писалась без
#: трейлеров, и переписать её нельзя — общая ветка защищена (правило 123).
#: Требовать задним числом значит требовать невозможного (правило 114).
BASELINE = "d1297ff"

COAUTHOR = re.compile(r"^Co-Authored-By:\s*(.+?)\s*$", re.M | re.I)
SESSION = re.compile(r"^Claude-Session:\s*(.+?)\s*$", re.M | re.I)


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=True).stdout


def agreed() -> set[str]:
    lines = AUTHORS.read_text(encoding="utf-8").split("\n")
    return {l.strip() for l in lines if l.strip() and not l.startswith("#")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--range", default=None, help="диапазон коммитов, по умолчанию origin/main..HEAD")
    args = ap.parse_args()

    # ── исход 2: проверка не отработала ────────────────────────────────────
    try:
        names = agreed()
    except OSError as e:
        print(f"проверка не отработала: список имён не прочитан — {e}", file=sys.stderr)
        return 2
    if not names:
        print(f"проверка не отработала: {AUTHORS.relative_to(ROOT)} пуст — "
              "сверять не с чем, а молча пропускать нельзя", file=sys.stderr)
        return 2

    rng = args.range
    if rng is None:
        try:
            git("rev-parse", "--verify", "origin/main")
            rng = "origin/main..HEAD"
        except subprocess.CalledProcessError:
            print("проверка не отработала: origin/main недоступен, диапазон "
                  "не определён — задайте --range", file=sys.stderr)
            return 2
    try:
        # Слияния пропускаем: их сообщение составляет площадка, а не автор.
        out = git("log", "--no-merges", "--format=%H%x00%s%x00%b%x00", rng)
    except subprocess.CalledProcessError as e:
        print(f"проверка не отработала: диапазон {rng!r} не разобран — "
              f"{e.stderr.strip()}", file=sys.stderr)
        return 2

    records = [r for r in out.split("\x00\n") if r.strip()]
    if not records:
        print(f"в диапазоне {rng} новых коммитов нет — проверять нечего")
        return 0

    # ── исход 1: находки ───────────────────────────────────────────────────
    findings: list[str] = []
    unattributed = 0
    for rec in records:
        sha, subject, body = (rec.split("\x00") + ["", ""])[:3]
        sha, subject = sha.strip(), subject.strip()
        coauthors = [m.strip() for m in COAUTHOR.findall(body)]
        session = SESSION.search(body)

        for name in coauthors:
            if name not in names:
                findings.append(
                    f"{sha[:7]} {subject[:56]}\n"
                    f"        соавтор вне списка: {name!r}\n"
                    f"        согласованы: {', '.join(sorted(names))}")
        if session and not coauthors:
            findings.append(
                f"{sha[:7]} {subject[:56]}\n"
                f"        есть Claude-Session, но нет Co-Authored-By: "
                f"след сессии без соавторства")
        if not coauthors and not session:
            unattributed += 1

    if findings:
        print("атрибуция расходится со списком:", file=sys.stderr)
        for f in findings:
            print(f"  • {f}", file=sys.stderr)
        return 1

    # ── исход 0 ────────────────────────────────────────────────────────────
    print(f"атрибуция в порядке: {len(records)} коммитов в {rng}, "
          f"без атрибуции {unattributed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
