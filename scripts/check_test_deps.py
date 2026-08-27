#!/usr/bin/env python3
"""Тест не зависит от того, что случайно стоит у автора.

ИНЦИДЕНТ, ИЗ КОТОРОГО ЭТО ВЫРОСЛО. Новый набор импортировал `yaml`, чтобы
убедиться, что собранный рабочий процесс вообще разбирается. У автора
библиотека стояла, и набор был зелёный; в конвейере её не было, и прогон упал
на `ModuleNotFoundError`. Классика 107: «у автора работает» означает
«проверено на выборке автора», и за её границами инструмент не сломан — он НЕ
ПРОВЕРЕН.

ЧТО ПРОВЕРЯЕТСЯ. Каждый импорт в `tests/` — это либо стандартная библиотека,
либо модуль самого каталога (`scripts/`, `conftest`), либо строка в
`requirements-test.txt`. Четвёртого не дано: импорт, которого нет ни там, ни
там, зеленеет ровно до первого чужого окружения.

ЧЕГО ГЕЙТ НЕ ДЕЛАЕТ. Он не проверяет, что зависимость установлена — это дело
прогона, и он падает сам. Здесь предмет другой: ОБЪЯВЛЕНА ли она.

Запуск:  python scripts/check_test_deps.py [--root <корень>]
Коды:    0 чисто · 1 есть находки · 2 проверка не отработала
"""

from __future__ import annotations

import argparse
import ast
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQS = "requirements-test.txt"

#: Модули самого каталога: лежат в scripts/ и рядом с тестами.
def local_modules(root: Path) -> set[str]:
    out = {p.stem for p in (root / "scripts").glob("*.py")}
    out |= {p.stem for p in (root / "tests").glob("*.py")}
    # `conftest` — соглашение самого pytest: он есть везде, где есть тесты, и
    # объявлять его зависимостью значило бы объявлять зависимостью пути.
    out.add("conftest")
    return out


def stdlib() -> set[str]:
    """Стандартная библиотека этого Python. Список её, а не наш."""
    names = set(sys.stdlib_module_names)
    # sysconfig знает про платформенные модули, которых нет в списке имён.
    names.add(Path(sysconfig.get_paths()["stdlib"]).name)
    return names


def imported(path: Path) -> set[str]:
    """Имена ВЕРХНЕГО уровня, которые модуль импортирует."""
    out: set[str] = set()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                out.add(node.module.split(".")[0])
    return out


def distributions_for(name: str) -> set[str]:
    """Дистрибутивы, которые ставят модуль с таким именем.

    ИМЯ ПАКЕТА И ИМЯ МОДУЛЯ — РАЗНЫЕ ВЕЩИ, и это не редкость: `pyyaml` даёт
    `yaml`, `pillow` даёт `PIL`. Таблица синонимов здесь была бы списком
    запрещённого наоборот — она не знает о том, что появится завтра (068).
    Метаданные знают точно, и спрашиваем мы их.
    """
    try:
        from importlib.metadata import packages_distributions
    except ImportError:  # pragma: no cover — Python старше 3.10
        return set()
    try:
        found = packages_distributions().get(name, [])
    except Exception:  # pragma: no cover — метаданные битые
        return set()
    return {d.lower().replace("-", "_") for d in found}


def declared(root: Path) -> tuple[set[str], str | None]:
    path = root / REQS
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return set(), f"{REQS} не прочитан — {e}"
    names = set()
    for raw in lines:
        line = raw.split("#")[0].strip()
        if not line or line.startswith("-"):
            continue
        # Имя до любого указателя версии; регистр и дефисы к одному виду.
        for sep in ("==", ">=", "<=", "~=", ">", "<", "[", ";"):
            line = line.split(sep)[0]
        names.add(line.strip().lower().replace("-", "_"))
    return names, None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    root: Path = ap.parse_args(argv).root

    # ── исход 2 ────────────────────────────────────────────────────────────
    tests = sorted((root / "tests").glob("*.py"))
    if not tests:
        print("проверка не отработала: тестов нет — смотреть нечего",
              file=sys.stderr)
        return 2
    allowed, err = declared(root)
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    known = stdlib() | local_modules(root)
    problems: list[str] = []
    for path in tests:
        try:
            names = imported(path)
        except SyntaxError as e:
            print(f"проверка не отработала: {path.name} не разобран — {e}",
                  file=sys.stderr)
            return 2
        for name in sorted(names):
            if name in known:
                continue
            if name.lower().replace("-", "_") in allowed:
                continue
            # Пакет мог быть объявлен под своим именем, а не именем модуля.
            if distributions_for(name) & allowed:
                continue
            problems.append(
                f"{path.name}: импортирует «{name}», которого нет ни в "
                f"стандартной библиотеке, ни в {REQS}. У автора он, возможно, "
                "стоит — в чужом окружении набор упадёт на импорте")

    # ── исход 1 ────────────────────────────────────────────────────────────
    if problems:
        print("тесты зависят от необъявленного:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        print(f"\n  «У автора работает» означает «проверено на выборке автора» "
              f"(правило 107).\n  Объявите зависимость в {REQS} — её ставят обе "
              "работы конвейера.", file=sys.stderr)
        return 1

    # ── исход 0 ────────────────────────────────────────────────────────────
    print(f"тесты зависят только от объявленного: модулей {len(tests)}, "
          f"объявленных зависимостей {len(allowed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
