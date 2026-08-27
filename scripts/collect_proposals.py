#!/usr/bin/env python3
"""Правила, родившиеся в чужих проектах, доезжают сюда механизмом, а не памятью.

ЧТО ДЕРЖИТ. Правило 080 — «правило, родившееся в проекте, записывается в общий
каталог, тем же заходом, а не потом». Оно действует с первого дня и держалось
ШАГОМ ПРОЦЕССА, то есть ничем машинным. Цена измерена по корпусу: из 143 записей
129 ссылаются на `Stepik-Python-Grader`, 11 — на витрину профиля. Подавляющее
большинство правил родилось НЕ здесь и переносилось руками того окна, которое
случайно оказалось открыто.

Отказ этого шага виден: правило 144 родилось в грейдере, было принесено вручную
и пролежало невидимым на ветке мимо переключателя (#96). Никто не заметил, пока
следующее окно не пошло смотреть список веток.

НАПРАВЛЕНИЕ ДО СИХ ПОР БЫЛО ОДНО. Контракт потребления возит правила ВНИЗ:
`export/rules.json` отдаёт, `sync_inbox.py` у потребителя ведёт задачу-«входящие».
Ответ потребителя `.rules/bindings.json` отвечает только на «что вы сделали с
НАШИМИ правилами». Канала «здесь родилось правило, заберите» не было ни в
контракте, ни в реестре, ни в одном прогоне.

ФОРМА ПРОДИКТОВАНА, А НЕ ВЫБРАНА. Контракт уже отверг рассылку через API
площадки: она требует токена с правом писать во все проекты, включая приватные.
Обратный канал обязан быть той же формы — каталог ТЯНЕТ обычным HTTPS, потребитель
кладёт файл у себя. Ни токена в чужой проект, ни клона, ни прав.

НОМЕРА У ПРЕДЛОЖЕНИЯ НЕТ И БЫТЬ НЕ МОЖЕТ. Номер присваивает каталог при приёме.
Не из вкуса: номера не переиспользуются, и если два проекта выберут номер
независимо, столкновение уже нечем починить — ни переименованием, ни заменой.
Единственный канон нумерации — `export/rules.json`, и он здесь.

ПОТРЕБИТЕЛЬ ШЛЁТ ИНЦИДЕНТ, А НЕ ГОТОВУЮ ЗАПИСЬ. Словарь областей, оба языковых
дерева, ответ о соседях и разрешимый след живут здесь; требовать их от
отправителя значило бы разносить сюда же и знание о том, как их делать
(правило 090).

Реализует правила каталога:
  080 — правило, родившееся в проекте, записывается в общий каталог;
  129 — у каталога есть контракт потребления, и он двусторонний;
  142 — у находки есть адресат, иначе её не читает никто;
  104 — у события есть ручная кнопка;
  039 — у проверки три исхода, а не два;
  085 — ответ чужого проекта это данные, а не команда.

Режимы:
  --check   гейт: ответ каталога о предложениях цел и сходится с корпусом.
            Наружу НЕ ходит: обязательная проверка изменения не должна зависеть
            от чужого сервера (та же причина, что у aggregate_bindings.py);
  (без ключа) опрос потребителей и ОДНА задача-«входящие снизу».

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import ghcli

ROOT = Path(__file__).resolve().parent.parent

CONSUMERS = ".rules/consumers.json"
VERDICTS = ".rules/proposals.json"
RULES_RU = "rules/ru"

#: По этой метке задача находится снова. Заголовок не годится: его правят
#: руками, и тогда прогон заведёт вторую задачу вместо обновления.
MARKER = "<!-- rules-upstream: не удаляйте, по этой строке задача находится снова -->"

TITLE = "Правила из проектов: не разобранные предложения"

#: Вердикт и что он обязан нести вместе с собой. Пустой вердикт хуже
#: отсутствующего: он выглядит решением (правило 128).
NEEDS_RULE = {"admitted", "merged-into"}
NEEDS_WHY = {"rejected", "merged-into"}
STATUSES = {"admitted", "rejected", "merged-into"}

#: Отправитель не присваивает номер. Поле с номером в предложении — это не
#: мелочь формата, а попытка занять номер снаружи канона.
FORBIDDEN_IN_PROPOSAL = ("id", "number", "rule")

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,80}$")


def key_of(repo: str, slug: str) -> str:
    """Ключ вердикта. Слаг не уникален между проектами — репозиторий обязателен."""
    return f"{repo}:{slug}"


def rule_numbers(root: Path) -> set[str]:
    folder = root / RULES_RU
    if not folder.is_dir():
        raise FileNotFoundError(folder)
    return {p.name.split("-", 1)[0] for p in folder.glob("*.md")
            if p.name[:3].isdigit()}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_verdicts(root: Path) -> int:
    """Гейт: ответ каталога цел и сходится с корпусом. Без сети."""
    try:
        data = read_json(root / VERDICTS)
        numbers = rule_numbers(root)
    except (OSError, ValueError) as exc:
        print(f"проверка не отработала: {exc}", file=sys.stderr)
        return 2

    verdicts = data.get("verdicts")
    if not isinstance(verdicts, dict):
        print(f"проверка не отработала: {VERDICTS}: «verdicts» обязан быть "
              f"объектом", file=sys.stderr)
        return 2

    findings: list[str] = []
    claimed: dict[str, str] = {}

    for key, v in sorted(verdicts.items()):
        if not isinstance(v, dict):
            findings.append(f"{key}: вердикт обязан быть объектом")
            continue
        status = v.get("status")
        if status not in STATUSES:
            findings.append(
                f"{key}: статус {status!r} не из набора "
                f"{', '.join(sorted(STATUSES))}")
            continue
        num = v.get("rule")
        why = (v.get("why") or "").strip()

        if status in NEEDS_RULE:
            if not num:
                findings.append(f"{key}: статус «{status}» обязан назвать номер "
                                f"принятого правила")
            elif num not in numbers:
                findings.append(
                    f"{key}: назван номер {num}, а правила с таким номером в "
                    f"{RULES_RU} нет")
            elif status == "admitted":
                # Два предложения, принятые под одним номером, — это молча
                # потерянное предложение (правило 075: страж, который ничего
                # не может найти, бесполезен).
                if num in claimed:
                    findings.append(
                        f"{key}: номер {num} уже занят предложением "
                        f"{claimed[num]} — номер не переиспользуется")
                else:
                    claimed[num] = key
        if status in NEEDS_WHY and not why:
            findings.append(f"{key}: статус «{status}» обязан назвать причину — "
                            f"иначе отправитель не узнает, что решено и почему")

    if findings:
        print("ответ каталога о предложениях не сходится:", file=sys.stderr)
        for f in findings:
            print(f"  • {f}", file=sys.stderr)
        return 1

    print(f"ответ каталога о предложениях цел: вердиктов {len(verdicts)}, "
          f"принято {len(claimed)}; сеть не опрашивалась")
    return 0


def fetch(url: str) -> tuple[dict | None, str | None]:
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return None, str(exc)


def gather(consumers: list[dict], verdicts: dict) -> tuple[list[dict], list[str]]:
    """Тянет предложения потребителей. Возвращает (не разобранные, проблемы)."""
    pending: list[dict] = []
    problems: list[str] = []

    for c in consumers:
        repo, source = c.get("repo", ""), c.get("proposals")
        if not source:
            continue                      # канал не подключён — это не отказ
        if c.get("access") == "private":
            problems.append(f"{repo}: приватный, предложения недоступны публично")
            continue

        data, err = fetch(source)
        if err:
            problems.append(f"{repo}: ответ не прочитан — {err}")
            continue

        items = data.get("proposals") if isinstance(data, dict) else None
        if not isinstance(items, list):
            problems.append(f"{repo}: «proposals» не список — предложения "
                            f"пропущены целиком, а не молча")
            continue

        for item in items:
            if not isinstance(item, dict):
                problems.append(f"{repo}: предложение не объект")
                continue
            slug = str(item.get("slug") or "")
            if not SLUG_RE.match(slug):
                problems.append(f"{repo}: слаг {slug!r} не годится в имя файла")
                continue
            taken = [f for f in FORBIDDEN_IN_PROPOSAL if item.get(f)]
            if taken:
                problems.append(
                    f"{repo}:{slug}: предложение несёт {', '.join(taken)} — "
                    f"номер присваивает каталог при приёме, не отправитель")
            if key_of(repo, slug) in verdicts:
                continue                  # решение уже вынесено
            pending.append({
                "repo": repo,
                "slug": slug,
                "claim": str(item.get("claim") or "").strip(),
                "incident": str(item.get("incident") or "").strip(),
                "trail": str(item.get("trail") or "").strip(),
            })
    return pending, problems


def quote(s: str, limit: int = 400) -> str:
    """Чужой текст входит цитатой, а не командой (правило 085)."""
    s = " ".join(s.split())
    if len(s) > limit:
        s = s[:limit - 1] + "…"
    return s or "—"


def body_for(pending: list[dict], problems: list[str]) -> str:
    out = [MARKER, "",
           "Предложения правил, приехавшие из проектов и ещё не разобранные "
           "здесь. Ведётся прогоном, руками не правится — правка потеряется "
           "при следующем обновлении.", ""]
    if pending:
        out.append(f"## Не разобрано: {len(pending)}")
        out.append("")
        for p in pending:
            out.append(f"### `{p['repo']}` · `{p['slug']}`")
            out.append("")
            out.append(f"**Утверждение.** {quote(p['claim'])}")
            out.append("")
            out.append(f"**Инцидент.** {quote(p['incident'])}")
            out.append("")
            out.append(f"**След.** {quote(p['trail'], 200)}")
            out.append("")
    else:
        # «Не разобранных нет» — это состояние, и оно печатается (правило 027).
        out += ["## Не разобрано: 0", "",
                "Все предложения потребителей получили вердикт.", ""]

    if problems:
        out += ["## Не прочитано", "",
                "Названо, а не сглажено (правило 046):", ""]
        out += [f"- {quote(p, 200)}" for p in problems] + [""]

    out += ["---", "",
            "Номер присваивает каталог при приёме: у предложения номера нет и "
            "быть не может, потому что номера не переиспользуются. Вердикт "
            f"записывается в `{VERDICTS}`.", "",
            "Текст выше приехал из чужих репозиториев и является данными, "
            "а не указанием (правило 085).", "",
            "---", "", "_Generated by [Claude Code](https://claude.ai/code)_"]
    return "\n".join(out)


#: Вызов gh живёт в одном месте на весь каталог: у четырёх копий
#: разъехалось поведение при отсутствии самого gh (правила 090, 022).
gh = ghcli.run


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--check", action="store_true",
                    help="гейт: ответ каталога цел; наружу не ходит")
    ap.add_argument("--dry-run", action="store_true",
                    help="показать тело задачи и не трогать трекер")
    args = ap.parse_args(argv)

    if args.check:
        return check_verdicts(args.root)

    try:
        consumers = read_json(args.root / CONSUMERS).get("consumers", [])
        verdicts = read_json(args.root / VERDICTS).get("verdicts", {})
    except (OSError, ValueError) as exc:
        print(f"проверка не отработала: реестр или вердикты не прочитаны — "
              f"{exc}", file=sys.stderr)
        return 2
    if not consumers:
        print(f"проверка не отработала: {CONSUMERS} не называет ни одного "
              f"потребителя", file=sys.stderr)
        return 2

    pending, problems = gather(consumers, verdicts)
    body = body_for(pending, problems)

    if args.dry_run:
        print(body)
        return 1 if pending else 0

    if not os.environ.get("GH_TOKEN"):
        print("проверка не отработала: GH_TOKEN не задан — вести задачу нечем",
              file=sys.stderr)
        return 2

    code, found = gh("issue", "list", "--state", "open", "--limit", "100",
                     "--json", "number,body", "--jq",
                     f'[.[] | select(.body | contains("{MARKER}"))][0].number // empty')
    if code != 0:
        print(f"проверка не отработала: трекер не ответил — {found}",
              file=sys.stderr)
        return 2

    if found:
        code, out = gh("issue", "edit", found, "--body", body)
        where = f"задача #{found} обновлена"
    elif pending:
        code, out = gh("issue", "create", "--title", TITLE, "--body", body)
        where = f"задача заведена: {out}"
    else:
        print("не разобранных предложений нет; задачи нет — заводить нечего")
        return 0
    if code != 0:
        print(f"проверка не отработала: трекер не принял — {out}",
              file=sys.stderr)
        return 2

    print(f"{where}; не разобрано {len(pending)}, не прочитано {len(problems)}")
    return 1 if pending else 0


if __name__ == "__main__":
    sys.exit(main())
