#!/usr/bin/env python3
"""Собирает единый двуязычный указатель правил из самих файлов.

Реализует правила каталога:
  120 — указатель пересобирается из файлов, а не правится руками;
  022 — одна тема, один канонический документ: указатель ровно один;
  049 — состояние выводится из живых артефактов;
  075 — не нашёл предмета проверки — падает, а не зеленеет;
  116 — сверка «сколько на входе / сколько на выходе» обязательна.

Падает (код 1), если:
  • правило есть на одном языке и отсутствует на другом — та самая ошибка,
    ради которой указатель и сделан единым;
  • номер встречается дважды;
  • перекрёстная ссылка ведёт в несуществующий файл;
  • в дереве не нашлось ни одного правила.

Пропуск в нумерации — не ошибка: номера не переиспользуются даже после
удаления (правило 120). Он печатается как факт.

Запуск:  python scripts/build_rules_index.py          # записать rules/README.md
         python scripts/build_rules_index.py --check   # только проверить
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"
LANGS = ("ru", "en")
OUT = RULES / "README.md"

RULE_RE = re.compile(r"^(\d{3})-[a-z0-9-]+\.md$")
LINK_RE = re.compile(r"\]\((\d{3}-[^)#]+\.md)\)")

#: Область правила — в паре «по-русски / in English». Ключ берётся из русской
#: колонки прежнего указателя; новые области дописываются сюда осознанно.
AREAS = {
    "квоты": "quotas", "API": "API", "процесс": "process", "CI": "CI",
    "конвейер": "pipeline", "автоматика": "automation", "документация": "documentation",
    "агентские сессии": "agent sessions", "витрины": "showcases", "метрики": "metrics",
    "наблюдение": "observation", "командная работа": "collaboration", "инструменты": "tooling",
    "тесты": "tests", "параллельная работа": "parallel work", "вывод": "output",
    "отчёты": "reports", "диагностика": "diagnostics", "среды": "environments",
    "аудит": "audit", "темп": "pace", "релиз": "release", "роли": "roles",
    "надёжность": "reliability", "решения": "decisions", "безопасность": "security",
    "гейты": "gates", "данные": "data", "ресурсы": "resources", "код": "code",
    "конкурентность": "concurrency", "архитектура": "architecture",
    "локализация": "localisation", "интерфейс": "interface", "приватность": "privacy",
    "продукт": "product", "сообщество": "community", "миграции": "migrations",
    "контракты": "contracts", "таксономия": "taxonomy", "сеть": "network",
    "качество": "quality", "сравнение": "comparison", "заимствование": "borrowing",
    "планирование": "planning", "каталог": "catalogue", "ИИ": "AI",
    "история": "history", "конфигурация": "configuration",
}


def title_of(path: Path) -> str:
    first = path.read_text(encoding="utf-8").split("\n", 1)[0]
    return first.lstrip("# ").strip()


def collect() -> tuple[dict[str, dict[str, Path]], list[str]]:
    found: dict[str, dict[str, Path]] = {}
    problems: list[str] = []
    for lang in LANGS:
        d = RULES / lang
        if not d.is_dir():
            problems.append(f"нет каталога {d.relative_to(ROOT)}")
            continue
        for f in sorted(d.iterdir()):
            m = RULE_RE.match(f.name)
            if not m:
                continue
            num = m.group(1)
            slot = found.setdefault(num, {})
            if lang in slot:
                problems.append(f"{lang}: номер {num} встречается дважды")
            slot[lang] = f
    if not found:
        problems.append("в дереве не нашлось ни одного правила")
    return found, problems


def check_links(found: dict[str, dict[str, Path]]) -> list[str]:
    problems = []
    for lang in LANGS:
        d = RULES / lang
        if not d.is_dir():
            continue
        for f in d.glob("*.md"):
            for m in LINK_RE.finditer(f.read_text(encoding="utf-8")):
                if not (d / m.group(1)).exists():
                    problems.append(f"{lang}/{f.name}: ссылка в никуда → {m.group(1)}")
    return problems


def check_pairs(found: dict[str, dict[str, Path]]) -> list[str]:
    problems = []
    for num in sorted(found):
        slot = found[num]
        missing = [l for l in LANGS if l not in slot]
        if missing:
            have = next(iter(slot.values())).name
            problems.append(
                f"{num}: нет перевода на {', '.join(missing)} — есть только {have}"
            )
        elif len({p.name for p in slot.values()}) > 1:
            names = " / ".join(f"{l}:{slot[l].name}" for l in LANGS)
            problems.append(f"{num}: имена файлов расходятся — {names}")
    return problems


def old_areas() -> dict[str, str]:
    """Область берётся из прежнего указателя, если он ещё существует."""
    areas: dict[str, str] = {}
    for legacy in (RULES / "ru" / "README.md", OUT):
        if not legacy.exists():
            continue
        for line in legacy.read_text(encoding="utf-8").split("\n"):
            m = re.match(r"\| \[(\d{3})\][^|]*\|[^|]*\|(?:[^|]*\|)*\s*([^|]+?)\s*\|$", line)
            if m:
                areas.setdefault(m.group(1), m.group(2))
    return areas


def render(found: dict[str, dict[str, Path]], gaps: list[int]) -> str:
    areas = old_areas()
    rows = []
    for num in sorted(found):
        slot = found[num]
        ru = slot.get("ru")
        en = slot.get("en")
        t_ru = title_of(ru) if ru else "—"
        t_en = title_of(en) if en else "—"
        l_ru = f"[ru](ru/{ru.name})" if ru else "—"
        l_en = f"[en](en/{en.name})" if en else "—"
        area = areas.get(num, "")
        area_en = ", ".join(AREAS.get(a.strip(), a.strip()) for a in area.split(",")) if area else ""
        both = f"{area} · {area_en}" if area else ""
        rows.append(f"| {num} | {t_ru} | {t_en} | {l_ru} {l_en} | {both} |")

    gap_note = ""
    if gaps:
        gap_note = (
            "\n> Пропуски в нумерации: "
            + ", ".join(str(g) for g in gaps)
            + ". Это не ошибка — номера не переиспользуются даже после удаления"
            + " ([`120`](ru/120-how-to-run-a-rule-catalogue.md)).\n"
        )

    return f"""# Правила · Rules

Один файл — одно правило, одинаковое имя в обоих деревьях.
One file, one rule, the same file name in both trees.

Формат: правило → инцидент → почему → применимость → след.
Shape: rule → incident → why → where it applies → trace.

> **Этот файл собирается скриптом** `scripts/build_rules_index.py` и не правится
> руками. Правило, добавленное только на одном языке, не пройдёт сборку — это и
> есть механизм, который не даёт деревьям разойтись.
>
> **This file is generated** by `scripts/build_rules_index.py` and is never
> edited by hand. A rule added in only one language fails the build — that is the
> mechanism keeping the two trees from diverging.
{gap_note}
Всего правил · rules in total: **{len(found)}**

| № | Правило | Rule | Файлы · Files | Область · Area |
|---|---|---|---|---|
{chr(10).join(rows)}

---

## Как добавить своё

Правило рождается — запись в тот же день. Материал портится быстро: инциденты
месячной давности приходится восстанавливать по документам, потому что в памяти
их уже нет. Заготовка — [`templates/rule-template.md`](../templates/rule-template.md).

Обязательны две части, которые чаще всего пропускают:

- **Применимость** — где правило **не** работает. Без неё каталог скопируют
  целиком, включая заведомо чужое.
- **След** — ссылка на issue, PR или документ, где поломка видна. Без неё запись
  за месяц превращается в «кто-то говорил, что так лучше».

Запись делается **на обоих языках сразу**. Не потому что так аккуратнее, а
потому что иначе она не пройдёт сборку указателя.

## How to add your own

A rule is born — the record is written the same day. The material spoils fast:
incidents a month old have to be reconstructed from documents, because nobody
remembers them any more. Boilerplate:
[`templates/rule-template.md`](../templates/rule-template.md).

Two parts are mandatory and are the ones most often skipped:

- **Where it applies** — where the rule does **not** work. Without it the
  catalogue gets copied wholesale, including what plainly belongs to somebody
  else.
- **Trace** — a link to the issue, pull request or document where the failure is
  visible. Without it, within a month the record becomes "somebody said this was
  better".

The record is written **in both languages at once**. Not out of tidiness, but
because otherwise it will not pass the index build.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="только проверить, не записывать")
    args = ap.parse_args()

    found, problems = collect()
    problems += check_pairs(found)
    problems += check_links(found)

    nums = sorted(int(n) for n in found)
    gaps = [i for i in range(nums[0], nums[-1] + 1) if i not in set(nums)] if nums else []

    if problems:
        print("указатель не собран:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    text = render(found, gaps)
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("указатель устарел — пересоберите: python scripts/build_rules_index.py",
                  file=sys.stderr)
            return 1
        print(f"указатель актуален: {len(found)} правил на {len(LANGS)} языках")
        return 0

    OUT.write_text(text, encoding="utf-8")
    print(f"собрано: {len(found)} правил, языков {len(LANGS)}, пропуски в нумерации: {gaps or 'нет'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
