#!/usr/bin/env python3
"""Прогоняет гейты по предмету, который они обязаны отвергнуть — и пропустить.

Критик метода: отвечает не про каталог, а про то, как его проверяют. Зелёный
прогон на хорошем входе подтверждает, что гейт запускается, — и ничего больше.
Гейт, который всегда возвращает ноль, проходит такую проверку идеально
(правила 140, 097).

Набор двусторонний, потому что ошибок у проверяющего две. Предмет, обязанный
быть отвергнутым, ловит ложное «прошло». Предмет, обязанный пройти, ловит
ложный отказ — и его не видно ничем другим: в конвейере без человека ложный
отказ выглядит как обычная краснота на верном изменении, жаловаться некому,
а окно чинит запись под проверку.

Предмет подделывается нарочно, а не ждётся из жизни: ждать настоящего нарушения
значит проверять гейт тогда, когда он уже не сработал.

Наборы:
  атрибуция      — подписи коммитов против согласованного списка;
  полнота записи — содержание разделов правила;
  сборка указателя — форма записи и разбор следа (правило 141).

Исходы:
  0 — гейт ведёт себя как объявлено;
  1 — расхождение: пропустил обязательное к отказу или отверг законное;
  2 — проверка не отработала.

Реализует правила каталога:
  039 — три исхода объявлены и прогоняются самопроверкой, а не подразумеваются;
  045 — исход «не отработала» печатается громко; тихого запасного пути нет;
  067 — уборка после сбоя не превращает сбой в успех: код возврата переживает её;
  072 — у каждого набора и причина, и факт: подделка, которую гейт обязан отвергнуть, и предмет, который обязан пройти;
  109 — терминальный статус обязателен — 0, 1 или 2, и третий не растворяется во втором;
  140 — это и есть его предмет: гейт проверяется тем, что он обязан отвергнуть;
  141 — маркер сверяется целиком — набор «сборка указателя» гоняет маркер и его расширение отдельными случаями;
  127 — маркер числа прогоняется с обеих сторон: на месте — переписывается, пропал — находка;
  145 — механизм, объявивший несколько исходов, прогоняется по каждому;
  150 — случай спрашивает решение гейта, а не повторяет его условие;
  043 — пометка «Заменено» прогоняется подделкой с обеих сторон: номер
        читается, проза вместо номера пометкой не считается.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

#: Сборка указателя проверяется вызовом функций, а не запуском: у неё нет ключа
#: «работай в другом корне», а заводить его ради проверки — менять предмет под
#: проверку. Байт-код при этом писать запрещено: производный файл в репозитории
#: уже стоил окну хода (задача #70, правило 125).
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "check_attribution.py"

TRAILER_OK = "Co-Authored-By: Claude <noreply@anthropic.com>"
TRAILER_STRANGER = "Co-Authored-By: Кто-то Посторонний <nobody@example.com>"
SESSION = "Claude-Session: https://example.invalid/session"

#: Подпись агента в поле АВТОРА — то, из чего squash делает бота в общей
#: ветке. Предмет подделывается именно ею, а не похожей на неё строкой.
AUTHOR_AGENT = "Claude <noreply@anthropic.com>"
AUTHOR_HUMAN = "Человек Подделкин <human@example.invalid>"

#: Что гейт обязан сделать с каждым предметом. Ожидание записано ЗДЕСЬ, рядом с
#: подделкой, а не в прозе свода: строку в своде никто не исполняет.
#: Пятое поле — автор коммита; None означает подпись сборщика подделки.
CASES = [
    ("подпись из согласованного списка", [TRAILER_OK, SESSION], 0,
     "законный коммит обязан проходить", None),
    ("подпись вне списка", [TRAILER_STRANGER], 1,
     "чужое имя — то, ради чего список и заведён", None),
    ("след сессии без соавторства", [SESSION], 1,
     "половина атрибуции хуже отсутствующей: выглядит подписанным", None),
    ("без трейлеров вовсе", [], 0,
     "считается и печатается числом, но не отвергается — "
     "требование трейлеров это договорённость про агентские коммиты, "
     "а не запрет для человека со стороны", None),
    ("агент стоит АВТОРОМ", [TRAILER_OK, SESSION], 1,
     "squash берёт автора из коммитов ветки: в общей ветке окажется бот, "
     "и переписать это нечем (правило 131)", AUTHOR_AGENT),
    ("человек автором, агент соавтором", [TRAILER_OK, SESSION], 0,
     "это и есть требуемая форма — отвергать её значило бы запретить "
     "единственный законный способ подписи", AUTHOR_HUMAN),
]


AUDIT_GATE = ROOT / "scripts" / "audit_catalogue.py"

#: Законная запись, с которой снимается каждая подделка. Порча делается ЗАМЕНОЙ
#: куска: так видно, чем именно случай отличается от проходящего, — а список
#: «что должно отвергаться» стоит рядом с предметом, а не в прозе свода.
GOOD = {
    "ru": """# Заголовок подделки

**Область.** гейты

**Правило.** Утверждение подделки в одну строку.

## Инцидент

Что сломалось.

## Почему

Механизм поломки.

## Применимость

**Работает** там-то.

**Не работает** там-то.

## След

ArtVsMark/claude-code-playbook#1
""",
    "en": """# Fixture heading

**Area.** gates

**The rule.** The fixture claim in one line.

## The incident

What broke.

## Why

The mechanism.

## Where it applies

**Works** here.

**Does not work** there.

## Trace

ArtVsMark/claude-code-playbook#1
""",
}

#: Порча: (язык, что заменить, на что). Пусто — подделка остаётся законной.
AUDIT_CASES = [
    ("полная запись", [], 0,
     "законная запись обязана проходить, иначе гейт заставит править корпус "
     "под себя"),
    ("«Применимость» без границы", [("ru", "**Не работает** там-то.\n\n", "")], 1,
     "без границы каталог копируют целиком, включая заведомо чужое — "
     "ради этого раздел и заведён"),
    ("след прозой", [("ru", "ArtVsMark/claude-code-playbook#1",
                      "Этот каталог, кажется.")], 1,
     "след, не ведущий ни в задачу, ни в потребителя, за месяц становится "
     "«кто-то говорил, что так лучше»"),
    ("нет утверждения правила", [("en", "**The rule.** The fixture claim in "
                                  "one line.\n\n", "")], 1,
     "заголовок называет тему, утверждение говорит, что делать; без него "
     "запись — заметка"),
    ("деревья разошлись по числу разделов",
     [("en", "## Why\n", "## Why\n\nProse.\n\n## An extra section\n")], 1,
     "разное число разделов — расхождение деревьев, а не стилистика"),
    ("«## Следствие» вместо «## След»",
     [("ru", "## След\n", "## Следствие второго порядка\n")], 0,
     "ОТСУТСТВИЕ раздела — предмет сборки указателя, а не этого гейта; здесь "
     "проверено, что заголовок сверяется целой строкой и «Следствие» не "
     "засчитывается за «След» (задача #69)"),
    ("заготовки правила нет", [("!template", "", "")], 1,
     "заготовку берут другие проекты: разъехавшись, она разносит расхождение "
     "дальше, и заметят это они, а не мы"),
    ("нет реестра потребителей", [("!", "consumers", "")], 2,
     "нечитаемый вход — третий исход, а не «всё хорошо» (правило 075)"),
]


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def build_catalogue(root: Path, spoil: list[tuple[str, str, str]]) -> str | None:
    """Собирает каталог из одного правила и портит его по описанию случая."""
    text = dict(GOOD)
    drop_consumers = False
    for lang, old, new in spoil:
        if lang == "!":
            drop_consumers = True
            continue
        if lang == "!template":
            continue
        if old not in text[lang]:
            return f"порча не нашла кусок {old!r} в дереве {lang}"
        text[lang] = text[lang].replace(old, new)

    for lang in ("ru", "en"):
        tree = root / "rules" / lang
        tree.mkdir(parents=True, exist_ok=True)
        (tree / "001-fixture-rule.md").write_text(text[lang], encoding="utf-8")

    # Заготовку каталог требует от себя же: гейт полноты сверяет её с каноном
    # разделов. В подделке она законная, а случай «заготовки нет» — отдельный.
    if "!template" not in {lang for lang, _, _ in spoil}:
        tpl = root / "templates"
        tpl.mkdir(parents=True, exist_ok=True)
        (tpl / "rule-template.md").write_text(GOOD["ru"], encoding="utf-8")

    if not drop_consumers:
        registry = root / ".rules"
        registry.mkdir(parents=True, exist_ok=True)
        (registry / "consumers.json").write_text(
            '{"schema": "1.0", "consumers": '
            '[{"repo": "ArtVsMark/claude-code-playbook"}]}\n', encoding="utf-8")
    return None


def build(repo: Path) -> str | None:
    """Собирает подделку: по коммиту на случай. Возвращает ошибку или None."""
    steps = [
        ("git", "init", "-q", "-b", "main"),
        ("git", "config", "user.email", "fixture@example.invalid"),
        ("git", "config", "user.name", "Подделка"),
    ]
    for step in steps:
        done = run(*step, cwd=repo)
        if done.returncode != 0:
            return f"{' '.join(step)} — {done.stderr.strip()}"

    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    run("git", "add", "seed.txt", cwd=repo)
    done = run("git", "commit", "-q", "-m", "основание, вне проверяемого диапазона",
               cwd=repo)
    if done.returncode != 0:
        return f"основание не создано — {done.stderr.strip()}"

    for i, (name, trailers, _, _, author) in enumerate(CASES):
        (repo / f"case{i}.txt").write_text(f"{name}\n", encoding="utf-8")
        run("git", "add", f"case{i}.txt", cwd=repo)
        message = f"случай: {name}"
        if trailers:
            message += "\n\n" + "\n".join(trailers)
        extra = ("--author", author) if author else ()
        done = run("git", "commit", "-q", *extra, "-m", message, cwd=repo)
        if done.returncode != 0:
            return f"коммит случая {name!r} не создан — {done.stderr.strip()}"
    return None


def suite_attribution() -> tuple[list[str], int]:
    """Гейт атрибуции. Возвращает расхождения и код инфраструктурного отказа."""
    if not GATE.exists():
        print(f"проверка не отработала: {GATE.relative_to(ROOT)} не найден",
              file=sys.stderr)
        return [], 2

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "fixture"
        repo.mkdir()
        err = build(repo)
        if err:
            print(f"проверка не отработала: подделка не собралась — {err}",
                  file=sys.stderr)
            return [], 2

        # Каждый случай проверяется по одному коммиту: иначе один отказ
        # закрывал бы собой все остальные, и «отверг» перестало бы означать
        # «отверг именно это».
        base = run("git", "rev-list", "--max-parents=0", "HEAD", cwd=repo).stdout.strip()
        log = run("git", "log", "--format=%H", "--reverse", cwd=repo).stdout.split()
        if len(log) != len(CASES) + 1:
            print("проверка не отработала: подделка собралась не той формы",
                  file=sys.stderr)
            return [], 2

        findings: list[str] = []
        for i, (name, _, want, why, _author) in enumerate(CASES):
            rng = f"{log[i]}..{log[i + 1]}"
            done = run(sys.executable, str(GATE), "--repo", str(repo),
                       "--authors", str(ROOT / ".github" / "authors.txt"),
                       "--baseline", "", "--range", rng, cwd=ROOT)
            got = done.returncode
            mark = "ок" if got == want else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалось {want}, получено {got}")
            if got != want:
                findings.append(
                    f"{name}: ожидалось {want}, получено {got}. {why}\n"
                    f"        вывод гейта: {(done.stdout or done.stderr).strip()[:160]}")

    return findings, 0


def suite_audit() -> tuple[list[str], int]:
    """Гейт содержательной полноты записи. Подделка — каталог из одного правила.

    Каждый случай получает СВОЙ корень: иначе один отказ закрывал бы собой
    остальные, и «отверг» перестало бы означать «отверг именно это» — та же
    причина, по которой атрибуция проверяется по одному коммиту.
    """
    if not AUDIT_GATE.exists():
        print(f"проверка не отработала: {AUDIT_GATE.relative_to(ROOT)} не найден",
              file=sys.stderr)
        return [], 2

    findings: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, spoil, want, why) in enumerate(AUDIT_CASES):
            root = Path(tmp) / f"case{i}"
            err = build_catalogue(root, spoil)
            if err:
                print(f"проверка не отработала: подделка {name!r} не собралась "
                      f"— {err}", file=sys.stderr)
                return [], 2
            done = run(sys.executable, str(AUDIT_GATE), "--root", str(root),
                       cwd=ROOT)
            got = done.returncode
            mark = "ок" if got == want else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалось {want}, получено {got}")
            if got != want:
                findings.append(
                    f"{name}: ожидалось {want}, получено {got}. {why}\n"
                    f"        вывод гейта: "
                    f"{(done.stdout or done.stderr).strip()[:160]}")
    return findings, 0


#: Заголовок, начинающийся с обязательного. Живёт в 002 не для красоты — там
#: «Следствие второго порядка» стоит рядом со «Следом», и именно на этой паре
#: сборка указателя молча зеленела (правило 141).
COLLIDING = "## Следствие второго порядка"
#: Три случая по форме записи плюс один по разбору следа.
SHAPE_COUNT = 4


def suite_shape() -> tuple[list[str], int]:
    """Сборка указателя: форма записи и разбор следа.

    Набор двусторонний. Предмет, который обязаны отвергнуть, ловит ложное
    «прошло»; предмет, который обязаны пропустить, ловит ложный отказ — и
    вторую половину видно только на таком наборе (правила 097, 140).
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import build_rules_index as index
    except ImportError as e:
        print(f"проверка не отработала: сборка указателя не импортируется — {e}",
              file=sys.stderr)
        return [], 2

    good = ("# Заголовок\n\n**Область.** гейты\n\n**Правило.** Утверждение.\n\n"
            "## Инцидент\n\nЧто сломалось.\n\n## Почему\n\nМеханизм.\n\n"
            "## Применимость\n\n**Не работает** там-то.\n\n"
            "## След\n\nArtVsMark/claude-code-playbook#1\n")

    cases = [
        ("полная запись проходит", good, False,
         "ложный отказ на законной записи заставит править корпус под гейт"),
        (f"«{COLLIDING}» вместо «## След»",
         good.replace("## След\n", COLLIDING + "\n"), True,
         "обязательного раздела нет, а заголовок начинается с него — "
         "сравнение началом строки давало здесь зелёное"),
        ("нет раздела «Почему»", good.replace("## Почему\n\nМеханизм.\n\n", ""),
         True, "без «Почему» запись становится предпочтением, а не правилом"),
    ]

    findings: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, text, must_find, why) in enumerate(cases):
            path = Path(tmp) / f"{i:03d}-fixture.md"
            path.write_text(text, encoding="utf-8")
            got = bool(index.check_shape({f"{i:03d}": {"ru": path}}))
            mark = "ок" if got == must_find else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалась находка {must_find}, "
                  f"получена {got}")
            if got != must_find:
                findings.append(f"{name}: ожидалась находка {must_find}, "
                                f"получена {got}. {why}")

        # Второе следствие той же ошибки: разбор начинался от «Следствия», то
        # есть прихватывал чужой кусок текста. Предмет — задача, названная ДО
        # настоящего следа: попасть в разбор она не имеет права.
        path = Path(tmp) / "999-trail.md"
        path.write_text(
            good.replace("## Почему\n\nМеханизм.\n",
                         f"{COLLIDING}\n\nArtVsMark/Stepik-Python-Grader#999\n"),
            encoding="utf-8")
        trails, err = index.trails_of(
            path, "ru", {"ArtVsMark/claude-code-playbook",
                         "ArtVsMark/Stepik-Python-Grader"})
        issues = [t["issue"] for t in trails]
        ok = err is None and issues == ["1"]
        print(f"  {'ок' if ok else 'РАСХОЖДЕНИЕ'}: след читается от «## След», "
              f"а не от «{COLLIDING}» — получено {issues or err}")
        if not ok:
            findings.append(
                "разбор следа начался не с того заголовка: получено "
                f"{issues or err}, ожидалось ['1']. Задача, названная выше "
                "настоящего следа, попадать в разбор не имеет права")
    return findings, 0


#: Сборщик указателя — 26 функций, из которых набор трогал шесть. Держал
#: остальные ОДИН ЗЕЛЁНЫЙ ПРОГОН НА ЖИВОМ КОРПУСЕ, то есть ровно тот способ
#: подтверждения, против которого 146: корпус здоров, и зелёное говорит об этом,
#: а не о верности проверок. Проверить проверку можно только подделкой (140).
#:
#: Взято по ПРЕДМЕТУ, а не по проценту: то, чья поломка тиха. Расхождение
#: деревьев, область вне словаря, происхождение записи и необязательные ключи
#: выгрузки — каждое ломается молча и каждое стоит корпуса.
INDEX_COUNT = 8


def suite_index() -> tuple[list[str], int]:
    """Сборщик указателя: пары деревьев, словарь областей, происхождение, ключи."""
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import build_rules_index as index
    except ImportError as e:
        print(f"проверка не отработала: сборка указателя не импортируется — {e}",
              file=sys.stderr)
        return [], 2

    findings: list[str] = []

    def случай(имя, вышло, ждём, почему):
        ок = вышло == ждём
        print(f"  {'ок' if ок else 'РАСХОЖДЕНИЕ'}: {имя} — ожидалось {ждём!r}, "
              f"получено {вышло!r}")
        if not ок:
            findings.append(f"{имя}: ожидалось {ждём!r}, получено {вышло!r}. {почему}")

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)

        # ── пары деревьев: правило на одном языке ──────────────────────────
        случай("правило только в ru — находка",
               bool(index.check_pairs({"001": {"ru": d / "a.md"}})), True,
               "запись на одном языке и есть та поломка, ради которой "
               "указатель сделан единым")
        случай("правило в обоих деревьях — не находка",
               bool(index.check_pairs({"001": {"ru": d / "ru" / "a.md",
                                               "en": d / "en" / "a.md"}})), False,
               "ложный отказ здесь заставит заводить лишние файлы")

        # ── область записи: закрытый словарь ───────────────────────────────
        def пара(область_ru, область_en):
            (d / "ru").mkdir(exist_ok=True)
            (d / "en").mkdir(exist_ok=True)
            for lang, значение, метка in (("ru", область_ru, "**Область.**"),
                                          ("en", область_en, "**Area.**")):
                (d / lang / "z.md").write_text(
                    f"# Заголовок\n\n{метка} {значение}\n", encoding="utf-8")
            return {"001": {"ru": d / "ru" / "z.md", "en": d / "en" / "z.md"}}

        случай("область вне словаря — находка",
               bool(index.check_areas(пара("выдуманная", "invented"))[1]), True,
               "опечатка иначе заводит новую область молча, и рядом живут "
               "«интерфейс» и «интерфейсы» (099)")
        случай("область из словаря — не находка",
               bool(index.check_areas(пара("гейты", "gates"))[1]), False,
               "ложный отказ на законной области заставит править словарь "
               "под гейт")

        # ── происхождение: первый названный ПОТРЕБИТЕЛЬ, а не первый токен ─
        известные = {"ArtVsMark/claude-code-playbook",
                     "ArtVsMark/Stepik-Python-Grader"}
        свой = d / "orig.md"
        свой.write_text(
            "# Заголовок\n\n## След\n\n`scripts/some_tool.py` — "
            "ArtVsMark/Stepik-Python-Grader#7\n", encoding="utf-8")
        случай("путь в кавычках происхождением не считается",
               index.origin_of(свой, "ru", известные),
               "ArtVsMark/Stepik-Python-Grader",
               "токен со слешем есть у любого пути; репозиторием считается "
               "только названный в реестре (068)")

        пусто = d / "noorig.md"
        пусто.write_text("# Заголовок\n\n## След\n\n`docs/x.md` § раздел\n",
                         encoding="utf-8")
        случай("следа без потребителя — происхождения нет",
               index.origin_of(пусто, "ru", известные), None,
               "выдуманное происхождение хуже отсутствующего: по нему считают "
               "метрику «кто наполняет каталог»")

        # ── маркер числа: пропал — сборка обязана упасть ───────────────────
        # ТРЕТЬЕ УСЛОВИЕ 127 И ЕСТЬ ВЕСЬ МЕХАНИЗМ. Маркер и сборка были и
        # раньше; без падения при пропаже маркера это ручное число с лишним
        # шагом — стереть маркер, и сборка молча оставит витрину со старым.
        с_маркером = d / "showcase.md"
        с_маркером.write_text("Правил: <!--m:rules-->1<!--/m:rules-->\n",
                              encoding="utf-8")
        случай("маркер на месте — число переписывается",
               index.marked(с_маркером, 154)[0].strip(),
               "Правил: <!--m:rules-->154<!--/m:rules-->",
               "сборка обязана подставить в маркер своё число, а не оставить "
               "прежнее")

        без_маркера = d / "plain.md"
        без_маркера.write_text("Правил: 154\n", encoding="utf-8")
        случай("маркера нет — это находка, а не тихий пропуск",
               index.marked(без_маркера, 154)[1] is not None, True,
               "число, которое некому переписать, устареет молча, а витрина "
               "будет выглядеть свежей (127)")

        # ── пометка «заменено»: номер, а не проза ──────────────────────────
        зам = d / "sup.md"
        зам.write_text("# Заголовок\n\n**Заменено.** 154\n\n## След\n\nx\n",
                       encoding="utf-8")
        случай("пометка «заменено» читается номером",
               index.superseded_of(зам, "ru"), "154",
               "без номера пометка не разрешается, а ссылка в пустоту хуже "
               "её отсутствия")

        проза = d / "sup2.md"
        проза.write_text("# Заголовок\n\n**Заменено.** новой записью\n\n"
                         "## След\n\nx\n", encoding="utf-8")
        случай("пометка прозой пометкой не считается",
               index.superseded_of(проза, "ru"), None,
               "проза вместо номера — то же молчание, только выглядит ответом")

    return findings, 0


#: Режим первопредков — вторая половина гейта атрибуции, и до этого набора её
#: не проверял никто. Цена: правка соседнего режима сломала разбор здесь,
#: все восемь гейтов остались зелёными, а общая ветка покраснела после слияния.
FIRST_PARENT_CASES = [
    ("вся история с атрибуцией", [True, True], None, 0,
     "законная история обязана проходить: ложный отказ здесь краснит общую "
     "ветку, где чинить уже нечего"),
    ("коммит без трейлеров в истории", [True, False], None, 1,
     "это и есть предмет проверки — иначе она бесполезна"),
    ("долг объявлен ключом --since", [False, True], 1, 0,
     "объявленный долг остаётся позади границы и краснить не должен: иначе "
     "объявить его невозможно (правило 114)"),
]


def suite_first_parents() -> tuple[list[str], int]:
    """Гейт атрибуции в режиме первопредков: обе стороны."""
    if not GATE.exists():
        print(f"проверка не отработала: {GATE.relative_to(ROOT)} не найден",
              file=sys.stderr)
        return [], 2

    findings: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, marks, since_at, want, why) in enumerate(FIRST_PARENT_CASES):
            repo = Path(tmp) / f"fp{i}"
            repo.mkdir()
            for step in (("git", "init", "-q", "-b", "main"),
                         ("git", "config", "user.email", "fixture@example.invalid"),
                         ("git", "config", "user.name", "Подделка")):
                if run(*step, cwd=repo).returncode != 0:
                    print(f"проверка не отработала: подделка {name!r} не собралась",
                          file=sys.stderr)
                    return [], 2
            shas: list[str] = []
            for j, signed in enumerate(marks):
                (repo / f"f{j}.txt").write_text(f"{j}\n", encoding="utf-8")
                run("git", "add", f"f{j}.txt", cwd=repo)
                msg = f"первопредок {j}"
                if signed:
                    msg += f"\n\n{TRAILER_OK}\n{SESSION}"
                if run("git", "commit", "-q", "-m", msg, cwd=repo).returncode != 0:
                    print(f"проверка не отработала: коммит подделки {name!r} не создан",
                          file=sys.stderr)
                    return [], 2
                shas.append(run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip())

            args = [sys.executable, str(GATE), "--repo", str(repo),
                    "--authors", str(ROOT / ".github" / "authors.txt"),
                    "--first-parents", "--ref", "HEAD"]
            if since_at is not None:
                args += ["--since", shas[since_at - 1]]
            done = run(*args, cwd=ROOT)
            got = done.returncode
            mark = "ок" if got == want else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалось {want}, получено {got}")
            if got != want:
                findings.append(
                    f"{name}: ожидалось {want}, получено {got}. {why}\n"
                    f"        вывод гейта: "
                    f"{(done.stdout or done.stderr).strip()[:160]}")
    return findings, 0


CHARTER_GATE = ROOT / "scripts" / "check_charter.py"

#: Подделка свода: таблица гейтов, список для участника и шаги конвейера.
#: Порча — снятие одной строки: так видно, чем случай отличается от законного.
CHARTER_CASES = [
    ("свод, участник и конвейер совпадают", None, 0,
     "законное состояние обязано проходить: ложный отказ здесь заставит "
     "править свод под гейт"),
    ("гейт есть в конвейере, но не в своде", "charter", 1,
     "окно читает свод целиком при старте — проверка, о которой там не "
     "сказано, остановит его без объяснения"),
    ("гейт обещан участнику, но не стоит в конвейере", "onramp-extra", 1,
     "обещание, которое никто не исполняет: новичок прогонит и решит, "
     "что защищён"),
]


def suite_charter() -> tuple[list[str], int]:
    """Гейт сходимости свода с конвейером: обе стороны."""
    if not CHARTER_GATE.exists():
        print(f"проверка не отработала: {CHARTER_GATE.relative_to(ROOT)} не найден",
              file=sys.stderr)
        return [], 2

    charter = ("# Подделка\n\n## \U0001F6E1 Гейты\n\n"
               "| Команда | Что держит |\n|---|---|\n"
               "| `python scripts/one.py` | первое |\n"
               "| `python scripts/two.py` | второе |\n\n## Дальше\n\nпроза\n")
    onramp = ("# Участнику\n\n```\npython scripts/one.py\n"
              "python scripts/two.py\n```\n")
    pipeline = ("name: ci\njobs:\n  x:\n    steps:\n"
                "      - run: python scripts/one.py\n"
                "      - run: python scripts/two.py\n")

    findings: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, spoil, want, why) in enumerate(CHARTER_CASES):
            root = Path(tmp) / f"ch{i}"
            (root / ".github" / "workflows").mkdir(parents=True)
            c, o = charter, onramp
            if spoil == "charter":
                c = c.replace("| `python scripts/two.py` | второе |\n", "")
            elif spoil == "onramp-extra":
                o = o.replace("python scripts/two.py\n",
                              "python scripts/two.py\npython scripts/three.py\n")
            # Таблица гейтов живёт в ЯДРЕ (задача #198), а надстройка обязана
            # на него сослаться и своей таблицы не заводить. Подделка повторяет
            # этот раскол: иначе набор проверял бы устройство, которого больше
            # нет, и краснел бы на верной работе.
            (root / "AGENTS.md").write_text(c, encoding="utf-8")
            (root / "CLAUDE.md").write_text(
                "# Надстройка\n\nЯдро — [AGENTS.md](AGENTS.md).\n",
                encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text(o, encoding="utf-8")
            (root / ".github" / "workflows" / "ci.yml").write_text(
                pipeline, encoding="utf-8")

            done = run(sys.executable, str(CHARTER_GATE), "--root", str(root),
                       cwd=ROOT)
            got = done.returncode
            mark = "ок" if got == want else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалось {want}, получено {got}")
            if got != want:
                findings.append(
                    f"{name}: ожидалось {want}, получено {got}. {why}\n"
                    f"        вывод гейта: "
                    f"{(done.stdout or done.stderr).strip()[:160]}")
    return findings, 0


NEAR_GATE = ROOT / "scripts" / "check_duplicates.py"

#: Подделка каталога для гейта соседей: три старых правила и одно новое.
#: Старые дают верхушку, новое обязано на неё ответить. Тексты разные, но
#: одного жанра — иначе близость выродится в ноль и случай перестанет быть
#: похожим на живой.
NEAR_RULES = {
    "001": "учётные данные подменяются на записи, и автором становится приложение",
    "002": "подпись записи это свойство окна, и узнаётся она пробой, а не доверием",
    "003": "атрибуция сверяется в конечной истории, а не в коммите ветки",
}
#: Новое правило: номер больше baseline подделки, значит ответ обязателен.
NEAR_NEW = "145"

#: (имя, порча ответа, ожидаемый код, зачем случай нужен)
NEAR_CASES = [
    ("ответ о соседях на месте", None, 0,
     "законное состояние обязано проходить: ложный отказ здесь заставит "
     "писать отписки, а не читать соседей"),
    ("правило новее baseline без ответа", "drop", 1,
     "ровно инцидент #91: запись появилась, вопроса о соседях никто не задал"),
    ("верхний сосед не рассмотрен", "partial", 1,
     "ответ по двум из трёх — это не ответ: пропущенный и окажется тем самым"),
    ("вердикт-отписка", "terse", 1,
     "«не дубль» под заголовком структурно неотличимо от разбора; гейт "
     "полноты записи ловит то же самое в другом месте (128)"),
    ("ответ по несуществующему правилу", "ghost", 1,
     "номер опечатан либо запись удалена — иначе ответы станут вторым "
     "источником правды о составе каталога"),
    ("правило старше baseline без ответа", "old", 0,
     "долг объявлен, а не забыт: краснеть на 144 записях, написанных до "
     "вопроса, значит требовать 144 отписки за присест (051)"),
]


def suite_near() -> tuple[list[str], int]:
    """Гейт «вопрос о соседях задан»: обе стороны."""
    if not NEAR_GATE.exists():
        print(f"проверка не отработала: {NEAR_GATE.relative_to(ROOT)} не найден",
              file=sys.stderr)
        return [], 2

    def rule(num: str, claim: str) -> str:
        return (f"# Подделка {num}\n\n**Область.** гейты\n\n"
                f"**Правило.** {claim}.\n\n## Инцидент\n\n"
                f"Механизм сломался так, что {claim}, и это стоило прогона.\n\n"
                f"## Почему\n\n{claim} — свойство площадки, а не намерения.\n\n"
                f"## Применимость\n\n**Работает** там, где {claim}.\n\n"
                f"**Не работает** там, где предмета нет.\n\n"
                f"## След\n\nArtVsMark/claude-code-playbook#1\n")

    findings: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, spoil, want, why) in enumerate(NEAR_CASES):
            root = Path(tmp) / f"nb{i}"
            tree = root / "rules" / "ru"
            tree.mkdir(parents=True)
            for num, claim in NEAR_RULES.items():
                (tree / f"{num}-fixture.md").write_text(rule(num, claim),
                                                        encoding="utf-8")
            new_num = "144" if spoil == "old" else NEAR_NEW
            (tree / f"{new_num}-fresh.md").write_text(
                rule(new_num, "учётные данные подменяются, и автором "
                              "становится приложение"), encoding="utf-8")

            verdict = ("Предмет другой: соседи говорят про подпись записи, "
                       "эта запись — про порядок очереди.")
            answers: dict = {NEAR_NEW: {"considered": sorted(NEAR_RULES),
                                        "verdict": verdict}}
            if spoil == "drop" or spoil == "old":
                answers = {}
            elif spoil == "partial":
                answers[NEAR_NEW]["considered"] = ["001", "002"]
            elif spoil == "terse":
                answers[NEAR_NEW]["verdict"] = "не дубль"
            elif spoil == "ghost":
                answers["999"] = {"considered": ["001"], "verdict": verdict}

            registry = root / ".rules"
            registry.mkdir(parents=True)
            (registry / "neighbours.json").write_text(
                json.dumps({"baseline": 144, "answers": answers},
                           ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")

            done = run(sys.executable, str(NEAR_GATE), "--check",
                       "--root", str(root), cwd=ROOT)
            got = done.returncode
            mark = "ок" if got == want else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалось {want}, получено {got}")
            if got != want:
                findings.append(
                    f"{name}: ожидалось {want}, получено {got}. {why}\n"
                    f"        вывод гейта: "
                    f"{(done.stdout or done.stderr).strip()[:160]}")
    return findings, 0


#: Новый вход гейта атрибуции (задача #80): «коммит вовсе без атрибуции» —
#: находка или число. Пара двусторонняя по построению: умолчание ОБЯЗАНО
#: сохранять прежнее решение (правило 041 — два честных числа), включённый
#: ключ обязан отвергать. Односторонний набор здесь был бы бесполезен: он не
#: отличил бы «ключ работает» от «гейт стал строже для всех».
REQUIRE_CASES = [
    ("без атрибуции, ключ выключен", [], 0,
     "умолчание сохраняет решение 041: такие коммиты считаются и печатаются "
     "числом, а не отвергаются — иначе ключ сменил бы поведение всем"),
    ("без атрибуции, ключ включён", ["--require-coauthor"], 1,
     "ровно то, ради чего вход заведён: потребителю, у которого весь поток "
     "идёт через облачные окна, нужен отказ (#80)"),
]


def suite_require_coauthor() -> tuple[list[str], int]:
    """Вход «требовать соавторство»: обе стороны на одном предмете."""
    if not GATE.exists():
        print(f"проверка не отработала: {GATE.relative_to(ROOT)} не найден",
              file=sys.stderr)
        return [], 2

    findings: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "bare"
        repo.mkdir()
        for cmd in (("git", "init", "-q", "-b", "main"),
                    ("git", "config", "user.name", "Человек Подделкин"),
                    ("git", "config", "user.email", "human@example.invalid")):
            run(*cmd, cwd=repo)
        (repo / "f.txt").write_text("x", encoding="utf-8")
        run("git", "add", "-A", cwd=repo)
        # Коммит БЕЗ единого трейлера — тот самый предмет.
        run("git", "commit", "-q", "-m", "правка без атрибуции", cwd=repo)
        base = run("git", "rev-list", "--max-parents=0", "HEAD",
                   cwd=repo).stdout.strip()
        (repo / "f.txt").write_text("y", encoding="utf-8")
        run("git", "commit", "-qam", "вторая правка без атрибуции", cwd=repo)

        for name, extra, want, why in REQUIRE_CASES:
            done = run(sys.executable, str(GATE), "--repo", str(repo),
                       "--authors", str(ROOT / ".github" / "authors.txt"),
                       "--baseline", "", "--range", f"{base}..HEAD",
                       *extra, cwd=ROOT)
            got = done.returncode
            mark = "ок" if got == want else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалось {want}, получено {got}")
            if got != want:
                findings.append(
                    f"{name}: ожидалось {want}, получено {got}. {why}\n"
                    f"        вывод гейта: "
                    f"{(done.stdout or done.stderr).strip()[:160]}")
    return findings, 0


#: Режим `--near` объявляет три исхода, и прогонять надо все три (#83).
#: Он не гейт — красным не бывает; но «предмет не разобран» обязан отличаться
#: от «соседей нет», иначе окно примет отказ за пустой ответ (правило 039).
NEAR_SUBJECTS = [
    ("номер правила в дереве", "001", 0,
     "основная форма: у записи в корпусе соседи есть всегда"),
    ("черновик без номера, вне дерева", "@draft", 0,
     "ровно та форма, ради которой режим и нужен: спрашивают ДО того, как "
     "запись написана, а у ненаписанной нет ни номера, ни места в дереве"),
    ("предмет не разобран", "ни-номер-ни-файл", 2,
     "третий исход обязан отличаться от пустого ответа: «не отработала» и "
     "«соседей нет» — разные вещи (039)"),
]


def suite_near_subject() -> tuple[list[str], int]:
    """Режим `--near`: все три объявленных исхода, на живом корпусе."""
    if not NEAR_GATE.exists():
        print(f"проверка не отработала: {NEAR_GATE.relative_to(ROOT)} не найден",
              file=sys.stderr)
        return [], 2

    findings: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        draft = Path(tmp) / "draft.md"
        draft.write_text(
            "# Черновик подделки\n\n**Правило.** Учётные данные подменяются "
            "на записи, и автором становится приложение.\n", encoding="utf-8")
        for name, arg, want, why in NEAR_SUBJECTS:
            target = str(draft) if arg == "@draft" else arg
            done = run(sys.executable, str(NEAR_GATE), "--near", target,
                       cwd=ROOT)
            got = done.returncode
            mark = "ок" if got == want else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалось {want}, получено {got}")
            if got != want:
                findings.append(
                    f"{name}: ожидалось {want}, получено {got}. {why}\n"
                    f"        вывод: "
                    f"{(done.stdout or done.stderr).strip()[:160]}")
    return findings, 0


PROPOSALS_GATE = ROOT / "scripts" / "collect_proposals.py"

#: Вердикт каталога о правиле, приехавшем из проекта. Порча — подмена одного
#: поля: так видно, чем случай отличается от законного.
PROPOSAL_OK = {"status": "admitted", "rule": "001",
               "why": "принято под номером, который присвоил каталог"}

PROPOSAL_CASES = [
    ("вердикт цел", None, 0,
     "законный ответ обязан проходить: ложный отказ здесь заставит писать "
     "вердикты под гейт"),
    ("статус не из набора", "status", 1,
     "четвёртый статус означает, что отправитель и каталог понимают исход "
     "по-разному, а выглядит это как решение"),
    ("принято без номера", "no-rule", 1,
     "«принято» без номера — не решение: отправитель не узнает, чем стало "
     "его предложение"),
    ("номер назван, а правила нет", "ghost-rule", 1,
     "вердикт ссылается в пустоту; корпус — канон нумерации, а не вердикты"),
    ("отклонено без причины", "no-why", 1,
     "отказ без причины вернётся тем же предложением через месяц "
     "(правило 026)"),
    ("два предложения под одним номером", "dup-number", 1,
     "номера не переиспользуются: второе предложение потеряно молча"),
    ("вердикты не объект", "broken", 2,
     "нечитаемый вход — третий исход, а не «всё хорошо» (правило 075)"),
]


def suite_proposals() -> tuple[list[str], int]:
    """Гейт вердикта о правилах из проектов: обе стороны."""
    if not PROPOSALS_GATE.exists():
        print(f"проверка не отработала: "
              f"{PROPOSALS_GATE.relative_to(ROOT)} не найден", file=sys.stderr)
        return [], 2

    findings: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, spoil, want, why) in enumerate(PROPOSAL_CASES):
            root = Path(tmp) / f"pr{i}"
            (root / "rules" / "ru").mkdir(parents=True)
            (root / "rules" / "ru" / "001-fixture.md").write_text(
                "# Подделка\n", encoding="utf-8")
            (root / ".rules").mkdir(parents=True)

            v = dict(PROPOSAL_OK)
            verdicts = {"owner/repo:slug": v}
            if spoil == "status":
                v["status"] = "почти-принято"
            elif spoil == "no-rule":
                v.pop("rule")
            elif spoil == "ghost-rule":
                v["rule"] = "999"
            elif spoil == "no-why":
                verdicts = {"owner/repo:slug": {"status": "rejected",
                                                "why": "   "}}
            elif spoil == "dup-number":
                verdicts["owner/repo:other"] = dict(PROPOSAL_OK)

            doc = ({"verdicts": "не объект"} if spoil == "broken"
                   else {"schema": "1.0", "verdicts": verdicts})
            (root / ".rules" / "proposals.json").write_text(
                json.dumps(doc, ensure_ascii=False), encoding="utf-8")

            done = run(sys.executable, str(PROPOSALS_GATE), "--check",
                       "--root", str(root), cwd=ROOT)
            got = done.returncode
            mark = "ок" if got == want else "РАСХОЖДЕНИЕ"
            print(f"  {mark}: {name} — ожидалось {want}, получено {got}")
            if got != want:
                findings.append(
                    f"{name}: ожидалось {want}, получено {got}. {why}\n"
                    f"        вывод гейта: "
                    f"{(done.stdout or done.stderr).strip()[:160]}")
    return findings, 0


def main() -> int:
    findings: list[str] = []
    ran = 0
    for title, suite, count in (("гейт атрибуции:", suite_attribution, len(CASES)),
                                ("гейт полноты записи:", suite_audit,
                                 len(AUDIT_CASES)),
                                ("сборка указателя:", suite_shape, SHAPE_COUNT),
                                ("сборщик: пары, словарь, происхождение:",
                                 suite_index, INDEX_COUNT),
                                ("гейт атрибуции, первопредки:",
                                 suite_first_parents, len(FIRST_PARENT_CASES)),
                                ("свод против конвейера:", suite_charter,
                                 len(CHARTER_CASES)),
                                ("вопрос о соседях:", suite_near,
                                 len(NEAR_CASES)),
                                ("требование соавторства:",
                                 suite_require_coauthor, len(REQUIRE_CASES)),
                                ("предмет вопроса о соседях:",
                                 suite_near_subject, len(NEAR_SUBJECTS)),
                                ("вердикт о правилах из проектов:",
                                 suite_proposals, len(PROPOSAL_CASES))):
        print(title)
        got, broke = suite()
        if broke:
            return broke
        findings += got
        ran += count

    if findings:
        print("\nгейт ведёт себя не так, как объявлено:", file=sys.stderr)
        for f in findings:
            print(f"  • {f}", file=sys.stderr)
        print("\n  Расхождение чинится с той стороны, которая неверна: либо гейт, "
              "либо\n  формулировка в своде. Молчание не чинит ни одну "
              "(правило 140).", file=sys.stderr)
        return 1

    print(f"гейты отвергают то, что обязаны, и пропускают то, что обязаны: "
          f"случаев {ran}, расхождений нет")
    return 0


if __name__ == "__main__":
    sys.exit(main())
