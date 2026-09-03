#!/usr/bin/env python3
"""Гейт перед пушем: один запуск вместо чек-листа в документации.

Реализует правила каталога:
  002 — правило без механизма не соблюдается: чек-лист переписан в команду;
  039 — у проверки три исхода: чисто · есть находки · инструмент не отработал;
  075 — шаг, не нашедший предмета проверки, падает, а не зеленеет на пустом входе;
  068 — секреты ищутся по списку разрешённого, а не запрещённого;
  100 — у каждого шага свой предел времени.

Правьте под себя: список шагов внизу — единственное место, которое обычно
меняется. Всё остальное — обвязка, отвечающая за исходы и вывод.

Запуск:  python preflight.py            # все шаги
         python preflight.py --only tests
         python preflight.py --list
Коды:    0 всё чисто · 1 есть находки · 2 шаг не отработал
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# --- Правило 068: перечисляем РАЗРЕШЁННОЕ, а не запрещённое -----------------
# Список запрещённого не переживёт появления нового поля — а именно так секрет
# и утекает. Здесь наоборот: перечислены имена файлов, которым можно содержать
# что-то похожее на ключ (примеры, фикстуры, сам этот файл).
SECRET_ALLOWLIST = (
    "preflight.py",
    "*/tests/fixtures/*",
    "*.example",
    "*.md",
)
# Что считаем похожим на секрет. Дополняйте — но каждое добавление есть
# решение, и его видно в истории файла.
SECRET_PATTERNS = (
    (re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{12,}"), "литерал ключа"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "приватный ключ"),
    (re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b"), "ключ облачного провайдера"),
)
SCAN_SUFFIXES = (".py", ".js", ".ts", ".json", ".yml", ".yaml", ".toml", ".sh", ".env")

# Правило 100: предел времени у каждого шага, а не один на весь прогон.
DEFAULT_TIMEOUT_S = 600

OK, FINDINGS, BROKEN = 0, 1, 2


@dataclass
class Step:
    name: str
    argv: list[str]
    #: Файлы, без которых шаг бессмыслен. Пусто — шаг всегда применим.
    requires_files: tuple[str, ...] = ()
    timeout_s: int = DEFAULT_TIMEOUT_S
    #: Шаг, который не блокирует пуш (правило 051: предупреждают о вероятном).
    advisory: bool = False


@dataclass
class Result:
    step: str
    outcome: int
    detail: str = ""
    seconds: float = 0.0
    lines: list[str] = field(default_factory=list)


def _tracked_files() -> list[Path]:
    """Файлы под контролем версий. Пустой ответ — повод упасть (правило 075)."""
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=60
    )
    if out.returncode != 0:
        raise RuntimeError(f"git ls-files не отработал: {out.stderr.strip()}")
    names = [n for n in out.stdout.split("\0") if n]
    if not names:
        raise RuntimeError("git ls-files вернул пустой список — репозиторий пуст или мы не в нём")
    return [ROOT / n for n in names]


def check_secrets() -> Result:
    """Правило 068: allowlist. Правило 075: пустой вход — ошибка входа."""
    t0 = time.monotonic()
    try:
        files = _tracked_files()
    except Exception as exc:  # noqa: BLE001 — исход «не отработал» отдельный
        return Result("secrets", BROKEN, str(exc), time.monotonic() - t0)

    scanned, hits = 0, []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if any(fnmatch.fnmatch(rel, pat) for pat in SECRET_ALLOWLIST):
            continue
        if path.suffix not in SCAN_SUFFIXES or not path.is_file():
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return Result("secrets", BROKEN, f"{rel}: {exc}", time.monotonic() - t0)
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, what in SECRET_PATTERNS:
                if pattern.search(line):
                    hits.append(f"{rel}:{lineno}: {what}")

    if scanned == 0:
        # Правило 075: нечего проверять — это не «чисто», это сломанный вход.
        return Result("secrets", BROKEN, "не найдено ни одного файла для проверки", time.monotonic() - t0)
    if hits:
        return Result("secrets", FINDINGS, f"{len(hits)} совпадений", time.monotonic() - t0, hits)
    return Result("secrets", OK, f"проверено файлов: {scanned}", time.monotonic() - t0)


def run_step(step: Step) -> Result:
    t0 = time.monotonic()
    if step.requires_files and not any(ROOT.glob(p) for p in step.requires_files):
        return Result(step.name, BROKEN, f"не найдено: {', '.join(step.requires_files)}", 0.0)
    exe = shutil.which(step.argv[0])
    if exe is None:
        # Правило 039: «инструмента нет» — третий исход, а не тихий успех.
        return Result(step.name, BROKEN, f"инструмент не установлен: {step.argv[0]}", 0.0)
    try:
        proc = subprocess.run(
            step.argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=step.timeout_s
        )
    except subprocess.TimeoutExpired:
        return Result(step.name, BROKEN, f"предел времени {step.timeout_s} с", time.monotonic() - t0)
    tail = (proc.stdout + proc.stderr).strip().splitlines()
    outcome = OK if proc.returncode == 0 else FINDINGS
    return Result(step.name, outcome, f"код {proc.returncode}", time.monotonic() - t0, tail[-40:])


# --- Правьте здесь ----------------------------------------------------------
# Порядок — от дешёвого к дорогому: быстрый отказ экономит время.
STEPS: list[Step] = [
    Step("format", ["ruff", "format", "--check", "."]),
    Step("lint", ["ruff", "check", "."]),
    Step("types", ["mypy", "."], advisory=True),
    Step("tests", ["pytest", "-q"], requires_files=("tests",), timeout_s=1800),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", action="append", default=[], help="запустить только названные шаги")
    ap.add_argument("--list", action="store_true", help="показать шаги и выйти")
    args = ap.parse_args()

    names = ["secrets"] + [s.name for s in STEPS]
    if args.list:
        print("\n".join(names))
        return OK

    unknown = [n for n in args.only if n not in names]
    if unknown:
        print(f"неизвестные шаги: {', '.join(unknown)}", file=sys.stderr)
        return BROKEN

    selected = set(args.only) or set(names)
    results: list[Result] = []
    if "secrets" in selected:
        results.append(check_secrets())
    results.extend(run_step(s) for s in STEPS if s.name in selected)

    print()
    worst = OK
    advisory = {s.name for s in STEPS if s.advisory}
    for r in results:
        mark = {OK: "ok      ", FINDINGS: "НАХОДКИ ", BROKEN: "НЕ РАБОТ"}[r.outcome]
        note = " (не блокирует)" if r.outcome and r.step in advisory else ""
        print(f"{mark} {r.step:<10} {r.seconds:6.1f}s  {r.detail}{note}")
        for line in r.lines:
            print(f"           {line}")
        if r.step not in advisory:
            worst = max(worst, r.outcome)

    print()
    if worst == OK:
        print("чисто — можно пушить")
    elif worst == FINDINGS:
        print("есть находки — чинить")
    else:
        # Правило 039: это не «всё хорошо» и не «всё плохо», это третье.
        print("часть проверок не отработала — о предмете проверки мы не знаем ничего")
    return worst


if __name__ == "__main__":
    sys.exit(main())
