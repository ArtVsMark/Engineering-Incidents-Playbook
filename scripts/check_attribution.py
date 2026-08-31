#!/usr/bin/env python3
"""Сверяет трейлеры авторства с согласованным списком до слияния.

Реализует правила каталога:
  123 — атрибуция проверяется в конечной истории, а не в коммите ветки;
  156 — трейлер читается из хвостового блока: прозаическое упоминание
        директивой не считается, иначе отказ бьёт по подробным сообщениям;
        трейлеры сверяются со списком согласованных имён;
  039 — у проверки три исхода, а не два;
  114 — миграция идёт от текущей версии, а не от нуля: требование действует
        с объявленного коммита, а не задним числом на всю историю;
  046 — пробел называется поимённо: коммиты без атрибуции печатаются числом;
  041 — два честных числа вместо одного усреднённого: сколько всего и сколько
        без атрибуции, а не «процент покрытия»;
  068 — список авторов разрешительный: имя, которого в нём нет, отвергается.

Два режима, потому что вопроса два.

  Коммиты ветки  (--range)  — проверка ДО слияния: историю ветки ещё можно
  переписать, и находка здесь чинится автором. Здесь же — и только здесь —
  проверяется ПОЛЕ АВТОРА: при слиянии объединяющим коммитом именно оно едет
  в общую ветку. Авторство при уплотнении задаёт не оно, а тот, кто открыл
  изменение, и эта проверка его не заменяет (правило 131).

  Первопредки    (--first-parents) — проверка ПОСЛЕ: коммит общей ветки
  составляет площадка, и в итоговой истории атрибуции может не быть вовсе при
  зелёном гейте на каждом изменении. Починить прошлое нельзя — но не знать о
  нём хуже (правила 002, 075).

Исходы:
  0 — чисто;
  1 — есть находки;
  2 — проверка не отработала (нет git, нет диапазона, нет списка имён).

Запуск:  python scripts/check_attribution.py                 # origin/main..HEAD
         python scripts/check_attribution.py --range A..B
         python scripts/check_attribution.py --first-parents  # origin/main
         python scripts/check_attribution.py --first-parents --ref main --since d1297ff
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

#: Дом самого скрипта. От него берутся ТОЛЬКО умолчания: список имён и начало
#: отсчёта принадлежат проверяемому проекту, а не инструменту, и у третьего
#: потребителя они другие (задача #54, правило 090 — общее уезжает вверх, а не
#: копируется вбок).
ROOT = Path(__file__).resolve().parent.parent
AUTHORS = ROOT / ".github" / "authors.txt"

#: С этого коммита атрибуция обязательна. Раньше него история писалась без
#: трейлеров, и переписать её нельзя — общая ветка защищена (правило 123).
#: Требовать задним числом значит требовать невозможного (правило 114).
BASELINE = "d1297ff"

COAUTHOR = re.compile(r"^Co-Authored-By:\s*(.+?)\s*$", re.M | re.I)
SESSION = re.compile(r"^Claude-Session:\s*(.+?)\s*$", re.M | re.I)
#: Строка хвостового блока: `Ключ: значение`, и ключ без пробелов.
TRAILER_LINE = re.compile(r"^[A-Za-z][A-Za-z0-9-]*:\s")


def tail(body: str) -> str:
    """Хвостовой блок сообщения: последний абзац из строк «Ключ: значение».

    ПОЧЕМУ НЕ «ЛЮБАЯ СТРОКА». Раньше трейлеры искались по всему телу с `re.M`,
    и признаком служило начало строки. Перенос строки в проработанном абзаце
    ставит первым любое слово без умысла автора: 30 августа этот гейт отверг
    изменение витрины ArtVsMark/ArtVsMark#95, назвав соавтором середину фразы
    «…Co-authored-by github-actions[bot] в уплотнённый коммит…». Изменение
    чинило красную общую ветку — отказ задержал починку того самого гейта,
    который его вынес (правило 156).

    ГРАНИЦА. Абзац считается хвостовым, только если ВСЕ его непустые строки —
    пары «ключ: значение». Один прозаический хвост делает блок прозой целиком:
    иначе разбор снова начнёт угадывать, где кончается объяснение.
    """
    blocks = [b for b in body.replace("\r\n", "\n").split("\n\n") if b.strip()]
    if not blocks:
        return ""
    last = [ln for ln in blocks[-1].splitlines() if ln.strip()]
    return "\n".join(last) if all(TRAILER_LINE.match(ln) for ln in last) else ""


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=True).stdout


#: Заголовок, после которого перечисляются АВТОРЫ, а не соавторы. До него —
#: соавторы, как было: файл читается старыми потребителями без изменений.
AUTHORS_HEAD = "[авторы"


def agreed(authors: Path) -> tuple[set[str], set[str]]:
    """Согласованные соавторы и согласованные авторы — двумя списками.

    ПОЧЕМУ ДВА СПИСКА СВЕРЯЮТСЯ ПО-РАЗНОМУ. Соавтор — это ТЕКСТ, написанный
    рукой в теле коммита, и там «один и тот же человек под двумя именами» и
    есть та поломка, ради которой список заведён: сверка точная, имя и почта.
    Автор — это ПОЛЕ, которое подставляет настройка машины, и площадка
    опознаёт человека по почте: имя там местная переменная, разная на разных
    машинах. Сверять автора по имени значит краснеть на смене настройки, а не
    на смене человека, — ложный отказ (правило 097).

    Замер, который это показал: за одни сутки в этом репозитории 18 коммитов
    подписаны `ArtVsMark <arvs.markitanov@gmail.com>` и 21 —
    `Artem Markitanov <86671904+ArtVsMark@users.noreply.github.com>`. Один
    человек, одна почта в GitHub, два написания имени.

    ПОЧЕМУ ВТОРОЙ СПИСОК РАЗРЕШИТЕЛЬНЫЙ. Проверка автора была запретительной:
    «автором не должен стоять известный соавтор». Она ловит ровно одно
    написание — `Claude <noreply@anthropic.com>` — и молчит на `claude[bot]`,
    у которого другое имя и другая почта. Именно так и вышло: изменение #78
    уехало в общую ветку автором `claude[bot]`, гейт не сказал ничего.

    Это 068 на живом предмете: запрет по чужим именам отваливается целиком,
    когда сторона переименовалась. Разрешительный список ломается в другую
    сторону — новый человек получает отказ и приходит с этим, а не уезжает
    молча в защищённую историю, где переписать уже нечем (правило 114).
    """
    co: set[str] = set()
    people: set[str] = set()
    target = co
    for raw in authors.read_text(encoding="utf-8").split("\n"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith(AUTHORS_HEAD):
            target = people
            continue
        target.add(line)
    return co, {mail_of(l) for l in people if mail_of(l)}


def mail_of(line: str) -> str:
    """Почта из строки «Имя <почта>». Личность человека для площадки — она."""
    m = re.search(r"<([^>]+)>", line)
    return m.group(1).strip().lower() if m else ""


def first_parents(repo: Path, ref: str, since: str | None, names: set[str]) -> int:
    """Атрибуция в итоговой истории общей ветки.

    Спрашиваются ВСЕ первопредки, а не только объединяющие коммиты. Это не
    придирка: способ слияния — настройка репозитория, и при squash слияний в
    истории не остаётся вовсе. Проверка, привязанная к виду коммита, после
    смены настройки нашла бы ноль предметов и промолчала бы зелёным — ровно то,
    от чего предостерегает правило 075.
    """
    try:
        git(repo, "rev-parse", "--verify", ref)
    except subprocess.CalledProcessError:
        print(f"проверка не отработала: {ref} недоступен — "
              "нужен полный клон и общая ветка", file=sys.stderr)
        return 2

    scope = f"{since}..{ref}" if since else ref
    try:
        out = git(repo, "log", "--first-parent",
                  "--format=%H%x00%s%x00%b%x00", scope)
    except subprocess.CalledProcessError as e:
        print(f"проверка не отработала: {scope!r} не разобран — "
              f"{e.stderr.strip()}", file=sys.stderr)
        return 2

    records = [r for r in out.split("\x00\n") if r.strip()]
    if not records:
        # Пусто — это состояние, а не тишина (правило 027). И это не «чисто»:
        # проверка, которой нечего смотреть, не подтверждает ничего (075).
        print(f"проверка не отработала: в {scope} нет первопредков — "
              "подтверждать нечего", file=sys.stderr)
        return 2

    missing: list[str] = []
    stranger: list[str] = []
    for rec in records:
        # Формат здесь трёхпольный: %H %s %b. Автора первопредка не
        # спрашиваем — при уплотнении его задаёт не подпись коммита, а тот,
        # кто открыл изменение (правило 131), и чинить это здесь нечем.
        sha, subject, body = (rec.split("\x00") + ["", ""])[:3]
        sha, subject = sha.strip(), subject.strip()
        coauthors = [m.strip() for m in COAUTHOR.findall(tail(body))]
        if not coauthors:
            missing.append(f"{sha[:7]} {subject[:64]}")
            continue
        for name in coauthors:
            if name not in names:
                stranger.append(f"{sha[:7]} соавтор вне списка: {name!r}")

    total = len(records)
    if missing or stranger:
        print(f"атрибуция в итоговой истории {scope}: "
              f"первопредков {total}, без атрибуции {len(missing)}",
              file=sys.stderr)
        for line in missing[:5]:
            print(f"  • {line}", file=sys.stderr)
        if len(missing) > 5:
            print(f"  • …и ещё {len(missing) - 5}", file=sys.stderr)
        for line in stranger:
            print(f"  • {line}", file=sys.stderr)
        print("\n  Прошлое не переписать: общая ветка защищена, и это долг, а не "
              "задача (правило 114).\n  Красное здесь означает, что коммит в общей "
              "ветке составляется без трейлеров — чинится\n  на стороне слияния, "
              "а не правкой истории. Объявить долг и спрашивать с\n  определённого "
              "коммита — ключ --since.", file=sys.stderr)
        return 1

    print(f"атрибуция в итоговой истории в порядке: {scope}, "
          f"объединяющих коммитов {total}, без атрибуции 0")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--range", default=None,
                    help="диапазон коммитов, по умолчанию origin/main..HEAD")
    ap.add_argument("--first-parents", action="store_true",
                    help="проверить первопредки общей ветки, а не коммиты ветки")
    ap.add_argument("--ref", default="origin/main",
                    help="общая ветка для --first-parents, по умолчанию origin/main")
    ap.add_argument("--repo", default=str(ROOT),
                    help="репозиторий, чью историю проверяем; по умолчанию тот, "
                         "где лежит скрипт")
    ap.add_argument("--authors", default=None,
                    help="список согласованных имён проверяемого проекта; "
                         "по умолчанию .github/authors.txt рядом со скриптом")
    ap.add_argument("--baseline", default=BASELINE,
                    help="коммит, с которого атрибуция обязательна; пустая "
                         "строка отключает подрезку")
    # Требование трейлеров — договорённость про АГЕНТСКИЕ коммиты, и по
    # умолчанию коммит человека со стороны она не отвергает: «без атрибуции N»
    # честным числом это решение по 041. Но потребителю, у которого весь поток
    # идёт через облачные окна, нужен отказ, а выразить его было нечем
    # (задача #80, найдено первым сторонним потребителем). Умолчание сохраняет
    # и поведение, и прежнее решение — включает его проект, а не инструмент.
    ap.add_argument("--require-declared-author", action="store_true",
                    help="автором каждого коммита обязан стоять человек из "
                         "раздела «[авторы]» списка. Ключ отдельный и "
                         "необязательный: у проекта такого раздела может не "
                         "быть, и тогда требовать его нечем")
    ap.add_argument("--require-coauthor", action="store_true",
                    help="считать отказом коммит вовсе без атрибуции; по "
                         "умолчанию такие только считаются и печатаются числом")
    ap.add_argument("--since", default=None,
                    help="объявленное начало для --first-parents: раньше него "
                         "не спрашивать. Без него спрашивается вся история — "
                         "долг виден числом, а не спрятан подрезкой")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    authors = Path(args.authors).resolve() if args.authors else AUTHORS
    baseline = args.baseline

    # ── исход 2: проверка не отработала ────────────────────────────────────
    try:
        names, people = agreed(authors)
    except OSError as e:
        print(f"проверка не отработала: список имён не прочитан — {e}", file=sys.stderr)
        return 2
    if args.require_declared_author and not people:
        print(f"проверка не отработала: запрошен разрешительный список авторов, "
              f"а раздел «[авторы]» в {authors} пуст — требовать нечем",
              file=sys.stderr)
        return 2
    if not names:
        print(f"проверка не отработала: {authors} пуст — "
              "сверять не с чем, а молча пропускать нельзя", file=sys.stderr)
        return 2

    if args.first_parents:
        return first_parents(repo, args.ref, args.since, names)

    rng = args.range
    if rng is None:
        try:
            git(repo, "rev-parse", "--verify", "origin/main")
            rng = "origin/main..HEAD"
        except subprocess.CalledProcessError:
            print("проверка не отработала: origin/main недоступен, диапазон "
                  "не определён — задайте --range", file=sys.stderr)
            return 2
    # Диапазон не уходит глубже объявленного начала: до него история писалась
    # без трейлеров, переписать её нельзя, и требовать оттуда нечего (114).
    try:
        if not baseline:
            raise subprocess.CalledProcessError(1, "git")  # подрезка отключена
        git(repo, "merge-base", "--is-ancestor", baseline, "HEAD")
        low, _, high = rng.partition("..")
        # Сравниваем разрешённые хеши, а не строки: «d1297ff» и полный хеш —
        # один коммит, и сообщать о подрезке там, где её нет, значит шуметь.
        same = low and git(repo, "rev-parse", low).strip() == git(repo, "rev-parse", baseline).strip()
        if low and not same and subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", low, baseline],
            capture_output=True,
        ).returncode == 0:
            rng = f"{baseline}..{high or 'HEAD'}"
            print(f"диапазон подрезан до объявленного начала: {rng}")
    except subprocess.CalledProcessError:
        pass  # начала нет в этой истории — проверяем, что просили

    try:
        # Слияния пропускаем: их сообщение составляет площадка, а не автор.
        out = git(repo, "log", "--no-merges",
                  "--format=%H%x00%an <%ae>%x00%s%x00%b%x00", rng)
    except subprocess.CalledProcessError as e:
        print(f"проверка не отработала: диапазон {rng!r} не разобран — "
              f"{e.stderr.strip()}", file=sys.stderr)
        return 2

    records = [r for r in out.split("\x00\n") if r.strip()]
    if not records:
        print(f"в диапазоне {rng} новых коммитов нет — проверять нечего")
        return 0

    # ── исход 1: находки ───────────────────────────────────────────────────
    findings: list[str] = []
    unattributed = 0
    for rec in records:
        sha, author, subject, body = (rec.split("\x00") + ["", "", ""])[:4]
        sha, author, subject = sha.strip(), author.strip(), subject.strip()
        coauthors = [m.strip() for m in COAUTHOR.findall(tail(body))]
        session = SESSION.search(tail(body))

        # Подпись агента принадлежит трейлеру, а не полю автора. Авторство в
        # общей ветке этим НЕ чинится — его задаёт тот, кто открыл изменение
        # (правило 131, замер по шести изменениям). Проверка остаётся потому,
        # что при слиянии объединяющим коммитом в историю едет именно эта
        # подпись, и тогда она решает.
        if author in names:
            findings.append(
                f"{sha[:7]} {subject[:56]}\n"
                f"        автором стоит {author!r} — это согласованный "
                f"СОАВТОР, а не автор\n"
                f"        squash перенесёт эту подпись в общую ветку, и там "
                f"её не переписать")
        elif args.require_declared_author and mail_of(author) not in people:
            # Разрешительный список, а не запретительный. Запрет ловил одно
            # написание и молчал на `claude[bot]` — так #78 и уехало в общую
            # ветку авторства бота (правило 068, задача #79).
            findings.append(
                f"{sha[:7]} {subject[:56]}\n"
                f"        автор {author!r} не объявлен в разделе «[авторы]»\n"
                f"        объявлены почты: "
                f"{', '.join(sorted(people)) or '— никто'}")

        for name in coauthors:
            if name not in names:
                findings.append(
                    f"{sha[:7]} {subject[:56]}\n"
                    f"        соавтор вне списка: {name!r}\n"
                    f"        согласованы: {', '.join(sorted(names))}")
        if session and not coauthors:
            findings.append(
                f"{sha[:7]} {subject[:56]}\n"
                f"        есть Claude-Session, но нет Co-Authored-By: "
                f"след сессии без соавторства")
        if not coauthors and not session:
            unattributed += 1
            if args.require_coauthor:
                findings.append(
                    f"{sha[:7]} {subject[:56]}\n"
                    f"        атрибуции нет вовсе, а проект её требует "
                    f"(--require-coauthor)")

    if findings:
        print("атрибуция расходится со списком:", file=sys.stderr)
        for f in findings:
            print(f"  • {f}", file=sys.stderr)
        return 1

    # ── исход 0 ────────────────────────────────────────────────────────────
    print(f"атрибуция в порядке: {len(records)} коммитов в {rng}, "
          f"без атрибуции {unattributed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
