#!/usr/bin/env python3
"""Код написан на версии планки, а не только объявлен на ней.

ПЛАНКА — ДВА ОБЕЩАНИЯ, А НЕ ОДНО. `requires-python` обещает потребителю, что
пакет заработает, — это держит check_python_version.py. Но то же число
говорит читателю «код пишется на этой версии», и это обещание до сих пор не
держал никто. Замер 2 октября, на следующий день после переезда планки на
3.14: из 132 файлов `from __future__ import annotations` стоял во всех 132,
`except (A, B):` без `as` — 21 раз. Номер переехал, стиль остался на 3.12:
переезд был формальным.

ЦЕЛЬ ВЫВОДИТСЯ ИЗ ПЛАНКИ, А НЕ ВПИСЫВАЕТСЯ (005). Каждое требование знает
версию, С КОТОРОЙ оно доступно, и действует, только когда планка до неё
доросла. Поднимется планка — гейт ужесточится сам, без правки здесь; ruff
получает ту же цель `--target-version` из той же планки.

ЗАГРУЗОЧНЫЕ ФАЙЛЫ — ИСКЛЮЧЕНИЕ НАОБОРОТ. Их исполняет системный python3 окна
(ОКНО) — до того, как хук старта собрал окружение на планке, и тогда, когда
собрать не смог: страж толчка и то, что он запускает, обязаны работать
именно там, где версия не та. Для них требование обратное: синтаксис планки
им запрещён, `__future__` обязателен. Список — замыкание по импортам и
запускам от `.claude/hooks/push_guard.py` и `check_python_version.py`;
тест сверяет, что он не отстал от кода.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.

Реализует правила каталога:
  005 — цель стиля выводится из планки, а не вписывается рукой;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  075 — не найден ruff или планка — отказ, а не чистый прогон.
"""

import argparse
import ast
import io
import json
import re
import shutil
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_python_version as cv  # noqa: E402

#: Исполняются системным python3 окна до окружения на планке (см. докстринг).
ЗАГРУЗОЧНЫЕ = frozenset({
    ".claude/hooks/push_guard.py",
    "scripts/check_python_version.py",
    "scripts/pr_body.py",
    "scripts/pr_source_commit.py",
})

#: Системный python3 образа облачного окна — на нём загрузочные файлы обязаны
#: РАЗБИРАТЬСЯ. ЧИСЛО РУЧНОЕ: замер 02.10.2026, `/usr/bin/python3 -V` → 3.11.15.
#: Это факт об образе, а не о проекте, и вывести его из дерева нечем. Сдвиг
#: образа этот гейт НЕ увидит — он разбирает файлы по константе, а образ не
#: опрашивает. Сдвинется образ ниже — правится здесь, руками, по новому замеру.
ОКНО = (3, 11)

#: С какой версии доступно то, что гейт требует. Ключ — версия языка.
ЛЕНИВЫЕ_АННОТАЦИИ = (3, 14)   # PEP 649/749: __future__ annotations лишний
EXCEPT_БЕЗ_СКОБОК = (3, 14)   # PEP 758: except A, B: без скобок

FUTURE = re.compile(r"^from __future__ import annotations\s*$", re.M)


def файлы(root: Path) -> list[str]:
    """Отслеживаемые .py — то, что поедет, а не то, что лежит рядом."""
    done = subprocess.run(["git", "ls-files", "-z", "*.py"], cwd=root,
                          capture_output=True, text=True, encoding="utf-8")
    if done.returncode != 0:
        raise RuntimeError(f"git ls-files не отработал: {done.stderr.strip()}")
    return sorted(п for п in done.stdout.split("\0") if п)


def except_в_скобках(text: str) -> list[int]:
    """Строки, где НЕСКОЛЬКО исключений взяты в скобки без `as`.

    Токенами, а не регулярным выражением: строка с `except (` внутри строкового
    литерала или комментария — не предмет. `except*` (группы исключений) —
    предмет тот же: PEP 758 снимает скобки и у него. Кортеж из одного
    элемента с хвостовой запятой, `except (A,):`, — не предмет: без скобок он
    не записывается вовсе."""
    ОТКРЫВАЮТ, ЗАКРЫВАЮТ = {"(", "[", "{"}, {")", "]", "}"}
    строки: list[int] = []
    токены = [t for t in tokenize.generate_tokens(io.StringIO(text).readline)
              if t.type not in (tokenize.NL, tokenize.COMMENT)]
    for i, t in enumerate(токены):
        if t.type != tokenize.NAME or t.string != "except":
            continue
        k = i + 1
        if k < len(токены) and токены[k].string == "*":
            k += 1
        if k >= len(токены) or токены[k].string != "(":
            continue
        глубина, элементов, j = 0, 1, k
        while j < len(токены):
            s = токены[j].string
            if s in ОТКРЫВАЮТ:
                глубина += 1
            elif s in ЗАКРЫВАЮТ:
                глубина -= 1
            elif (глубина == 1 and s == "," and j + 1 < len(токены)
                  and токены[j + 1].string != ")"):
                элементов += 1
            if глубина == 0:
                break
            j += 1
        if элементов > 1 and j + 1 < len(токены) and токены[j + 1].string == ":":
            строки.append(t.start[0])
    return строки


def находки_стиля(путь: str, text: str, планка: tuple[int, int]) -> list[str]:
    """Что в файле отстаёт от планки — или, у загрузочного, обгоняет окно."""
    out: list[str] = []
    if путь in ЗАГРУЗОЧНЫЕ:
        if not FUTURE.search(text):
            out.append(f"{путь}: загрузочный файл без `from __future__ import "
                       "annotations` — системный python3 окна вычислит аннотации сразу")
        try:
            # Разбор грамматикой окна. feature_version — best-effort, и граница
            # замерена (02.10.2026, тесты): отвергает `except A, B:`, оператор
            # `type`, обобщённые `def f[T]`, t-строки; ПРОПУСКАЕТ одинаковые
            # кавычки внутри f-строки (PEP 701). Этот пробел не закрыт: в CI
            # нет интерпретатора окна, на котором разбор был бы точным.
            ast.parse(text, feature_version=ОКНО)
        except SyntaxError as e:
            out.append(f"{путь}:{e.lineno}: загрузочный файл не разбирается "
                       f"python {ОКНО[0]}.{ОКНО[1]} окна — {e.msg}")
        return out
    if планка >= ЛЕНИВЫЕ_АННОТАЦИИ and FUTURE.search(text):
        out.append(f"{путь}: `from __future__ import annotations` при планке "
                   f"{планка[0]}.{планка[1]} — аннотации и так ленивые (PEP 649)")
    if планка >= EXCEPT_БЕЗ_СКОБОК:
        out += [f"{путь}:{n}: `except (A, B):` без `as` при планке "
                f"{планка[0]}.{планка[1]} — скобки не нужны (PEP 758)"
                for n in except_в_скобках(text)]
    return out


def находки_ruff(root: Path, пути: list[str], планка: tuple[int, int]) -> list[str]:
    """ruff UP с целью = планка. Ruff ищется рядом с интерпретатором, затем в PATH."""
    рядом = Path(sys.executable).with_name("ruff")
    ruff = str(рядом) if рядом.exists() else shutil.which("ruff")
    if ruff is None:
        raise RuntimeError("ruff не найден — ни рядом с интерпретатором, ни в PATH "
                           "(он в requirements-test.txt)")
    done = subprocess.run(
        [ruff, "check", "--isolated", "--no-cache", "--output-format", "json",
         "--target-version", f"py{планка[0]}{планка[1]}", "--select", "UP,FURB188",
         *пути], cwd=root, capture_output=True, text=True, encoding="utf-8")
    if done.returncode not in (0, 1):
        raise RuntimeError(f"ruff не отработал: {done.stderr.strip()[:300]}")
    return [f"{Path(d['filename']).relative_to(root.resolve())}:{d['location']['row']}: "
            f"{d['code']} {d['message']}" for d in json.loads(done.stdout or "[]")]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    root: Path = args.root.resolve()
    try:
        планка = cv.floor((root / "pyproject.toml").read_text(encoding="utf-8"))
        if планка is None:
            raise RuntimeError("в pyproject.toml нет requires-python — сверять стиль не с чем")
        пути = файлы(root)
        if not пути:
            raise RuntimeError("отслеживаемых .py нет ни одного — проверять нечего")
        находки = [н for п in пути
                   for н in находки_стиля(п, (root / п).read_text(encoding="utf-8"), планка)]
        находки += находки_ruff(root, [п for п in пути if п not in ЗАГРУЗОЧНЫЕ], планка)
    except (OSError, RuntimeError, ValueError, tokenize.TokenError) as e:
        print(f"стиль не проверен: {e}", file=sys.stderr)
        return 2
    if находки:
        print(f"стиль отстаёт от планки {планка[0]}.{планка[1]}: {len(находки)}")
        for н in находки:
            print(f"  {н}")
        return 1
    print(f"стиль на планке {планка[0]}.{планка[1]}: файлов {len(пути)}, "
          f"загрузочных {len(ЗАГРУЗОЧНЫЕ & set(пути))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
