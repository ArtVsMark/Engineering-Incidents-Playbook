#!/usr/bin/env python3
"""Применяет `.github/labels.yml` к репозиторию и называет расхождения.

Правило 064: метка — вход механизма, а не украшение. Здесь механизма не было с
обеих сторон: файл никем не применялся, а расстановкой пользовались метки,
которых файл не признаёт. Решение, не доехавшее до предмета, неотличимо от
несуществующего (правило 002).

Что делает и чего НЕ делает:
  • объявленную метку заводит или приводит к объявленному цвету и описанию;
  • **не удаляет** метку, которой в файле нет: удаление снимает её со всех
    задач разом, а это решение человека, не побочный эффект синхронизации
    (правило 051 — запрещают достоверное, предупреждают о вероятном).
    Лишние метки печатаются списком, чтобы решение было чем принимать.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.

Запуск:  python scripts/sync_labels.py --dry-run   # показать, ничего не менять
         python scripts/sync_labels.py             # применить, нужен GH_TOKEN
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = ROOT / ".github" / "labels.yml"


def declared() -> tuple[list[dict], str | None]:
    """Читает объявленные метки. Формат простой и разбирается без зависимостей.

    Своего разбора YAML здесь ровно столько, сколько нужно файлу: список из
    трёх полей. Тянуть библиотеку ради этого значит добавить установку в
    конвейер и точку отказа туда, где её можно не иметь.
    """
    try:
        lines = LABELS.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return [], f"{LABELS.relative_to(ROOT)} не прочитан — {e}"

    out: list[dict] = []
    for raw in lines:
        line = raw.strip()
        if line.startswith("#") or not line:
            continue
        if line.startswith("- name:"):
            out.append({"name": _value(line.split(":", 1)[1])})
        elif out and line.startswith("color:"):
            out[-1]["color"] = _value(line.split(":", 1)[1])
        elif out and line.startswith("description:"):
            out[-1]["description"] = _value(line.split(":", 1)[1])
    bad = [l for l in out if not l.get("color")]
    if bad:
        return [], ("без цвета объявлены: "
                    + ", ".join(l["name"] for l in bad)
                    + " — файл разобран неверно или запись неполна")
    return out, None


def _value(chunk: str) -> str:
    return chunk.strip().strip('"').strip("'")


#: Код, которым gh_json сообщает «инструмента нет». Не из набора кодов gh:
#: тот возвращает 1 и 2, и совпадение сделало бы находку неотличимой от
#: неотработавшей проверки — ровно то, что здесь и чинится.
NO_GH = 127


def gh_json(*args: str) -> tuple[int, str]:
    """Вызов gh. Отсутствие самого gh — тоже исход, и он третий.

    Раньше здесь вылетала трассировка, а оболочка отдавала код 1 — то есть
    «есть находки». Разница не косметическая: находку чинит автор изменения,
    а отсутствующий инструмент чинит тот, кто запускает, и перепутать их
    значит послать человека искать несуществующее расхождение (правило 039).
    Объявленный третий исход у скрипта был, но эта ветка до него не доходила
    (правило 145).
    """
    try:
        done = subprocess.run(["gh", *args], capture_output=True, text=True)
    except FileNotFoundError:
        return NO_GH, "нет команды gh — поставьте GitHub CLI или задайте PATH"
    return done.returncode, (done.stdout or done.stderr).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="показать расхождения и ничего не менять")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = ap.parse_args()

    # ── исход 2: проверка не отработала ────────────────────────────────────
    want, err = declared()
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2
    if not want:
        print(f"проверка не отработала: {LABELS.relative_to(ROOT)} не объявляет "
              "ни одной метки — применять нечего, а молчать нельзя",
              file=sys.stderr)
        return 2
    if not args.repo:
        print("проверка не отработала: репозиторий не определён — задайте --repo",
              file=sys.stderr)
        return 2

    code, out = gh_json("api", f"repos/{args.repo}/labels?per_page=100",
                        "--jq", "[.[] | {name, color, description}]")
    if code != 0:
        print(f"проверка не отработала: список меток не прочитан — {out}",
              file=sys.stderr)
        return 2
    have = {l["name"]: l for l in json.loads(out)}

    created, fixed = [], []
    for label in want:
        name, color = label["name"], label["color"]
        desc = label.get("description", "")
        current = have.get(name)
        if current is None:
            created.append(name)
            if not args.dry_run:
                code, msg = gh_json("api", "-X", "POST",
                                    f"repos/{args.repo}/labels",
                                    "-f", f"name={name}", "-f", f"color={color}",
                                    "-f", f"description={desc}")
                if code != 0:
                    print(f"проверка не отработала: метка {name!r} не заведена — "
                          f"{msg}", file=sys.stderr)
                    return 2
        elif (current.get("color") or "").lower() != color.lower() or \
                (current.get("description") or "") != desc:
            fixed.append(name)
            if not args.dry_run:
                code, msg = gh_json("api", "-X", "PATCH",
                                    f"repos/{args.repo}/labels/{name}",
                                    "-f", f"color={color}", "-f", f"description={desc}")
                if code != 0:
                    print(f"проверка не отработала: метка {name!r} не приведена "
                          f"к объявленной — {msg}", file=sys.stderr)
                    return 2

    extra = sorted(set(have) - {l["name"] for l in want})

    verb = "завелись бы" if args.dry_run else "заведены"
    if created:
        print(f"{verb}: {', '.join(created)}")
    if fixed:
        print(f"{'привелись бы' if args.dry_run else 'приведены'} к объявленному: "
              f"{', '.join(fixed)}")
    if not created and not fixed:
        print("объявленные метки на месте и совпадают")

    # ── исход 1: находки ───────────────────────────────────────────────────
    if extra:
        print("\nв репозитории есть метки, которых файл не объявляет:",
              file=sys.stderr)
        print("  " + ", ".join(extra), file=sys.stderr)
        print("  Не удаляю: удаление снимает метку со всех задач разом, и это "
              "решение\n  человека. Либо вычеркнуть их в репозитории, либо "
              "вписать в файл с причиной.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
