#!/usr/bin/env python3
"""Прогон перед толчком: одна команда вместо чек-листа в своде.

Каталог раздаёт потребителям `templates/preflight.py` — заготовку, чья первая
строка обещает «один запуск вместо чек-листа в документации», — а у себя держал
чек-лист из семи строк в конце `AGENTS.md`. Ровно то расхождение, ради которого
в карте направлений заведён хранитель заготовок: заготовка разошлась с тем, что
мы делаем сами.

Замер, на котором это вскрылось: окно, перезапущенное 31 августа, собрало
список гейтов для локального прогона по памяти и назвало 16 из 19 — три шага,
которым нужен контекст изменения, оно просто забыло. Чек-лист при этом лежал
перед ним и не помог: он перечисляет не гейты, а их последствия.

ШАГИ НЕ ПЕРЕЧИСЛЯЮТСЯ ЗАНОВО, а читаются из `.github/workflows/ci.yml`. Второй
список тех же шагов — это вторая классификация одной территории, и разъехался
бы он молча (022). Канон здесь тот же, что у `check_charter.py`: шаги конвейера
исполняет площадка, а строку в документе не исполняет никто.

ЧЕГО ЗАПУСТИТЬ НЕЛЬЗЯ — НАЗЫВАЕТСЯ, А НЕ ПРОПУСКАЕТСЯ. Четыре шага конвейера
живут только на изменении: им нужны номер изменения, его тело, метки, границы
диапазона. Локально предмета у них нет — и молчание о них было бы ровно тем,
что запрещает 075: «не смогли проверить» неотличимо от «проверено и чисто».

Реализует правила каталога:
  002 — чек-лист переписывается в команду, а не дополняется пунктом;
  022 — список шагов один и живёт в конвейере;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  075 — шаг без предмета называется, а не зеленеет молча;
  046 — «нечего запускать» и «всё прошло» различимы в выводе;
  100 — у каждого шага свой предел времени;
  029 — свод держит ссылку на команду, а не пересказ того, что она делает.

Запуск:  python scripts/preflight.py          # все исполнимые локально шаги
         python scripts/preflight.py --list   # план без запуска
         python scripts/preflight.py --only bindings
Коды:    0 чисто · 1 есть находки · 2 проверка не отработала
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Предел на шаг. Тесты идут дольше остальных, и общий предел пришлось бы
#: ставить по самому долгому — то есть не ставить вовсе (правило 100).
TIMEOUT_DEFAULT_S = 300
TIMEOUT_TESTS_S = 1800

#: Переменные, которых на рабочем столе не существует: их подставляет площадка
#: из события. Шаг, чья команда их поминает, локально запускается вхолостую —
#: и отвечает не о предмете, а о пустой строке.
EVENT_VARS = ("$BASE", "$HEAD_SHA", "$PR", "$RUNNER_TEMP", "$GH_TOKEN")

#: ЛОКАЛЬНАЯ ЗАМЕНА ВХОДА, А НЕ ВТОРАЯ ПРОВЕРКА. Шаг связи с задачей спрашивает
#: тело изменения у площадки — локально его нет, и шаг честно значился
#: непроверяемым. Но предмет есть: тело изменения СОБИРАЕТСЯ ИЗ ПЕРВОГО КОММИТА
#: ветки (`agent-pr.yml` берёт `git log -1 --format=%b`), а коммит лежит здесь.
#:
#: Замер, из которого это выросло: три изменения подряд за одно окно уехали без
#: строки связи и вернулись красными — каждое стоило круга «поправить тело,
#: перезапустить работу вручную». Прогон говорил «предмет появляется только на
#: изменении», и это было неверно: предмет появляется в момент коммита.
#:
#: Запускается ТОТ ЖЕ скрипт тем же ключом; подменяется только источник текста.
#: Второй проверки здесь нет и быть не должно (правило 022).
STAND_IN = {"изменение связано с задачей или освобождено с причиной":
            ("scripts/pr_body.py", "тело первого коммита ветки")}


def branch_body(root: Path, base: str = "origin/main") -> tuple[str, str]:
    """Тело первого коммита ветки — ровно то, что уедет телом изменения.

    Ошибка возвращается строкой: «спросить не вышло» и «строки нет» — разные
    ответы, и путать их значит врать прогоном (039).
    """
    done = subprocess.run(["git", "-C", str(root), "rev-list", "--reverse",
                           f"{base}..HEAD"], capture_output=True, text=True)
    if done.returncode != 0:
        return "", f"не спросить коммиты ветки: {done.stderr.strip()}"
    first = done.stdout.split("\n")[0].strip()
    if not first:
        return "", f"ветка не несёт своих коммитов поверх {base}"
    done = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%b",
                           first], capture_output=True, text=True)
    if done.returncode != 0:
        return "", f"не спросить тело коммита {first[:7]}: {done.stderr.strip()}"
    return done.stdout, ""

STEP_RE = re.compile(r"^      - (name|uses):\s*(.*)$")
FIELD_RE = re.compile(r"^        (\w+):\s*(.*)$")


@dataclass
class Step:
    """Шаг конвейера: как он назван, чем запускается, чем ограничен."""

    name: str
    command: list[str]
    skip_why: str = ""

    @property
    def timeout_s(self) -> int:
        return TIMEOUT_TESTS_S if "pytest" in self.command else TIMEOUT_DEFAULT_S


def parse_steps(text: str) -> list[Step]:
    """Шаги из `ci.yml`: имя, команда, причина невозможности запуска.

    Разбор построчный, а не через YAML: у всех прежних шагов конвейера
    зависимостей нет, и тащить их сюда значило бы сделать прогон перед толчком
    тем, что сперва надо установить.
    """
    steps: list[Step] = []
    name = ""
    cond = ""
    run_lines: list[str] = []
    in_run = False

    def flush() -> None:
        nonlocal name, cond, run_lines
        if name and run_lines:
            steps.append(build(name, cond, "\n".join(run_lines)))
        name, cond, run_lines = "", "", []

    for line in text.splitlines():
        head = STEP_RE.match(line)
        if head:
            flush()
            in_run = False
            if head.group(1) == "name":
                name = head.group(2).strip()
            continue
        if in_run:
            # Тело блочного `run: |` — всё, что глубже поля.
            if line.startswith("          ") or not line.strip():
                run_lines.append(line.strip())
                continue
            in_run = False
        field = FIELD_RE.match(line)
        if field:
            key, value = field.group(1), field.group(2)
            if key == "if":
                cond = value.strip()
            elif key == "run":
                if value.strip() in ("|", ">"):
                    in_run = True
                else:
                    run_lines.append(value.strip())
    flush()
    return steps


def build(name: str, cond: str, run: str) -> Step:
    """Собирает шаг и решает, запускается ли он без изменения."""
    calls = [ln.strip() for ln in run.splitlines()
             if ln.strip().startswith("python ")]
    command = calls[-1].split() if calls else []
    why = ""
    if cond:
        why = f"только на изменении: {cond}"
    elif any(v in run for v in EVENT_VARS):
        why = "команде нужен контекст изменения, которого локально нет"
    elif not command:
        why = "шаг не запускает python — его исполняет площадка"
    return Step(name=name, command=command, skip_why=why)


def run_step(step: Step, root: Path) -> tuple[int, str]:
    """Запускает шаг. Возвращает код и вывод; таймаут — третий исход."""
    started = time.monotonic()
    try:
        done = subprocess.run(  # noqa: S603 — команда взята из своего же ci.yml
            [sys.executable, *step.command[1:]],
            cwd=root, capture_output=True, text=True, timeout=step.timeout_s)
    except subprocess.TimeoutExpired:
        return 2, f"шаг не уложился в {step.timeout_s} с"
    except OSError as exc:
        return 2, f"шаг не запустился: {exc}"
    spent = time.monotonic() - started
    tail = (done.stdout or "") + (done.stderr or "")
    return done.returncode, f"{tail.strip()}\n  ({spent:.1f} с)".strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    parser.add_argument("--list", action="store_true",
                        help="показать план и выйти, ничего не запуская")
    parser.add_argument("--only", metavar="ПОДСТРОКА",
                        help="запустить шаги, чьё имя или скрипт её содержат")
    args = parser.parse_args(argv)
    root: Path = args.root
    pipeline = root / ".github" / "workflows" / "ci.yml"

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not pipeline.exists():
        print(f"проверка не отработала: нет {pipeline} — "
              "список шагов брать неоткуда", file=sys.stderr)
        return 2
    steps = parse_steps(pipeline.read_text(encoding="utf-8"))
    runnable = [s for s in steps if not s.skip_why]
    if not runnable:
        print("проверка не отработала: в ci.yml не нашлось ни одного шага, "
              "запускаемого локально — это ошибка разбора, а не пустой "
              "конвейер", file=sys.stderr)
        return 2

    skipped = [s for s in steps if s.skip_why]
    if args.only:
        needle = args.only.lower()
        runnable = [s for s in runnable
                    if needle in s.name.lower()
                    or needle in " ".join(s.command).lower()]
        if not runnable:
            print(f"проверка не отработала: под «{args.only}» не подошёл ни "
                  "один шаг — выборка пуста, а не чиста", file=sys.stderr)
            return 2

    if args.list:
        print(f"шаги конвейера, запускаемые локально — {len(runnable)}:")
        for s in runnable:
            print(f"  · {' '.join(s.command)}   — {s.name}")
        if skipped:
            print(f"\nтолько на изменении — {len(skipped)}:")
            for s in skipped:
                print(f"  ~ {s.name}: {s.skip_why}")
        return 0

    # ── прогон ─────────────────────────────────────────────────────────────
    findings: list[str] = []
    broken: list[str] = []
    for step in runnable:
        code, out = run_step(step, root)
        mark = {0: "✓"}.get(code, "✗")
        print(f"{mark} {step.name}")
        if code != 0:
            print("\n".join(f"    {ln}" for ln in out.splitlines()))
            (broken if code == 2 else findings).append(step.name)

    # ЛОКАЛЬНАЯ ЗАМЕНА ВХОДА. Шаг, чей предмет есть здесь под другим именем,
    # спрашивается тем же скриптом — но текст берётся у коммита, а не у
    # площадки. Печатается отдельно от прогнанных: «проверено по коммиту» и
    # «проверено на изменении» — разные ответы (158).
    подменено: list[str] = []
    остались = []
    for step in skipped:
        замена = STAND_IN.get(step.name)
        if замена is None:
            остались.append(step)
            continue
        скрипт, откуда = замена
        текст, ошибка = branch_body(root)
        if ошибка:
            остались.append(step)
            print(f"~ {step.name}: замена не сработала — {ошибка}")
            continue
        done = subprocess.run(  # noqa: S603 — скрипт назван в таблице замен
            [sys.executable, скрипт, "--check", "--body-file", "-"],
            cwd=root, input=текст, capture_output=True, text=True)
        подменено.append(step.name)
        mark = {0: "✓"}.get(done.returncode, "✗")
        print(f"{mark} {step.name}  ({откуда})")
        if done.returncode != 0:
            tail = (done.stdout or "") + (done.stderr or "")
            print("\n".join(f"    {ln}" for ln in tail.strip().splitlines()))
            (broken if done.returncode == 2 else findings).append(step.name)
    skipped = остались

    # ЧЕГО НЕ ЗАПУСКАЛИ — ГОВОРИТСЯ ВСЕГДА, и говорится в конце, рядом с
    # итогом. Строка «прогон чист» без этого списка читалась бы как «проверено
    # всё», а проверено четырьмя шагами меньше (075).
    if skipped:
        print(f"\nне запускалось локально — {len(skipped)}, "
              "предмет появляется только на изменении:")
        for s in skipped:
            print(f"  ~ {s.name}")

    if broken:
        print(f"\nне отработало шагов: {len(broken)} — "
              + ", ".join(broken), file=sys.stderr)
        print("  Это третий исход, а не находка: проверка не состоялась "
              "(039).", file=sys.stderr)
        return 2
    if findings:
        print(f"\nнаходки в шагах: {len(findings)} — "
              + ", ".join(findings), file=sys.stderr)
        return 1
    print(f"\nчисто: {len(runnable)} шагов конвейера прошли локально")
    return 0


if __name__ == "__main__":
    sys.exit(main())
