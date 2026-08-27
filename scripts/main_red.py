#!/usr/bin/env python3
"""Дежурный по общей ветке: заводит одну задачу, пока `main` красная.

Запускается **в репозитории потребителя**, а не в каталоге (правило 129).
Каталог не рассылает ничего сам: рассылка потребовала бы токена с правом писать
во все проекты, включая приватный, — одна точка отказа и широкие права ради
уведомления. Тянет потребитель, своим токеном и в свой трекер.

ЗАЧЕМ ЭТО ВЫНЕСЕНО ИЗ `main-red.yml`. Механизм существовал одним прогоном
каталога и потребителю был доступен только копированием. Копия вбок разъезжается
с первой правки — правило 090; а нужен он каждому потребителю, у которого есть
прогоны по расписанию (задача #139, инцидент у витрины:
ArtVsMark/ArtVsMark#56 — `attribution-history` покраснел, и увидело это окно
только потому, что специально пошло смотреть).

ПОЧЕМУ ЗАДАЧА, А НЕ КРАСНОЕ. Трекер — первый источник работы по 091, и
единственный, в который окно смотрит обязательно. Задача попадает туда, где её
нельзя не увидеть; красное на вкладке прогонов — туда, куда не ходят (142).

ПОЧЕМУ ОДНА. Ежедневная копия завалила бы трекер и приучила листать его мимо —
то есть починила бы видимость способом, который её ломает (051).

ЧТО ЗДЕСЬ ИЗМЕНИЛОСЬ ПРИ ВЫНОСЕ, И ЭТО НЕ МОЛЧА. Прежний прогон, найдя открытую
задачу, не делал НИЧЕГО. Список красных работ в ней при этом устаревал: работа
починена, а задача продолжает называть её красной — то же самое число, вписанное
руками. Теперь тело обновляется по месту. Идемпотентность держится **скрытым
маркером**, а не совпадением заголовка: заголовок правят руками, и тогда прогон
завёл бы вторую задачу вместо обновления.

ЧЕГО ДЕЖУРНЫЙ НЕ ДЕЛАЕТ. Не закрывает задачу, когда ветка позеленела. Закрытие —
жест человека: он говорит «я это починил и посмотрел», а механизм такого сказать
не может. Позеленевшую ветку он печатает и напоминает, что задачу пора закрыть.

Исходы:
  0 — общая ветка зелёная;
  1 — есть красные работы, задача заведена или обновлена;
  2 — дежурный не отработал (площадка не ответила, ответ не разобран).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

import ghcli

#: По этой строке задача находится снова. Заголовок для этого не годится: его
#: правят руками, и тогда прогон заведёт вторую задачу вместо обновления.
MARKER = "<!-- main-red: не удаляйте, по этой строке задача находится снова -->"


#: Вызов gh живёт в одном месте на весь каталог (правила 090, 022). Свой
#: обработчик здесь возвращал код 2 — а он занят у самого gh, и
#: «инструмента нет» становилось неотличимо от находки.
gh = ghcli.run

def red_names(runs: list[dict], excluded: frozenset[str]) -> list[str]:
    """Имена работ, у которых ПОСЛЕДНИЙ завершённый прогон не зелёный.

    Свёртка по имени, а не по записям: площадка отдаёт по одному имени столько
    записей, сколько раз проверка запускалась, и это история событий, а не
    текущее состояние (правило 009). Считать по записям значит объявить красной
    работу, у которой рядом со свежим успехом висит отменённый прогон.

    Незавершённые пропускаются: «ещё идёт» — не отказ, и заводить задачу на
    состояние, которое пройдёт само, значит приучать листать трекер мимо.

    Исключения принадлежат ПОТРЕБИТЕЛЮ, а не инструменту: у каталога это
    `attribution-history`, чьё красное означало бы долг прошлой истории; у
    другого проекта список свой и по своей причине.
    """
    latest: dict[str, dict] = {}
    for run in runs:
        if run.get("status") != "completed":
            continue
        name = run.get("name") or ""
        if name in excluded:
            continue
        seen = latest.get(name)
        if seen is None or (run.get("createdAt") or "") > (seen.get("createdAt") or ""):
            latest[name] = run
    return sorted(name for name, run in latest.items()
                  if run.get("conclusion") != "success")


def body_for(template: str, red: list[str], run_url: str) -> str:
    """Тело задачи: шаблон потребителя, список красных работ, ссылка на прогон.

    Шаблон лежит файлом у потребителя, а не строкой внутри YAML: иначе между
    ним и площадкой встали бы две интерпретации подряд (правило 013).
    """
    return "\n".join([
        MARKER, "", template.strip(), "",
        "Красные работы: " + ", ".join(red), "",
        f"Прогон: {run_url}",
    ])


def find_issue(title_marker: str = MARKER) -> tuple[int | None, str | None]:
    """Номер открытой задачи дежурного, либо None. Вторая строка — причина отказа."""
    # СПИСОК, А НЕ ПОИСК. `--search` ходит в поисковый индекс площадки, а он
    # догоняет с задержкой в минуты: два прогона с разницей в три минуты оба
    # не нашли только что заведённую задачу и завели по своей — #133 и #134,
    # при обещанной ОДНОЙ (правило 142). Обычный список отдаёт актуальное
    # состояние сразу, и отбор по маркеру идёт ниже, у себя.
    code, out = gh("issue", "list", "--state", "open",
                   "--json", "number,body", "--limit", "200")
    if code != 0:
        return None, out
    try:
        found = json.loads(out or "[]")
    except ValueError as e:
        return None, f"ответ не разобран: {e}"
    for issue in found:
        if MARKER in (issue.get("body") or ""):
            return issue["number"], None
    return None, None


def selftest() -> int:
    """Прогоняет свёртку тем, что она обязана пометить и обязана пропустить.

    Набор двусторонний (правило 140): из одних «обязан пометить» не виден ложный
    отказ, а он здесь дороже пропуска — дежурный, заводящий задачу на зелёной
    ветке, приучает закрывать его не читая.

    Прогоняется и третий объявленный исход (правило 145): «дежурный не
    отработал» живёт в `main`, и вызовом свёртки его не достать.
    """
    R = lambda n, s, c, t="2026-01-01": {"name": n, "status": s, "conclusion": c, "createdAt": t}
    cases = [
        ("красная работа", [R("ci", "completed", "failure")], set(), ["ci"]),
        ("зелёная работа", [R("ci", "completed", "success")], set(), []),
        ("ещё идёт — не отказ", [R("ci", "in_progress", None)], set(), []),
        ("отменённый прогон рядом со свежим успехом",
         [R("ci", "completed", "cancelled", "2026-01-01"),
          R("ci", "completed", "success", "2026-01-02")], set(), []),
        ("свежий отказ поверх старого успеха",
         [R("ci", "completed", "success", "2026-01-01"),
          R("ci", "completed", "failure", "2026-01-02")], set(), ["ci"]),
        ("исключённая работа не считается",
         [R("attribution-history", "completed", "failure")], {"attribution-history"}, []),
        ("исключение не глушит остальных",
         [R("attribution-history", "completed", "failure"), R("ci", "completed", "failure")],
         {"attribution-history"}, ["ci"]),
        ("прогонов нет вовсе", [], set(), []),
        ("несколько красных — по алфавиту",
         [R("release", "completed", "failure"), R("ci", "completed", "timed_out")], set(),
         ["ci", "release"]),
    ]
    broken: list[str] = []
    for name, runs, excluded, expected in cases:
        got = red_names(runs, frozenset(excluded))
        if got != expected:
            broken.append(f"{name}: ожидалось {expected}, вышло {got}")
        print(f"  {'красных: ' + ', '.join(got) if got else 'зелено':<28} — {name}")

    body = body_for("Текст потребителя.", ["ci"], "https://example/run/1")
    if MARKER not in body:
        broken.append("тело задачи без маркера — идемпотентность держаться не на чем")
    if "ci" not in body or "Текст потребителя." not in body:
        broken.append("тело задачи не несёт ни списка работ, ни шаблона потребителя")

    probe = subprocess.run([sys.executable, __file__, "--body-file", "/nonexistent"],
                           capture_output=True, text=True)
    if probe.returncode != 2:
        broken.append(f"исход «дежурный не отработал» дал код {probe.returncode}, а не 2")
    print(f"  код {probe.returncode}                            — шаблон не прочитан")

    if broken:
        print("\nсамопроверка провалена:", file=sys.stderr)
        for line in broken:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("самопроверка пройдена: дежурный отличает красное от зелёного и называет исход")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--branch", default="main", help="общая ветка")
    parser.add_argument("--exclude", action="append", default=[],
                        help="имя работы, чьё красное не считается; можно повторять")
    parser.add_argument("--title", default="Общая ветка красная: работу не начинают, пока это не починено")
    parser.add_argument("--label", default="", help="метка задачи; зоны у проектов разные")
    parser.add_argument("--body-file", required=False, help="файл с текстом задачи")
    parser.add_argument("--run-url", default="", help="ссылка на текущий прогон")
    parser.add_argument("--limit", type=int, default=40, help="сколько прогонов спрашивать")
    parser.add_argument("--apply", action="store_true", help="писать в трекер, а не только печатать")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    if not args.body_file:
        print("дежурный не отработал: не задан --body-file", file=sys.stderr)
        return 2
    try:
        template = open(args.body_file, encoding="utf-8").read()
    except OSError as e:
        print(f"дежурный не отработал: шаблон не прочитан — {e}", file=sys.stderr)
        return 2

    code, out = gh("run", "list", "--branch", args.branch, "--limit", str(args.limit),
                   "--json", "name,status,conclusion,createdAt")
    if code != 0:
        print(f"дежурный не отработал: вкладка прогонов не прочитана — {out}", file=sys.stderr)
        print("Права на Actions API отдельные: без `actions: read` первый же запрос "
              "получает 403, и дежурный по красноте молчит о собственной слепоте.",
              file=sys.stderr)
        return 2
    try:
        runs = json.loads(out or "[]")
    except ValueError as e:
        print(f"дежурный не отработал: ответ площадки не разобран — {e}", file=sys.stderr)
        return 2

    red = red_names(runs, frozenset(args.exclude))
    number, failure = find_issue()
    if failure is not None:
        print(f"дежурный не отработал: трекер не прочитан — {failure}", file=sys.stderr)
        return 2

    if not red:
        print(f"общая ветка {args.branch} зелёная: красных работ нет")
        if number is not None:
            print(f"задача дежурного #{number} ещё открыта — закройте её вместе с починкой. "
                  "Закрытие оставлено человеку: оно говорит «я посмотрел», а механизм "
                  "такого сказать не может.")
        return 0

    print(f"красные работы на {args.branch}: {', '.join(red)}")
    body = body_for(template, red, args.run_url)
    if not args.apply:
        print("--apply не задан: в трекер ничего не пишу")
        return 1

    if number is not None:
        code, out = gh("issue", "edit", str(number), "--body", body)
        action = f"задача #{number} обновлена"
    else:
        create = ["issue", "create", "--title", args.title, "--body", body]
        if args.label:
            create += ["--label", args.label]
        code, out = gh(*create)
        action = f"задача заведена: {out}"
    if code != 0:
        print(f"дежурный не отработал: трекер не принял запись — {out}", file=sys.stderr)
        return 2
    print(action)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
