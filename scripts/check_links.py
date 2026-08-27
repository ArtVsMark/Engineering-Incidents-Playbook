#!/usr/bin/env python3
"""Проверяет, что каждая относительная ссылка ведёт в существующий файл.

Реализует правила каталога:
  002 — разовая проверка руками не гарантирует ничего, нужен механизм;
  075 — не нашёл предмета проверки — падает, а не зеленеет на пустом входе;
  039 — три исхода: чисто · есть находки · проверка не отработала.

Внешние ссылки (http/https/mailto) намеренно не проверяются: сеть сделала бы
гейт флаки, а флаки гейт перестают читать.

Запуск:  python scripts/check_links.py
Коды:    0 чисто · 1 есть битые ссылки · 2 проверять было нечего
"""

from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL = ("http://", "https://", "mailto:", "#")


def anchors(path: Path) -> set[str]:
    """Якоря документа: заголовки, приведённые к виду ссылки GitHub."""
    out = set()
    for line in path.read_text(encoding="utf-8").split("\n"):
        if not line.startswith("#"):
            continue
        title = line.lstrip("#").strip().lower()
        title = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE)
        out.add(re.sub(r"\s+", "-", title))
    return out


def main(argv: list[str] | None = None) -> int:
    # Ключ «работай в другом корне» заведён не ради удобства: без него у гейта
    # нет предмета, который он обязан отвергнуть, и проверить его можно только
    # запуском на здоровом дереве — то есть никак (правила 140, 145).
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT,
                    help="корень дерева документов; по умолчанию сам репозиторий")
    root = ap.parse_args(argv).root

    files = [
        p for p in root.rglob("*.md")
        if not any(part in SKIP_DIRS for part in p.parts)
    ]
    if not files:
        print("не найдено ни одного документа — проверять нечего", file=sys.stderr)
        return 2

    problems: list[str] = []
    checked = 0
    for f in files:
        for m in LINK_RE.finditer(f.read_text(encoding="utf-8")):
            raw = m.group(1)
            if raw.startswith(EXTERNAL):
                continue
            checked += 1
            target, _, anchor = raw.partition("#")
            path = (f.parent / unquote(target)).resolve() if target else f
            rel = f.relative_to(root)
            if not path.exists():
                problems.append(f"{rel}: ссылка в никуда → {raw}")
                continue
            # Якорь проверяем только у документов: у каталога его быть не может.
            if anchor and path.is_file() and path.suffix == ".md":
                if re.sub(r"[^\w-]", "", anchor.lower()) not in {
                    re.sub(r"[^\w-]", "", a) for a in anchors(path)
                }:
                    problems.append(f"{rel}: якоря нет → {raw}")

    if checked == 0:
        print("в документах нет ни одной локальной ссылки — вход подозрителен", file=sys.stderr)
        return 2

    if problems:
        print(f"битых ссылок: {len(problems)} (проверено {checked})", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    print(f"ссылки в порядке: {checked} локальных в {len(files)} документах")
    return 0


if __name__ == "__main__":
    sys.exit(main())
