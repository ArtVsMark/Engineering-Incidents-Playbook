#!/usr/bin/env python3
"""Зона изменения выводится из тронутых файлов и сверяется с тем, что стоит.

ИНЦИДЕНТ. Правило 064 говорит прямо: «классификация на задаче и на изменении
обязательна и проверяется машиной». Замер 28 августа: у последних ДЕСЯТИ
изменений каталога метки не было ни у одного. Правило объявляло себя
обеспеченным гейтом, а держало совсем другую половину — `labels-sync.yml`
применяет НАБОР меток к репозиторию, а `pr_body.py` проверяет строку связи с
задачей. Того, что изменение несёт зону, не проверял никто.

Нашёл это владелец глазами, а не механизм, — и это тот же случай, что уже
записан в карте направлений: окно проверяло свою работу, а не своё утверждение.

ПОЧЕМУ ВЫВОДИТСЯ, А НЕ ТРЕБУЕТСЯ. Инцидент самого 064: «машина метила
исправнее человека» — всё, что ставилось автоматикой, стояло; всё, что зависело
от дисциплины, отсутствовало у двух третей. Требовать метку от человека значит
воспроизвести ровно тот замер. Поэтому зона выводится из путей, конвейер её
ставит, а гейт сверяет.

ГРАНИЦА. Тронутый путь, не попавший ни в одну зону, зоной НЕ считается и
находкой тоже: зоны покрывают артефакты каталога, а не всякий файл в дереве
(`LICENSE`, `.gitignore`). Изменение только из таких файлов не обязано нести
зону — требовать её значило бы толкать к выдумыванию. А вот изменение, которое
трогает зону и не несёт её метку, — находка.

Соответствие «путь → зона» живёт в `.github/labels.yml`, рядом с самой меткой,
и читается отсюда. Держать его здесь значило бы завести вторую классификацию
одной территории (022).

Запуск:
  python scripts/check_labels.py --paths-from <файл>       # какие зоны нужны
  python scripts/check_labels.py --paths-from <файл> --have "area/rules,…"
Коды: 0 чисто · 1 есть находки · 2 проверка не отработала

Реализует правила каталога:
  064 — зона изменения выводится из тронутых путей и сверяется с тем, что на нём стоит.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = ROOT / ".github" / "labels.yml"

NAME_RE = re.compile(r'^-\s*name:\s*"([^"]+)"')
PATHS_RE = re.compile(r'^\s*paths:\s*\[(.*)\]\s*$')
ITEM_RE = re.compile(r'"([^"]+)"')


def zones(path: Path = LABELS) -> tuple[dict[str, list[str]], str | None]:
    """Метка → образцы путей. Читается построчно, как и `sync_labels.py`.

    Разбирать YAML целиком нечем без зависимости, а заводить её ради пяти
    строк — плата больше пользы. Форма узкая и проверяется: `paths` в одну
    строку списком в кавычках.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return {}, f"набор меток не прочитан: {e}"
    out: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        m = NAME_RE.match(line)
        if m:
            current = m.group(1)
            continue
        m = PATHS_RE.match(line)
        if m and current:
            out[current] = ITEM_RE.findall(m.group(1))
    if not out:
        return {}, (f"в {path.name} нет ни одной метки с `paths` — сверять "
                    "зону не с чем. Это не «зон нет», это проверка не отработала")
    return out, None


def matches(name: str, pattern: str) -> bool:
    """Образец `rules/**` покрывает и `rules/ru/001.md`, и сам `rules`.

    `fnmatch` трактует `*` как «что угодно, включая косую», поэтому `**` и `*`
    для него одно и то же. Здесь это НЕ упрощение: зоны заданы каталогами, и
    различать глубину незачем — а вот `README.md` обязан не совпасть с
    `rules/README.md`, и не совпадает, потому что образец без косой якорится
    целиком.
    """
    return fnmatch.fnmatch(name, pattern)


def needed(paths: list[str], zmap: dict[str, list[str]]) -> list[str]:
    """Зоны, которых изменение обязано нести, — по тронутым файлам."""
    out = set()
    for p in paths:
        for label, patterns in zmap.items():
            if any(matches(p, pat) for pat in patterns):
                out.add(label)
    return sorted(out)


def selftest() -> int:
    zmap, err = zones()
    if err:
        print(f"  ✗ живой набор меток не прочитан: {err}", file=sys.stderr)
        return 1
    bad = []

    def case(name, paths, ждём):
        вышло = needed(paths, zmap)
        if вышло != ждём:
            bad.append(f"{name}: ждали {ждём}, вышло {вышло}")

    case("запись каталога", ["rules/ru/001-a.md", "rules/en/001-a.md"],
         ["area/rules"])
    case("гейт и его набор", ["scripts/check_links.py", "tests/test_x.py"],
         ["area/gates"])
    case("витрина", ["README.md"], ["area/showcase"])
    case("контракт", ["export/rules.json", ".rules/bindings.json"],
         ["area/export"])
    case("заготовка", ["templates/bindings.json"], ["area/templates"])
    # Изменение через границы несёт ОБЕ зоны, а не первую попавшуюся.
    case("через границу", ["rules/ru/001-a.md", "scripts/check_links.py"],
         ["area/gates", "area/rules"])
    # ГЛАВНАЯ ГРАНИЦА: файл вне зон зоной не становится и находкой не делает.
    case("вне зон", ["LICENSE", ".gitignore"], [])
    # `README.md` витрины не должен ловиться на `rules/README.md`.
    case("указатель — это записи", ["rules/README.md"], ["area/rules"])

    # Исход 2: набор меток без `paths` — «сверять не с чем», а не «зон нет».
    import tempfile
    пусто = Path(tempfile.mkdtemp()) / "labels.yml"
    пусто.write_text('- name: "area/rules"\n  color: "1d76db"\n', encoding="utf-8")
    _, err2 = zones(пусто)
    if not err2:
        bad.append("набор без paths обязан дать «не отработала», дал молчание")

    for b in bad:
        print(f"  ✗ {b}", file=sys.stderr)
    print(f"самопроверка зон: случаев 9, провалов {len(bad)}",
          file=sys.stderr if bad else sys.stdout)
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--paths-from", type=Path,
                    help="файл со списком тронутых путей, по одному в строке")
    ap.add_argument("--have", default=None,
                    help="метки, стоящие на изменении, через запятую; "
                         "без ключа — только напечатать нужные")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    zmap, err = zones()
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2
    if not args.paths_from:
        print("проверка не отработала: не сказано, какие пути тронуты "
              "(--paths-from)", file=sys.stderr)
        return 2
    try:
        paths = [l.strip() for l in
                 args.paths_from.read_text(encoding="utf-8").splitlines()
                 if l.strip()]
    except OSError as e:
        print(f"проверка не отработала: список путей не прочитан — {e}",
              file=sys.stderr)
        return 2
    if not paths:
        print(f"проверка не отработала: {args.paths_from} пуст — изменение "
              "без файлов сверять не с чем", file=sys.stderr)
        return 2

    надо = needed(paths, zmap)
    if args.have is None:
        print("\n".join(надо))
        return 0

    есть = {x.strip() for x in args.have.split(",") if x.strip()}
    нет = [z for z in надо if z not in есть]
    if нет:
        print("зона изменения не проставлена: " + ", ".join(нет),
              file=sys.stderr)
        print("  Метка — вход механизма, а не украшение (правило 064): от неё "
              "зависят\n  очередь и зона работы. Ставит её конвейер при "
              "открытии изменения;\n  если её нет — открыли не конвейером либо "
              "сняли руками.", file=sys.stderr)
        return 1
    print(f"зона изменения на месте: {', '.join(надо) if надо else 'зон не тронуто'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
