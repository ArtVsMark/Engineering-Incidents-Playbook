#!/usr/bin/env python3
"""Свод, документ для участника и конвейер называют одни и те же гейты.

У `CLAUDE.md` не было владельца. Обход артефактов по 082 это и показал: за
записями следит автор правил, за скриптами — инженер гейтов, за витриной —
редактор, а за сводом, который читается при старте **каждого** окна, — никто.

Цена уже заплачена трижды за одно окно: документ для участника обещал новичку
пять гейтов, когда их было семь; свод требовал от следа номера задачи, которого
не было у большинства записей; карта направлений называла непокрытым то, что уже
покрыто. Все три расхождения нашлись чтением, а не проверкой.

Что проверяется:

  • множество гейтов в таблице свода == множество шагов `ci.yml`;
  • множество команд в CONTRIBUTING == то же самое;
  • метрика: у скольких гейтов есть предмет, который они обязаны отвергнуть.

Чего здесь НЕТ: сверки ключей и порядка. Свод называет `check_attribution.py`
без ключа, конвейер — с диапазоном, и это законно: свод отвечает на «чем
держится», а не «как запускается». Сверяются имена скриптов.

Реализует правила каталога:
  022 — две формулировки одной территории расходятся молча;
  002 — договорённость «не забыть обновить свод» механизмом не является;
  082 — пласт без владельца это слепая зона, а не мелочь;
  140 — гейт без отвергаемого предмета проверен только на запуск (метрика);
  051 — запрещают достоверное, предупреждают о вероятном;
  039 — у проверки три исхода, а не два;
  009 — считаются уникальные имена гейтов, а не строки таблицы;
  029 — свод держит триггеры и ссылки: таблица называет гейты, а не пересказывает их;
  041 — печатаются два честных числа — чем гейт проверен и чем не проверен, — а не одно усреднённое.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Шаг конвейера, который гейтом каталога не является: он проверяет, что
#: заготовка для чужих проектов хотя бы запускается. Список разрешительный и
#: короткий: запретительный («всё, что не в scripts/») завтра пропустит новое
#: (правило 068).
NOT_A_GATE = {
    # Заготовка для чужих проектов: шаг проверяет, что она хотя бы запускается.
    "templates/preflight.py",
    # ГЕНЕРАТОРЫ, а не проверки. Они ничего не отвергают: собирают каркас
    # записи и набор подключения. В конвейере им делать нечего — там нет
    # предмета, который они бы сторожили, — но в документе для участника они
    # названы обязаны быть: с них начинается порядок.
    "scripts/new_rule.py",
    "scripts/onboard_consumer.py",
}

CALL_RE = re.compile(r"python\s+((?:scripts|templates)/[a-z_0-9]+\.py)")
#: Раздел свода, в котором гейты перечислены. Заголовок сверяется целой
#: строкой: «## 🛡 Гейты» — префикс никого не задевает, но приём тот же, что
#: спас разбор следа (правило 141).
CHARTER_SECTION = "## 🛡 Гейты"


def section(text: str, head: str) -> str | None:
    """Тело раздела до следующего заголовка того же уровня."""
    m = re.search("^" + re.escape(head) + r"[ \t]*$", text, re.M)
    if m is None:
        return None
    rest = text[m.end():]
    nxt = rest.find("\n## ")
    return rest if nxt < 0 else rest[:nxt]


def named_in(text: str) -> set[str]:
    """Скрипты, названные в тексте, без ключей: сверяются имена, не запуск."""
    return {p for p in CALL_RE.findall(text) if p not in NOT_A_GATE}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    args = parser.parse_args(argv)
    root: Path = args.root

    charter = root / "CLAUDE.md"
    onramp = root / "CONTRIBUTING.md"
    pipeline = root / ".github" / "workflows" / "ci.yml"
    harness = root / "scripts" / "check_gates.py"

    # ── исход 2 ────────────────────────────────────────────────────────────
    for path in (charter, onramp, pipeline):
        if not path.exists():
            print(f"проверка не отработала: нет {path.name} — "
                  "сверять не с чем", file=sys.stderr)
            return 2

    charter_text = charter.read_text(encoding="utf-8")
    gates_section = section(charter_text, CHARTER_SECTION)
    if gates_section is None:
        print(f"проверка не отработала: в своде нет раздела «{CHARTER_SECTION}» — "
              "таблицы гейтов, с которой сверяется конвейер", file=sys.stderr)
        return 2

    in_pipeline = named_in(pipeline.read_text(encoding="utf-8"))
    if not in_pipeline:
        print("проверка не отработала: в ci.yml не нашлось ни одного гейта — "
              "это ошибка разбора, а не пустой конвейер", file=sys.stderr)
        return 2

    in_charter = named_in(gates_section)
    in_onramp = named_in(onramp.read_text(encoding="utf-8"))

    # ── исход 1 ────────────────────────────────────────────────────────────
    problems: list[str] = []

    def compare(name: str, declared: set[str], where: str) -> None:
        for missing in sorted(in_pipeline - declared):
            problems.append(
                f"{name}: гейт {missing} стоит в конвейере, а в {where} его нет. "
                "Читающий не узнает о проверке, которая его остановит")
        for extra in sorted(declared - in_pipeline):
            problems.append(
                f"{name}: в {where} обещан {extra}, а в конвейере такого шага "
                "нет. Обещание, которое никто не исполняет")

    compare("свод", in_charter, "таблице CLAUDE.md")
    compare("документ для участника", in_onramp, "списке CONTRIBUTING.md")

    if problems:
        print("объявленные гейты разошлись с конвейером:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        print("\n  Канон — шаги ci.yml: их исполняет площадка, а строку в "
              "документе\n  не исполняет никто (правила 022, 002).",
              file=sys.stderr)
        return 1

    # ── исход 0 плюс метрика ───────────────────────────────────────────────
    # Правило 140: гейт без отвергаемого предмета проверен только на запуск.
    # Это метрика, а не отказ: чинится она работой, а не правкой изменения,
    # и красное здесь приучало бы читать красное как фон (правило 051).
    # Отвергаемый предмет гейт получает ДВУМЯ разными механизмами, и метрика
    # обязана видеть оба. Пока она смотрела в один check_gates.py, она называла
    # непроверенными гейты, у которых уже лежал набор в tests/, — то есть врала
    # ровно в ту сторону, в какую метрике врать нельзя (правила 022, 146).
    by_harness: set[str] = set()
    if harness.exists():
        harness_text = harness.read_text(encoding="utf-8")
        by_harness = {g for g in in_pipeline if Path(g).stem in harness_text}
    by_tests = {g for g in in_pipeline
                if (root / "tests" / f"test_{Path(g).stem}.py").exists()}
    untested = sorted(in_pipeline - by_harness - by_tests)

    print(f"свод и конвейер называют одно и то же: гейтов {len(in_pipeline)}, "
          f"расхождений нет")
    print(f"  подделкой в check_gates: {len(by_harness)}, "
          f"набором в tests: {len(by_tests)}, "
          f"только запуском {len(untested)}")
    if untested:
        print("  без отвергаемого предмета: "
              + ", ".join(Path(g).stem for g in untested))
    return 0


if __name__ == "__main__":
    sys.exit(main())
