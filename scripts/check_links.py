#!/usr/bin/env python3
"""Проверяет, что каждая относительная ссылка ведёт в существующий файл.

Реализует правила каталога:
  002 — разовая проверка руками не гарантирует ничего, нужен механизм;
  075 — не нашёл предмета проверки — падает, а не зеленеет на пустом входе;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  119 — маска обхода не втягивает свои же служебные файлы;
  166 — ссылка ищется разметкой, а не подстрокой адреса: адрес стоит и в
        подписи ссылки, и проверка на подстроку зеленеет после подмены цели;
  076 — заготовка уходит к потребителю, и ссылка в ней обязана вести туда,
        что есть у получателя: относительная ссылка из templates/ в наше
        дерево у него мертва. Поэтому там стоят абсолютные ссылки на каталог,
        а они проверяются здесь как локальные — иначе умирали бы молча.

Внешние ссылки (http/https/mailto) намеренно не проверяются: сеть сделала бы
гейт флаки, а флаки гейт перестают читать. Исключение одно — абсолютная ссылка
на СВОЙ репозиторий (`https://github.com/<своё имя>/blob/<ветка>/<путь>`): её
цель лежит в этом же дереве, и сеть для проверки не нужна. Своё имя берётся у
origin (check_own_name.py), а не константой; нет origin — такие ссылки не
проверены, и итоговая строка говорит это вслух.

Запуск:  python scripts/check_links.py
Коды:    0 чисто · 1 есть битые ссылки · 2 проверять было нечего
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

from check_own_name import own_slug

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL = ("http://", "https://", "mailto:", "#")
#: Заготовки, которые уходят к потребителю: всё в templates/, кроме оглавления —
#: его читают здесь, в каталоге, и относительные ссылки у него живы.
ЗАГОТОВКИ = "templates"
ОГЛАВЛЕНИЕ = "README.md"


def своя_ссылка(slug: str) -> re.Pattern[str]:
    """Образец абсолютной ссылки на свой репозиторий; группа 1 — путь в дереве."""
    return re.compile(rf"^https://github\.com/{re.escape(slug)}/(?:blob|tree)/[^/]+/(.+)$")


def уходит_к_потребителю(doc: Path) -> bool:
    """Документ — заготовка, которую берут в чужой репозиторий."""
    rel = doc.relative_to(ROOT)
    return rel.parts[:1] == (ЗАГОТОВКИ,) and rel.name != ОГЛАВЛЕНИЕ


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


def main() -> int:
    files = [
        p for p in ROOT.rglob("*.md")
        if not any(part in SKIP_DIRS for part in p.parts)
    ]
    if not files:
        print(f"проверка не отработала: под {ROOT} не нашлось ни одного "
              f"*.md вне {sorted(SKIP_DIRS)} — проверять нечего",
              file=sys.stderr)
        return 2

    slug, почему = own_slug(ROOT)
    свои = своя_ссылка(slug) if slug else None
    problems: list[str] = []
    checked = 0
    своих = 0
    for f in files:
        rel = f.relative_to(ROOT)
        for m in LINK_RE.finditer(f.read_text(encoding="utf-8")):
            raw = m.group(1)
            if raw.startswith(EXTERNAL):
                hit = свои.match(raw) if свои else None
                if not hit:
                    continue
                своих += 1
                target, _, anchor = hit.group(1).partition("#")
                path = (ROOT / unquote(target)).resolve()
            else:
                checked += 1
                target, _, anchor = raw.partition("#")
                path = (f.parent / unquote(target)).resolve() if target else f
                if уходит_к_потребителю(f) and not path.is_relative_to(
                        (ROOT / ЗАГОТОВКИ).resolve()):
                    problems.append(
                        f"{rel}: заготовка уходит к потребителю, а ссылка ведёт "
                        f"в наше дерево → {raw}. У получателя этого пути нет — "
                        "нужна абсолютная ссылка на каталог (076)")
                    continue
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
        print(f"проверка не отработала: в {len(files)} документах под {ROOT} "
              "нет ни одной локальной ссылки — вход подозрителен",
              file=sys.stderr)
        return 2

    if problems:
        print(f"битых ссылок: {len(problems)} (проверено {checked})", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    print(f"ссылки в порядке: {checked} локальных и {своих} своих абсолютных "
          f"в {len(files)} документах"
          + ("" if свои else f" — свои абсолютные НЕ проверены: {почему}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
