#!/usr/bin/env python3
"""У каталога спрашивают о соседях, прежде чем писать новое правило.

ИНЦИДЕНТ (#91). Окно написало правило 143 — «авторство задаёт тот, кто открыл
изменение». На тот же вопрос уже отвечали 131 и 135, оба прочитанные при старте
и оба названные в своде. Запись переоткрыла то, что каталог знал, и была удалена
как дубль. Перед тем как писать её, окно не искало по каталогу вовсе: механизма,
который спросил бы «нет ли уже такого правила», не было.

ЧТО ЭТОТ ГЕЙТ ДЕЛАЕТ И ЧЕГО НЕ ДЕЛАЕТ — это результат замера, а не выбор вкуса.
Замер провели на живом предмете: удалённое 143 против всех 143 остальных правил.

  • Ранжирование работает, но ТОЛЬКО по полному тексту. По одному утверждению
    «Правило.» настоящие соседи уходят на 6-е и 13-е места; по полному тексту
    131 и 135 занимают первое и второе (0.243 и 0.241). Гейт, построенный по
    утверждению — казалось бы, именно оно описывает предмет, — живой случай
    пропустил бы.

  • Порога для отказа НЕ существует. Живой дубль 143↔131 даёт 0.243, а самая
    близкая ЗАКОННАЯ пара корпуса 131↔135 — 0.296; выше дубля или вровень с ним
    стоят ещё 006↔047 (0.257), 120↔129 (0.244) и 132↔133 (0.243). Любой порог,
    ловящий дубль, сначала покраснеет на четырёх законных парах. Поэтому гейт
    НЕ судит о дубле: запрещают достоверное, предупреждают о вероятном
    (правило 051).

  • Требование «сошлись на ближайшего соседа» тоже отменено замером: его не
    выполняют 92 правила из 143, а 143 его ВЫПОЛНЯЛО — ссылалось на 123 из
    своей же верхушки. Такой гейт покрасил бы две трети корпуса и пропустил
    единственный известный дубль.

Остаётся то, что механизм может: не решить, а ЗАСТАВИТЬ ВОПРОС БЫТЬ ЗАДАННЫМ —
как `main-red.yml` для красноты общей ветки (задача #87). Гейт требует, чтобы у
нового правила был записан ответ: каких соседей автор посмотрел и почему это не
они. Решение остаётся за человеком, но незаданным вопрос больше не бывает.

ДОЛГ ОБЪЯВЛЕН, А НЕ СПРЯТАН. Существующие правила писались без этого вопроса.
Спрашивать с них задним числом значило бы завести 143 отписки за один присест —
то есть починить видимость способом, который её ломает (правило 051). Поэтому
в `.rules/neighbours.json` объявлен `baseline`: правила с номером больше него
обязаны иметь ответ, остальные — declared debt, ровно как `--since` у гейта
атрибуции.

Реализует правила каталога:
  051 — предупреждают о вероятном, запрещают достоверное;
  026 — рассмотренная и отклонённая находка записывается, а не забывается;
  075 — проверка, которая ничего не может найти, бесполезна;
  039 — у проверки три исхода, а не два;
  140 — у гейта есть предмет, который он обязан отвергнуть (см. check_gates.py);
  096 — ответ о соседях живёт в .rules/neighbours.json — свой жизненный цикл, свой сторож.

Режимы:
  --near <номер|файл|-> печатает ближайших соседей: инструмент для автора,
                        вызывается ДО того, как правило написано. Предмет —
                        номер в дереве, любой файл-черновик или поток: у
                        ненаписанной записи номера нет, а у приехавшей из
                        чужого проекта его нет и не должно быть;
  --check               гейт: у каждого правила новее baseline есть ответ.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RULES_RU = "rules/ru"
ANSWERS = ".rules/neighbours.json"

#: Сколько ближайших соседей показываем автору.
NEAR = 5
#: Сколько верхних обязан назвать ответ. Меньше верхушки, которую печатаем:
#: показать стоит с запасом, а требовать — только то, что метрика уверенно
#: ставит наверх.
REQUIRED_TOP = 3
#: Длина вердикта, ниже которой это отписка, а не ответ. Ровно та же логика,
#: что у гейта полноты записи: заголовок можно поставить и оставить под ним
#: что угодно (правило 128).
MIN_VERDICT = 40

WORD = re.compile(r"[а-яёa-z0-9]+", re.I)
NUM_RE = re.compile(r"^(\d{3})-")

#: Служебные слова каталога. Они есть в каждой записи, и близость по ним
#: измеряет жанр, а не предмет.
STOP = frozenset("""
и в во не на что он с со как а то все она так его но да ты к у же вы за бы по
только ее мне было вот от меня еще нет о из ему теперь когда даже ну вдруг ли
если или быть был чтобы этом этого этой этот эта эти тем чем над без под при
для про есть их им них ей его где куда чего чему кем это тот та те был была
были будет может можно надо нужно должен должна должно который которая которое
которые которых правило правила правил каталог каталога область след инцидент
применимость почему
""".split())


def rule_number(name: str) -> str | None:
    m = NUM_RE.match(name)
    return m.group(1) if m else None


def tokens(s: str) -> list[str]:
    return [w.lower() for w in WORD.findall(s)
            if len(w) > 2 and w.lower() not in STOP]


def shingles(text: str, k: int = 4) -> frozenset[str]:
    """Символьные k-граммы по нормализованному тексту.

    Символьные, а не словесные: русская морфология разводит «открыл» и
    «открывший» в разные токены, а k-граммы их сближают. Замер выбрал эту
    метрику, а не наоборот.
    """
    flat = " ".join(tokens(text))
    if len(flat) < k:
        return frozenset()
    return frozenset(flat[i:i + k] for i in range(len(flat) - k + 1))


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def load_rules(root: Path) -> dict[str, dict]:
    """Номер → {title, text, shingles, path}. Дерево ru — канон номеров."""
    out: dict[str, dict] = {}
    folder = root / RULES_RU
    if not folder.is_dir():
        raise FileNotFoundError(folder)
    for path in sorted(folder.glob("*.md")):
        num = rule_number(path.name)
        if num is None:
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(r"^#\s+(.+)$", text, re.M)
        out[num] = {
            "title": m.group(1).strip() if m else path.stem,
            "text": text,
            "shingles": shingles(text),
            "path": path,
        }
    return out


def neighbours(num: str, rules: dict[str, dict], limit: int) -> list[tuple[float, str]]:
    """Ближайшие к `num`, по убыванию близости. Само правило исключено."""
    target = rules[num]["shingles"]
    scored = [(jaccard(target, r["shingles"]), n)
              for n, r in rules.items() if n != num]
    # Сортировка по номеру во вторую очередь: одинаковая близость не должна
    # давать разный порядок от запуска к запуску (правило 049 — состояние
    # выводится воспроизводимо).
    scored.sort(key=lambda p: (-p[0], p[1]))
    return scored[:limit]


def read_answers(root: Path) -> tuple[int, dict]:
    path = root / ANSWERS
    if not path.is_file():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    baseline = data.get("baseline")
    if not isinstance(baseline, int):
        raise ValueError(f"{ANSWERS}: baseline обязан быть числом")
    answers = data.get("answers")
    if not isinstance(answers, dict):
        raise ValueError(f"{ANSWERS}: answers обязан быть объектом")
    return baseline, answers


def subject(root: Path, target: str, rules: dict[str, dict]):
    """Предмет сравнения: номер в дереве, ЛЮБОЙ файл-черновик или `-` (поток).

    Черновик — не роскошь. Спрашивать полагается ДО того, как запись написана,
    а у ненаписанной записи нет ни номера, ни места в дереве. Правило, приехавшее
    из чужого проекта, номера не имеет тем более: его присваивает каталог при
    приёме, а не отправитель. Требовать `rules/ru/NNN-*.md` значило бы требовать
    номер раньше решения — то есть закрывать вход тем, ради кого вход и заведён.

    Возвращает (имя, текст, номер-или-None) либо (None, ошибка, None).
    """
    if target == "-":
        return "черновик из потока", sys.stdin.read(), None

    if target in rules:
        return f"{target} — {rules[target]['title']}", rules[target]["text"], target

    path = Path(target)
    num = rule_number(path.name)
    if num and num in rules:
        return f"{num} — {rules[num]['title']}", rules[num]["text"], num

    if path.is_file():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            return None, f"черновик {target!r} не прочитан — {exc}", None
        if not tokens(text):
            return None, (f"черновик {target!r} пуст после нормализации — "
                          f"сравнивать нечего"), None
        return f"черновик {path.name}", text, None

    return None, (f"{target!r} — не номер правила в {RULES_RU}, не файл и "
                  f"не `-`"), None


def mode_near(root: Path, target: str) -> int:
    """Печатает соседей. Это не гейт: исход 0, если предмет нашёлся."""
    rules = load_rules(root)
    label, text, num = subject(root, target, rules)
    if label is None:
        print(f"проверка не отработала: {text}", file=sys.stderr)
        return 2

    if num is not None:
        scored = neighbours(num, rules, NEAR)
    else:
        # Черновика в корпусе нет, значит и исключать нечего: сравниваем со
        # всеми. Тот же порядок сортировки, что и у соседей записи, — иначе
        # верхушка «до» и «после» коммита разъехалась бы (правило 049).
        target_sh = shingles(text)
        scored = sorted(
            ((jaccard(target_sh, r["shingles"]), n) for n, r in rules.items()),
            key=lambda p: (-p[0], p[1]))[:NEAR]

    print(label)
    print(f"\nближайшие {NEAR} записей каталога:\n")
    for score, other in scored:
        print(f"  {score:.3f}  {other}  {rules[other]['title']}")
    print(f"\n  Близость — повод прочитать, а не приговор: самая близкая пара "
          f"каталога\n  законна. Ответ записывается в {ANSWERS}.")
    return 0


def mode_check(root: Path) -> int:
    rules = load_rules(root)
    baseline, answers = read_answers(root)

    findings: list[str] = []
    notes: list[str] = []

    owed = sorted(n for n in rules if int(n) > baseline)

    # Ответ по правилу, которого нет: номер опечатан либо запись удалена, а
    # ответ остался. Молча пропустить — значит завести второй источник правды.
    for num in sorted(answers):
        if num not in rules:
            findings.append(
                f"{num}: ответ есть, а правила нет. Номер опечатан или запись "
                f"удалена — ответ убирается вместе с ней")

    for num in owed:
        answer = answers.get(num)
        top = neighbours(num, rules, NEAR)
        must = {n for _, n in top[:REQUIRED_TOP]}

        if answer is None:
            shown = ", ".join(f"{n} ({s:.3f})" for s, n in top)
            findings.append(
                f"{num}: ответа о соседях нет. Ближайшие: {shown}.\n"
                f"        Прочитайте их и запишите в {ANSWERS}, каких "
                f"посмотрели и почему это не они")
            continue

        if not isinstance(answer, dict):
            findings.append(f"{num}: ответ обязан быть объектом")
            continue

        considered = answer.get("considered")
        verdict = (answer.get("verdict") or "").strip()

        if not isinstance(considered, list) or not all(
                isinstance(x, str) for x in considered):
            findings.append(f"{num}: «considered» обязан быть списком номеров")
            continue

        unknown = [c for c in considered if c not in rules]
        if unknown:
            findings.append(
                f"{num}: в «considered» правил не существует: "
                f"{', '.join(sorted(unknown))}")

        missed = sorted(must - set(considered))
        if missed:
            shown = ", ".join(f"{n} ({s:.3f})" for s, n in top[:REQUIRED_TOP])
            findings.append(
                f"{num}: верхние соседи не рассмотрены — {', '.join(missed)}. "
                f"Верхушка: {shown}")

        if len(verdict) < MIN_VERDICT:
            findings.append(
                f"{num}: вердикт короче {MIN_VERDICT} символов — это отписка, "
                f"а не ответ. Скажите, чем предмет отличается")

    # Предупреждение, не отказ: пара ближе самой близкой законной пары корпуса
    # — повод посмотреть, но не повод краснеть. Порога у этой метрики нет, и
    # это измерено (см. заголовок файла).
    hottest = 0.0
    hot_pair = ("", "")
    nums = sorted(rules)
    for i, a in enumerate(nums):
        for b in nums[i + 1:]:
            s = jaccard(rules[a]["shingles"], rules[b]["shingles"])
            if s > hottest:
                hottest, hot_pair = s, (a, b)

    if findings:
        print("вопрос о соседях не задан:", file=sys.stderr)
        for f in findings:
            print(f"  • {f}", file=sys.stderr)
        print(f"\n  Гейт не решает, дубль это или нет — порога у метрики нет, "
              f"и это\n  измерено. Он требует, чтобы вопрос был задан "
              f"(задача #91).", file=sys.stderr)
        return 1

    if notes:
        print("на что стоит посмотреть (не отказ):")
        for n in notes:
            print(f"  ~ {n}")

    print(f"вопрос о соседях задан по каждому новому правилу: "
          f"правил {len(rules)}, с ответом {len(owed)}, "
          f"объявлено долгом {baseline}")
    print(f"  самая близкая пара корпуса: {hot_pair[0]} ↔ {hot_pair[1]} "
          f"({hottest:.3f}) — законная, порогом не отсекается")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--near", metavar="ПРЕДМЕТ",
                       help="показать ближайших соседей: номер правила, файл-черновик\n(ещё без номера) или `-` — читать черновик из потока")
    group.add_argument("--check", action="store_true",
                       help="гейт: у каждого правила новее baseline есть ответ")
    args = parser.parse_args(argv)

    try:
        if args.near:
            return mode_near(args.root, args.near)
        return mode_check(args.root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"проверка не отработала: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
