#!/usr/bin/env python3
"""Толчок в ветку, отличную от текущей, отвергается ДО вызова git.

Правило 012 держалось ничем с ответом «предмет вне досягаемости: чья ветка,
знает человек». Ответ описывал не тот предмет. Признак «чужая ветка» машине
и правда недоступен — а признак, которым пользуется сосед, доступен вполне:
**имя ветки в команде не совпадает с текущей головой**. Промах пальцем,
скопированная из передачи строка, старое имя из прошлой смены — все три дают
одно и то же наблюдаемое: содержимое уезжает не туда, куда смотрит окно.

ПОЧЕМУ ХУК, А НЕ ГЕЙТ. Конвейер видит артефакт, а не действие: к моменту его
запуска толчок уже состоялся, ветка уже сдвинута, а `git push` в общую ветку
из окна и вовсе запрещён отдельно (131). Отвергать надо до вызова git —
единственное место, где это возможно, стоит перед инструментом. Приём взят у
грейдера (`.claude/hooks/pre_tool_use.py`), файл — нет: у него запрет шире и
собран под его конвейер (правило 162).

ЧТО РАЗРЕШЕНО. Толчок без имени ветки (`git push`), толчок текущей ветки под
любым её собственным именем, `HEAD:<ветка>` — там имя цели задаётся явно и
осознанно, и запрет на общую ветку живёт не здесь. Всё остальное с явным
именем ветки отвергается.

Вход: JSON события PreToolUse на stdin. Выход: 0 — пропустить, 2 — отвергнуть
с причиной в stderr.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys

#: Ключи, за которыми идёт значение, а не имя ветки.
WITH_VALUE = {"--repo", "-o", "--push-option", "--exec", "--receive-pack"}
#: Ссылка вида `HEAD:main` или `refs/heads/x:y` — цель названа явно.
REFSPEC = re.compile(r"^[^:]+:[^:]+$")
#: Перенаправление вывода: `>`, `2>&1`, `<file`. В имени ветки этих знаков
#: не бывает, а в команде окна они бывают почти всегда.
REDIRECT = re.compile(r"[<>]")


def current_branch() -> str | None:
    done = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                          capture_output=True, text=True)
    return done.stdout.strip() or None if done.returncode == 0 else None


def targets(command: str) -> list[str]:
    """Имена веток, названные в командах `git push` этой строки."""
    out: list[str] = []
    for part in re.split(r"&&|\|\||;|\|", command):
        try:
            words = shlex.split(part)
        except ValueError:              # незакрытая кавычка — не наше дело
            continue
        if len(words) < 2 or words[0] != "git" or "push" not in words[:3]:
            continue
        tail = words[words.index("push") + 1:]
        positional: list[str] = []
        skip = False
        for word in tail:
            # Перенаправление и всё, что за ним, — не ссылки, а имена файлов.
            # Замер на первой же пробе: `2>&1` уехало в список веток, и хук
            # назвал предметом отказа то, чего в команде не было (158).
            if REDIRECT.search(word):
                break
            if skip:
                skip = False
                continue
            if word in WITH_VALUE:
                skip = True
                continue
            if word.startswith("-"):
                continue
            positional.append(word)
        # Первый позиционный — удалённый репозиторий, дальше ссылки.
        for ref in positional[1:]:
            if REFSPEC.match(ref):
                continue                # `HEAD:ветка` — цель названа явно
            out.append(ref.removeprefix("refs/heads/"))
    return out


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0                        # не разобрали событие — не мешаем
    if event.get("tool_name") != "Bash":
        return 0
    command = (event.get("tool_input") or {}).get("command") or ""
    named = targets(command)
    if not named:
        return 0
    branch = current_branch()
    if branch is None or branch == "HEAD":
        return 0                        # отделённая голова — сравнивать не с чем
    чужие = [b for b in named if b != branch]
    if not чужие:
        return 0

    print(f"толчок в {', '.join(чужие)}, а окно стоит на {branch}. "
          "Содержимое уехало бы не туда, куда смотрит окно (правило 012). "
          f"Если ветка верна — перейдите в неё: git switch {чужие[0]}",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
