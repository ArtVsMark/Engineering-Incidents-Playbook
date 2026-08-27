#!/usr/bin/env python3
"""Собирает готовый набор файлов, которым проект подключается к каталогу.

ПОЧЕМУ ГЕНЕРАТОР, А НЕ ИНСТРУКЦИЯ. Подключение — это три файла с точным
содержимым, и «скопируйте из контракта» уже дало то, что дало: канал построен
с обеих сторон, а объявленных потребителей подключено меньше половины и адрес
предложений не назван ни одним. Шаг, который надо помнить, пропускают —
и человек, и окно (правило 002).

ПОЧЕМУ СОБИРАЕТ КАТАЛОГ, А НЕ КАЖДЫЙ У СЕБЯ. Реализация одна и у автора: копия
генератора в каждом репозитории — это N реализаций одного алгоритма, и первая
же правка разведёт их (090, 022). Отсюда и форма: скрипт КЛАДЁТ файлы в
указанную папку, а несёт их в чужой репозиторий человек. Каталог наружу не
пишет — это исполнение 131, а не ограничение инструмента.

ЗАКРЕПЛЁННЫЙ ТЕГ БЕРЁТСЯ ИЗ КОНТРАКТА, А НЕ ВПИСЫВАЕТСЯ СЮДА. Иначе рядом
появится второе место, где живёт номер версии, и они разойдутся молча (035,
022). Маркер в export/README.md переписывает выпуск.

ВСЕ ПРАВИЛА ПРИХОДЯТ СО СТАТУСОМ «не рассмотрено», и это не заготовка-пустышка:
ответ нужен по КАЖДОМУ правилу, а не по тем, до которых дошли руки (128).
Проект отвечает, а не начинает с чистого листа, где отсутствие ответа
неотличимо от «нам это не нужно».

Запуск:  python scripts/onboard_consumer.py --repo владелец/имя --out ПАПКА
Коды:    0 собрано · 1 собрать нечего · 2 проверка не отработала
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / "export" / "rules.json"
CONTRACT = ROOT / "export" / "README.md"
CATALOGUE = "ArtVsMark/claude-code-playbook"

#: Закреплённый тег живёт в маркере контракта: его переписывает выпуск.
REF_RE = re.compile(r"<!--m:ref-->(.+?)<!--/m:ref-->")
REPO_RE = re.compile(r"^[\w.-]+/[\w.-]+$")

WORKFLOW = """# Входящие правила каталога {catalogue}.
#
# Собрано `scripts/onboard_consumer.py` каталога — руками не правится целиком,
# но закрепление тега и расписание менять можно и нужно осознанно.
#
# Своего скрипта здесь нет намеренно: реализация одна и живёт у автора
# каталога. Копия генератора в каждом проекте — это N реализаций одного
# алгоритма, и первая же правка разведёт их.
name: rules-inbox

on:
  schedule:
    # Не в 0 и не в 30: минута выбрана так, чтобы не совпадать с пиком.
    - cron: "17 6 * * *"
  # У события всегда есть ручная кнопка.
  workflow_dispatch:

permissions:
  contents: read
  issues: write

concurrency:
  group: rules-inbox
  cancel-in-progress: true

jobs:
  inbox:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: {catalogue}@{ref}
        with:
          token: ${{{{ secrets.GITHUB_TOKEN }}}}
"""

PROPOSALS = {
    "_": ("Правила, родившиеся ЗДЕСЬ и предлагаемые общему каталогу. Адрес этого "
          "файла называется в реестре каталога, .rules/consumers.json, поле "
          "proposals. Контракт: export/README.md каталога."),
    "_номер": ("Номера здесь нет и быть не может: его присваивает каталог при "
               "приёме. Номера не переиспользуются, и если два проекта выберут "
               "номер независимо, столкновение уже нечем починить. Поля id, "
               "number, rule — ошибка, и прогон каталога о ней скажет."),
    "_что_слать": ("Инцидент, а не готовую запись: что сломалось, с числами и "
                   "последовательностью событий. Оба языковых дерева, словарь "
                   "областей, ответ о соседях и разрешимый след живут в каталоге."),
    "_пусто": ("Пустой список — законное состояние и означает «предлагать пока "
               "нечего». Отсутствие файла означает другое: «канал не подключён»."),
    "schema": "1.0",
    "proposals": [],
}


def pinned_ref(contract: Path) -> tuple[str | None, str | None]:
    """Тег из маркера контракта. Второй элемент — причина отказа."""
    try:
        m = REF_RE.search(contract.read_text(encoding="utf-8"))
    except OSError as e:
        return None, f"контракт не прочитан — {e}"
    if not m:
        return None, ("в контракте нет маркера закреплённого тега — брать номер "
                      "неоткуда, а вписывать его сюда значит завести второе "
                      "место для версии")
    return m.group(1).strip(), None


def build(repo: str, ids: list[str], ref: str) -> dict[str, str]:
    """Пути и содержимое набора. Ключ — путь внутри репозитория проекта."""
    bindings = {
        "schema": "1.0",
        "project": repo,
        "catalogue": f"https://github.com/{CATALOGUE}",
        "_": ("Ответ ЭТОГО проекта по каждому правилу каталога. Статус — active, "
              "rejected, not-applicable или unreviewed; у двух отрицательных "
              "обязательна причина в поле why, у active — mechanism и where."),
        "_зачем": ("Ответ живёт здесь, а не в каталоге, потому что здесь живёт "
                   "механизм: одно правило в разных проектах держится по-разному."),
        "rules": {i: {"status": "unreviewed"} for i in ids},
    }
    return {
        ".rules/bindings.json": json.dumps(bindings, ensure_ascii=False, indent=2) + "\n",
        ".rules/proposals.json": json.dumps(PROPOSALS, ensure_ascii=False, indent=2) + "\n",
        ".github/workflows/rules-inbox.yml": WORKFLOW.format(catalogue=CATALOGUE, ref=ref),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, metavar="ВЛАДЕЛЕЦ/ИМЯ")
    ap.add_argument("--out", type=Path, required=True, metavar="ПАПКА",
                    help="куда сложить набор; папка создаётся")
    ap.add_argument("--export", type=Path, default=EXPORT)
    ap.add_argument("--contract", type=Path, default=CONTRACT)
    args = ap.parse_args(argv)

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not REPO_RE.match(args.repo):
        print(f"проверка не отработала: {args.repo!r} не похоже на "
              "«владелец/имя»", file=sys.stderr)
        return 2
    try:
        doc = json.loads(args.export.read_text(encoding="utf-8"))
        ids = [r["id"] for r in doc["rules"]]
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"проверка не отработала: экспорт каталога не разобран — {e}",
              file=sys.stderr)
        return 2
    ref, err = pinned_ref(args.contract)
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    # ── исход 1 ────────────────────────────────────────────────────────────
    if not ids:
        print("собирать нечего: в экспорте каталога нет ни одного правила",
              file=sys.stderr)
        return 1

    # ── исход 0 ────────────────────────────────────────────────────────────
    for rel, body in build(args.repo, ids, ref).items():
        path = args.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        print(f"  {rel}")
    print(f"набор для {args.repo} собран: правил {len(ids)}, действие закреплено "
          f"на {ref}")
    print("\nПоложите эти файлы в репозиторий проекта, затем добавьте его в "
          "реестр каталога\n.rules/consumers.json одной записью:\n")
    print(json.dumps({
        "repo": args.repo, "role": "потребитель", "access": "public",
        "since": "<день объявления, ГГГГ-ММ-ДД>",
        "bindings": f"https://raw.githubusercontent.com/{args.repo}/main/.rules/bindings.json",
        "proposals": f"https://raw.githubusercontent.com/{args.repo}/main/.rules/proposals.json",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
