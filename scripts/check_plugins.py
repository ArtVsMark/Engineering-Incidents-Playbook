#!/usr/bin/env python3
"""Витрина плагинов сходится с деревом, и версию плагина руками никто не вписывает.

ЗАЧЕМ. Навыки работы с каталогом держит каталог, а ставит их проект-потребитель
плагином. Площадка читает `.claude-plugin/marketplace.json` в корне, по нему —
`plugins/<имя>/.claude-plugin/plugin.json` и навыки в `plugins/<имя>/skills/`.
Расхождение витрины с деревом потребитель увидит отказом установки, а мы — ничем:
у каталога плагин не ставится, его навыки лежат не там, где их читает окно.

ВЕРСИЮ ВЫВОДИТ КОММИТ, И ПОЭТОМУ ПОЛЕ ЗАПРЕЩЕНО, А НЕ ТРЕБУЕТСЯ. Замер 25
сентября на площадке (`claude` 2.1.282): у плагина без поля `version` версией
записывается коммит витрины — `d08f87974c17`, — и следующий коммит доезжает
обновлением: `d08f87974c17 → 1a44b1c2bf01`, в кеше лежат оба текста. Кеш
ключуется версией, и вписанное число, которое забыли поднять, оставляет
поставивших на старом тексте молча. `claude plugin validate` советует обратное
— вписать `"1.0.0"`, — и совет этот верен для витрины, где версию поднимает
выпуск; здесь её не поднимает никто (035).

ЧТО ПРОВЕРЯЕТСЯ:
  • витрина разбирается, у неё непустые `name`, `owner.name` и список `plugins`;
  • у каждого плагина витрины имя латиницей через дефис, `source` — ровно
    `./plugins/<имя>`, и там `.claude-plugin/plugin.json` с тем же `name`: три
    имени одного плагина расходятся молча (035);
  • в `plugins/` нет папки, о которой молчит витрина: такой плагин не поставит
    никто, а выглядит он отданным;
  • поля `version` нет ни в записи витрины, ни в `plugin.json`.

ЧЕГО ЗДЕСЬ НЕТ — И ЭТО ГРАНИЦА. Навыки плагина — список, заголовок, разделы
заготовки — сверяет `check_skills.py`, тот же гейт, что у навыков окна: форма у
них одна (214). Ссылки из плагина в наше дерево — `check_links.py`: у
потребителя этих путей нет (076). Ставится ли плагин на площадке, в конвейере
не проверяет никто — это спросил бы `claude plugin validate`, а площадки в шаге
конвейера нет; замер выше сделан им вручную.

Реализует правила каталога:
  035 — версия не вписывается руками: у плагина её выводит коммит витрины, и
        имя одного плагина стоит в трёх местах, которые сверяются здесь;
  075 — нет витрины при папке `plugins/` или нет ни того ни другого — отказ,
        а не чистый прогон.

Исходы:
  0 — витрина и дерево сходятся;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Витрина — там, где её ищет площадка: `.claude-plugin/` в корне репозитория.
MARKETPLACE = Path(".claude-plugin") / "marketplace.json"
#: Плагины каталога — по папке на плагин.
PLUGINS = Path("plugins")
#: Манифест плагина — там, где его ищет площадка внутри папки плагина.
MANIFEST = Path(".claude-plugin") / "plugin.json"
#: Имя плагина: латиница, цифры, дефис — оно же имя папки и часть вызова
#: `/<плагин>:<навык>`.
ИМЯ_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def прочитать(путь: Path) -> tuple[dict | None, str]:
    """JSON-объект из файла. Вторая строка — чего не хватило."""
    try:
        d = json.loads(путь.read_text(encoding="utf-8"))
    except OSError as e:
        return None, f"не прочитан — {e}"
    except ValueError as e:
        return None, f"не разобран — {e}"
    if not isinstance(d, dict):
        return None, "не объект"
    return d, ""


def сверить(root: Path) -> tuple[list[str] | None, str, int]:
    """Находки витрины и дерева. Вторая строка — отказ, третье — плагинов."""
    витрина, папка = root / MARKETPLACE, root / PLUGINS
    if not витрина.exists():
        if папка.is_dir():
            return None, (f"{MARKETPLACE.as_posix()} нет, а {PLUGINS.as_posix()}/ "
                          "есть — плагины лежат, и площадка их не найдёт"), 0
        return None, (f"нет ни {MARKETPLACE.as_posix()}, ни {PLUGINS.as_posix()}/ "
                      "— гейт без предмета не зеленеет (075)"), 0
    d, чего = прочитать(витрина)
    if d is None:
        return None, f"{MARKETPLACE.as_posix()} {чего}", 0

    находки: list[str] = []
    имя = MARKETPLACE.as_posix()
    if not str(d.get("name") or "").strip():
        находки.append(f"{имя}: нет `name` — витрину ставят по имени")
    владелец = d.get("owner")
    if not (isinstance(владелец, dict) and str(владелец.get("name") or "").strip()):
        находки.append(f"{имя}: нет `owner.name`")
    плагины = d.get("plugins")
    if not (isinstance(плагины, list) and плагины):
        находки.append(f"{имя}: `plugins` не непустой список — витрина, которая "
                       "ничего не отдаёт, выглядит отданной")
        плагины = []

    названы: set[str] = set()
    for запись in плагины:
        if not isinstance(запись, dict):
            находки.append(f"{имя}: запись плагина не объект — {запись!r}")
            continue
        плагин = str(запись.get("name") or "")
        if not ИМЯ_RE.match(плагин):
            находки.append(f"{имя}: имя плагина {плагин!r} — не латиница через "
                           "дефис; оно же имя папки и часть вызова навыка")
            continue
        if плагин in названы:
            находки.append(f"{имя}: плагин «{плагин}» назван дважды")
        названы.add(плагин)
        if "version" in запись:
            находки.append(
                f"{имя}: у «{плагин}» вписана версия {запись['version']!r}. "
                "Версию выводит коммит витрины; вписанную некому поднять, и "
                "поставившие остаются на старом тексте молча (035)")
        ждём = f"./{(PLUGINS / плагин).as_posix()}"
        if запись.get("source") != ждём:
            находки.append(f"{имя}: у «{плагин}» source {запись.get('source')!r}, "
                           f"а ждётся {ждём!r} — папка плагина и есть его имя")
            continue
        манифест = PLUGINS / плагин / MANIFEST
        м, чего = прочитать(root / манифест)
        if м is None:
            находки.append(f"{манифест.as_posix()} {чего}")
            continue
        if м.get("name") != плагин:
            находки.append(
                f"{манифест.as_posix()}: name {м.get('name')!r}, а витрина зовёт "
                f"плагин «{плагин}» — три имени одного плагина расходятся молча (035)")
        if "version" in м:
            находки.append(
                f"{манифест.as_posix()}: вписана версия {м['version']!r}. Версию "
                "выводит коммит витрины; вписанную некому поднять (035)")

    if папка.is_dir():
        for лишняя in sorted(п.name for п in папка.iterdir() if п.is_dir()):
            if лишняя not in названы:
                находки.append(
                    f"{(PLUGINS / лишняя).as_posix()}/ есть, а {имя} о нём "
                    "молчит — такой плагин не поставит никто")
    return находки, "", len(названы)


def selftest() -> int:
    """Гейт отличает сошедшуюся витрину от каждого из своих предметов."""
    import tempfile
    годная = {"name": "m", "owner": {"name": "o"},
              "plugins": [{"name": "p", "source": "./plugins/p"}]}
    манифест = {"name": "p"}
    случаи: list[tuple[str, dict, dict | None, list[str], int]] = [
        ("сошедшаяся витрина", годная, манифест, [], 0),
        ("версия в витрине", {**годная, "plugins": [
            {"name": "p", "source": "./plugins/p", "version": "1.0.0"}]},
         манифест, [], 1),
        ("версия в манифесте", годная, {"name": "p", "version": "1.0.0"}, [], 1),
        ("имя в манифесте другое", годная, {"name": "q"}, [], 1),
        ("source мимо папки", {**годная, "plugins": [
            {"name": "p", "source": "./elsewhere"}]}, манифест, [], 1),
        ("папка без записи в витрине", годная, манифест, ["лишний"], 1),
        ("витрина без плагинов", {**годная, "plugins": []}, None, [], 1),
    ]
    плохо = []
    for что, витрина, м, лишние, ждём in случаи:
        with tempfile.TemporaryDirectory() as t:
            корень = Path(t)
            (корень / MARKETPLACE).parent.mkdir(parents=True)
            (корень / MARKETPLACE).write_text(json.dumps(витрина), encoding="utf-8")
            if м is not None:
                (корень / PLUGINS / "p" / MANIFEST).parent.mkdir(parents=True)
                (корень / PLUGINS / "p" / MANIFEST).write_text(json.dumps(м),
                                                              encoding="utf-8")
            for л in лишние:
                (корень / PLUGINS / л).mkdir(parents=True)
            находки, отказ, _ = сверить(корень)
        вышло = 2 if отказ else (1 if находки else 0)
        print(f"  {'находка ' if вышло else 'чисто   '} — {что}")
        if вышло != ждём:
            плохо.append(f"{что}: ждали {ждём}, вышло {вышло}")
    for строка in плохо:
        print(f"РАСХОЖДЕНИЕ: {строка}", file=sys.stderr)
    if плохо:
        return 1
    print("самопроверка пройдена: вписанная версия, чужое имя, source мимо "
          "папки и плагин без записи отличаются от сошедшейся витрины")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--selftest", action="store_true",
                   help="прогнать гейт по случаям, а не по дереву (140)")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()

    находки, отказ, плагинов = сверить(args.root)
    if отказ:
        print(f"проверка не отработала: {отказ}", file=sys.stderr)
        return 2
    if находки:
        print("витрина плагинов разошлась с деревом:", file=sys.stderr)
        for н in находки:
            print(f"  • {н}", file=sys.stderr)
        return 1
    print(f"витрина плагинов в порядке: плагинов {плагинов}, у каждого папка и "
          f"манифест с тем же именем, вписанной версии нет — её выводит коммит")
    return 0


if __name__ == "__main__":
    sys.exit(main())
