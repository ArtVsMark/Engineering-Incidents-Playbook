#!/usr/bin/env python3
"""Версия каталога по схеме MAJOR.MINOR.PATCH. Единственный источник — git-тег.

СХЕМА ВЗЯТА У ГРЕЙДЕРА (ArtVsMark/Stepik-Python-Grader, docs/dev/versioning.md)
и это НЕ SemVer. Привычные правила SemVer её ломают, потому что здесь держится
инвариант «каждый тег = vX.Y.0»:

  MAJOR . MINOR . PATCH
    │       │       └─ +1 на принятое изменение; обнуляется при инкременте MINOR
    │       └───────── +1 ВСЕГДА при постановке тега и релиза
    └───────────────── только фундаментальное: каталог перестаёт быть каталогом
                       правил для Claude Code и GitHub

Следствие инварианта: PATCH-тегов не существует, поэтому двух версий с одним
номером быть не может. `1.0.17` читается как «17 принятых изменений после тега
v1.0.0», а НЕ «семнадцатый патч-релиз»: релиза с таким номером нет.

ПОЧЕМУ СЧИТАЮТСЯ СУЩНОСТИ, А НЕ РЁБРА ГРАФА. Топологическая формула меряет
ФОРМУ истории, а форма зависит от окна: в свежем клоне она линейная (слияния
уплотнением), но `git pull` мержем уводит пришедшее с площадки во ВТОРОЙ
родитель, и на first-parent линию оно не попадает. У грейдера это измерено:
`--first-parent` давал 2 вместо 3, `--no-merges` — 6 вместо 4. Ни одна
топологическая формула не даёт обе цифры, поэтому считаются номера изменений.

ЧЕМ ЭТО ОТЛИЧАЕТСЯ ОТ ГРЕЙДЕРА, И ЭТО НАЗВАНО, А НЕ СГЛАЖЕНО (правило 046).
У грейдера версия живёт в двух формах: метаданные пакета от setuptools-scm
(PEP 440, `X.Y.0.postN+g<hash>`) и логический счётчик. Здесь пакета нет —
каталог не публикуется в PyPI, `pyproject.toml` версии не объявляет. Поэтому
форма ОДНА, логическая, и запасного пути через метаданные установленного
пакета нет: до первого тега схемы версия недостоверна, и скрипт говорит об
этом третьим исходом, а не печатает правдоподобное «0.0.N».

Старый тег `0.1.0` под схему не подпадает (нет префикса `v`) и в расчёт не
идёт намеренно: он предшествует самой схеме и не несёт ни экспорта правил, ни
действий — ровно то, о чём задача #76.

Реализует правила каталога:
  035 — версия задаётся в одном месте и подставляется везде;
  046 — названный пробел лучше сглаженного;
  039 — у проверки три исхода, а не два;
  127 — число в прозе живёт под маркером, который переписывает сборка;
  163 — пример подключения закрепляется тегом в ОБОИХ документах входа:
        контракт и CONNECT.md учат одному и тому же номеру, а не разным;
  074 — тег ставится после проверки инвариантов, а не до: переписать его нечем.

Запуск:
  python scripts/version.py            # 1.0.17
  python scripts/version.py --release  # 1.0
  python scripts/version.py --badges   # записать .github/badges/{release,version}.json

Исходы:
  0 — версия определена;  2 — тега схемы не видно, версия недостоверна.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BADGES = ROOT / ".github" / "badges"

#: Следы самих механизмов: не принятые изменения, а их собственные отпечатки.
#: Считать их значило бы двигать счётчик тем, что счётчик и обслуживает.
BOT_COMMITS = ("chore(ci): update badges", "chore(release): pin examples")

#: Релизный тег строго `vX.Y.Z`. Маска нужна git-у, чтобы `describe` сразу искал
#: нужный тег; регулярка — потому что маска не отличает `v1.0.0` от `v1.0.0-rc`.
TAG_GLOB = "v[0-9]*.[0-9]*.[0-9]*"
TAG_RE = re.compile(r"^v\d+\.\d+\.\d+$")

#: Номер изменения в теме коммита. Две формы: уплотнение дописывает `(#N)` в
#: конец, обычное слияние даёт `Merge pull request #N from ...`. Обе ведут к
#: одному изменению, поэтому попадают в одно множество.
PR_RE = re.compile(r"\(#(\d+)\)")
MERGE_PR_RE = re.compile(r"^Merge pull request #(\d+)\b")

#: Склеивающее слияние `git pull`: сводит локальную копию ветки с удалённой,
#: своего изменения не несёт. Слияние ветки-темы (`Merge branch 'feat'`) под
#: шаблон не подпадает и считается — в нём и есть принятая работа.
SYNC_MERGE_RE = re.compile(
    r"^Merge (?:remote-tracking )?branch '[^']+' of |^Merge remote-tracking branch '"
)


def git(*args: str) -> str | None:
    """stdout git-команды без хвостового перевода строки; None при любой ошибке."""
    try:
        done = subprocess.run(("git", "-C", str(ROOT), *args),
                              capture_output=True, text=True, encoding="utf-8", check=False)
    except OSError:
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def subjects(rev_range: str, *, first_parent: bool = False) -> list[str]:
    args = ["log", "--pretty=%s"]
    if first_parent:
        args.append("--first-parent")
    out = git(*args, rev_range)
    return [line for line in out.split("\n") if line] if out else []


def pr_numbers(lines: list[str]) -> set[str]:
    found: set[str] = set()
    for subject in lines:
        found.update(PR_RE.findall(subject))
        merged = MERGE_PR_RE.match(subject)
        if merged:
            found.add(merged.group(1))
    return found


def countable_unnumbered(subject: str) -> bool:
    """Коммит без номера — прямой пуш, и он реален. Кроме бота и склеек."""
    return (not any(mark in subject for mark in BOT_COMMITS)
            and not SYNC_MERGE_RE.match(subject))


def accepted_since(rev_range: str) -> int:
    """Принятые изменения в диапазоне: множество номеров + безномерные с first-parent.

    Номера собираются по ВСЕЙ истории диапазона: при `git pull` мержем пришедшее
    с площадки лежит во втором родителе. Множество гасит и двойной учёт, если
    изменение попало в историю дважды — своим коммитом и уплотнённой версией.

    Безномерные берутся ТОЛЬКО с first-parent линии: иначе внутренние коммиты
    слитой ветки считались бы поштучно, и дробление снова завышало бы счёт.
    """
    numbered = pr_numbers(subjects(rev_range))
    unnumbered = [
        s for s in subjects(rev_range, first_parent=True)
        if not PR_RE.search(s) and not MERGE_PR_RE.match(s)
        and countable_unnumbered(s)
    ]
    return len(numbered) + len(unnumbered)


def latest_tag() -> str | None:
    """Ближайший релизный тег или None. Форма проверяется дважды — маской и регуляркой."""
    tag = git("describe", "--tags", "--abbrev=0", "--match", TAG_GLOB)
    return tag if tag and TAG_RE.match(tag) else None


def version() -> tuple[str, str] | None:
    """(релизная «X.Y», полная «X.Y.N») либо None, если тега схемы не видно."""
    tag = latest_tag()
    if tag is None:
        return None
    major, minor, _ = tag.lstrip("v").split(".")
    return f"{major}.{minor}", f"{major}.{minor}.{accepted_since(f'{tag}..HEAD')}"


def write_badges(release: str, full: str) -> list[Path]:
    """Два значка, и они не дублируют друг друга.

    `release` меняется на релизе, `version` — на каждое принятое изменение.
    Один значок вместо двух отвечал бы на два разных вопроса одним числом.
    """
    BADGES.mkdir(parents=True, exist_ok=True)
    written = []
    for name, label, message, color in (
        ("release", "release", release, "brightgreen"),
        ("version", "version", full, "blue"),
    ):
        path = BADGES / f"{name}.json"
        path.write_text(json.dumps(
            {"schemaVersion": 1, "label": label, "message": message,
             "color": color}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        written.append(path)
    return written


#: Маркер версии в прозе контракта. Число, которое некому переписать,
#: устаревает молча — а документ выглядит свежим (правила 035, 127).
PIN_RE = re.compile(r"(<!--m:ref-->)v[\d.]+(<!--/m:ref-->)")
#: Оба документа, где потребитель видит номер версии: машинный контракт и
#: страница подключения. Список, а не один файл: пример, который некому
#: переписать, вернётся к устаревшему тегу молча — и второй такой пример
#: появился ровно тогда, когда вход в проект описали инструментами.
PINNED = (ROOT / "export" / "README.md", ROOT / "CONNECT.md")


def pin(tag: str) -> str | None:
    """Подставляет тег в маркеры примеров. Возвращает находку, если маркера нет."""
    for path in PINNED:
        text = path.read_text(encoding="utf-8")
        if not PIN_RE.search(text):
            return (f"{path.name}: маркера <!--m:ref--> нет. Пример подключения, "
                    f"который некому переписать, вернётся к устаревшему тегу молча")
        path.write_text(PIN_RE.sub(rf"\g<1>{tag}\g<2>", text), encoding="utf-8")
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--release", action="store_true",
                       help="печатать только релизную часть «X.Y»")
    group.add_argument("--badges", action="store_true",
                       help="записать значки release и version")
    group.add_argument("--pin", action="store_true",
                       help="подставить последний релизный тег в пример контракта")
    args = ap.parse_args(argv)

    got = version()
    if got is None:
        # Третий исход, а не правдоподобное «0.0.N». Клон без тегов неотличим
        # от репозитория до первого релиза, и молчаливое число здесь хуже
        # отказа: значок выглядел бы свежим (правило 075).
        print("проверка не отработала: релизного тега вида vX.Y.0 не видно. "
              "Либо схема ещё не начата, либо клон без тегов — "
              "подтяните: git fetch --tags", file=sys.stderr)
        return 2

    release, full = got
    if args.pin:
        tag = latest_tag()
        problem = pin(tag)
        if problem:
            print(f"проверка не отработала: {problem}", file=sys.stderr)
            return 2
        print(f"пример контракта закреплён на {tag}")
    elif args.badges:
        for path in write_badges(release, full):
            print(f"записан {path.relative_to(ROOT)}")
    elif args.release:
        print(release)
    else:
        print(full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
