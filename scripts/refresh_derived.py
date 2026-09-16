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

Реализует правила каталога:
  039 — три исхода объявлены и прогоняются самопроверкой, а не подразумеваются;
  045 — исход «не отработала» печатается громко; тихого запасного пути нет;
  067 — уборка после сбоя не превращает сбой в успех: код возврата переживает её;
  109 — терминальный статус обязателен — 0, 1 или 2, и третий не растворяется во втором.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Что в сводке меняется само по себе, знает тот, кто это пишет. Импорт, а не
# копия: копия молча отстанет, и пересборка начнёт заводить пустые изменения.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from aggregate_bindings import VOLATILE, VOLATILE_TOP  # noqa: E402

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
    # КАРТИНОК ЗДЕСЬ БОЛЬШЕ НЕТ, и это решение, а не пропуск (правило 160).
    # Витрина читает их с ветки `badges`; копия в дереве пересобиралась этим
    # же прогоном и давала коммит в общую ветку на каждое обновление ответа
    # потребителя — четыре за одну смену, при том что читают другую копию.
    # Рисует их badges.yml на каждый толчок в main и кладёт на свою ветку.
)


#: Ветка, на которой лежит ОПУБЛИКОВАННАЯ копия производных.
#:
#: ПОЧЕМУ НЕ `HEAD`. До 4 сентября сводка лежала в общей ветке, и «отличается
#: от истории» означало «отличается от опубликованного» — одно и то же. В тот
#: день #330 увёз её на отдельную ветку и записал оба файла в `.gitignore`
#: (правило 160), и вопрос распался надвое: в `HEAD` их нет вовсе, а
#: `git status` игнорируемых не показывает. Ответ «ничего не изменилось»
#: стал приходить ВСЕГДА — 0 пробуждений публикации за 321 прогон.
#:
#: Тем же коммитом #330 был заведён шаг «разбудить публикацию»: механизм
#: родился слепым, и отказ у него бесшумный — код 0, то есть зелёный (039).
PUBLISHED_REF = os.environ.get("DERIVED_PUBLISHED_REF", "origin/badges")


def run(args: list[str], cwd: Path) -> tuple[int, str]:
    """Запуск с прочитанным выводом. Отказ — значение, а не исключение."""
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
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


def опубликовано(root: Path, name: str) -> tuple[str | None, str, str | None]:
    """Содержимое ОПУБЛИКОВАННОЙ копии производного: текст, откуда, жалоба.

    ДВА МЕСТА, И ВЫБИРАЕТ МЕЖДУ НИМИ ФАКТ, А НЕ НАСТРОЙКА. Производное,
    лежащее в общей ветке, сверяется с ней: скрипт ездит и к потребителям, где
    сводка бывает закоммичена. Производное, которого в общей ветке НЕТ, — с
    веткой публикации: спрашивать про него `HEAD` значит спрашивать про то,
    чего там не было никогда, и получать «не изменилось» всегда.

    ВЕТКА ПУБЛИКАЦИИ НЕДОСТУПНА — ЭТО ЖАЛОБА, А НЕ ТИШИНА. Считаем такое
    изменением: лишнее пробуждение публикации безвредно, она сама решает,
    коммитить ли, а пропущенное — та самая протухшая картинка. Ложный отказ
    дороже пропуска наоборот (051), и потому здесь громко, но не смертельно.
    """
    rc, _ = run(["git", "cat-file", "-e", f"HEAD:{name}"], root)
    if rc == 0:
        rc, out = run(["git", "show", f"HEAD:{name}"], root)
        return (out if rc == 0 else None), "HEAD", None

    rc, _ = run(["git", "rev-parse", "--verify", "--quiet", PUBLISHED_REF], root)
    if rc != 0:
        return None, PUBLISHED_REF, (
            f"{name}: в общей ветке файла нет, а ветка публикации "
            f"{PUBLISHED_REF} недоступна — сверить не с чем, считаю изменением")

    rc, out = run(["git", "show", f"{PUBLISHED_REF}:{name}"], root)
    # Файла на ветке публикации ещё нет — это первая публикация, а не отказ.
    return (out if rc == 0 else None), PUBLISHED_REF, None


def совпало_без_летучего(было: str, стало: str, name: str) -> bool:
    """Отличие свелось к полю, которое меняется само по себе.

    Дата последнего чтения меняется каждым прогоном независимо от данных. Файл
    целиком сравнивать нельзя: пересборка заводила бы изменение КАЖДЫЙ ДЕНЬ,
    ничего при этом не меняя, и такие изменения научились бы пролистывать не
    глядя (051) — то есть механизм починил бы свежесть способом, который её
    ломает.

    ГРАНИЦА. Работает только по JSON и только по верхнему уровню документа и
    записи потребителя. Нечитаемое сравнить нечем, и такое считается
    ОТЛИЧИЕМ: промолчать о непонятном — худший из двух исходов.
    """
    # ТЕКСТ СРАВНИВАЕТСЯ ПЕРВЫМ, И ЭТО НЕ ОПТИМИЗАЦИЯ. Раньше разбор JSON шёл
    # после git, который уже установил отличие; теперь он ПЕРВИЧЕН, и на
    # нечитаемом содержимом («исходное\n» в наборе самопроверки) отвечал
    # «отличается» про два одинаковых файла. Поймано самопроверкой, а не глазом.
    if было == стало:
        return True
    if not name.endswith(".json"):
        return False
    try:
        was = json.loads(было)
        now = json.loads(стало)
    except ValueError:
        return False
    for doc in (was, now):
        # ДВА УРОВНЯ, И ВТОРОЙ СТОИЛ ЦИКЛА. Летучее поле есть и внутри записи
        # потребителя (дата чтения), и на верхнем уровне документа (время
        # сборки). Первый уровень снимался с самого начала, второй появился
        # вместе с `generated_at` — и пересборка немедленно завела два
        # изменения подряд, в каждом одна строка со временем. Слияние такого
        # изменения — снова толчок в общую ветку, то есть цикл сам себя кормит.
        for key in VOLATILE_TOP:
            doc.pop(key, None)
        for entry in doc.get("consumers", []):
            for key in VOLATILE:
                entry.pop(key, None)
    return was == now


def differ(root: Path) -> tuple[list[str] | None, str, list[str]]:
    """Производные, отличающиеся от того, что ОПУБЛИКОВАНО. И жалобы по пути.

    Не «что изменил этот запуск». Разница видна на втором запуске подряд:
    первый пересобрал и отличается от опубликованного, второй ничего не менял
    — и сказал бы «обновлять нечего» при свежих производных на диске.

    Сравнивается СОДЕРЖИМОЕ, а не отчёт git о дереве. Отчёт о дереве молчит
    про игнорируемые файлы, и на нём механизм и ослеп (#492).
    """
    вышло: list[str] = []
    жалобы: list[str] = []
    for name in DERIVED:
        путь = root / name
        if not путь.exists():
            continue                    # сборщик его не делает — не наш предмет
        try:
            стало = путь.read_text(encoding="utf-8")
        except OSError as e:
            жалобы.append(f"{name}: не прочитан с диска — {e}")
            вышло.append(name)
            continue
        было, откуда, беда = опубликовано(root, name)
        if беда:
            жалобы.append(беда)
        if было is None or not совпало_без_летучего(было, стало, name):
            вышло.append(name)
    return sorted(вышло), "", жалобы


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

    touched, _, жалобы = differ(root)
    # ЖАЛОБА ЕДЕТ ВМЕСТЕ С ИСХОДОМ, А НЕ ВМЕСТО НЕГО. Недоступная ветка
    # публикации не отказ: она названа вслух и считается изменением (051).
    problems.extend(жалобы)
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
    # сводка в непустом репозитории приезжает именно так. Раньше предметом
    # этого случая была картинка витрины — она ушла из набора вместе с уходом
    # из дерева общей ветки (правило 160), и случай переехал на сводку.
    d = repo("from pathlib import Path\n"
             "Path('export/where.md').write_text('новая\\n', encoding='utf-8')\n")
    (d / "export/where.md").unlink()
    run(["git", "commit", "-qam", "сводки не было"], d)
    rc, names, _ = refresh(d)
    if rc != 1 or names != ["export/where.md"]:
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

    # ТО ЖЕ НА ВЕРХНЕМ УРОВНЕ, И ЭТО СТОИЛО ЦИКЛА. Отметка времени сборки лежит
    # не внутри записи потребителя, а над ней; первая редакция снимала только
    # внутренний уровень. 3 сентября пересборка стала заводить изменение на
    # каждый толчок в общую ветку — слияние рождало новое время, новое время
    # рождало слияние (#304, #305, в каждом одна строка).
    d = repo("import json, pathlib\n"
             "p = pathlib.Path('export/where.json')\n"
             "d = json.loads(p.read_text(encoding='utf-8'))\n"
             "d['generated_at'] = 'завтра'\n"
             "p.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')\n",
             json_seed=True)
    rc, names, _ = refresh(d)
    if rc != 0 or names:
        bad.append(f"одно время сборки обязано дать 0, дало {rc} {names}")

    # ...и обратная сторона: данные рядом с новым временем — изменение (140).
    d = repo("import json, pathlib\n"
             "p = pathlib.Path('export/where.json')\n"
             "d = json.loads(p.read_text(encoding='utf-8'))\n"
             "d['generated_at'] = 'завтра'\n"
             "d['consumers'][0]['answered'] = 99\n"
             "p.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')\n",
             json_seed=True)
    rc, names, _ = refresh(d)
    if rc != 1 or names != ["export/where.json"]:
        bad.append(f"данные рядом со временем обязаны дать 1, дали {rc} {names}")

    # ── #492: ПРОИЗВОДНОЕ ВНЕ ОБЩЕЙ ВЕТКИ. Ради этой границы всё и правлено.
    #
    # С 4 сентября сводка живёт на ветке публикации, а в общей ветке её нет и
    # она в `.gitignore`. Прежний разбор спрашивал про неё `git status`, тот
    # игнорируемых не показывает — и ответ «не изменилось» приходил ВСЕГДА.
    # Отказ бесшумный: код 0, зелёный. Проверяется обеими сторонами (140).
    def вне_общей(опубликованное: str, на_диске: str, с_веткой: bool = True) -> Path:
        d = Path(tempfile.mkdtemp())
        run(["git", "init", "-q"], d)
        run(["git", "config", "user.email", "s@e"], d)
        run(["git", "config", "user.name", "s"], d)
        (d / "scripts").mkdir()
        (d / "export").mkdir()
        for script, _ in BUILDERS:
            (d / script).write_text("pass\n", encoding="utf-8")
        for name in DERIVED:
            (d / name).write_text(опубликованное, encoding="utf-8")
        run(["git", "add", "-A"], d)
        run(["git", "commit", "-qm", "сводка ещё в общей ветке"], d)
        if с_веткой:
            run(["git", "branch", "публикация"], d)
        # ...и уходит из неё, как это сделало #330.
        run(["git", "rm", "-q", "--cached", *DERIVED], d)
        (d / ".gitignore").write_text("\n".join(DERIVED) + "\n", encoding="utf-8")
        run(["git", "add", "-A"], d)
        run(["git", "commit", "-qm", "сводка ушла на ветку публикации"], d)
        for name in DERIVED:
            (d / name).write_text(на_диске, encoding="utf-8")
        return d

    global PUBLISHED_REF
    прежняя_ветка = PUBLISHED_REF
    PUBLISHED_REF = "публикация"
    try:
        # Опубликованное отличается от пересобранного — это работа.
        rc, names, _ = refresh(вне_общей("опубликовано\n", "пересобрано\n"))
        if rc != 1 or names != sorted(DERIVED):
            bad.append(f"игнорируемое производное, отличное от опубликованного, "
                       f"обязано дать 1 и оба имени, дало {rc} {names}")

        # ...и обратная сторона: совпало — значит будить публикацию незачем.
        rc, names, _ = refresh(вне_общей("одно и то же\n", "одно и то же\n"))
        if rc != 0 or names:
            bad.append(f"игнорируемое производное, равное опубликованному, "
                       f"обязано дать 0, дало {rc} {names}")

        # Ветки публикации нет — считаем изменением и ГОВОРИМ об этом (039, 051).
        rc, names, problems = refresh(
            вне_общей("всё равно\n", "всё равно\n", с_веткой=False))
        if rc != 1 or not any("недоступна" in p for p in problems):
            bad.append(f"недоступная ветка публикации обязана дать 1 и жалобу, "
                       f"дала {rc} {problems}")
    finally:
        PUBLISHED_REF = прежняя_ветка

    for b in bad:
        print(f"  ✗ {b}", file=sys.stderr)
    print(f"самопроверка обновления производных: случаев 16, провалов {len(bad)}",
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
        print(f"обновление производных НЕ отработало: смотрите {DERIVED} — "
              "это чинит человек", file=sys.stderr)
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
