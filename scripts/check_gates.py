#!/usr/bin/env python3
"""Прогоняет гейты по предмету, который они обязаны отвергнуть.

Критик метода: отвечает не про каталог, а про то, как его проверяют. Зелёный
прогон на хорошем входе подтверждает, что гейт запускается, — и ничего больше.
Гейт, который всегда возвращает ноль, проходит такую проверку идеально
(правила 140, 097).

Предмет подделывается нарочно, а не ждётся из жизни: ждать настоящего нарушения
значит проверять гейт тогда, когда он уже не сработал.

Исходы:
  0 — гейт ведёт себя как объявлено;
  1 — расхождение: пропустил обязательное к отказу или отверг законное;
  2 — проверка не отработала.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "check_attribution.py"

TRAILER_OK = "Co-Authored-By: Claude <noreply@anthropic.com>"
TRAILER_STRANGER = "Co-Authored-By: Кто-то Посторонний <nobody@example.com>"
SESSION = "Claude-Session: https://example.invalid/session"

#: Что гейт обязан сделать с каждым предметом. Ожидание записано ЗДЕСЬ, рядом с
#: подделкой, а не в прозе свода: строку в своде никто не исполняет.
CASES = [
    ("подпись из согласованного списка", [TRAILER_OK, SESSION], 0,
     "законный коммит обязан проходить"),
    ("подпись вне списка", [TRAILER_STRANGER], 1,
     "чужое имя — то, ради чего список и заведён"),
    ("след сессии без соавторства", [SESSION], 1,
     "половина атрибуции хуже отсутствующей: выглядит подписанным"),
    ("без трейлеров вовсе", [], 0,
     "считается и печатается числом, но не отвергается — "
     "требование трейлеров это договорённость про агентские коммиты, "
     "а не запрет для человека со стороны"),
]


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def build(repo: Path) -> str | None:
    """Собирает подделку: по коммиту на случай. Возвращает ошибку или None."""
    steps = [
        ("git", "init", "-q", "-b", "main"),
        ("git", "config", "user.email", "fixture@example.invalid"),
        ("git", "config", "user.name", "Подделка"),
    ]
    for step in steps:
        done = run(*step, cwd=repo)
        if done.returncode != 0:
            return f"{' '.join(step)} — {done.stderr.strip()}"

    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    run("git", "add", "seed.txt", cwd=repo)
    done = run("git", "commit", "-q", "-m", "основание, вне проверяемого диапазона",
               cwd=repo)
    if done.returncode != 0:
        return f"основание не создано — {done.stderr.strip()}"

    for i, (name, trailers, _, _) in enumerate(CASES):
        (repo / f"case{i}.txt").write_text(f"{name}\n", encoding="utf-8")
        run("git", "add", f"case{i}.txt", cwd=repo)
        message = f"случай: {name}"
        if trailers:
            message += "\n\n" + "\n".join(trailers)
        done = run("git", "commit", "-q", "-m", message, cwd=repo)
        if done.returncode != 0:
            return f"коммит случая {name!r} не создан — {done.stderr.strip()}"
    return None


def main() -> int:
    if not GATE.exists():
        print(f"проверка не отработала: {GATE.relative_to(ROOT)} не найден",
              file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "fixture"
        repo.mkdir()
        err = build(repo)
        if err:
            print(f"проверка не отработала: подделка не собралась — {err}",
                  file=sys.stderr)
            return 2

        # Каждый случай проверяется по одному коммиту: иначе один отказ
        # закрывал бы собой все остальные, и «отверг» перестало бы означать
        # «отверг именно это».
        base = run("git", "rev-list", "--max-parents=0", "HEAD", cwd=repo).stdout.strip()
        log = run("git", "log", "--format=%H", "--reverse", cwd=repo).stdout.split()
        if len(log) != len(CASES) + 1:
            print("проверка не отработала: подделка собралась не той формы",
                  file=sys.stderr)
            return 2

        findings: list[str] = []
        for i, (name, _, want, why) in enumerate(CASES):
            rng = f"{log[i]}..{log[i + 1]}"
            done = run(sys.executable, str(GATE), "--repo", str(repo),
                       "--authors", str(ROOT / ".github" / "authors.txt"),
                       "--baseline", "", "--range", rng, cwd=ROOT)
            got = done.returncode
            mark = "ок" if got == want else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалось {want}, получено {got}")
            if got != want:
                findings.append(
                    f"{name}: ожидалось {want}, получено {got}. {why}\n"
                    f"        вывод гейта: {(done.stdout or done.stderr).strip()[:160]}")

    if findings:
        print("\nгейт ведёт себя не так, как объявлено:", file=sys.stderr)
        for f in findings:
            print(f"  • {f}", file=sys.stderr)
        print("\n  Расхождение чинится с той стороны, которая неверна: либо гейт, "
              "либо\n  формулировка в своде. Молчание не чинит ни одну "
              "(правило 140).", file=sys.stderr)
        return 1

    print(f"гейт атрибуции отвергает то, что обязан: случаев {len(CASES)}, "
          "расхождений нет")
    return 0


if __name__ == "__main__":
    sys.exit(main())
