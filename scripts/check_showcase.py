#!/usr/bin/env python3
"""Витрина отвечает на объявленный набор вопросов — или называет, чего нет.

ЗАЧЕМ НАБОР ОДИН НА ВСЕ ПРОЕКТЫ. Замер по пяти публичным проектам (#105): из
восьми вопросов пять отвечает один грейдер, остальные четыре проекта — ни
одного. Пока набор у каждого свой, проекты не сравнить, и то, что один
перестал отвечать, не заметит никто. Это 022 в применении к витрине.

ЗАЧЕМ НАЗЫВАТЬ ОТСУТСТВУЮЩИЙ ВОПРОС. Значок, которого нет, и значок, который
застыл, с витрины НЕОТЛИЧИМЫ. «У нас нет покрытия, потому что нет кода» и
«механизм покрытия сломался и молчит» — разные вещи, и разница видна только
если пробел назван (правила 046, 075). Поэтому у каждого вопроса набора либо
живой значок, либо строка `absent` с причиной; пропуск не проходит.

ЧЕГО ЭТОТ ГЕЙТ НЕ ДЕЛАЕТ. Он не судит, верное ли число в значке: значок
вычисляет сборка, а сверять её саму с собой бессмысленно. Он проверяет, что
на каждый объявленный вопрос ЕСТЬ ответ и что живой ответ назван в витрине —
значок, который никто не показывает, отвечает в пустоту.

Запуск:  python scripts/check_showcase.py [--build] [--root <корень>]
Коды:    0 чисто · 1 есть находки · 2 проверка не отработала
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SET = ROOT / ".rules" / "showcase.json"
SHOWCASES = ("README.md", "README.en.md")

#: Значки, которые вычисляются здесь. Остальные считает тот, кто их придумал:
#: покрытие — coverage_badge.py, число правил — сборка указателя.
TEST_RE = re.compile(r"(?m)^\s*def (test_\w+)")
GATE_RE = re.compile(r"scripts/(\w+)\.py")
COLOR = "1d76db"


def counted(root: Path) -> dict[str, int]:
    """Числа, которые витрина обещает: тесты, тестовые модули, гейты."""
    tests = sorted((root / "tests").glob("test_*.py"))
    total = sum(len(TEST_RE.findall(p.read_text(encoding="utf-8"))) for p in tests)
    ci = root / ".github" / "workflows" / "ci.yml"
    gates = len(set(GATE_RE.findall(ci.read_text(encoding="utf-8")))) if ci.exists() else 0
    return {"tests": total, "test-modules": len(tests), "gates": gates}


def render(label: str, value: int) -> str:
    return ('{\n  "schemaVersion": 1,\n'
            f'  "label": "{label}",\n'
            f'  "message": "{value}",\n'
            f'  "color": "{COLOR}"\n' + "}\n")


LABELS = {"tests": "tests", "test-modules": "test modules", "gates": "pr checks"}
BADGE_OF = {"tests": ".github/badges/tests.json",
            "test-modules": ".github/badges/test-modules.json",
            "gates": ".github/badges/gates.json"}


def build(root: Path) -> list[str]:
    """Пересобирает вычисляемые здесь значки. Возвращает список изменённых."""
    changed = []
    for key, value in counted(root).items():
        path = root / BADGE_OF[key]
        want = render(LABELS[key], value)
        have = path.read_text(encoding="utf-8") if path.exists() else ""
        if have != want:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(want, encoding="utf-8")
            changed.append(f"{key}: {value}")
    return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--build", action="store_true",
                    help="пересобрать вычисляемые здесь значки")
    ap.add_argument("--root", type=Path, default=ROOT,
                    help="корень дерева; по умолчанию сам репозиторий")
    args = ap.parse_args(argv)
    root: Path = args.root
    declared = root / ".rules" / "showcase.json"

    # ── исход 2 ────────────────────────────────────────────────────────────
    try:
        doc = json.loads(declared.read_text(encoding="utf-8"))
        questions = doc["questions"]
    except (OSError, ValueError, KeyError) as e:
        print(f"проверка не отработала: набор вопросов витрины не прочитан — {e}",
              file=sys.stderr)
        return 2
    if not questions:
        print("проверка не отработала: набор не называет ни одного вопроса — "
              "витрина без вопросов не витрина", file=sys.stderr)
        return 2

    if args.build:
        changed = build(root)
        print("значки пересобраны: " + (", ".join(changed) if changed
                                        else "изменений нет"))
        return 0

    shown = "\n".join((root / name).read_text(encoding="utf-8")
                      for name in SHOWCASES if (root / name).exists())
    if not shown:
        print("проверка не отработала: витрины нет — показывать ответы негде",
              file=sys.stderr)
        return 2

    # ── исход 1 ────────────────────────────────────────────────────────────
    problems: list[str] = []
    for q in questions:
        qid, ask = q.get("id", "?"), q.get("ask", "")
        badge, absent = q.get("badge"), q.get("absent")
        if badge and absent:
            problems.append(f"{qid}: и значок, и причина отсутствия — ответ один")
            continue
        if not badge and not absent:
            problems.append(
                f"{qid} «{ask}»: ответа нет вовсе. Либо значок, либо строка "
                "absent с причиной — пропуск и отсутствие предмета обязаны "
                "выглядеть по-разному")
            continue
        if absent:
            if len(absent.strip()) < 20:
                problems.append(f"{qid}: причина отсутствия слишком коротка, "
                                "чтобы ею что-то объяснить")
            continue
        # Значок с отдельной ветки в этом дереве не лежит и лежать не должен:
        # она заводится ровно для того, чтобы пересборка значка не двигала
        # общую ветку. Требовать файл здесь значило бы требовать того, чего
        # быть не может, — ложный отказ (правило 097).
        if q.get("branch", "main") == "main" and not (root / badge).exists():
            problems.append(f"{qid}: значок {badge} объявлен, а файла нет — "
                            "витрина обещает ответ, которого не существует")
            continue
        if Path(badge).name not in shown:
            problems.append(f"{qid}: значок {badge} есть, но в витрине его "
                            "нет — ответ в пустоту")

    for key, value in counted(root).items():
        path = root / BADGE_OF[key]
        if path.exists() and path.read_text(encoding="utf-8") != \
                render(LABELS[key], value):
            problems.append(f"{key}: значок устарел, замер даёт {value}. "
                            "Пересоберите: python scripts/check_showcase.py --build")

    if problems:
        print("витрина отвечает не на весь объявленный набор:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        print("\n  Значок, которого нет, и значок, который застыл, с витрины "
              "неотличимы.\n  Поэтому вопрос без предмета называется, а не "
              "опускается (правила 046, 075).", file=sys.stderr)
        return 1

    # ── исход 0 ────────────────────────────────────────────────────────────
    live = sum(1 for q in questions if q.get("badge"))
    named = len(questions) - live
    print(f"витрина отвечает на весь набор: вопросов {len(questions)}, "
          f"живым числом {live}, названо без предмета {named}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
