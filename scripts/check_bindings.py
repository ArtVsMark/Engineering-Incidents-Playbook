#!/usr/bin/env python3
"""Проверяет ответ каталога о самом себе и печатает, чем правила держатся.

Каталог — такой же проект-потребитель, как и остальные: у него есть механизмы,
и он обязан отвечать за каждое правило (правило 129). Этот скрипт проверяет
ответ по контракту из export/README.md и считает метрику из 120.

Реализует правила каталога:
  129 — ответ потребителя: статус, чем держится, где, причина для отрицательных;
  128 — обязательное поле проверяется на полноту: ответ нужен по КАЖДОМУ правилу,
        а не по тем, до которых дошли руки;
  120 — «сколько правил не обеспечено ничем» — метрика, и она должна уменьшаться;
  039 — у проверки три исхода, а не два;
  026 — отрицательное решение записывается с причиной.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BINDINGS = ROOT / ".rules" / "bindings.json"
EXPORT = ROOT / "export" / "rules.json"

STATUSES = ("active", "rejected", "not-applicable", "unreviewed")
MECHANISMS = ("gate", "process-step", "none")

#: Ревизор входит от списка деклараций и ищет расхождение с фактом. Ответ
#: каталога — это список деклараций: «держится гейтом вот здесь». Проверять
#: надо не форму записи, а то, что заявленное существует (правило 082 —
#: направление без владельца; здесь владелец машинный).
PATH_RE = re.compile(r"[\w./-]+\.(?:py|yml|yaml|json|md|txt)")

#: Корневые документы, которые в прозе называют БЕЗ расширения: «CONTRIBUTING»,
#: «README». Под PATH_RE такой токен не попадает, и утверждение о нём проходило
#: молча — ровно так ответ по 065 год говорил «точки входа новичка нет», когда
#: CONTRIBUTING.md лежал в корне (задача #67).
BARE_DOCS = ("CONTRIBUTING", "README", "LICENSE", "CHANGELOG", "SECURITY",
             "HISTORY", "CLAUDE", "VERSIONING", "START", "TOP-10")
BARE_RE = re.compile(r"\b(" + "|".join(BARE_DOCS) + r")\b")

#: Слова, которыми утверждают ОТСУТСТВИЕ. Не всякое отрицание годится:
#: «не проверяется» — про механизм, «нет» — про предмет. Ловим только второе,
#: иначе шум забьёт находку (правило 051).
ABSENCE_RE = re.compile(
    r"\b(нет|не существует|отсутству\w*|не заведён\w*|не заведена|не создан\w*)\b")

#: Окно разбора — фрагмент вокруг имени, а не всё поле: в длинном пояснении
#: «нет» из соседнего предложения относилось бы не к тому (правило 144).
ABSENCE_WINDOW = 60
#: Число словом внутри ответа устареет так же, как цифра (правила 005, 127).
COUNT_RE = re.compile(r"\b(два|две|три|четыре|пять|шесть|семь|восемь|девять|десять)\b")


def main() -> int:
    # ── исход 2 ────────────────────────────────────────────────────────────
    for path in (BINDINGS, EXPORT):
        if not path.exists():
            print(f"проверка не отработала: нет {path.relative_to(ROOT)}", file=sys.stderr)
            return 2
    try:
        answer = json.loads(BINDINGS.read_text(encoding="utf-8"))
        export = json.loads(EXPORT.read_text(encoding="utf-8"))
    except ValueError as e:
        print(f"проверка не отработала: не разобрать JSON — {e}", file=sys.stderr)
        return 2

    rules = answer.get("rules")
    if not isinstance(rules, dict) or not rules:
        print("проверка не отработала: в ответе нет записей — сверять нечего",
              file=sys.stderr)
        return 2

    known = {r["id"]: r for r in export["rules"]}

    # ── исход 1 ────────────────────────────────────────────────────────────
    problems: list[str] = []
    warnings: list[str] = []
    for rid in sorted(set(known) - set(rules)):
        problems.append(f"{rid}: ответа нет. «Не дошли руки» — это статус "
                        "unreviewed, а не отсутствующая запись")
    for rid in sorted(set(rules) - set(known)):
        problems.append(f"{rid}: ответ есть, а правила такого в каталоге нет")

    for rid, rec in sorted(rules.items()):
        status = rec.get("status")
        if status not in STATUSES:
            problems.append(f"{rid}: статус {status!r} вне набора {STATUSES}")
            continue
        if status == "active":
            if rec.get("mechanism") not in MECHANISMS:
                problems.append(f"{rid}: действует, но механизм "
                                f"{rec.get('mechanism')!r} вне набора {MECHANISMS}")
            if not rec.get("where"):
                problems.append(f"{rid}: действует, а где именно — не сказано")
        # Ревизия: заявленное должно существовать, а не звучать правдоподобно.
        claim = f"{rec.get('where', '')} {rec.get('why', '')}"
        for token in PATH_RE.findall(claim):
            if not (ROOT / token).exists():
                problems.append(f"{rid}: заявлено «{token}», а такого файла нет — "
                                "декларация разошлась с фактом")
        # Утверждение об отсутствии документа, который есть. Предупреждение,
        # а не отказ: «нет» рядом с именем — подозрение, а не факт, и живая
        # проза даёт достаточно законных сочетаний (правило 051).
        for m in BARE_RE.finditer(claim):
            near = claim[max(0, m.start() - ABSENCE_WINDOW):
                         m.end() + ABSENCE_WINDOW]
            if not ABSENCE_RE.search(near):
                continue
            name = m.group(1)
            found = [c for c in (name, f"{name}.md", f"{name}.txt")
                     if (ROOT / c).exists()]
            if found:
                warnings.append(
                    f"{rid}: сказано, что {name} нет, а {found[0]} есть — "
                    f"похоже на устаревший ответ")

        # Правило 051: запрещают достоверное, предупреждают о вероятном.
        # Несуществующий путь — факт. Число словом — подозрение: «два дерева»
        # не устареет, «четыре гейта» устареет. Отказ здесь был бы ложным.
        if COUNT_RE.search(claim):
            warnings.append(f"{rid}: число словом — «{claim.strip()[:60]}». "
                            "Считать должен тот, кто печатает метрику")

        if status in ("rejected", "not-applicable") and not rec.get("why"):
            problems.append(f"{rid}: статус {status!r} без причины — "
                            "решение без причины вернётся следующей ревизией")

    if problems:
        print("ответ каталога о себе не в порядке:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    # ── исход 0 плюс метрика ───────────────────────────────────────────────
    by_status = Counter(r["status"] for r in rules.values())
    by_mech = Counter(r.get("mechanism") for r in rules.values()
                      if r["status"] == "active")

    unreviewed = [rid for rid, r in rules.items() if r["status"] == "unreviewed"]
    oldest = ""
    if unreviewed:
        dates = [known[rid]["added"] for rid in unreviewed if known[rid].get("added")]
        if dates:
            days = (dt.date.today() - dt.date.fromisoformat(min(dates))).days
            oldest = f", самому старому {days} дн."

    if warnings:
        print("на что стоит посмотреть (не отказ):")
        for w in warnings:
            print(f"  ~ {w}")
    print(f"ответ каталога о себе полон: {len(rules)} правил")
    print(f"  действует {by_status['active']}: "
          f"гейтом {by_mech['gate']}, шагом процесса {by_mech['process-step']}, "
          f"НИЧЕМ {by_mech['none']}")
    print(f"  отклонено {by_status['rejected']}, "
          f"нет предмета {by_status['not-applicable']}")
    print(f"  не рассмотрено {by_status['unreviewed']}{oldest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
