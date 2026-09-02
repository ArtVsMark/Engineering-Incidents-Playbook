#!/usr/bin/env python3
"""Сверяет правила каталога с ответом проекта и ведёт одну задачу-«входящие».

ОТДАЁТСЯ ПОТРЕБИТЕЛЮ. Обычно через действие каталога, но зовётся и напрямую;
названо в CONNECT.md (правило 163).

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
  162 — дыру в своём механизме сначала ищут у соседа: раздел «У соседей это уже
        решено» кладётся во входящие адресно, с механизмом и адресом; та же
        свёртка отвечает и самому каталогу в scripts/check_bindings.py;
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


def fetch_where(catalogue: str, ref: str) -> tuple[list[dict] | None, str | None]:
    """Сводка «чем держат другие» — чтобы соседский механизм доехал сюда.

    Раздел «Чем держат другие» существует в сводке каталога с самого её
    появления, и отвечает он ровно на нужный вопрос: кто уже сталкивался и чем
    закрыл. Но лежит он в ЧУЖОМ репозитории, файлом в двести строк, и приходят
    в него те, кто УЖЕ выбрал, чем держать правило. Знание собрано и никому не
    доставлено — та же поломка, что у красного без адресата (правило 142).

    ТРЕТИЙ ИСХОД НАЗЫВАЕТ ПРЕДМЕТ (158): адрес возвращается вместе с ошибкой,
    иначе на два источника выйдет одно неразличимое «не ответил».
    """
    url = f"https://raw.githubusercontent.com/{catalogue}/{ref}/export/where.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")).get("consumers", []), None
    except (urllib.error.URLError, OSError, ValueError) as e:
        return None, f"{url} — {e}"


def solved_next_door(answered: dict, consumers: list[dict], me: str) -> list[dict]:
    """Правила, что у меня не держатся ничем, а у соседа держатся — с адресом.

    ГРАНИЦА. Чужой механизм не обязан подойти: стеки разные, и правило,
    закрытое у соседа гейтом, здесь может быть неприменимо вовсе. Раздел
    отвечает не «сделай так», а «вот кто уже сталкивался»; решение остаётся за
    тем, кто правит свой ответ.

    Берутся только записи с РАЗРЕШИМЫМ адресом: пересказ соседа помогает не
    больше, чем его отсутствие, и это та же граница, что у поля `where`.
    """
    свои = {rid for rid, rec in answered.items()
            if rec.get("status") == "active"
            and (rec.get("mechanism") or "none") == "none"}
    out: list[dict] = []
    for rid in sorted(свои):
        для_него = []
        for c in consumers:
            if c.get("repo") == me:
                continue
            held = (c.get("holds") or {}).get(rid) or {}
            mech, where = held.get("mechanism"), (held.get("where") or "").strip()
            if mech and mech != "none" and where:
                для_него.append({"repo": c["repo"], "mechanism": mech, "where": where})
        if для_него:
            out.append({"rule": rid, "held": для_него})
    return out


#: Вызов gh живёт в одном месте на весь каталог: у четырёх копий
#: разъехалось поведение при отсутствии самого gh (правила 090, 022).
gh = ghcli.run


def stale_here(answered: dict, rules: list[dict]) -> list[str]:
    """Ответы ЭТОГО проекта о правилах, которых в каталоге нет.

    Половина вопроса, которой у потребителя не было. Каталог такой ответ у
    себя отвергает гейтом, и с этого прогона видит его у потребителей — но
    ПОЧИНИТЬ оттуда не может: файл чужой. Чинится здесь, и потому называется
    здесь же.

    Правило снимают, номер остаётся занятым навсегда — а ответ о снятом
    правиле нет: пока номер свободен, это мусор, а как только номер займёт
    новая запись, тот же ответ прочитается как решение по НЕЙ. Не покраснеет
    ничто: статус есть, механизм назван, полнота ответа сойдётся.
    """
    return sorted(set(answered) - {r["id"] for r in rules})


def body_for(missing: list[dict], unreviewed: list[dict], catalogue: str,
             stale: list[str] | None = None, total: int | None = None,
             answered: int | None = None,
             solved: list[dict] | None = None) -> str:
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
    # ПЕРЕПИСЬ ПЕЧАТАЕТСЯ ВСЕГДА, а не только когда есть очередь. Число,
    # видное лишь при поломке, отвечает на вопрос «что сломалось» и не
    # отвечает на вопрос «куда мы движемся»; второй здесь и есть предмет.
    if total is not None:
        разобрано = answered if answered is not None else 0
        lines += [
            f"**Правил в каталоге: {total}. Разобрано здесь: {разобрано}.** "
            f"Ответа нет вовсе у {len(missing)}, записано `unreviewed` "
            f"у {len(unreviewed)}.",
            "",
        ]

    if solved:
        lines += [
            "## У соседей это уже решено",
            "",
            "Правила, которые здесь признаны действующими и **не держатся "
            "ничем**, а у соседнего проекта держатся — с адресом механизма.",
            "",
            "Чужой механизм не обязан подойти: стеки разные, и правило, "
            "закрытое у соседа гейтом, здесь может быть неприменимо вовсе. "
            "Раздел отвечает не «сделай так», а «вот кто уже сталкивался».",
            "",
            "| № | Кто держит | Чем и где |",
            "|---|---|---|",
        ]
        for item in solved:
            for h in item["held"]:
                где = h["where"].split(";")[0].strip()
                lines.append(f"| {item['rule']} | `{h['repo'].split('/')[-1]}` | "
                             f"{h['mechanism']}: {где} |")
        lines.append("")

    if stale:
        # ЭТО НАХОДКА, А НЕ ОЧЕРЕДЬ, и потому стоит выше очереди: очередь
        # рассосётся решением, лишний ответ не рассосётся никогда.
        lines += [
            "## Ответ о правиле, которого в каталоге нет",
            "",
            "Правило снято, а ответ о нём остался: " + ", ".join(
                f"**{rid}**" for rid in stale) + ".",
            "",
            "Номера не переиспользуются, но ответ о снятом правиле лежать не "
            "должен: как только номер займёт новая запись, этот ответ "
            "прочитается как решение по НЕЙ — и не покраснеет ничто, потому "
            "что статус есть и механизм назван. Запись удаляется из "
            "`.rules/bindings.json` целиком.",
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



def found_issue(out: str) -> tuple[str, str]:
    """Разобрать ответ трекера о задаче-«входящих»: номер и состояние.

    ПУСТОТА ОТ jq — ЭТО СТРОКА "null null", А НЕ ПУСТАЯ СТРОКА. Индексация
    пустого массива даёт `null`, а интерполяция `"\\(.number) \\(.state)"`
    печатает его словом. Дальше «null» — непустая строка, то есть истинная, и
    ветка «завести задачу» не выполняется никогда: вместо неё уходит
    `gh issue edit null`, а площадка отвечает `invalid issue format: "null"`.

    То есть у потребителя, у которого задачи-«входящих» ещё нет, механизм
    отказывал на КАЖДОМ прогоне и завести первую задачу не мог в принципе.
    Замер: ArtVsMark/claude-code-usage, четыре прогона подряд с 29 августа —
    все красные, ни одного зелёного.

    Само выражение jq теперь отдаёт пустоту (`// empty`), и «null» сюда
    приходить перестал. Разбор всё равно его переживает: ответ внешней команды
    — контракт, который нам не принадлежит, и второй способ ошибиться здесь
    дороже одной строки кода.
    """
    number, state = (out.split() + ["", ""])[:2]
    if number == "null":
        return "", ""
    return number, state


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--catalogue", default="ArtVsMark/Engineering-Incidents-Playbook")
    ap.add_argument("--ref", default="main")
    ap.add_argument("--bindings", default=".rules/bindings.json")
    # КТО Я — чтобы не показывать проекту его собственный механизм как
    # соседский. Умолчание берётся из окружения площадки: там это уже есть, и
    # требовать его руками значило бы завести второй источник того же факта.
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""),
                    help="владелец/репозиторий этого проекта; по умолчанию из "
                         "GITHUB_REPOSITORY")
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

    stale = stale_here(answered, rules)
    # СОСЕДСКИЙ МЕХАНИЗМ — ДОПОЛНЕНИЕ, И ОНО НЕ РОНЯЕТ ОСНОВНУЮ РАБОТУ (084).
    # Сводка лежит в чужом репозитории; её недоступность делает раздел пустым,
    # а не задачу — неоткрытой. Отказ называет адрес (158) и печатается, чтобы
    # молчание не выдавалось за «у соседей ничего нет» (046).
    neighbours, err = fetch_where(args.catalogue, args.ref)
    if err:
        print(f"сводка соседей не прочитана — {err}; раздел пропущен",
              file=sys.stderr)
    solved = solved_next_door(answered, neighbours or [], args.repo)
    решено = sum(1 for r in rules
                 if answered.get(r["id"], {}).get("status") not in (None, "unreviewed"))
    body = body_for(missing, unreviewed, args.catalogue, stale=stale,
                    total=len(rules), answered=решено, solved=solved)
    if args.dry_run:
        print(body)
        return 1 if (missing or unreviewed or stale) else 0

    if not os.environ.get("GH_TOKEN"):
        print("проверка не отработала: GH_TOKEN не задан — обновлять задачу "
              "нечем", file=sys.stderr)
        return 2

    # Ищется среди ВСЕХ состояний, а не только открытых. Пока искали среди
    # открытых, закрыть задачу было нельзя ни рукой, ни механизмом: следующий
    # прогон не находил её и заводил вторую. Потребитель это и наблюдал —
    # ArtVsMark/ArtVsMark#52 висел открытым с нулём нерассмотренных, потому что
    # иначе он бы раздвоился.
    code, found = gh("issue", "list", "--state", "all", "--limit", "100",
                     "--json", "number,body,state",
                     "--jq", f'[.[] | select(.body | contains("{MARKER}"))][0] '
                             f'// empty | "\\(.number) \\(.state)"')
    if code != 0:
        print(f"проверка не отработала: трекер не ответил — {found}", file=sys.stderr)
        return 2

    number, state = found_issue(found)
    pending = bool(missing or unreviewed or stale)

    if number:
        code, out = gh("issue", "edit", number, "--body", body)
        where = f"задача #{number} обновлена"
    elif pending:
        code, out = gh("issue", "create", "--title", args.title, "--body", body)
        where = f"задача заведена: {out}"
    else:
        # Завести задачу, чтобы тут же закрыть, — шум без адресата.
        print("нерассмотренных нет, задачи-«входящих» тоже: заводить нечего")
        return 0
    if code != 0:
        print(f"проверка не отработала: задача не записана — {out}", file=sys.stderr)
        return 2

    # ОТКРЫТА ЛИ ЗАДАЧА — ЭТО УТВЕРЖДЕНИЕ, А НЕ ОФОРМЛЕНИЕ. Открытая задача
    # говорит «здесь есть работа». При нуле нерассмотренных это неправда, и
    # ежедневная неправда в трекере приучает листать его мимо — тем самым
    # способом, каким ломается 091: трекер и есть первый источник работы.
    #
    # ПОЧЕМУ ЗАКРЫВАЕТ МЕХАНИЗМ, А НЕ ЧЕЛОВЕК. Пустота здесь — ФАКТ, который
    # машина проверяет целиком: ответ есть по каждому правилу и лишних ответов
    # нет. Это отличает «входящие» от дежурного по красной ветке: там закрытие
    # говорит «я посмотрел», а такого механизм сказать не может (142).
    want = "OPEN" if pending else "CLOSED"
    if state and state.upper() != want:
        code, out = gh("issue", "reopen" if pending else "close", number)
        if code != 0:
            print(f"проверка не отработала: состояние задачи #{number} не "
                  f"изменено — {out}", file=sys.stderr)
            return 2
        where += ", открыта заново" if pending else ", закрыта: работы в ней нет"

    print(f"{where}; правил {len(rules)}, разобрано {решено}, ответа нет "
          f"у {len(missing)}, не рассмотрено {len(unreviewed)}, "
          f"лишних {len(stale)}")
    return 1 if (missing or unreviewed or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
