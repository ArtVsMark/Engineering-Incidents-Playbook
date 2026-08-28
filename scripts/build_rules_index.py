#!/usr/bin/env python3
"""Собирает единый двуязычный указатель правил из самих файлов.

Реализует правила каталога:
  120 — указатель пересобирается из файлов, а не правится руками;
  022 — одна тема, один канонический документ: указатель ровно один;
  049 — состояние выводится из живых артефактов;
  075 — не нашёл предмета проверки — падает, а не зеленеет;
  116 — сверка «сколько на входе / сколько на выходе» обязательна.

Падает (код 1), если:
  • правило есть на одном языке и отсутствует на другом — та самая ошибка,
    ради которой указатель и сделан единым;
  • номер встречается дважды;
  • перекрёстная ссылка ведёт в несуществующий файл;
  • в дереве не нашлось ни одного правила;
  • у правила нет строки «Область» — молча пустая колонка уже стоила каталогу
    всей классификации (правило 125);
  • область не значится в словаре AREAS: опечатка иначе заводит новую область;
  • области ru и en не соответствуют друг другу через словарь;
  • у области в словаре нет описания: пустая ячейка снова прошла бы за данные;
  • у правила нет раздела «След» или его ссылки не разбираются;
  • следы русского и английского деревьев расходятся;
  • в витрине пропал маркер числа правил.

Пропуск в нумерации — не ошибка: номера не переиспользуются даже после
удаления (правило 120). Он печатается как факт.

Запуск:  python scripts/build_rules_index.py          # записать rules/README.md
         python scripts/build_rules_index.py --check   # только проверить
Коды:    0 чисто · 1 есть находки · 2 проверка не отработала
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"
LANGS = ("ru", "en")
OUT = RULES / "README.md"
#: Машиночитаемый экспорт каталога: его тянет проект-потребитель обычным HTTP,
#: без GitHub API и без клона. Формат и правила его эволюции — export/README.md.
EXPORT = ROOT / "export" / "rules.json"
#: Версия контракта выгрузки. Поле `candidates` добавлено — по правилам
#: эволюции (export/README.md) добавление поля это MINOR.
EXPORT_SCHEMA = "1.2"
CATALOGUE_URL = "https://github.com/ArtVsMark/claude-code-playbook"

#: Значки берут число из этой же сборки: раздельно на язык, потому что подпись
#: у них разная. Файлы производные и руками не правятся, как и указатель.
#: Число правил в прозе витрин: значок несёт подпись, а не значение, и парсер,
#: скринридер и модель числа из него не получают (правила 127, 008). Маркер
#: переписывается этой же сборкой, а пропажа маркера роняет её.
MARKERS = (ROOT / "README.md", ROOT / "README.en.md")
MARKER_RE = re.compile(r"(<!--m:rules-->)\d+(<!--/m:rules-->)")

BADGES = {
    "ru": (ROOT / ".github" / "badges" / "rules-ru.json", "правил в каталоге"),
    "en": (ROOT / ".github" / "badges" / "rules-en.json", "rules in the catalogue"),
}

#: Пути правил, заполняется в main() — из него строятся ссылки навигации.
FILES: dict[str, dict[str, Path]] = {}

RULE_RE = re.compile(r"^(\d{3})-[a-z0-9-]+\.md$")
LINK_RE = re.compile(r"\]\((\d{3}-[^)#]+\.md)\)")
#: Область живёт в самом правиле, строкой под заголовком.
#: След — обязательный раздел записи. Из него достаётся структура
#: {репозиторий, задача}: строка раздела потребителю бесполезна (правило 129).
TRACE_HEAD = {"ru": "## След", "en": "## Trace"}
#: Форма записи объявлена в своде: правило → инцидент → почему → применимость →
#: след. Объявлена — и не проверялась ничем: одно правило из ста тридцати шло
#: без «Почему», и заметил это не гейт, а разбор руками (правило 002).
#: Заголовок сверяется по началу строки: «Почему знание не помогло» засчитывается,
#: потому что отвечает на тот же вопрос, а лишние разделы не запрещены.
SHAPE = {
    "ru": ("## Инцидент", "## Почему", "## Применимость", "## След"),
    "en": ("## The incident", "## Why", "## Where it applies", "## Trace"),
}
#: Реестр потребителей. Разрешительный список: репозиторием в следе считается
#: только то, что здесь названо. Запретительным («не начинается с src/») это не
#: закрывается — завтра появится tools/foo (правило 068).
CONSUMERS = ROOT / ".rules" / "consumers.json"
TRAIL_RE = re.compile(
    r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#(\d+)"   # владелец/репозиторий#номер
    r"|([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"          # репозиторий без номера — контекст
    r"|#(\d+)"                                     # голый номер — к последнему контексту
)

AREA_RE = {
    "ru": re.compile(r"^\*\*Область\.\*\*\s*(.+?)\s*$", re.M),
    "en": re.compile(r"^\*\*Area\.\*\*\s*(.+?)\s*$", re.M),
}

#: Словарь областей: английское имя и описание «что в области лежит» —
#: оно печатается в разделах навигации указателя. Список закрытый: область,
#: которой здесь нет, сборку не проходит. Иначе опечатка заводит новую
#: область молча, и рядом живут «интерфейс» и «интерфейсы» (правило 099).
AREAS = {
    "аудит": {
        "en": "audit",
        "about_ru": "как искать неизвестное и что делать с найденным: поверхности, статус находки, вердикты",
        "about_en": "finding the unknown and handling what turns up: surfaces, finding status, verdicts",
    },
    "документация": {
        "en": "documentation",
        "about_ru": "кто это читает, где канон и что в документе устаревает",
        "about_en": "who reads this, where the canon lives, and what goes stale in a document",
    },
    "процесс": {
        "en": "process",
        "about_ru": "как устроена сама работа: чем правило держится, откуда берётся план, чем доказано завершение",
        "about_en": "how the work itself is arranged: what backs a rule, where the plan comes from, what proves completion",
    },
    "код": {
        "en": "code",
        "about_ru": "решения внутри кода: блокировки, запись, уборка после сбоя, переходные состояния",
        "about_en": "decisions inside the code: locks, writes, cleanup after failure, transient states",
    },
    "параллельная работа": {
        "en": "parallel work",
        "about_ru": "несколько исполнителей одновременно: волны, зоны, задания, сборка результата",
        "about_en": "several executors at once: waves, zones, briefs, collecting the result",
    },
    "данные": {
        "en": "data",
        "about_ru": "где данные лежат, как переезжают и что теряется по дороге",
        "about_en": "where data lives, how it migrates, and what is lost on the way",
    },
    "квоты": {
        "en": "quotas",
        "about_ru": "исчерпаемое: лимиты, цена операции, темп и что делать на нуле",
        "about_en": "what runs out: limits, cost per operation, pace, and what to do at zero",
    },
    "конвейер": {
        "en": "pipeline",
        "about_ru": "путь изменения до основной ветки: ветки, очередь, конфликты, метки",
        "about_en": "a change's path to the main branch: branches, queue, conflicts, labels",
    },
    "тесты": {
        "en": "tests",
        "about_ru": "чем доказано, что тест проверяет именно то и краснеет когда надо",
        "about_en": "what proves a test checks the right thing and goes red when it should",
    },
    "CI": {
        "en": "CI",
        "about_ru": "проверки в облаке: исходы, пустой список, необратимые шаги, перезапуски",
        "about_en": "checks in the cloud: outcomes, an empty list, irreversible steps, re-runs",
    },
    "архитектура": {
        "en": "architecture",
        "about_ru": "границы и швы: где обобщать, куда поднимать общее, чем платит заглушка",
        "about_en": "boundaries and seams: when to generalise, where shared code goes, what a shim costs",
    },
    "надёжность": {
        "en": "reliability",
        "about_ru": "поведение при отказе: громкий провал, дедлайны, повторы, порядок операций",
        "about_en": "behaviour on failure: loud failure, deadlines, retries, order of operations",
    },
    "безопасность": {
        "en": "security",
        "about_ru": "недоверенный вход и права: списки разрешённого, изоляция, осознанное ослабление",
        "about_en": "untrusted input and privilege: allowlists, isolation, deliberate weakening",
    },
    "гейты": {
        "en": "gates",
        "about_ru": "устройство самих проверок: что ловят, чем краснеют, куда двигают бюджет",
        "about_en": "how the guards themselves work: what they catch, when they go red, which way the budget moves",
    },
    "агентские сессии": {
        "en": "agent sessions",
        "about_ru": "жизнь окна: срок, состояние, имя, повод перезапустить",
        "about_en": "the life of a session: its span, its state, its name, when to restart it",
    },
    "интерфейс": {
        "en": "interface",
        "about_ru": "что видит и понимает получатель: пустое состояние, сообщения, завершённость действия",
        "about_en": "what the recipient sees and understands: empty states, messages, whether an action finished",
    },
    "контракты": {
        "en": "contracts",
        "about_ru": "договор между частями: что значит сигнал, что такое отмена, как контракт меняется",
        "about_en": "the agreement between parts: what a signal means, what cancellation is, how a contract may change",
    },
    "релиз": {
        "en": "release",
        "about_ru": "выпуск наружу: версия, журнал изменений, необратимые шаги, огласка",
        "about_en": "shipping outward: version, changelog, irreversible steps, publicity",
    },
    "автоматика": {
        "en": "automation",
        "about_ru": "когда машина вмешивается сама и как остановить её руками",
        "about_en": "when the machine intervenes on its own, and how to stop it by hand",
    },
    "каталог": {
        "en": "catalogue",
        "about_ru": "как ведётся сам этот каталог и чем он связан с проектом",
        "about_en": "how this catalogue itself is kept, and how it links back to a project",
    },
    "качество": {
        "en": "quality",
        "about_ru": "чем измеряют качество проверки, а не продукта",
        "about_en": "how the quality of a check is measured, rather than of the product",
    },
    "метрики": {
        "en": "metrics",
        "about_ru": "что именно считать и когда среднее врёт",
        "about_en": "what exactly to count, and when an average lies",
    },
    "продукт": {
        "en": "product",
        "about_ru": "решения в пользу пользователя: умолчания, право удалить, момент показа",
        "about_en": "decisions made in the user's favour: defaults, the right to delete, when to show it",
    },
    "роли": {
        "en": "roles",
        "about_ru": "зачем нужна роль, что она обязана делать и все ли пласты покрыты",
        "about_en": "why a role exists, what it must do, and whether every layer is covered",
    },
    "ИИ": {
        "en": "AI",
        "about_ru": "модель как часть продукта: чем проверяют сгенерированное, что уходит в промпт",
        "about_en": "the model as part of the product: what verifies generated output, what goes into the prompt",
    },
    "витрины": {
        "en": "showcases",
        "about_ru": "первые пять минут читателя: что на виду и что за ссылкой",
        "about_en": "the reader's first five minutes: what is on show and what sits behind a link",
    },
    "инструменты": {
        "en": "tooling",
        "about_ru": "чем работают: версии инструментов и способ передать им код",
        "about_en": "what you work with: tool versions and how code reaches them",
    },
    "конкурентность": {
        "en": "concurrency",
        "about_ru": "несколько писателей одновременно: что блокировать и что записывать",
        "about_en": "several writers at once: what to lock and what to write",
    },
    "миграции": {
        "en": "migrations",
        "about_ru": "переход со старого на новое: откуда считать и чем кончается заглушка",
        "about_en": "moving from old to new: where to count from, and how a shim ends",
    },
    "приватность": {
        "en": "privacy",
        "about_ru": "что собирают о пользователе и что он может стереть",
        "about_en": "what is collected about the user, and what they can erase",
    },
    "решения": {
        "en": "decisions",
        "about_ru": "запись решения: отвергнутые варианты и запрет правки задним числом",
        "about_en": "recording a decision: the rejected options, and no edits after the fact",
    },
    "среды": {
        "en": "environments",
        "about_ru": "чем окружения различаются и что проверяется только в своём",
        "about_en": "how environments differ, and what can only be checked in its own",
    },
    "API": {
        "en": "API",
        "about_ru": "выбор транспорта к внешнему сервису и его цена",
        "about_en": "choosing the transport to an external service, and what it costs",
    },
    "вывод": {
        "en": "output",
        "about_ru": "то, что печатается: обрыв, маркеры, полнота",
        "about_en": "what gets printed: truncation, markers, completeness",
    },
    "диагностика": {
        "en": "diagnostics",
        "about_ru": "как узнать состояние, прежде чем действовать",
        "about_en": "finding out the state before acting on it",
    },
    "заимствование": {
        "en": "borrowing",
        "about_ru": "перенос чужого решения и границы «у автора работает»",
        "about_en": "adopting somebody else's solution, and the limits of \u201cit works for the author\u201d",
    },
    "история": {
        "en": "history",
        "about_ru": "что остаётся в истории репозитория и где это проверять",
        "about_en": "what stays in the repository's history, and where to verify it",
    },
    "командная работа": {
        "en": "collaboration",
        "about_ru": "границы чужого: во что нельзя вмешиваться",
        "about_en": "somebody else's boundaries: what not to touch",
    },
    "конфигурация": {
        "en": "configuration",
        "about_ru": "откуда берутся настройки и где их ищут",
        "about_en": "where settings come from and where they are looked up",
    },
    "локализация": {
        "en": "localisation",
        "about_ru": "второй язык: чем перевод отличается от совпадения ключей",
        "about_en": "the second language: how translation differs from key parity",
    },
    "наблюдение": {
        "en": "observation",
        "about_ru": "как узнавать об изменениях: событие против опроса",
        "about_en": "learning that something changed: events versus polling",
    },
    "отчёты": {
        "en": "reports",
        "about_ru": "форма отчёта: что в нём обязано быть видно",
        "about_en": "the shape of a report: what must be visible in it",
    },
    "планирование": {
        "en": "planning",
        "about_ru": "что готовят заранее, пока ресурс ещё есть",
        "about_en": "what to prepare in advance, while the resource lasts",
    },
    "прогоны": {
        "en": "runs",
        "about_ru": "разделение проходов: сбор отдельно, разбор отдельно",
        "about_en": "separating the passes: collecting apart from analysing",
    },
    "ресурсы": {
        "en": "resources",
        "about_ru": "что занимает место и когда это освобождается",
        "about_en": "what takes up space, and when it is released",
    },
    "сеть": {
        "en": "network",
        "about_ru": "отказы, которые приходят снаружи и проходят сами",
        "about_en": "failures that arrive from outside and pass on their own",
    },
    "сообщество": {
        "en": "community",
        "about_ru": "как сюда попадает новый человек",
        "about_en": "how a newcomer gets here",
    },
    "сравнение": {
        "en": "comparison",
        "about_ru": "сопоставление с ожидаемым и допуски в нём",
        "about_en": "comparing against what was expected, and the tolerances in it",
    },
    "таксономия": {
        "en": "taxonomy",
        "about_ru": "как классифицировать, когда признаки спорят",
        "about_en": "how to classify when the criteria disagree",
    },
    "темп": {
        "en": "pace",
        "about_ru": "с какой скоростью вести длинную работу",
        "about_en": "how fast to run long work",
    },
    "трекер": {
        "en": "tracker",
        "about_ru": "как выглядит задача, по которой ведут работу",
        "about_en": "what a task looks like when work runs on it",
    },
}


#: Переносимость записи за пределы Claude Code. Поле НЕОБЯЗАТЕЛЬНОЕ и задним
#: числом не проставляется: у README каталога есть общее предупреждение «не
#: копируйте целиком, половина заточена под агентские окна», и это поле делает
#: предупреждение выбираемым по записям, а не общим на всё (задача #63).
#:
#: Областью переносимость НЕ является и не станет: область говорит, О ЧЁМ
#: запись, а не куда её можно унести. Смешать два измерения в одном словаре
#: значит потерять оба — по 099 туда же приходят «интерфейс» и «интерфейсы».
PORTABLE_RE = {
    "ru": re.compile(r"^\*\*Переносится вне Claude Code\.\*\*\s*(.+?)\s*$", re.M),
    "en": re.compile(r"^\*\*Portable beyond Claude Code\.\*\*\s*(.+?)\s*$", re.M),
}
#: Значения закрытым списком, по той же причине, что и у областей.
PORTABLE_VALUES = {"да": "yes", "нет": "no", "частично": "partly"}
PORTABLE_VALUES_EN = {"yes", "no", "partly"}


def portable_of(path: Path, lang: str) -> str | None:
    """Значение поля переносимости или None, если поля нет. Причину не берём:
    её место в записи, а в экспорте потребителю нужен признак для отбора."""
    m = PORTABLE_RE[lang].search(path.read_text(encoding="utf-8"))
    if not m:
        return None
    head = m.group(1).split("—")[0].split("--")[0].strip().lower()
    if lang == "ru":
        return PORTABLE_VALUES.get(head)
    return head if head in PORTABLE_VALUES_EN else None


def title_of(path: Path) -> str:
    first = path.read_text(encoding="utf-8").split("\n", 1)[0]
    return first.lstrip("# ").strip()


def collect() -> tuple[dict[str, dict[str, Path]], list[str], list[str]]:
    """Возвращает найденное, находки и то, из-за чего проверка невозможна.

    Различие не косметическое (правило 039): «правило есть только на одном
    языке» — находка, её чинит автор. «Дерева правил нет вовсе» — проверка не
    отработала, и чинить надо запуск, а не содержимое.
    """
    found: dict[str, dict[str, Path]] = {}
    problems: list[str] = []
    blockers: list[str] = []
    for lang in LANGS:
        d = RULES / lang
        if not d.is_dir():
            blockers.append(f"нет каталога {d.relative_to(ROOT)} — проверять нечего")
            continue
        for f in sorted(d.iterdir()):
            m = RULE_RE.match(f.name)
            if not m:
                continue
            num = m.group(1)
            slot = found.setdefault(num, {})
            if lang in slot:
                problems.append(f"{lang}: номер {num} встречается дважды")
            slot[lang] = f
    if not found:
        blockers.append("в дереве не нашлось ни одного правила — "
                        "это ошибка входа, а не пустой каталог")
    return found, problems, blockers


def head_at(text: str, head: str) -> int | None:
    """Позиция сразу за заголовком, если он стоит ЦЕЛОЙ строкой.

    Сверять началом строки нельзя: «## След» — префикс заголовка «## Следствие
    второго порядка», который живёт в 002. От такого сравнения ломались обе
    стороны сразу — запись без обязательного раздела проходила проверку формы,
    а разбор следа начинался не с того места (задача #69, правило 141).
    """
    m = re.search("^" + re.escape(head) + r"[ \t]*$", text, re.M)
    return None if m is None else m.end()


def check_shape(found: dict[str, dict[str, Path]]) -> list[str]:
    """Каждая запись несёт разделы, объявленные сводом.

    Раздел «Применимость» отвечает, где правило НЕ работает, — без него каталог
    копируют целиком, включая заведомо чужое. «Почему» отвечает за механизм
    поломки: без него запись становится предпочтением, а не правилом.
    """
    problems: list[str] = []
    for num in sorted(found):
        for lang, path in sorted(found[num].items()):
            text = path.read_text(encoding="utf-8")
            missing = [h for h in SHAPE[lang] if not head_at(text, h)]
            if missing:
                problems.append(
                    f"{num}: {lang}/{path.name} — нет разделов "
                    f"{', '.join(chr(171) + m[3:] + chr(187) for m in missing)}. "
                    "Форма записи объявлена в своде и одинакова для всех")
    return problems


def check_links(found: dict[str, dict[str, Path]]) -> list[str]:
    problems = []
    for lang in LANGS:
        d = RULES / lang
        if not d.is_dir():
            continue
        for f in d.glob("*.md"):
            for m in LINK_RE.finditer(f.read_text(encoding="utf-8")):
                if not (d / m.group(1)).exists():
                    problems.append(f"{lang}/{f.name}: ссылка в никуда → {m.group(1)}")
    return problems


def check_pairs(found: dict[str, dict[str, Path]]) -> list[str]:
    problems = []
    for num in sorted(found):
        slot = found[num]
        missing = [l for l in LANGS if l not in slot]
        if missing:
            have = next(iter(slot.values())).name
            problems.append(
                f"{num}: нет перевода на {', '.join(missing)} — есть только {have}"
            )
        elif len({p.name for p in slot.values()}) > 1:
            names = " / ".join(f"{l}:{slot[l].name}" for l in LANGS)
            problems.append(f"{num}: имена файлов расходятся — {names}")
    return problems


def check_vocabulary() -> list[str]:
    """Область без описания дала бы пустую ячейку — а пустота проходит за
    значение (правило 125). Поэтому неполная запись словаря роняет сборку."""
    problems = []
    for name, fields in AREAS.items():
        missing = [k for k in ("en", "about_ru", "about_en") if not fields.get(k)]
        if missing:
            problems.append(f"словарь AREAS, «{name}»: не заполнено — {', '.join(missing)}")
    if not AREAS:
        problems.append("словарь AREAS пуст")
    return problems


def areas_of(path: Path, lang: str) -> list[str]:
    """Область правила — из самого файла. Пусто, если строки нет."""
    m = AREA_RE[lang].search(path.read_text(encoding="utf-8"))
    return [a.strip() for a in m.group(1).split(",") if a.strip()] if m else []


def check_areas(found: dict[str, dict[str, Path]]) -> tuple[dict[str, list[str]], list[str]]:
    """Читает области из правил и сверяет деревья.

    Область хранится в самих правилах, а не в этом указателе: производный файл
    не может быть хранилищем — регенерация обнуляет его молча (правило 125).
    """
    problems: list[str] = []
    result: dict[str, list[str]] = {}
    for num in sorted(found):
        slot = found[num]
        if not all(l in slot for l in LANGS):
            continue                      # об этом уже скажет check_pairs
        ru = areas_of(slot["ru"], "ru")
        en = areas_of(slot["en"], "en")
        for lang, got in (("ru", ru), ("en", en)):
            if not got:
                problems.append(f"{num}: нет строки «Область» в {lang}/{slot[lang].name}")
        if not ru or not en:
            continue
        unknown = [a for a in ru if a not in AREAS]
        if unknown:
            problems.append(
                f"{num}: область вне словаря AREAS — {', '.join(unknown)}"
                " (опечатка или новая область: допишите её в словарь осознанно)"
            )
            continue
        expected = [AREAS[a]["en"] for a in ru]
        if en != expected:
            problems.append(
                f"{num}: области деревьев расходятся — ru «{', '.join(ru)}»"
                f" ждёт en «{', '.join(expected)}», а стоит «{', '.join(en)}»"
            )
            continue
        result[num] = ru
    return result, problems


def by_area(areas: dict[str, list[str]], lang: str) -> str:
    """Таблица навигации по областям: сначала крупные, потом одиночные.

    Колонка «о чём» берётся из словаря AREAS: имя области само по себе не
    объясняет, что в ней лежит, а по одному названию правило не ищут.
    """
    buckets: dict[str, list[str]] = {}
    for num, names in areas.items():
        for a in names:
            buckets.setdefault(a, []).append(num)

    if lang == "ru":
        name_of, about_of = (lambda a: a), (lambda a: AREAS[a]["about_ru"])
        head = "| Область | О чём это | Правил | Правила |"
    else:
        name_of, about_of = (lambda a: AREAS[a]["en"]), (lambda a: AREAS[a]["about_en"])
        head = "| Area | What it covers | Count | Rules |"

    rows = [head, "|---|---|---:|---|"]
    for a in sorted(buckets, key=lambda a: (-len(buckets[a]), name_of(a))):
        nums = sorted(buckets[a])
        links = " · ".join(f"[{n}]({lang}/{FILES[n][lang].name})" for n in nums)
        rows.append(f"| **{name_of(a)}** | {about_of(a)} | {len(nums)} | {links} |")
    return "\n".join(rows)


def added_dates() -> tuple[dict[str, str], list[str]]:
    """Дата появления правила — из истории, а не из поля в файле.

    Поле пришлось бы заполнять руками, а руками вписанная дата устаревает и
    врёт так же, как число (правило 005). История — живой артефакт: правило
    появилось тогда, когда появился его файл (правило 049).
    """
    try:
        shallow = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--is-shallow-repository"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        if shallow == "true":
            return {}, [("клон мелкий: истории нет, а дата появления взялась бы от "
                        "единственного коммита — правдоподобная и неверная. "
                        "Нужен полный клон (fetch-depth: 0)")]
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--diff-filter=A", "--name-only",
             "--format=%aI", "--", "rules/ru/[0-9][0-9][0-9]-*.md"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        return {}, [f"история недоступна, дату появления взять неоткуда: {e}"]

    dates: dict[str, str] = {}
    stamp = ""
    for line in out.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line[0].isdigit() and "T" in line:
            stamp = line[:10]
        elif line.startswith("rules/ru/"):
            dates.setdefault(Path(line).name[:3], stamp)
    return dates, []


def render_export(found: dict[str, dict[str, Path]], areas: dict[str, list[str]],
                  dates: dict[str, str], trails: dict[str, list]) -> str:
    rules = []
    for num in sorted(found):
        ru, en = found[num]["ru"], found[num]["en"]
        names = areas.get(num, [])
        rules.append({
            "id": num,
            "slug": ru.stem[4:],
            "title": {"ru": title_of(ru), "en": title_of(en)},
            "areas": {"ru": names, "en": [AREAS[a]["en"] for a in names]},
            "added": dates[num],
            "files": {"ru": f"rules/ru/{ru.name}", "en": f"rules/en/{en.name}"},
            "trails": trails.get(num, []),
        })
        # Необязательное поле: отсутствует у записи — отсутствует и в экспорте.
        # Ключ со значением null означал бы «ответили не знаю», а мы не
        # отвечали вовсе (правило 128 про полноту поля, а не про его наличие).
        portable = portable_of(ru, "ru")
        if portable:
            rules[-1]["portable"] = portable
    doc = {
        "schema": EXPORT_SCHEMA,
        "catalogue": CATALOGUE_URL,
        "count": len(rules),
        "rules": rules,
        "candidates": candidates_export(),
    }
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def section_of(text: str, head: str) -> str:
    """Тело раздела до следующего заголовка того же уровня."""
    at = head_at(text, f"## {head}")
    if at is None:
        return ""
    rest = text[at:]
    nxt = rest.find("\n## ")
    return (rest if nxt < 0 else rest[:nxt]).strip()


def candidates_export() -> list[dict]:
    """Гипотезы едут потребителям — без номера и помеченными гипотезами.

    ЗАЧЕМ. Растут не только правила. Гипотеза лежала только у нас, и потому
    подтвердить её мог только НАШ инцидент; у неё есть раздел «Чем
    подтвердится» — готовый вопрос, на который у соседа может быть ответ уже
    сегодня. Как только гипотеза подтверждается где-то, рождается правило: путь
    обратно уже построен — предложение потребителя по правилу 080.

    ЧЕМ ЭТО ОПАСНО И ЧТО ЗДЕСЬ СДЕЛАНО ПРОТИВ. Папка «почти правил» — готовый
    обход требования инцидента, и обход происходит сползанием: сперва на
    кандидата ссылается правило, потом свод, потом никто не помнит, что это
    гипотеза (`check_candidates.py`). Публикация переносит этот риск К
    ПОТРЕБИТЕЛЮ, где нашего гейта нет. Поэтому в выгрузке у кандидата **нет
    поля `id`** — ни пустого, ни `null`: номер занимать нельзя, а пустой ключ
    той же формы, что у правила, — приглашение его заполнить. Есть `kind:
    "hypothesis"` и обязательное `confirmed_by`: гипотеза, не назвавшая своего
    опровержения, не подтвердится и не отвергнется, а просто придаст уверенности
    самим фактом существования.

    ГРАНИЦА. Кандидат одноязычен, в отличие от правила: дерева `candidates/en`
    нет, и требовать перевод гипотезы значило бы платить за то, что может не
    подтвердиться никогда. Язык объявлен полем `lang`, а не подразумевается.

    Пустой список — законное состояние: кандидатов может не быть (091).
    """
    folder = ROOT / "candidates"
    if not folder.is_dir():
        return []
    out = []
    for path in sorted(p for p in folder.glob("*.md") if p.name != "README.md"):
        text = path.read_text(encoding="utf-8")
        m = re.search(r"(?im)^\*\*Гипотеза\.\*\*\s+(.+?)(?=\n\n)", text, re.S)
        area = re.search(r"(?im)^\*\*Область\.\*\*\s+(.+)$", text)
        out.append({
            "kind": "hypothesis",
            "slug": path.stem,
            "lang": "ru",
            "title": title_of(path),
            "area": area.group(1).strip() if area else "",
            "hypothesis": " ".join(m.group(1).split()) if m else "",
            "source": section_of(text, "Источник"),
            "confirmed_by": section_of(text, "Чем подтвердится"),
            "applicability": section_of(text, "Применимость"),
            "file": str(path.relative_to(ROOT)),
        })
    return out


def known_consumers() -> tuple[set[str], str | None]:
    """Репозитории, которые вообще могут стоять в следе.

    Без этого списка «репозиторием» становился любой токен с косой чертой, и
    путь в обратных кавычках перетирал настоящий репозиторий: у 23 правил след
    уезжал в экспорт в виде куска пути. Поле было непустым, а бессмысленным —
    правило 128.
    """
    try:
        data = json.loads(CONSUMERS.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return set(), (f"реестр потребителей не прочитан — {e}. Без него "
                       "следы разбирать нечем, а разбирать наугад нельзя")
    repos = {c.get("repo") for c in data.get("consumers", []) if c.get("repo")}
    if not repos:
        return set(), (f"{CONSUMERS.relative_to(ROOT)} не называет ни одного "
                       "потребителя — пустой список это состояние, но не "
                       "основание разбирать следы")
    return repos, None


def trails_of(path: Path, lang: str, known: set[str]) -> tuple[list[dict[str, str]], str | None]:
    """Ссылки на задачи из раздела «След», по порядку и без повторов.

    Голый номер наследует последний упомянутый рядом репозиторий — так он и
    читается человеком. Номер, которому не предшествует ни один репозиторий,
    разобрать нельзя: это не пустой след, а неразбираемый, и он назван ошибкой,
    а не пропущен молча (правила 075, 128).

    Репозиторием считается только тот, что есть в реестре потребителей. Токен
    вида «путь/файл.py» контекст не перебивает — он просто проза.
    """
    text = path.read_text(encoding="utf-8")
    head = TRACE_HEAD[lang]
    at = head_at(text, head)
    if at is None:
        return [], f"нет раздела «{head}» — это обязательный раздел записи"

    out: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    current: str | None = None
    for m in TRAIL_RE.finditer(text[at:]):
        full, num, repo_only, bare = m.groups()
        if full:
            if full not in known:
                return [], (f"след ведёт в {full}#{num}, а такого потребителя "
                            f"нет в {CONSUMERS.relative_to(ROOT)}. Либо опечатка, "
                            "либо реестр пора дополнить — осознанно, а не молча")
            current = full
            key = (full, num)
        elif repo_only:
            # Не потребитель — значит это путь, кусок URL или проза. Контекст
            # не трогаем: перетереть его тем, что репозиторием не является, и
            # значит потерять след.
            if repo_only in known:
                current = repo_only
            continue
        else:
            if current is None:
                return [], f"ссылка #{bare} без репозитория рядом — непонятно, чья задача"
            # ГОЛЫЙ НОМЕР РАЗБИРАЕТСЯ, НО НЕ ЧИТАЕТСЯ. Площадка автоссылает
            # `владелец/репозиторий#номер` прямо в отрендеренном .md — это
            # проверено живой страницей, а не предположено. Голый `#номер`
            # рядом остаётся ОБЫЧНЫМ ТЕКСТОМ. Замер по корпусу: 44 ссылки
            # кликались, 57 в каждом дереве — нет.
            #
            # То есть след существовал для машины и не существовал для
            # человека: разбор здесь контекст несёт, а читатель видит живую
            # ссылку и рядом мёртвое число (правило 049 — вычисляемое
            # состояние расходится с показанным молча). След затем и нужен,
            # чтобы по нему пройти.
            return [], (f"голый #{bare} в разделе следа: разбирается, но не "
                        f"кликается. Полная форма — {current}#{bare}")
        if key not in seen:
            seen.add(key)
            out.append({"repo": key[0], "issue": key[1]})
    return out, None


def check_trails(found: dict[str, dict[str, Path]]) -> tuple[dict[str, list], list[str]]:
    """Следы читаются из русского дерева и сверяются с английским.

    Расхождение — не мелочь оформления: потребитель получает один список задач
    на правило, и если деревья спорят, непонятно, какое из них право.
    """
    problems: list[str] = []
    result: dict[str, list] = {}
    known, err = known_consumers()
    if err:
        return {}, [f"реестр потребителей: {err}"]
    for num in sorted(found):
        slot = found[num]
        if not all(l in slot for l in LANGS):
            continue
        ru, err_ru = trails_of(slot["ru"], "ru", known)
        en, err_en = trails_of(slot["en"], "en", known)
        for lang, err in (("ru", err_ru), ("en", err_en)):
            if err:
                problems.append(f"{num}: {lang}/{slot[lang].name}: {err}")
        if err_ru or err_en:
            continue
        if {(d["repo"], d["issue"]) for d in ru} != {(d["repo"], d["issue"]) for d in en}:
            problems.append(
                f"{num}: следы деревьев расходятся — "
                f"ru {[d['repo'] + '#' + d['issue'] for d in ru]}, "
                f"en {[d['repo'] + '#' + d['issue'] for d in en]}"
            )
            continue
        result[num] = ru
    return result, problems


def marked(path: Path, count: int) -> tuple[str, str | None]:
    """Подставляет число в маркер. Возвращает текст и находку, если маркера нет."""
    text = path.read_text(encoding="utf-8")
    if not MARKER_RE.search(text):
        return text, (f"{path.name}: маркера <!--m:rules--> нет. Число, которое "
                      "некому переписать, устареет молча — а витрина будет "
                      "выглядеть свежей")
    return MARKER_RE.sub(rf"\g<1>{count}\g<2>", text), None


def area_stats(areas: dict[str, list[str]]) -> tuple[int, int]:
    """Сколько всего областей и сколько из них держат единственное правило.

    Второе число — не дефект, а наблюдение: одиночная область это либо пустая
    полка, которая заполнится, либо тег к чужому правилу. Различить можно
    только по движению, поэтому число печатается каждой сборкой (правило 005).
    """
    buckets: dict[str, int] = {}
    for names in areas.values():
        for a in names:
            buckets[a] = buckets.get(a, 0) + 1
    return len(buckets), sum(1 for n in buckets.values() if n == 1)


def render_badge(label: str, count: int) -> str:
    """Значок shields.io в формате endpoint. Число — из этой же сборки."""
    return (
        "{\n"
        '  "schemaVersion": 1,\n'
        f'  "label": "{label}",\n'
        f'  "message": "{count}",\n'
        '  "color": "blue"\n'
        "}\n"
    )


def render(found: dict[str, dict[str, Path]], gaps: list[int],
           areas: dict[str, list[str]]) -> str:
    rows = []
    for num in sorted(found):
        slot = found[num]
        ru = slot.get("ru")
        en = slot.get("en")
        t_ru = title_of(ru) if ru else "—"
        t_en = title_of(en) if en else "—"
        l_ru = f"[ru](ru/{ru.name})" if ru else "—"
        l_en = f"[en](en/{en.name})" if en else "—"
        names = areas.get(num, [])
        both = f"{', '.join(names)} · {', '.join(AREAS[a]['en'] for a in names)}" if names else ""
        rows.append(f"| {num} | {t_ru} | {t_en} | {l_ru} {l_en} | {both} |")

    gap_note = ""
    if gaps:
        gap_note = (
            "\n> Пропуски в нумерации: "
            + ", ".join(str(g) for g in gaps)
            + ". Это не ошибка — номера не переиспользуются даже после удаления"
            + " ([`120`](ru/120-how-to-run-a-rule-catalogue.md)).\n"
        )

    return f"""# Правила · Rules

Один файл — одно правило, одинаковое имя в обоих деревьях.
One file, one rule, the same file name in both trees.

Формат: правило → инцидент → почему → применимость → след.
Shape: rule → incident → why → where it applies → trace.

> **Этот файл собирается скриптом** `scripts/build_rules_index.py` и не правится
> руками. Правило, добавленное только на одном языке, не пройдёт сборку — это и
> есть механизм, который не даёт деревьям разойтись.
>
> **This file is generated** by `scripts/build_rules_index.py` and is never
> edited by hand. A rule added in only one language fails the build — that is the
> mechanism keeping the two trees from diverging.
{gap_note}
Всего правил · rules in total: **{len(found)}**

| № | Правило | Rule | Файлы · Files | Область · Area |
|---|---|---|---|---|
{chr(10).join(rows)}

---

## По областям

Быстрый вход в каталог не по номеру, а по предмету. Правило стоит в нескольких
областях, если относится к нескольким, — поэтому сумма по областям больше числа
правил. Порядок — по числу правил: крупные области сверху, одиночные внизу.
Ссылки ведут в русское дерево.

{by_area(areas, "ru")}

## By area

A way into the catalogue by subject rather than by number. A rule sits in several
areas when it belongs to several, so the areas add up to more than the number of
rules. Ordered by rule count: the large areas first, the singletons last. Links
point at the English tree.

{by_area(areas, "en")}

---

## Как добавить своё

Правило рождается — запись в тот же день. Материал портится быстро: инциденты
месячной давности приходится восстанавливать по документам, потому что в памяти
их уже нет. Заготовка — [`templates/rule-template.md`](../templates/rule-template.md).

Обязательны две части, которые чаще всего пропускают:

- **Применимость** — где правило **не** работает. Без неё каталог скопируют
  целиком, включая заведомо чужое.
- **След** — ссылка на issue, PR или документ, где поломка видна. Без неё запись
  за месяц превращается в «кто-то говорил, что так лучше».

Запись делается **на обоих языках сразу**. Не потому что так аккуратнее, а
потому что иначе она не пройдёт сборку указателя.

## How to add your own

A rule is born — the record is written the same day. The material spoils fast:
incidents a month old have to be reconstructed from documents, because nobody
remembers them any more. Boilerplate:
[`templates/rule-template.md`](../templates/rule-template.md).

Two parts are mandatory and are the ones most often skipped:

- **Where it applies** — where the rule does **not** work. Without it the
  catalogue gets copied wholesale, including what plainly belongs to somebody
  else.
- **Trace** — a link to the issue, pull request or document where the failure is
  visible. Without it, within a month the record becomes "somebody said this was
  better".

The record is written **in both languages at once**. Not out of tidiness, but
because otherwise it will not pass the index build.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="только проверить, не записывать")
    args = ap.parse_args()

    found, problems, blockers = collect()
    problems += check_pairs(found)
    problems += check_shape(found)
    problems += check_links(found)
    problems += check_vocabulary()
    # История недоступна или клон мелкий — это невозможность проверки, а не
    # находка: чинится запуском, а не правкой правил.
    dates, date_problems = added_dates()
    blockers += date_problems
    trails, trail_problems = check_trails(found)
    problems += trail_problems
    FILES.update(found)
    areas, area_problems = check_areas(found)
    problems += area_problems

    nums = sorted(int(n) for n in found)
    gaps = [i for i in range(nums[0], nums[-1] + 1) if i not in set(nums)] if nums else []

    if blockers:
        print("проверка не отработала:", file=sys.stderr)
        for b in blockers:
            print(f"  • {b}", file=sys.stderr)
        return 2

    if problems:
        print("указатель не собран:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    # Дата без источника — пустое поле, а пустота проходит за данные (125, 128).
    # Клон полный (иначе вышли бы выше), значит правила просто ещё не в истории:
    # их только что завели. Сказать про «мелкий клон» здесь значит отправить
    # автора чинить не то — сторож обязан называть виновника (правило 103).
    undated = [f"{n}: правило ещё не в истории — закоммитьте его и пересоберите. "
               "Дата появления берётся из истории, а не из поля (правило 049)"
               for n in sorted(found) if n not in dates]
    if undated:
        print("указатель не собран:", file=sys.stderr)
        for u in undated:
            print(f"  • {u}", file=sys.stderr)
        return 1

    text = render(found, gaps, areas)
    export = render_export(found, areas, dates, trails)
    marks: dict[Path, str] = {}
    for path in MARKERS:
        body, gap = marked(path, len(found))
        if gap:
            problems.append(gap)
        else:
            marks[path] = body
    if problems:
        print("указатель не собран:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1
    total_areas, singles = area_stats(areas)
    badges = {p: render_badge(label, len(found)) for p, label in BADGES.values()}

    if args.check:
        # ЗНАЧКИ В СВЕРКЕ НЕ УЧАСТВУЮТ. Они живут на отдельной ветке `badges` и
        # в дереве общей ветки их нет вовсе — сверять здесь нечего и не с чем.
        # Держать их в `main` под гейтом значило бы требовать пересборки
        # значка от КАЖДОГО изменения: конфликт на каждом слиянии и красная
        # общая ветка после каждого — то есть проверка, которую приучаются
        # пропускать (051). Свежесть значков держит работа badges.yml, которая
        # запускается на каждый толчок в main.
        stale = [OUT] if (OUT.read_text(encoding="utf-8") if OUT.exists() else "") != text else []
        if (EXPORT.read_text(encoding="utf-8") if EXPORT.exists() else "") != export:
            stale.append(EXPORT)
        stale += [p for p, want in marks.items()
                  if p.read_text(encoding="utf-8") != want]
        if stale:
            print("устарело — пересоберите (python scripts/build_rules_index.py): "
                  + ", ".join(str(p.relative_to(ROOT)) for p in stale), file=sys.stderr)
            return 1
        print(f"указатель актуален: {len(found)} правил на {len(LANGS)} языках,"
              f" областей {total_areas} (с одним правилом {singles})")
        return 0

    OUT.write_text(text, encoding="utf-8")
    for path, want in badges.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(want, encoding="utf-8")
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    EXPORT.write_text(export, encoding="utf-8")
    for path, body in marks.items():
        path.write_text(body, encoding="utf-8")
    print(f"собрано: {len(found)} правил, языков {len(LANGS)},"
          f" областей {total_areas} (с одним правилом {singles}),"
          f" пропуски в нумерации: {gaps or 'нет'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
