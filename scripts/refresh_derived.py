#!/usr/bin/env python3
"""Производные пересобираются сами, а не краснеют в ожидании человека.

ИНЦИДЕНТ. `consumers-sync` краснел на том, что потребитель обновил свой ответ.
28 августа `ArtVsMark` дописал вердикт по правилу 146 — прогон пересобрал сводку,
увидел расхождение с той, что лежит в репозитории, и покрасил общую ветку. По
091 это останавливает всю остальную работу; по 053 — до починки. А чинилось это
одной командой, которую всё равно выполнял бы человек, и результат её был
известен прогону заранее: он его только что посчитал.

ПОЧЕМУ ЭТО БЫЛА ОШИБКА, А НЕ СТРОГОСТЬ. Красное обязано звать человека туда, где
без него нельзя. Здесь без него было можно: вход — чужой ответ, выход —
производный файл, суждения между ними нет. Красное на такой находке приучает
читать красное как фон (051), и тогда оно перестаёт работать там, где оно
настоящее — а настоящих находок у того же прогона три: ответ не читается,
потребитель отвечает о несуществующем правиле, объявленный молчит дольше срока.
Все три требуют человека, и все три теперь одни в красном.

ГРАНИЦА — ГЛАВНОЕ ЗДЕСЬ. Пересобирать вслепую нельзя. Сборщик, тронувший что-то
кроме объявленного набора производных, означает поломку сборщика, а не свежие
данные; закоммитить такое автоматически — раздать поломку по потребителям.
Поэтому набор объявлен ПОИМЁННО, и всё, что вне его, — исход 2 «не отработала»,
то есть красное с человеком, а не тихий коммит.

ЧЕГО ЭТОТ СКРИПТ НЕ ДЕЛАЕТ. Не коммитит и не толкает. Он отвечает на один
вопрос — «что пересобралось и можно ли этому верить», — а решение о записи
принимает прогон, у которого есть токен. Разделено потому, что проверить можно
только то, что можно запустить всухую.

Исходы:
  0 — производные совпали с тем, что лежит: обновлять нечего;
  1 — производные обновлены, набор изменённых файлов напечатан;
  2 — не отработала: сборщик отказал либо тронул файл вне объявленного набора.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Что в сводке меняется само по себе, знает тот, кто это пишет. Импорт, а не
# копия: копия молча отстанет, и пересборка начнёт заводить пустые изменения.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from aggregate_bindings import VOLATILE  # noqa: E402

#: Сборщики в порядке зависимости: картинка рисуется из `export/where.json`,
#: который пишет сводка. Обратный порядок нарисовал бы вчерашние числа.
BUILDERS = (
    ("scripts/aggregate_bindings.py", ()),
    ("scripts/consumers_picture.py", ()),
)

#: Что этим сборщикам РАЗРЕШЕНО менять. Список закрытый и разрешительный — по
#: той же причине, что и реестр потребителей (068): всё, чего здесь нет, есть
#: находка, а не свежие данные.
DERIVED = (
    "export/where.md",
    "export/where.json",
    ".github/badges/consumers-light.svg",
    ".github/badges/consumers-dark.svg",
    ".github/badges/consumers-en-light.svg",
    ".github/badges/consumers-en-dark.svg",
)


def run(args: list[str], cwd: Path) -> tuple[int, str]:
    """Запуск с прочитанным выводом. Отказ — значение, а не исключение."""
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    except OSError as e:
        return 127, str(e)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def changed(root: Path) -> tuple[list[str] | None, str]:
    """Что в рабочем дереве отличается от индекса. `None` — спросить не вышло.

    `core.quotePath=false` не косметика: по умолчанию git печатает не-ASCII имя
    восьмеричными последовательностями (`\\321\\201...`). Сравнение с набором
    производных на таком имени молча не совпадёт, а человек в жалобе прогона
    увидит мусор вместо имени файла. Поймано самопроверкой, а не глазом.
    """
    rc, out = run(["git", "-c", "core.quotePath=false",
                   "status", "--porcelain", "--untracked-files=all"], root)
    if rc != 0:
        return None, out
    names = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        name = line[3:]
        # Переименование печатается как «было -> стало»; интересует второе.
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        names.append(name.strip().strip('"'))
    return names, out


def differ(root: Path) -> tuple[list[str] | None, str]:
    """Производные, отличающиеся от того, что ЛЕЖИТ в истории.

    Не «что изменил этот запуск». Разница видна на втором запуске подряд:
    первый пересобрал и отличается от истории, второй ничего не менял — и
    сказал бы «обновлять нечего» при грязных производных на диске. Замер:
    ровно так и получилось при первой сборке этого скрипта.
    """
    rc, out = run(["git", "-c", "core.quotePath=false", "diff", "--name-only",
                   "HEAD", "--", *DERIVED], root)
    if rc != 0:
        return None, out
    names = {n.strip() for n in out.splitlines() if n.strip()}
    # Файла может ещё не быть в истории — тогда он не в `diff`, а в untracked.
    known, raw = changed(root)
    if known is None:
        return None, raw
    names |= {n for n in known if n in DERIVED}
    return sorted(n for n in names if not only_volatile(root, n)), out


def only_volatile(root: Path, name: str) -> bool:
    """Отличие свелось к полю, которое меняется само по себе.

    Дата последнего чтения меняется каждым прогоном независимо от данных. Файл
    целиком сравнивать нельзя: пересборка заводила бы изменение КАЖДЫЙ ДЕНЬ,
    ничего при этом не меняя, и такие изменения научились бы пролистывать не
    глядя (051) — то есть механизм починил бы свежесть способом, который её
    ломает.

    ГРАНИЦА. Работает только по JSON и только по верхнему уровню записи
    потребителя. Нечитаемое сравнить нечем, и такое считается ОТЛИЧИЕМ:
    промолчать о непонятном — худший из двух исходов.
    """
    if not name.endswith(".json"):
        return False
    rc, head = run(["git", "show", f"HEAD:{name}"], root)
    if rc != 0:
        return False
    try:
        was = json.loads(head)
        now = json.loads((root / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    for doc in (was, now):
        for entry in doc.get("consumers", []):
            for key in VOLATILE:
                entry.pop(key, None)
    return was == now


def refresh(root: Path) -> tuple[int, list[str], list[str]]:
    """Пересобрать производные. Возвращает исход, изменённое и жалобы.

    ДВА РАЗНЫХ ВОПРОСА, И МЕРЯЮТСЯ ОНИ ПО-РАЗНОМУ.

    «Что пересобралось» — против ИСТОРИИ: производное, отличающееся от того,
    что лежит в `HEAD`, есть работа, даже если этот запуск его не трогал.
    Первая версия сравнивала до и после запуска, и второй запуск подряд
    говорил «обновлять нечего» при грязных производных на диске.

    «Сборщик тронул лишнее» — против СОСТОЯНИЯ ДЕРЕВА ДО запуска: файл, уже
    грязный у человека, сборщику не принадлежит. Первая версия объявляла
    находкой всё грязное и на первом же локальном запуске обвинила сборщик в
    правках, которых тот не делал.

    ГРАНИЦА. Файл вне набора, который был грязным ДО сборки и который сборщик
    изменил ещё раз, здесь не ловится: имя было в списке и осталось. На чистом
    дереве прогона такого не бывает, а запуск на грязном — работа человека, и
    решение он принимает сам.
    """
    problems: list[str] = []

    before, raw = changed(root)
    if before is None:
        problems.append(f"состояние дерева не прочитано: {raw.strip()}")
        return 2, [], problems

    for script, extra in BUILDERS:
        if not (root / script).exists():
            problems.append(f"сборщика нет: {script}")
            return 2, [], problems
        rc, out = run([sys.executable, script, *extra], root)
        if rc != 0:
            problems.append(f"{script} отказал (код {rc}):\n{out.strip()}")
            return 2, [], problems

    after, raw = changed(root)
    if after is None:
        problems.append(f"состояние дерева не прочитано: {raw.strip()}")
        return 2, [], problems

    # ВНЕ НАБОРА — ЭТО НАХОДКА. Не «заодно закоммитим»: файл, который сборка
    # загрязнила ВПЕРВЫЕ и которого нет в наборе, означает, что сборщик делает
    # не то, что объявлено.
    stray = sorted(set(after) - set(before) - set(DERIVED))
    if stray:
        problems.append("сборщик тронул файлы вне объявленного набора: "
                        + ", ".join(stray))
        return 2, [], problems

    touched, raw = differ(root)
    if touched is None:
        problems.append(f"история не прочитана: {raw.strip()}")
        return 2, [], problems
    return (1 if touched else 0), touched, problems


# ── самопроверка: три исхода, а не «запустилось» ───────────────────────────
#
# Набор двусторонний (140): у каждого исхода есть предмет, который обязан его
# дать. Проверяется именно граница — ради неё скрипт и существует.

def selftest() -> int:
    import tempfile

    def repo(builder: str, json_seed: bool = False) -> Path:
        d = Path(tempfile.mkdtemp())
        run(["git", "init", "-q"], d)
        run(["git", "config", "user.email", "s@e"], d)
        run(["git", "config", "user.name", "s"], d)
        (d / "scripts").mkdir()
        (d / "export").mkdir()
        (d / ".github" / "badges").mkdir(parents=True)
        for name in DERIVED:
            f = d / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("исходное\n", encoding="utf-8")
        if json_seed:
            (d / "export" / "where.json").write_text(json.dumps(
                {"consumers": [{"repo": "o/a", "read_at": "вчера", "answered": 1}]},
                ensure_ascii=False), encoding="utf-8")
        (d / "чужой.txt").write_text("исходное\n", encoding="utf-8")
        for script, _ in BUILDERS:
            (d / script).write_text(builder, encoding="utf-8")
        run(["git", "add", "-A"], d)
        run(["git", "commit", "-qm", "начало"], d)
        return d

    bad = []

    # Исход 0: сборщик ничего не меняет.
    rc, names, _ = refresh(repo("pass\n"))
    if rc != 0 or names:
        bad.append(f"тихий сборщик обязан дать 0 и пустой список, дал {rc} {names}")

    # Исход 1: сборщик обновил объявленное производное.
    d = repo("from pathlib import Path\n"
             "Path('export/where.md').write_text('свежее\\n', encoding='utf-8')\n")
    rc, names, _ = refresh(d)
    if rc != 1 or names != ["export/where.md"]:
        bad.append(f"обновление производного обязано дать 1 и его имя, дало {rc} {names}")

    # Исход 2: сборщик тронул файл ВНЕ набора. Ради этой границы всё и написано.
    d = repo("from pathlib import Path\n"
             "Path('чужой.txt').write_text('свежее\\n', encoding='utf-8')\n")
    rc, _, problems = refresh(d)
    if rc != 2 or not any("вне объявленного набора" in p for p in problems):
        bad.append(f"файл вне набора обязан дать 2 и назвать его, дал {rc} {problems}")

    # Исход 2: сборщик отказал. Красное здесь настоящее — чинит человек.
    rc, _, problems = refresh(repo("import sys; sys.exit(3)\n"))
    if rc != 2 or not any("отказал" in p for p in problems):
        bad.append(f"отказ сборщика обязан дать 2, дал {rc} {problems}")

    # Исход 2: сборщика нет вовсе. Отличается от «отработал и ничего не нашёл».
    d = repo("pass\n")
    (d / BUILDERS[0][0]).unlink()
    rc, _, problems = refresh(d)
    if rc != 2 or not any("сборщика нет" in p for p in problems):
        bad.append(f"пропавший сборщик обязан дать 2, дал {rc} {problems}")

    # Новый файл внутри набора считается изменением, а не пропускается: свежая
    # картинка в непустом репозитории приезжает именно так.
    d = repo("from pathlib import Path\n"
             "Path('.github/badges/consumers-dark.svg')"
             ".write_text('новая\\n', encoding='utf-8')\n")
    (d / ".github/badges/consumers-dark.svg").unlink()
    run(["git", "commit", "-qam", "картинки не было"], d)
    rc, names, _ = refresh(d)
    if rc != 1 or names != [".github/badges/consumers-dark.svg"]:
        bad.append(f"новое производное обязано дать 1 и его имя, дало {rc} {names}")

    # ГРЯЗНОЕ ДЕРЕВО ЧЕЛОВЕКА — НЕ НАХОДКА СБОРЩИКА. Ровно на этом первая
    # версия дала 2 на первом же локальном запуске.
    d = repo("pass\n")
    (d / "чужой.txt").write_text("правка человека\n", encoding="utf-8")
    (d / "новый-от-человека.txt").write_text("и это тоже\n", encoding="utf-8")
    rc, names, problems = refresh(d)
    if rc != 0 or names:
        bad.append(f"чужая незакоммиченная правка обязана дать 0, дала {rc} {problems}")

    # ...но сборщик, ТРОНУВШИЙ вне набора на грязном дереве, всё равно находка.
    d = repo("from pathlib import Path\n"
             "Path('свой-мусор.txt').write_text('сборщик\\n', encoding='utf-8')\n")
    (d / "чужой.txt").write_text("правка человека\n", encoding="utf-8")
    rc, _, problems = refresh(d)
    if rc != 2 or not any("свой-мусор.txt" in p for p in problems):
        bad.append(f"мусор сборщика на грязном дереве обязан дать 2, дал {rc} {problems}")

    # ДВА ЗАПУСКА ПОДРЯД ОТВЕЧАЮТ ОДИНАКОВО. Пока производное отличается от
    # истории, работа есть — независимо от того, кто её сделал и когда.
    d = repo("from pathlib import Path\n"
             "Path('export/where.md').write_text('свежее\\n', encoding='utf-8')\n")
    first = refresh(d)[0]
    second = refresh(d)[0]
    if (first, second) != (1, 1):
        bad.append(f"второй запуск подряд обязан ответить то же, что первый: {first} {second}")

    # ТОЛЬКО ДАТА ЧТЕНИЯ — НЕ ИЗМЕНЕНИЕ. Ловушка, ради которой всё это писано:
    # иначе пересборка заводила бы изменение каждый день, ничего не меняя.
    d = repo("import json, pathlib\n"
             "p = pathlib.Path('export/where.json')\n"
             "d = json.loads(p.read_text(encoding='utf-8'))\n"
             "d['consumers'][0]['read_at'] = 'завтра'\n"
             "p.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')\n",
             json_seed=True)
    rc, names, problems = refresh(d)
    if rc != 0 or names:
        bad.append(f"смена одной даты чтения обязана дать 0, дала {rc} {names}")

    # ...а данные рядом с той же датой — изменение. Обратная сторона (140).
    d = repo("import json, pathlib\n"
             "p = pathlib.Path('export/where.json')\n"
             "d = json.loads(p.read_text(encoding='utf-8'))\n"
             "d['consumers'][0]['read_at'] = 'завтра'\n"
             "d['consumers'][0]['answered'] = 99\n"
             "p.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')\n",
             json_seed=True)
    rc, names, _ = refresh(d)
    if rc != 1 or names != ["export/where.json"]:
        bad.append(f"данные рядом с датой обязаны дать 1, дали {rc} {names}")

    for b in bad:
        print(f"  ✗ {b}", file=sys.stderr)
    print(f"самопроверка обновления производных: случаев 11, провалов {len(bad)}",
          file=sys.stderr if bad else sys.stdout)
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--selftest", action="store_true",
                    help="прогнать все объявленные исходы и выйти")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    rc, names, problems = refresh(args.root)
    for p in problems:
        print(f"  ✗ {p}", file=sys.stderr)
    if rc == 2:
        print("обновление производных НЕ отработало — это чинит человек",
              file=sys.stderr)
        return 2
    if rc == 0:
        print("производные совпадают с тем, что отдают потребители")
        return 0
    print(f"производные обновлены: {len(names)} файлов")
    for n in names:
        print(f"  · {n}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
