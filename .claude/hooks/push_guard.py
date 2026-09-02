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

ТЕЛО ДОКУМЕНТА НА ВХОДЕ — ДАННЫЕ, А НЕ КОМАНДЫ. `cat > файл <<'EOF' … EOF`
пишет файл, и строка `git push` внутри него — текст, а не действие. Сторож
смотрит на действие: это уже было сказано в его наборе про запись чужим
инструментом, но запись через оболочку тем же случаем не покрывалась, и
сторож отверг запись файла с примером для человека.

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


#: Начало документа на входе: `<<EOF`, `<<-'EOF'`, `<< "EOF"`. Тело такого
#: документа — ДАННЫЕ, а не команды: им пишут файлы.
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")


def without_heredocs(command: str) -> str:
    """Команда без тел документов на входе.

    ЗАМЕР, ИЗ КОТОРОГО ЭТО ВЫРОСЛО. Окно писало файл прогона через `cat > … <<
    'YML'`, и внутри файла стоял ПРИМЕР для человека: «переименуйте ветку —
    git push -u origin agent/$BRANCH». Сторож разобрал строку примера как
    команду и отверг запись файла. Собственный набор сторожа этот случай уже
    называл — «строка в файле не команда», — но проверял его только на записи
    ЧУЖИМ инструментом, а не на записи через оболочку.

    Тот же приём, что у самого сторожа с перенаправлением: то, что после
    признака перестаёт быть командой, дальше не разбирается.
    """
    lines = command.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        m = HEREDOC_RE.search(lines[i])
        if m:
            конец = m.group(2)
            i += 1
            while i < len(lines) and lines[i].strip() != конец:
                i += 1                  # тело документа — данные, пропускаем
        i += 1
    return "\n".join(out)


#: Команды, которые МЕНЯЮТ текущую ветку. Сторож обязан их учитывать: он
#: спрашивает ветку у git ДО того, как команда выполнится, и `git checkout X &&
#: git push origin X` выглядел бы толчком в чужую. Замер: за одну смену это
#: отвергло верный толчок трижды подряд.
SWITCH = {"checkout", "switch"}
#: Ключи `checkout`/`switch`, за которыми идёт имя новой ветки.
SWITCH_WITH_NAME = {"-b", "-B", "-c", "-C"}


def switched_to(words: list[str]) -> str | None:
    """Ветка, на которую переходит эта команда, если она переходит."""
    if len(words) < 3 or words[0] != "git" or words[1] not in SWITCH:
        return None
    tail = words[2:]
    for i, w in enumerate(tail):
        if w in SWITCH_WITH_NAME and i + 1 < len(tail):
            return tail[i + 1]
        if not w.startswith("-") and not REDIRECT.search(w):
            return w
    return None


def targets(command: str, current: str | None = None) -> list[str]:
    """Имена веток, названные в командах `git push`, — те, что ЧУЖИЕ.

    Ветка считается по ходу строки: `git switch X && git push origin X` — это
    толчок в свою, а не в чужую, и отвергать его значит краснеть на верной
    работе (051).

    Имя, собранное подстановкой (`$b`, `${имя}`), сторож не разворачивает и не
    угадывает: он пропускает такой толчок. Его предмет — НАЗВАННАЯ чужая
    ветка; «неизвестно» и «чужая» — разные ответы, и путать их значит
    запрещать недостоверное (051).
    """
    out: list[str] = []
    # Перевод строки разделяет команды не хуже `&&`, и в записи файла
    # через оболочку он единственный разделитель.
    for part in re.split(r"&&|\|\||;|\||\n", without_heredocs(command)):
        try:
            words = shlex.split(part)
        except ValueError:              # незакрытая кавычка — не наше дело
            continue
        переход = switched_to(words)
        if переход is not None:
            current = переход
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
            имя = ref.removeprefix("refs/heads/")
            # Подстановка оболочки: значения сторож не знает и не выдумывает.
            if "$" in имя or "`" in имя:
                continue
            if current is not None and имя != current:
                out.append(имя)
    return out


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0                        # не разобрали событие — не мешаем
    if event.get("tool_name") != "Bash":
        return 0
    command = (event.get("tool_input") or {}).get("command") or ""
    branch = current_branch()
    if branch is None or branch == "HEAD":
        return 0                        # отделённая голова — сравнивать не с чем
    чужие = targets(command, branch)
    if not чужие:
        return 0

    print(f"толчок в {', '.join(чужие)}, а окно стоит на {branch}. "
          "Содержимое уехало бы не туда, куда смотрит окно (правило 012). "
          f"Если ветка верна — перейдите в неё: git switch {чужие[0]}",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
