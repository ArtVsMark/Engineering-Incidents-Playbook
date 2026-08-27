#!/usr/bin/env python3
"""Сверяет правила каталога с ответом проекта и ведёт одну задачу-«входящие».

Запускается **в репозитории потребителя**, а не в каталоге: механизм живёт у
того, у кого живёт ответ (правило 129). Каталог не рассылает ничего сам —
рассылка потребовала бы токена с правом писать во все проекты, включая
приватный, то есть одной точки отказа и широких прав ради уведомления.

Что делает:
  1. тянет export/rules.json каталога обычным HTTPS — без API и без клона;
  2. сверяет со своим .rules/bindings.json;
  3. обновляет ОДНУ задачу-«входящие» — идемпотентно, а не плодит по задаче
     за прогон (правило 104: у события есть ручная кнопка, но не свалка).

Реализует правила каталога:
  129 — контракт потребления и обратная связь;
  128 — ответ нужен по КАЖДОМУ правилу, а не по тем, до которых дошли руки;
  027 — «нерассмотренных нет» это состояние, и оно печатается;
  039 — три исхода, а не два.

Исходы:
  0 — чисто;  1 — есть нерассмотренные;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import ghcli
import urllib.error
import urllib.request

#: По этой метке задача находится снова. Заголовок для этого не годится: его
#: правят руками, и тогда прогон заведёт вторую задачу вместо обновления.
MARKER = "<!-- rules-inbox: не удаляйте, по этой строке задача находится снова -->"


def fetch_rules(catalogue: str, ref: str) -> tuple[list[dict] | None, str | None]:
    url = f"https://raw.githubusercontent.com/{catalogue}/{ref}/export/rules.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")).get("rules", []), None
    except (urllib.error.URLError, OSError, ValueError) as e:
        return None, f"{url} — {e}"


#: Вызов gh живёт в одном месте на весь каталог: у четырёх копий
#: разъехалось поведение при отсутствии самого gh (правила 090, 022).
gh = ghcli.run


def body_for(missing: list[dict], unreviewed: list[dict], catalogue: str) -> str:
    lines = [
        MARKER,
        "",
        f"Правила каталога [`{catalogue}`](https://github.com/{catalogue}), по "
        "которым этот проект ещё не ответил.",
        "",
        "Ответ живёт здесь, в `.rules/bindings.json`, потому что здесь живёт "
        "механизм: одно правило в разных проектах держится по-разному. Статус — "
        "`active`, `rejected`, `not-applicable` или `unreviewed`; у двух "
        "отрицательных обязательна причина.",
        "",
    ]
    if not missing and not unreviewed:
        lines += ["**Нерассмотренных нет.** Это состояние, а не пустая задача: "
                  "ответ есть по каждому правилу каталога."]
        return "\n".join(lines) + "\n"

    if missing:
        lines += ["## Ответа нет вовсе", "",
                  "Правило появилось в каталоге, а записи о нём в ответе нет.", ""]
        lines += [f"- **{r['id']}** — {r['title']['ru']}" for r in missing]
        lines += [""]
    if unreviewed:
        lines += ["## Записано `unreviewed`", "",
                  "Очередь на рассмотрение, а не позор: «не дошли руки» — "
                  "честный статус, пока он не застаивается.", ""]
        lines += [f"- **{r['id']}** — {r['title']['ru']}" for r in unreviewed]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--catalogue", default="ArtVsMark/claude-code-playbook")
    ap.add_argument("--ref", default="main")
    ap.add_argument("--bindings", default=".rules/bindings.json")
    ap.add_argument("--title", default="Правила каталога: входящие")
    ap.add_argument("--dry-run", action="store_true",
                    help="показать тело задачи и не трогать трекер")
    args = ap.parse_args()

    # ── исход 2: проверка не отработала ────────────────────────────────────
    rules, err = fetch_rules(args.catalogue, args.ref)
    if err:
        print(f"проверка не отработала: экспорт каталога не прочитан — {err}",
              file=sys.stderr)
        return 2
    if not rules:
        print("проверка не отработала: каталог отдал пустой список правил — "
              "сверять не с чем, а молча пропускать нельзя", file=sys.stderr)
        return 2

    try:
        with open(args.bindings, encoding="utf-8") as fh:
            answered = json.load(fh).get("rules", {})
    except FileNotFoundError:
        # Проект ещё не подключён. Это не поломка: все правила нерассмотрены,
        # и задача-«входящие» именно об этом и скажет.
        answered = {}
    except (OSError, ValueError) as e:
        print(f"проверка не отработала: {args.bindings} не разобран — {e}",
              file=sys.stderr)
        return 2

    missing = [r for r in rules if r["id"] not in answered]
    unreviewed = [r for r in rules
                  if answered.get(r["id"], {}).get("status") == "unreviewed"]

    body = body_for(missing, unreviewed, args.catalogue)
    if args.dry_run:
        print(body)
        return 1 if (missing or unreviewed) else 0

    if not os.environ.get("GH_TOKEN"):
        print("проверка не отработала: GH_TOKEN не задан — обновлять задачу "
              "нечем", file=sys.stderr)
        return 2

    code, found = gh("issue", "list", "--state", "open", "--limit", "100",
                     "--json", "number,body", "--jq", f'[.[] | select(.body | contains("{MARKER}"))][0].number // empty')
    if code != 0:
        print(f"проверка не отработала: трекер не ответил — {found}", file=sys.stderr)
        return 2

    if found:
        code, out = gh("issue", "edit", found, "--body", body)
        where = f"задача #{found} обновлена"
    else:
        code, out = gh("issue", "create", "--title", args.title, "--body", body)
        where = f"задача заведена: {out}"
    if code != 0:
        print(f"проверка не отработала: задача не записана — {out}", file=sys.stderr)
        return 2

    print(f"{where}; ответа нет у {len(missing)}, не рассмотрено {len(unreviewed)}")
    return 1 if (missing or unreviewed) else 0


if __name__ == "__main__":
    sys.exit(main())
