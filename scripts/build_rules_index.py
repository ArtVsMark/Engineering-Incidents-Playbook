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
  • в дереве не нашлось ни одного правила;
  • у правила нет строки «Область» — молча пустая колонка уже стоила каталогу
    всей классификации (правило 125);
  • область не значится в словаре AREAS: опечатка иначе заводит новую область;
  • области ru и en не соответствуют друг другу через словарь.

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

#: Пути правил, заполняется в main() — из него строятся ссылки навигации.
FILES: dict[str, dict[str, Path]] = {}

RULE_RE = re.compile(r"^(\d{3})-[a-z0-9-]+\.md$")
LINK_RE = re.compile(r"\]\((\d{3}-[^)#]+\.md)\)")
#: Область живёт в самом правиле, строкой под заголовком.
AREA_RE = {
    "ru": re.compile(r"^\*\*Область\.\*\*\s*(.+?)\s*$", re.M),
    "en": re.compile(r"^\*\*Area\.\*\*\s*(.+?)\s*$", re.M),
}

#: Словарь областей — в паре «по-русски / in English». Это закрытый список:
#: область, которой здесь нет, сборку не проходит. Иначе опечатка заводит новую
#: область молча, и рядом живут «интерфейс» и «интерфейсы» (правило 099).
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
    "трекер": "tracker", "прогоны": "runs",
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


def areas_of(path: Path, lang: str) -> list[str]:
    """Область правила — из самого файла. Пусто, если строки нет."""
    m = AREA_RE[lang].search(path.read_text(encoding="utf-8"))
    return [a.strip() for a in m.group(1).split(",") if a.strip()] if m else []


def check_areas(found: dict[str, dict[str, Path]]) -> tuple[dict[str, list[str]], list[str]]:
    """Читает области из правил и сверяет деревья.

    Область хранится в самих правилах, а не в этом указателе: производный файл
    не может быть хранилищем — регенерация обнуляет его молча (правило 125).
    """
    problems: list[str] = []
    result: dict[str, list[str]] = {}
    for num in sorted(found):
        slot = found[num]
        if not all(l in slot for l in LANGS):
            continue                      # об этом уже скажет check_pairs
        ru = areas_of(slot["ru"], "ru")
        en = areas_of(slot["en"], "en")
        for lang, got in (("ru", ru), ("en", en)):
            if not got:
                problems.append(f"{num}: нет строки «Область» в {lang}/{slot[lang].name}")
        if not ru or not en:
            continue
        unknown = [a for a in ru if a not in AREAS]
        if unknown:
            problems.append(
                f"{num}: область вне словаря AREAS — {', '.join(unknown)}"
                " (опечатка или новая область: допишите её в словарь осознанно)"
            )
            continue
        expected = [AREAS[a] for a in ru]
        if en != expected:
            problems.append(
                f"{num}: области деревьев расходятся — ru «{', '.join(ru)}»"
                f" ждёт en «{', '.join(expected)}», а стоит «{', '.join(en)}»"
            )
            continue
        result[num] = ru
    return result, problems


def by_area(areas: dict[str, list[str]], lang: str) -> str:
    """Строки навигации по областям: сначала крупные, потом одиночные."""
    buckets: dict[str, list[str]] = {}
    for num, names in areas.items():
        for a in names:
            buckets.setdefault(a, []).append(num)
    name_of = (lambda a: a) if lang == "ru" else (lambda a: AREAS[a])
    order = sorted(buckets, key=lambda a: (-len(buckets[a]), name_of(a)))
    lines = []
    for a in order:
        nums = sorted(buckets[a])
        links = ", ".join(f"[{n}]({lang}/{FILES[n][lang].name})" for n in nums)
        lines.append(f"- **{name_of(a)}** ({len(nums)}) — {links}")
    return "\n".join(lines)


def render(found: dict[str, dict[str, Path]], gaps: list[int],
           areas: dict[str, list[str]]) -> str:
    rows = []
    for num in sorted(found):
        slot = found[num]
        ru = slot.get("ru")
        en = slot.get("en")
        t_ru = title_of(ru) if ru else "—"
        t_en = title_of(en) if en else "—"
        l_ru = f"[ru](ru/{ru.name})" if ru else "—"
        l_en = f"[en](en/{en.name})" if en else "—"
        names = areas.get(num, [])
        both = f"{', '.join(names)} · {', '.join(AREAS[a] for a in names)}" if names else ""
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

## По областям

Быстрый вход в каталог не по номеру, а по предмету. Правило стоит в нескольких
областях, если относится к нескольким, — поэтому сумма по областям больше числа
правил. Порядок — по числу правил: крупные области сверху, одиночные внизу.
Ссылки ведут в русское дерево.

{by_area(areas, "ru")}

## By area

A way into the catalogue by subject rather than by number. A rule sits in several
areas when it belongs to several, so the areas add up to more than the number of
rules. Ordered by rule count: the large areas first, the singletons last. Links
point at the English tree.

{by_area(areas, "en")}

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
    FILES.update(found)
    areas, area_problems = check_areas(found)
    problems += area_problems

    nums = sorted(int(n) for n in found)
    gaps = [i for i in range(nums[0], nums[-1] + 1) if i not in set(nums)] if nums else []

    if problems:
        print("указатель не собран:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    text = render(found, gaps, areas)
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("указатель устарел — пересоберите: python scripts/build_rules_index.py",
                  file=sys.stderr)
            return 1
        print(f"указатель актуален: {len(found)} правил на {len(LANGS)} языках,"
              f" областей {len({a for v in areas.values() for a in v})}")
        return 0

    OUT.write_text(text, encoding="utf-8")
    print(f"собрано: {len(found)} правил, языков {len(LANGS)},"
          f" областей {len({a for v in areas.values() for a in v})},"
          f" пропуски в нумерации: {gaps or 'нет'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
