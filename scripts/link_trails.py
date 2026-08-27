#!/usr/bin/env python3
"""Задача знает, что породила правило: обратная сторона следа.

Связь «задача → правило» односторонняя по устройству: у записи есть раздел
«След» с номером задачи потребителя, а у самой задачи о правиле ни слова.
Читатель задачи не узнает, что из неё вышло правило, — и следующий разбор того
же места начинается с нуля, потому что вывод прошлого лежит в другом
репозитории.

ПОЧЕМУ ЭТО ЗДЕСЬ, А НЕ У ПОТРЕБИТЕЛЯ. Механизм нужен КАЖДОМУ потребителю, у
которого есть следы: у грейдера он написан свой (`link_rules_to_issues.py`), и
второй такой же у витрины был бы третьей реализацией одного алгоритма. Правило
090 — общая утилита поднимается выше обеих подсистем, а не копируется вбок.
Заказано задачей потребителя ArtVsMark/ArtVsMark#15 («обратная ссылка»).

ЗАПУСКАЕТСЯ У ПОТРЕБИТЕЛЯ, как `sync_inbox.py` (правило 129). Каталог не
рассылает ничего сам: рассылка потребовала бы токена с правом писать во все
проекты, включая приватный. Тянет потребитель — своим токеном и в свой трекер.

ИСТОЧНИК — МАШИННЫЙ ЭКСПОРТ, а не разбор Markdown: у `export/rules.json` есть
поле ``trails`` с репозиторием и номером задачи, и это контракт, объявленный
самим каталогом. Разбор прозы дал бы вторую интерпретацию той же территории.

ИДЕМПОТЕНТНОСТЬ ДЕРЖИТСЯ СКРЫТЫМ МАРКЕРОМ, а не совпадением текста: текст
растёт вместе с числом правил, и сравнение по нему плодило бы дубли на каждом
прогоне. Заголовка у комментария нет вовсе — искать не по чему, кроме маркера.

ПИШЕТ ТОЛЬКО С ``--apply``. Умолчание сухое намеренно: скрипт пишет в трекер, и
«случайно запустил» не должно означать «прошёлся по тридцати задачам».

Исходы:
  0 — обратные ссылки на месте либо ставить нечего;
  1 — есть задачи без обратной ссылки (с --apply они обновлены);
  2 — не отработал: экспорт не прочитан, разобрать нечем, трекер недоступен.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import urllib.error
import urllib.request

import ghcli

#: По этой строке комментарий находится снова. Заголовок для этого не годится:
#: его правят руками, и тогда прогон заведёт второй вместо обновления.
MARKER = "<!-- rule-trail: не удаляйте, по этой строке запись находится снова -->"


def fetch_rules(catalogue: str, ref: str) -> tuple[list[dict] | None, str | None]:
    url = f"https://raw.githubusercontent.com/{catalogue}/{ref}/export/rules.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")).get("rules", []), None
    except (urllib.error.URLError, OSError, ValueError) as e:
        return None, f"{url} — {e}"


def trails_for(rules: list[dict], repo: str) -> dict[str, list[dict]]:
    """Задачи потребителя и правила, чей след ведёт в каждую.

    Ключ — номер задачи строкой; значение — правила по возрастанию номера.
    Одно правило может ссылаться на несколько задач, и одна задача породить
    несколько правил: перебираются все следы, а не первый.
    """
    found: dict[str, list[dict]] = collections.defaultdict(list)
    for rule in rules:
        for trail in rule.get("trails") or []:
            if not isinstance(trail, dict) or trail.get("repo") != repo:
                continue
            issue = str(trail.get("issue") or "").strip()
            if issue.isdigit():
                found[issue].append(rule)
    return {issue: sorted(rr, key=lambda r: str(r.get("id")))
            for issue, rr in sorted(found.items(), key=lambda kv: int(kv[0]))}


def title_of(rule: dict) -> str:
    """Заголовок записи. У экспорта он двуязычный — берём русский, потом любой."""
    title = rule.get("title")
    if isinstance(title, dict):
        return str(title.get("ru") or title.get("en") or "")
    return str(title or "")


def comment_for(rules: list[dict], catalogue: str) -> str:
    """Один комментарий на задачу: что из неё выросло и куда смотреть."""
    lines = [MARKER, "",
             "Из этой задачи выросли правила общего каталога "
             f"[`{catalogue}`](https://github.com/{catalogue}):", ""]
    for rule in rules:
        rid, slug = str(rule.get("id")), str(rule.get("slug") or "")
        link = f"https://github.com/{catalogue}/blob/main/rules/ru/{rid}-{slug}.md"
        lines.append(f"- [**{rid}**]({link}) — {title_of(rule)}")
    lines += ["",
              "Запись ведёт прогон, а не человек: она одна на задачу и "
              "обновляется по месту. Инцидент и границы применимости живут в "
              "каталоге, здесь остаётся ссылка."]
    return "\n".join(lines)


def selftest() -> int:
    """Прогоняет через разбор то, что он обязан найти и обязан пропустить.

    Набор двусторонний (правило 140). Ложный след здесь дороже пропущенного:
    комментарий уезжает в чужую задачу, и «правило выросло отсюда» о чужом
    месте читатель уже не проверит.
    """
    R = lambda i, repo, issue, slug="x": {
        "id": i, "slug": slug, "title": {"ru": f"правило {i}"},
        "trails": [{"repo": repo, "issue": issue}]}
    ME = "ArtVsMark/ArtVsMark"
    cases = [
        ("след ведёт сюда", [R("005", ME, "7")], {"7": ["005"]}),
        ("след ведёт в чужой проект", [R("005", "ArtVsMark/Other", "7")], {}),
        ("одна задача — несколько правил",
         [R("005", ME, "7"), R("009", ME, "7")], {"7": ["005", "009"]}),
        ("одно правило — несколько задач",
         [{"id": "132", "slug": "s", "title": {"ru": "t"},
           "trails": [{"repo": ME, "issue": "19"}, {"repo": ME, "issue": "20"}]}],
         {"19": ["132"], "20": ["132"]}),
        ("следов нет вовсе", [{"id": "001", "slug": "s", "title": {"ru": "t"}}], {}),
        ("след без номера", [R("005", ME, "")], {}),
        ("номер не число", [R("005", ME, "abc")], {}),
        ("правил нет", [], {}),
    ]
    broken: list[str] = []
    for name, rules, expected in cases:
        got = {i: [str(r["id"]) for r in rr] for i, rr in trails_for(rules, ME).items()}
        if got != expected:
            broken.append(f"{name}: ожидалось {expected}, вышло {got}")
        print(f"  {str(got) if got else 'следов нет':<34} — {name}")

    body = comment_for([R("005", ME, "7")], "ArtVsMark/claude-code-playbook")
    if MARKER not in body:
        broken.append("комментарий без маркера — идемпотентность держаться не на чем")
    if "005" not in body or "rules/ru/005-x.md" not in body:
        broken.append("комментарий не называет правило или не ведёт в него")

    probe = ghcli.run("--нет-такой-команды")
    if not ghcli.failed(probe[0]):
        broken.append("отказ gh не распознан как отказ")

    if broken:
        print("\nсамопроверка провалена:", file=sys.stderr)
        for line in broken:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("самопроверка пройдена: разбор находит свои следы и не берёт чужие")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalogue", default="ArtVsMark/claude-code-playbook")
    parser.add_argument("--ref", default="main")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""),
                        help="репозиторий потребителя; по умолчанию из окружения")
    parser.add_argument("--label", default="", help="метка на задачи со следом")
    parser.add_argument("--apply", action="store_true", help="писать в трекер")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        return selftest()
    if not args.repo:
        print("не отработал: не задан --repo и пуст GITHUB_REPOSITORY", file=sys.stderr)
        return 2

    rules, err = fetch_rules(args.catalogue, args.ref)
    if err:
        print(f"не отработал: экспорт каталога не прочитан — {err}", file=sys.stderr)
        return 2

    found = trails_for(rules, args.repo)
    if not found:
        print(f"следов каталога в задачи {args.repo} нет — ставить нечего")
        return 0

    missing: list[str] = []
    for issue, rr in found.items():
        code, out = ghcli.run("issue", "view", issue, "--repo", args.repo,
                              "--json", "comments",
                              "--jq", f'[.comments[] | select(.body | contains("{MARKER}"))] | length')
        if ghcli.failed(code):
            print(f"не отработал: задача #{issue} не прочитана — {out}", file=sys.stderr)
            return 2
        if out.strip() not in ("0", ""):
            continue                       # обратная ссылка уже стоит
        missing.append(issue)
        if not args.apply:
            continue
        code, out = ghcli.run("issue", "comment", issue, "--repo", args.repo,
                              "--body", comment_for(rr, args.catalogue))
        if ghcli.failed(code):
            print(f"не отработал: запись в #{issue} не принята — {out}", file=sys.stderr)
            return 2
        if args.label:
            ghcli.run("issue", "edit", issue, "--repo", args.repo, "--add-label", args.label)

    print(f"задач со следом: {len(found)}; без обратной ссылки было: {len(missing)}"
          + (f" — дописано {len(missing)}" if args.apply and missing else ""))
    if missing and not args.apply:
        print("--apply не задан: в трекер ничего не пишу")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
