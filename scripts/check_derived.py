#!/usr/bin/env python3
"""Производное, которым владеет прогон, в изменении не едет.

ЗАПРЕТ БЫЛ, МЕХАНИЗМА НЕ БЫЛО. Ядро говорит дословно: «НЕ править
export/where.* руками — это сводка ответов потребителей, её пересобирает
scripts/aggregate_bindings.py». Запрет читался как «не правь текстом», и
пересборка сборщиком под него не попадала. Цена измерена: 3 сентября сводка
дала ТРИ конфликта за смену — изменения #280 и #285 против плановой пересборки
#284, — и каждый разрешался одинаково, прогоном сборщика поверх слитого.

ПОЧЕМУ ЭТО НЕ ЧИНИТСЯ ГЕЙТОМ СВЕЖЕСТИ. Его и нет: `aggregate_bindings --check`
на изменении сводку НЕ требует — замер показал, что правка ответа каталога
проходит без пересборки. То есть файл ехал в изменениях не по требованию
механизма, а по привычке окна, и ловить это было нечем.

ТО ЖЕ РЕШЕНИЕ УЖЕ ПРИНИМАЛОСЬ — ДЛЯ ЗНАЧКОВ. Они живут на отдельной ветке
именно потому, что «гейт свежести значка требовал пересборки от каждого
изменения и краснел на верной работе». Здесь предмет тот же, а ответ был
другим: сводка осталась в общей ветке, и её пересобирали обе стороны.

ГРАНИЦА, И ОНА НЕ ФОРМАЛЬНАЯ. Если изменение правит САМ СБОРЩИК, новый вид
сводки принадлежит ему: без неё нельзя ни отревьюить смену формата, ни
проверить её. Запрет действует на изменение, которое сборщик не трогает.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.

Реализует правила каталога:
  125 — производный файл не может быть хранилищем: у него один владелец;
  160 — производное, обновляемое чаще изменений, живёт вне пути изменений;
  068 — список разрешительный: освобождённая ветка названа поимённо и с причиной;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  051 — отказ на достоверном: файл в диапазоне — факт, а не подозрение.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Производные, которыми владеет прогон, и кто именно их пересобирает.
#: Разрешительно и с причиной у каждой строки: список «всё, кроме…» завтра
#: пропустил бы новый файл (068).
OWNED_BY_JOB = {
    "export/where.md": "consumers-sync → refresh_derived.py: вход — ответы "
                       "потребителей, они меняются без нас",
    "export/where.json": "consumers-sync → refresh_derived.py: тот же вход и "
                         "тот же владелец",
}

#: Ветка, на которой эти файлы и есть предмет работы. Одна и названа поимённо.
REFRESH_BRANCH = "agent/consumers-refresh"

#: Правка сборщика меняет ВИД сводки, и тогда новая сводка едет с ним: иначе
#: смену формата нечем ни отревьюить, ни проверить.
BUILDERS = ("scripts/aggregate_bindings.py", "scripts/refresh_derived.py")


def changed(rng: str, root: Path) -> tuple[list[str] | None, str]:
    """Пути, тронутые диапазоном. None — спросить не удалось."""
    done = subprocess.run(["git", "-C", str(root), "diff", "--name-only", "-z", rng],
                          capture_output=True, text=True)
    if done.returncode != 0:
        return None, (done.stderr or "").strip()
    # По NUL, а не по строкам: имя с не-ASCII символами git отдаёт
    # экранированным, и путь молча выпадает из проверки (правило 165).
    return [p for p in done.stdout.split("\0") if p], ""


def findings(paths: list[str], branch: str) -> list[str]:
    """Производные, которые едут в изменении вопреки владельцу."""
    if branch == REFRESH_BRANCH:
        return []
    if any(b in paths for b in BUILDERS):
        return []
    return sorted(p for p in paths if p in OWNED_BY_JOB)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--range", default="origin/main...HEAD",
                        help="диапазон изменения")
    parser.add_argument("--branch", default="", help="имя ветки изменения")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    paths, err = changed(args.range, args.root)
    # ── исход 2 ────────────────────────────────────────────────────────────
    if paths is None:
        print(f"проверка не отработала: диапазон {args.range} не разобран — "
              f"{err or 'git промолчал'}. Мелкий клон или ветка без основания",
              file=sys.stderr)
        return 2

    found = findings(paths, args.branch)
    # ── исход 1 ────────────────────────────────────────────────────────────
    if found:
        print("производные едут в изменении, а владеет ими прогон:",
              file=sys.stderr)
        for p in found:
            print(f"  • {p} — {OWNED_BY_JOB[p]}", file=sys.stderr)
        print("\n  Уберите их из изменения: `git checkout origin/main -- "
              + " ".join(found) + "`.\n  Пересоберёт их прогон, и в общей ветке "
              "они окажутся свежее, чем здесь.\n  Замер: три конфликта за одну "
              "смену, и все — в этих файлах.", file=sys.stderr)
        return 1

    print(f"производные в порядке: тронуто путей {len(paths)}, "
          f"чужого владения нет ({len(OWNED_BY_JOB)} под охраной)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
