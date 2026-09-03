#!/usr/bin/env python3
"""Журнал изменений собирается из фрагментов, а не правится общим файлом.

Реализует правила каталога:
  030 — запись приезжает вместе с изменением, отдельным файлом;
  039 — у проверки три исхода, а не два;
  022 — «что изменилось» и «как мы сюда пришли» — разные документы:
        CHANGELOG.md отвечает на первый вопрос, HISTORY.md на второй;
  075 — не нашёл предмета проверки — падает, а не зеленеет;
  024 — журнал работ не ведётся внутри действующего документа: запись приезжает фрагментом;
  138 — эстафета собирается по ходу: запись едет ТЕМ ЖЕ заходом, что и
        правка поведения, а не перед выпуском. Замер: из 34 изменений с
        поведением запись несут 34 — гейт снимает правило с дисциплины;
  002 — «не забыть закрыть раздел при выпуске» механизмом не является: v1.1.0
        вышел, а раздела [1.1.0] в журнале не появилось, и 42 записи выпуска
        полгода лежали в [Unreleased], где их читают как ещё не вышедшие.

Фрагмент:  changelog.d/<слаг>.<секция>.md
Секции:    added · changed · fixed · removed · internal
Внутри:    одна строка текста, без ведущего «-» и без имени секции.

РАЗДЕЛ ВЫПУСКА ЗАКРЫВАЕТ САМ ВЫПУСК. `--close vX.Y.0` переименовывает
[Unreleased] в раздел выпуска и заводит пустой [Unreleased] заново; зовёт его
.github/workflows/release.yml перед постановкой тега. Проверка спрашивает
обратное: у каждого тега выпуска обязан быть свой раздел.

Исходы:
  0 — чисто;
  1 — есть находки (плохое имя, пустой фрагмент, нужна запись, а её нет;
      у тега выпуска нет раздела);
  2 — проверка не отработала (нет каталога фрагментов, нет CHANGELOG.md,
      не читаются теги выпусков).

Запуск:  python scripts/collect_changelog.py --check     # проверить
         python scripts/collect_changelog.py --preview   # показать сборку
         python scripts/collect_changelog.py --collect   # собрать в [Unreleased]
         python scripts/collect_changelog.py --close v1.2.0   # закрыть раздел
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

# Что считается тегом выпуска, решает одно место на весь каталог: у второго
# выражения разъехались бы границы, а разъехавшись — молча (правила 090, 022).
import history_metrics

ROOT = Path(__file__).resolve().parent.parent
FRAGMENTS = ROOT / "changelog.d"

#: Пути, правка которых меняет ПОВЕДЕНИЕ каталога. Список разрешительный по
#: смыслу: он называет, где поведение живёт, а не перечисляет исключения (068).
BEHAVIOUR = ("scripts/", ".github/workflows/", ".github/actions/")
#: Названный выход из требования. Без выхода гейт обходили бы пустым
#: фрагментом, а пустой фрагмент хуже отсутствующего — он выглядит памятью
#: (правило 126: у заморозки должен быть выход, не проходящий через неё саму).
WAIVER_RE = re.compile(
    r"(?m)^\s*Журнал:\s*не\s+требуется\s*[—–-]\s*(?P<why>.+?)\s*$")


def entry_required(paths: list[str], body: str) -> tuple[bool, str]:
    """Нужна ли запись журнала этому изменению, и почему.

    ЗАЧЕМ ГЕЙТ, ЕСЛИ ПРАКТИКА И ТАК ДЕРЖИТСЯ. Замер по общей ветке: из 34
    изменений, тронувших поведение, запись несут 34 — то есть ноль нарушений.
    Ровно поэтому гейт и дешёв: он не чинит поломку, он снимает правило с
    дисциплины (002). Дисциплина, о которой известно, что она сто процентов,
    ломается ровно один раз — и незаметно, потому что смотреть на неё уже
    перестали.

    Второй половиной правила 138 это и является: решение оседает артефактом
    ТЕМ ЖЕ ЗАХОДОМ, а не перед выпуском. Отложенная запись означает, что
    следующее окно разбирает тот же вопрос заново.
    """
    трогает = [p for p in paths if p.startswith(BEHAVIOUR)]
    if not трогает:
        return False, "поведение не тронуто: записи журнала не требуется"
    if any(p.startswith("changelog.d/") for p in paths):
        return False, f"поведение тронуто (путей: {len(трогает)}), запись есть"
    m = WAIVER_RE.search(body or "")
    if m and m.group("why").strip():
        return False, f"освобождено с причиной: {m.group('why').strip()}"
    return True, ("изменение трогает поведение и не несёт записи журнала: "
                  + ", ".join(sorted(трогает)[:5])
                  + (" и другие" if len(трогает) > 5 else ""))
CHANGELOG = ROOT / "CHANGELOG.md"

#: Порядок фиксирован: «что нового» читается раньше, чем «что починили».
SECTIONS = ("added", "changed", "fixed", "removed", "internal")
TITLES = {
    "added": "Добавлено · Added",
    "changed": "Изменено · Changed",
    "fixed": "Починено · Fixed",
    "removed": "Удалено · Removed",
    "internal": "Внутреннее · Internal",
}
NAME_RE = re.compile(rf"^([a-z0-9][a-z0-9-]*)\.({'|'.join(SECTIONS)})\.md$")
UNRELEASED = "## [Unreleased]"
#: Заголовок вышедшего раздела: «## [1.1.0] — 2026-08-28».
RELEASE_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.M)
#: Пустой раздел говорит, что он пуст (правило 027): голый заголовок читается
#: как «журнал сломался». Строка не начинается с «-» и потому записью не
#: считается, а первая же сборка её заменяет.
EMPTY_NOTE = ("Пока пусто: записи приезжают фрагментами и собираются "
              "перед выпуском.")


#: Строка вердикта. Начинается с «>», в журнал НЕ едет и живёт только во
#: фрагменте: читателю выпуска она не адресована, а автору починки — да.
VERDICT_PREFIX = ">"
#: Ссылка на правило: номер рядом со словом «правил» либо путь в дерево.
RULE_RE = re.compile(r"(?i)правил\w*\s+№?\s*\d{3}|rules/(?:ru|en)/\d{3}-")
#: Заполненный отказ. Причина обязательна: «не правило» без неё — это пустота,
#: которую зададут заново следующей починкой (правило 026).
NOT_A_RULE_RE = re.compile(r"(?i)не\s+(?:станови\w+|стало|тянет|правило)[^.]*?потому что\s+\S+")
VERDICT_HINT = ("> правило NNN — <как связано>   ·   "
                "> правилом не становится, потому что <причина>")


def split_verdict(text: str) -> tuple[str, str]:
    """Делит фрагмент на тело журнала и вердикт о правиле."""
    body, verdict = [], []
    for line in text.splitlines():
        (verdict if line.lstrip().startswith(VERDICT_PREFIX) else body).append(line)
    return ("\n".join(body).strip(),
            " ".join(l.lstrip().lstrip(VERDICT_PREFIX).strip() for l in verdict).strip())


def verdict_problems(paths: list[Path]) -> list[str]:
    """Починка обязана ответить, тянет ли она на правило.

    ГДЕ ЗДЕСЬ МОМЕНТ. Фильтр на входе в каталог есть и работает машинно: запись
    без границы «не работает» отвергает audit_catalogue.py, запись без
    инцидента не принимает документ для участника. Но срабатывает он для того,
    кто УЖЕ решил писать. Момента, в который это решают, не было — и замер по
    корпусу показывает форму пропажи: записи появляются пачками там, где кто-то
    целенаправленно садился их писать, а не по одной вслед за починками.

    Момент выбран здесь потому, что фрагмент журнала пишут ровно тогда, когда
    починка сделана и инцидент ещё цел: известны причина, цена и чем чинили.
    Через сутки остаётся след поломки, а не она сама (правило 138).

    СПРАШИВАЕТСЯ ТОЛЬКО У НОВЫХ ФРАГМЕНТОВ. Спросить со старых задним числом
    значило бы завести два десятка отписок за присест — ровно то, чего не хочет
    026: отказ без причины возвращается следующей ревизией.
    """
    out: list[str] = []
    for path in paths:
        m = NAME_RE.match(path.name)
        if not m or m.group(2) != "fixed" or not path.exists():
            continue
        _, verdict = split_verdict(path.read_text(encoding="utf-8"))
        if not verdict:
            out.append(f"{path.name}: починка не ответила, тянет ли она на "
                       f"правило. Строкой с «>»:\n        {VERDICT_HINT}")
        elif not (RULE_RE.search(verdict) or NOT_A_RULE_RE.search(verdict)):
            out.append(f"{path.name}: вердикт есть, но не разбирается — нужен "
                       f"номер правила либо отказ С ПРИЧИНОЙ.\n        {VERDICT_HINT}")
    return out


def added_since(ref: str) -> tuple[list[Path], str | None]:
    """Фрагменты, ДОБАВЛЕННЫЕ этим изменением. Спрашивать со всех нельзя."""
    try:
        done = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=A", f"{ref}...HEAD",
             "--", FRAGMENTS.name],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        return [], "нет команды git"
    if done.returncode != 0:
        return [], (done.stderr or done.stdout).strip()
    return [ROOT / line for line in done.stdout.split() if line], None


def fragments() -> list[Path]:
    return sorted(p for p in FRAGMENTS.glob("*.md") if p.name != "README.md")


def validate() -> tuple[dict[str, list[str]], list[str]]:
    """Разбирает фрагменты. Возвращает записи по секциям и список находок."""
    found: dict[str, list[str]] = {s: [] for s in SECTIONS}
    problems: list[str] = []
    for path in fragments():
        m = NAME_RE.match(path.name)
        if not m:
            problems.append(
                f"{path.name}: имя не по форме «<слаг>.<секция>.md», "
                f"секции — {', '.join(SECTIONS)}")
            continue
        text, _ = split_verdict(path.read_text(encoding="utf-8"))
        text = text.strip()
        if not text:
            problems.append(f"{path.name}: фрагмент пуст — запись, которой нет, "
                            "хуже отсутствующего файла: он выглядит сделанным")
            continue
        if text.startswith("-"):
            problems.append(f"{path.name}: ведущий «-» подставит сборка, "
                            "в тексте он лишний")
            continue
        found[m.group(2)].append(" ".join(text.split()))
    return found, problems


def existing(text: str) -> dict[str, list[str]]:
    """Записи, УЖЕ лежащие в [Unreleased], разложенные по секциям.

    ПОЧЕМУ ЭТО ПОНАДОБИЛОСЬ. Сборка вставляла свежий блок сразу после
    заголовка `[Unreleased]`, а прежнее содержимое оставляла ниже. Пока
    раздел собирали ровно один раз перед выпуском, это работало. Замер на
    подготовке 1.1.0: раздел собрали, потом слили ещё три изменения и
    собрали снова — и в теле выпуска встали ДВА «Добавлено» и ДВА
    «Изменено». Читателю это выглядит как две разные группы, хотя группа
    одна; а разделить их обратно нечем — порядок внутри уже перемешан.

    Разбор идёт по строкам, а не выражением через весь текст: заголовок
    секции и запись различаются началом строки, и этого достаточно.
    """
    by_title = {TITLES[s]: s for s in SECTIONS}
    found: dict[str, list[str]] = {s: [] for s in SECTIONS}
    head, _, tail = text.partition(UNRELEASED)
    if not tail:
        return found
    section = None
    for line in tail.splitlines():
        if line.startswith("## ["):        # начался следующий выпуск
            break
        if line.startswith("### "):
            section = by_title.get(line[4:].strip())
            continue
        if section and line.startswith("- "):
            found[section].append(line[2:].strip())
    return found


def render(found: dict[str, list[str]]) -> str:
    out = []
    for section in SECTIONS:
        if not found[section]:
            continue
        out.append(f"### {TITLES[section]}\n")
        out += [f"- {line}" for line in sorted(found[section])]
        out.append("")
    return "\n".join(out).rstrip() + "\n" if out else ""


def missing_releases() -> tuple[list[str], str | None]:
    """Теги выпусков, у которых нет своего раздела в журнале.

    ПОЧЕМУ ЭТО СПРАШИВАЕТСЯ ЗДЕСЬ. Раздел закрывает выпуск, но заметить
    незакрытый может только тот, кто читает журнал целиком, — а его читают
    сверху и до первого знакомого заголовка. Замер: `v1.1.0` вышел 28 августа,
    и 42 его записи остались в [Unreleased]; нашлось это через два выпуска и
    не проверкой.
    """
    found, err = history_metrics.tags(ROOT)
    if err:
        return [], err
    have = set(RELEASE_RE.findall(CHANGELOG.read_text(encoding="utf-8")))
    return [t for t in found
            if history_metrics.release(t) not in have], None


def close(tag: str, date: str) -> int:
    """Переименовывает [Unreleased] в раздел выпуска и заводит пустой заново."""
    text = CHANGELOG.read_text(encoding="utf-8")
    if UNRELEASED not in text:
        print(f"закрывать нечего: в {CHANGELOG.name} нет раздела {UNRELEASED!r}",
              file=sys.stderr)
        return 2
    num = history_metrics.release(tag)
    if f"## [{num}]" in text:
        print(f"раздел [{num}] уже есть — номера не переиспользуются",
              file=sys.stderr)
        return 1
    head, _, tail = text.partition(UNRELEASED)
    cut = tail.index("## [") if "## [" in tail else len(tail)
    body, rest = tail[:cut], tail[cut:]
    if not body.strip():
        print("раздел [Unreleased] пуст: выпуск без записей читается как "
              "«ничего не изменилось» — хуже, чем отсутствие выпуска (075)",
              file=sys.stderr)
        return 1
    CHANGELOG.write_text(
        f"{head}{UNRELEASED}\n\n{EMPTY_NOTE}\n\n## [{num}] — {date}{body}{rest}",
        encoding="utf-8")
    print(f"раздел [{num}] закрыт датой {date}; [Unreleased] заведён пустым")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="только проверить")
    mode.add_argument("--preview", action="store_true", help="показать сборку")
    mode.add_argument("--collect", action="store_true", help="собрать в [Unreleased]")
    mode.add_argument("--close", metavar="ТЕГ",
                      help="закрыть [Unreleased] разделом выпуска")
    ap.add_argument("--date", default=dt.date.today().isoformat(),
                    help="дата выпуска для --close; по умолчанию сегодня")
    ap.add_argument("--added-since", metavar="REF",
                    help="спросить у ДОБАВЛЕННЫХ с этой точки починок, "
                         "тянут ли они на правило")
    ap.add_argument("--require-entry", action="store_true",
                    help="изменение, трогающее поведение, обязано нести запись "
                         "журнала — либо освобождение строкой «Журнал: не "
                         "требуется — причина»")
    ap.add_argument("--paths-from", type=Path, metavar="ФАЙЛ",
                    help="файл со списком изменённых путей, по строке на путь")
    ap.add_argument("--body-file", type=Path, metavar="ФАЙЛ",
                    help="тело изменения: в нём ищется освобождение")
    args = ap.parse_args()

    # ── запись едет вместе с изменением (правило 138) ──────────────────────
    if args.require_entry:
        if args.paths_from is None:
            print("проверка не отработала: --require-entry без --paths-from — "
                  "спрашивать не о чем", file=sys.stderr)
            return 2
        try:
            paths = [s.strip() for s in
                     args.paths_from.read_text(encoding="utf-8").splitlines()
                     if s.strip()]
        except OSError as exc:
            print(f"проверка не отработала: список путей не прочитан — {exc}",
                  file=sys.stderr)
            return 2
        body = ""
        if args.body_file is not None:
            try:
                body = args.body_file.read_text(encoding="utf-8")
            except OSError as exc:
                print(f"проверка не отработала: тело изменения не прочитано — "
                      f"{exc}", file=sys.stderr)
                return 2
        нужна, почему = entry_required(paths, body)
        if нужна:
            print(почему + ".\n\n  Решение оседает артефактом ТЕМ ЖЕ заходом, а "
                  "не перед выпуском (правило 138):\n  отложенная запись "
                  "означает, что следующее окно разбирает тот же вопрос "
                  "заново.\n  Выход назван: строка «Журнал: не требуется — "
                  "<причина>» в теле изменения.", file=sys.stderr)
            return 1
        print(почему)
        return 0

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not FRAGMENTS.is_dir():
        print(f"проверка не отработала: нет каталога {FRAGMENTS.relative_to(ROOT)}",
              file=sys.stderr)
        return 2
    if not CHANGELOG.exists():
        print(f"проверка не отработала: нет {CHANGELOG.relative_to(ROOT)} — "
              "собирать некуда", file=sys.stderr)
        return 2

    if args.close:
        return close(args.close, args.date)

    found, problems = validate()

    if args.added_since:
        paths, err = added_since(args.added_since)
        if err:
            print(f"проверка не отработала: список добавленных фрагментов не "
                  f"получен — {err}", file=sys.stderr)
            return 2
        problems += verdict_problems(paths)

    # У КАЖДОГО ТЕГА ВЫПУСКА — СВОЙ РАЗДЕЛ. Спрашивается всегда, кроме сборки
    # и показа: те правят или печатают [Unreleased] и о вышедшем не говорят.
    if not (args.collect or args.preview):
        missing, err = missing_releases()
        if err:
            print(f"проверка не отработала: теги выпусков не читаются — {err}",
                  file=sys.stderr)
            return 2
        for tag in missing:
            problems.append(
                f"выпуск {tag} состоялся, а раздела [{history_metrics.release(tag)}] "
                "в журнале нет. Его записи остались в [Unreleased], где их "
                "читают как ещё не вышедшие — закройте: "
                f"python scripts/collect_changelog.py --close {tag}")

    # ── исход 1 ────────────────────────────────────────────────────────────
    if problems:
        print("фрагменты журнала не в порядке:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        # Пояснение печатается только к своей находке: приложенное к чужой,
        # оно отправляет чинить не то (правило 158).
        if any("тянет ли она на правило" in p for p in problems):
            print("\n  Вопрос «тянет ли эта поломка на правило» задаётся здесь "
                  "потому, что\n  здесь инцидент ещё цел: известны причина, цена и "
                  "чем чинили. Ответ\n  «нет» так же полезен, как «да», — но "
                  "только если он записан (026).", file=sys.stderr)
        return 1

    body = render(found)
    total = sum(len(v) for v in found.values())

    if args.preview:
        print(body or "фрагментов нет — собирать нечего")
        return 0

    if args.collect:
        text = CHANGELOG.read_text(encoding="utf-8")
        if UNRELEASED not in text:
            print(f"проверка не отработала: в {CHANGELOG.name} нет раздела "
                  f"{UNRELEASED!r}", file=sys.stderr)
            return 2
        if not body:
            print("фрагментов нет — собирать нечего")
            return 0
        # СЛИЯНИЕ, А НЕ ВСТАВКА СВЕРХУ. Раздел могли собрать раньше — тогда
        # в нём уже есть записи, и новый блок обязан войти в те же секции, а
        # не встать вторым комплектом заголовков рядом.
        was = existing(text)
        merged = {s: sorted(set(was[s]) | set(found[s])) for s in SECTIONS}
        head, _, tail = text.partition(UNRELEASED)
        rest = tail[tail.index("## ["):] if "## [" in tail else ""
        CHANGELOG.write_text(f"{head}{UNRELEASED}\n\n{render(merged)}\n{rest}",
                             encoding="utf-8")
        for path in fragments():
            path.unlink()
        print(f"собрано записей: {total}, в разделе стало "
              f"{sum(len(v) for v in merged.values())}; фрагменты удалены")
        return 0

    # ── исход 0 ────────────────────────────────────────────────────────────
    print(f"фрагменты журнала в порядке: {total} записей в {len(fragments())} файлах")
    return 0


if __name__ == "__main__":
    sys.exit(main())
