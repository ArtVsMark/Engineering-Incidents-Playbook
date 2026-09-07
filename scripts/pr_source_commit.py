#!/usr/bin/env python3
"""Заголовок изменения берётся у коммита ЭТОЙ ветки, а не у первого попавшегося.

ИНЦИДЕНТ, ЗАМЕР 7 сентября. Конвейер собирает заголовок и тело изменения из
ПЕРВОГО коммита в диапазоне `origin/main..HEAD`. Ветка, начатая поверх другой
ветки, отдаёт в этом диапазоне сначала ЧУЖИЕ коммиты, и заголовок уезжает
чужой. Наступило дважды подряд:

  • #368 «fix(bindings): отложенное — не долг, но и не исчезнувшее (177, 146)» —
    слово в слово заголовок #367, слитого получасом раньше;
  • #376 ушёл в общую ветку под заголовком работы про следы, а собственную
    работу про сверку контрактов пришлось открывать заново (#377).

ПОЧЕМУ ДИАПАЗОН НЕ СУЖАЕТСЯ САМ. Слияние здесь уплотняющее: коммиты соседней
ветки не становятся предками общей — в `main` встаёт ОДИН новый коммит с другим
отпечатком. Поэтому `origin/main..HEAD` держит чужие коммиты и после того, как
их содержимое слито, а `git merge-base` указывает на точку ДО них. Ни диапазон,
ни точка расхождения соседа не видят (тот же довод записан в agent-pr.yml
рядом с проверкой содержимого).

ЧТО ВИДНО. Уплотняющее слияние ставит заголовком нового коммита в общей ветке
заголовок изменения, а его площадка берёт из первого коммита ветки — того
самого. Значит чужой коммит опознаётся по совпадению заголовка с уже стоящим в
общей ветке, и это не догадка о содержимом, а замер по истории.

ГРАНИЦА, КОТОРУЮ ВЫБОР НЕ ПЕРЕХОДИТ. Соседнюю ветку, ещё НЕ слитую, он не
отличит: её заголовка в общей ветке нет. Это остаток, а не оговорка — ветка
поверх неслитой ветки нарушает 132 сама по себе, и ловить это надо там, а не
здесь. Не судит выбор и о содержимом: два разных изменения с одинаковым
заголовком он разведёт неверно, и это осознанный размен — заголовок ветки
повторяет заголовок уже слитой работы только при копировании.

ПОЧЕМУ ОТДЕЛЬНЫМ СКРИПТОМ, А НЕ СТРОКОЙ В ПРОГОНЕ. Прежний выбор был строкой
оболочки внутри `agent-pr.yml`, и проверить его можно было только толчком
настоящей ветки — то есть после того, как заголовок уже уехал. Разбор в скрипте
спрашивается набором на выдуманной истории (018, 139).

Запуск:
  python scripts/pr_source_commit.py --base main [--root .] [--head HEAD]

Печатает отпечаток коммита, дающего заголовок и тело.

Исходы:
  0 — коммит назван;
  1 — сверх общей ветки коммитов нет, открывать нечего;
  2 — выбор не отработал.

Реализует правила каталога:
  132 — одна тема на изменение: заголовок обязан говорить о ЕЁ теме;
  049 — состояние вычисляется по живым артефактам: история спрашивается у git,
        а не хранится реестром «чей это коммит»;
  039 — три исхода, и третий не молчит;
  158 — третий исход называет предмет: команду git, которая не ответила.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(root: Path, *args: str) -> tuple[int, str, str]:
    """Вызов git с явной кодировкой (176): локаль раннера здесь не решает."""
    done = subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, encoding="utf-8")
    return done.returncode, done.stdout, done.stderr


def base_subjects(root: Path, base: str) -> tuple[set[str] | None, str | None]:
    """Заголовки коммитов общей ветки. Вторым — причина отказа с адресом."""
    code, out, err = git(root, "log", "--format=%s", base)
    if code != 0:
        return None, f"`git log --format=%s {base}` — {err.strip()[:160] or f'код {code}'}"
    return {line for line in out.splitlines() if line.strip()}, None


def choose(root: Path, base: str, head: str = "HEAD") -> tuple[str | None, int, str]:
    """Отпечаток, исход и объяснение — в том виде, в каком их печатает main."""
    code, out, err = git(root, "rev-list", "--reverse", f"{base}..{head}")
    if code != 0:
        return None, 2, (f"выбор не отработал: `git rev-list {base}..{head}` — "
                         f"{err.strip()[:160] or f'код {code}'}")
    commits = [line.strip() for line in out.splitlines() if line.strip()]
    if not commits:
        return None, 1, f"сверх {base} коммитов нет"

    subjects, why = base_subjects(root, base)
    if why:
        return None, 2, f"выбор не отработал: {why}"

    for sha in commits:
        code, out, err = git(root, "log", "-1", "--format=%s", sha)
        if code != 0:
            return None, 2, (f"выбор не отработал: `git log -1 --format=%s {sha}` — "
                             f"{err.strip()[:160] or f'код {code}'}")
        subject = out.strip()
        if subject in subjects:
            continue
        return sha, 0, f"заголовок даёт {sha[:8]}: «{subject}»"

    # ВСЕ ЗАГОЛОВКИ УЖЕ СТОЯТ В ОБЩЕЙ ВЕТКЕ. Своей работы у ветки нет, а
    # «неизвестно» и «чужое» — разные ответы (051): выбор не молчит и не
    # выдумывает, он называет первый коммит и говорит, что это запасной путь.
    return commits[0], 0, (f"ни один из {len(commits)} коммитов не отличается "
                           f"заголовком от {base}; запасной путь — первый "
                           f"коммит, {commits[0][:8]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень дерева; по умолчанию сам этот репозиторий")
    parser.add_argument("--base", default="origin/main",
                        help="общая ветка; по умолчанию origin/main")
    parser.add_argument("--head", default="HEAD",
                        help="голова ветки; по умолчанию HEAD")
    args = parser.parse_args(argv)

    sha, code, why = choose(args.root, args.base, args.head)
    if code == 0:
        print(why, file=sys.stderr)
        print(sha)
        return 0
    print(why, file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
