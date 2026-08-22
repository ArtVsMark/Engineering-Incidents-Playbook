#!/usr/bin/env python3
"""Сверяет трейлеры авторства с согласованным списком до слияния.

Реализует правила каталога:
  123 — атрибуция проверяется в конечной истории, а не в коммите ветки;
        трейлеры сверяются со списком согласованных имён;
  039 — у проверки три исхода, а не два;
  114 — миграция идёт от текущей версии, а не от нуля: требование действует
        с объявленного коммита, а не задним числом на всю историю;
  046 — пробел называется поимённо: коммиты без атрибуции печатаются числом;
  041 — два честных числа вместо одного усреднённого: сколько всего и сколько
        без атрибуции, а не «процент покрытия».

Два режима, потому что вопроса два.

  Коммиты ветки  (--range)  — проверка ДО слияния: историю ветки ещё можно
  переписать, и находка здесь чинится автором.

  Первопредки    (--first-parents) — проверка ПОСЛЕ: коммит общей ветки
  составляет площадка, и в итоговой истории атрибуции может не быть вовсе при
  зелёном гейте на каждом изменении. Починить прошлое нельзя — но не знать о
  нём хуже (правила 002, 075).

Исходы:
  0 — чисто;
  1 — есть находки;
  2 — проверка не отработала (нет git, нет диапазона, нет списка имён).

Запуск:  python scripts/check_attribution.py                 # origin/main..HEAD
         python scripts/check_attribution.py --range A..B
         python scripts/check_attribution.py --first-parents  # origin/main
         python scripts/check_attribution.py --first-parents --ref main --since d1297ff
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


def first_parents(ref: str, since: str | None, names: set[str]) -> int:
    """Атрибуция в итоговой истории общей ветки.

    Спрашиваются ВСЕ первопредки, а не только объединяющие коммиты. Это не
    придирка: способ слияния — настройка репозитория, и при squash слияний в
    истории не остаётся вовсе. Проверка, привязанная к виду коммита, после
    смены настройки нашла бы ноль предметов и промолчала бы зелёным — ровно то,
    от чего предостерегает правило 075.
    """
    try:
        git("rev-parse", "--verify", ref)
    except subprocess.CalledProcessError:
        print(f"проверка не отработала: {ref} недоступен — "
              "нужен полный клон и общая ветка", file=sys.stderr)
        return 2

    scope = f"{since}..{ref}" if since else ref
    try:
        out = git("log", "--first-parent",
                  "--format=%H%x00%s%x00%b%x00", scope)
    except subprocess.CalledProcessError as e:
        print(f"проверка не отработала: {scope!r} не разобран — "
              f"{e.stderr.strip()}", file=sys.stderr)
        return 2

    records = [r for r in out.split("\x00\n") if r.strip()]
    if not records:
        # Пусто — это состояние, а не тишина (правило 027). И это не «чисто»:
        # проверка, которой нечего смотреть, не подтверждает ничего (075).
        print(f"проверка не отработала: в {scope} нет первопредков — "
              "подтверждать нечего", file=sys.stderr)
        return 2

    missing: list[str] = []
    stranger: list[str] = []
    for rec in records:
        sha, subject, body = (rec.split("\x00") + ["", ""])[:3]
        sha, subject = sha.strip(), subject.strip()
        coauthors = [m.strip() for m in COAUTHOR.findall(body)]
        if not coauthors:
            missing.append(f"{sha[:7]} {subject[:64]}")
            continue
        for name in coauthors:
            if name not in names:
                stranger.append(f"{sha[:7]} соавтор вне списка: {name!r}")

    total = len(records)
    if missing or stranger:
        print(f"атрибуция в итоговой истории {scope}: "
              f"первопредков {total}, без атрибуции {len(missing)}",
              file=sys.stderr)
        for line in missing[:5]:
            print(f"  • {line}", file=sys.stderr)
        if len(missing) > 5:
            print(f"  • …и ещё {len(missing) - 5}", file=sys.stderr)
        for line in stranger:
            print(f"  • {line}", file=sys.stderr)
        print("\n  Прошлое не переписать: общая ветка защищена, и это долг, а не "
              "задача (правило 114).\n  Красное здесь означает, что коммит в общей "
              "ветке составляется без трейлеров — чинится\n  на стороне слияния, "
              "а не правкой истории. Объявить долг и спрашивать с\n  определённого "
              "коммита — ключ --since.", file=sys.stderr)
        return 1

    print(f"атрибуция в итоговой истории в порядке: {scope}, "
          f"объединяющих коммитов {total}, без атрибуции 0")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--range", default=None,
                    help="диапазон коммитов, по умолчанию origin/main..HEAD")
    ap.add_argument("--first-parents", action="store_true",
                    help="проверить первопредки общей ветки, а не коммиты ветки")
    ap.add_argument("--ref", default="origin/main",
                    help="общая ветка для --first-parents, по умолчанию origin/main")
    ap.add_argument("--since", default=None,
                    help="объявленное начало для --first-parents: раньше него "
                         "не спрашивать. Без него спрашивается вся история — "
                         "долг виден числом, а не спрятан подрезкой")
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

    if args.first_parents:
        return first_parents(args.ref, args.since, names)

    rng = args.range
    if rng is None:
        try:
            git("rev-parse", "--verify", "origin/main")
            rng = "origin/main..HEAD"
        except subprocess.CalledProcessError:
            print("проверка не отработала: origin/main недоступен, диапазон "
                  "не определён — задайте --range", file=sys.stderr)
            return 2
    # Диапазон не уходит глубже объявленного начала: до него история писалась
    # без трейлеров, переписать её нельзя, и требовать оттуда нечего (114).
    try:
        git("merge-base", "--is-ancestor", BASELINE, "HEAD")
        low, _, high = rng.partition("..")
        # Сравниваем разрешённые хеши, а не строки: «d1297ff» и полный хеш —
        # один коммит, и сообщать о подрезке там, где её нет, значит шуметь.
        same = low and git("rev-parse", low).strip() == git("rev-parse", BASELINE).strip()
        if low and not same and subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", low, BASELINE],
            capture_output=True,
        ).returncode == 0:
            rng = f"{BASELINE}..{high or 'HEAD'}"
            print(f"диапазон подрезан до объявленного начала: {rng}")
    except subprocess.CalledProcessError:
        pass  # BASELINE вне этой истории — проверяем, что просили

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
