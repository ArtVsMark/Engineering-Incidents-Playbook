"""Гейт эволюции метрик: строка на каждый выпуск и числа, сверенные с тегом.

Подделка — НАСТОЯЩИЙ репозиторий с настоящим тегом: гейт выгружает дерево
через `git archive`, и подмена его входа проверяла бы разбор таблицы, а не
гейт (правило 150).

Чистый случай нарочно считает числа руками: два правила, две области, одна
локальная ссылка на всё дерево, один ответ «ничем» из двух действующих.
Возьми мы ожидаемое у самого скрипта — набор подтверждал бы, что скрипт
согласен сам с собой, и молчал бы ровно про ту арифметику, ради которой
заведён (правило 146).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import history_metrics as hm
from conftest import write

ROW = "| v1.0.0 | 2 | 2 | 1 | 1 из 2 | Первый выпуск подделки |"

HISTORY = """# История подделки

## Эволюция метрик каталога

| Релиз | Правил | Областей | Ссылок | Ничем | Ключевое |
|---|---:|---:|---:|---:|---|
{rows}

Числа живут только строками таблицы: это снимок на момент выпуска.
"""

RULE = """# {title}

**Область.** {areas}

**Правило.** Что-нибудь одно.
"""

BINDINGS = """{
  "schema": "1.2",
  "rules": {
    "001": {"status": "active", "mechanism": "gate", "where": "подделка"},
    "002": {"status": "active", "mechanism": "none", "why": "подделка"},
    "003": {"status": "not-applicable", "why": "подделка"}
  }
}
"""


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True)


def fake(repo: Path, rows: str = ROW) -> Path:
    """Репозиторий с одним выпуском: две записи и ровно одна локальная ссылка."""
    write(repo / "HISTORY.md", HISTORY.format(rows=rows))
    # Единственная локальная ссылка во всём дереве — она и есть «Ссылок: 1».
    write(repo / "rules/ru/001-first.md",
          RULE.format(title="Первое", areas="гейты, тесты")
          + "\nСмежное: [002](002-second.md)\n")
    write(repo / "rules/ru/002-second.md",
          RULE.format(title="Второе", areas="тесты"))
    write(repo / ".rules/bindings.json", BINDINGS)

    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "Владелец")
    git(repo, "config", "user.email", "owner@example.com")
    git(repo, "add", "-A")
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "подделка")
    git(repo, "tag", "v1.0.0")
    return repo


def test_снимок_сошёлся_с_деревом_тега(repo):
    """Счастливый случай считает числа руками: иначе отказ ниже означал бы
    только несогласие скрипта с собой."""
    assert hm.main(["--root", str(fake(repo)), "--check"]) == 0


def test_выпуск_без_строки_это_отказ(repo):
    """Ровно то, что случилось дважды: тег есть, строки нет, и никто не заметил."""
    fake(repo, rows="")

    assert hm.main(["--root", str(repo), "--check"]) == 1


def test_число_разошлось_с_деревом_это_отказ(repo):
    """Снимок, разошедшийся с тем, что был снимком, — вписанное руками число."""
    fake(repo, rows=ROW.replace("| 1668 |", "| 1 |").replace("| 2 | 2 |", "| 9 | 2 |"))

    assert hm.main(["--root", str(repo), "--check"]) == 1


def test_метрика_ничем_считается_из_действующих(repo):
    """Знаменатель — не украшение: без него 1 неотличима от 1 из 200."""
    fake(repo, rows=ROW.replace("1 из 2", "1 из 3"))

    assert hm.main(["--root", str(repo), "--check"]) == 1


def test_пустое_ключевое_это_отказ(repo):
    fake(repo, rows="| v1.0.0 | 2 | 2 | 1 | 1 из 2 |  |")

    assert hm.main(["--root", str(repo), "--check"]) == 1


def test_ссылка_в_ключевом_это_отказ(repo):
    """Ссылка в ячейке сдвигает число ссылок в том же дереве, по которому
    строка и сверяется, — строка становится неверной о самой себе."""
    fake(repo, rows=ROW.replace("Первый выпуск подделки",
                                "Первый выпуск, см. [журнал](CHANGELOG.md)"))

    assert hm.main(["--root", str(repo), "--check"]) == 1


def test_строка_без_тега_это_отказ(repo):
    """Строка, поставленная вперёд выпуска, обещает то, чего не было."""
    fake(repo, rows=ROW + "\n| v9.9.0 | 2 | 2 | 1 | 1 из 2 | Ещё не вышло |")

    assert hm.main(["--root", str(repo), "--check"]) == 1


def test_нет_истории_это_третий_исход(repo):
    """«Нечего проверять» не равно «всё хорошо» (039): документа может не быть
    у потребителя заготовки, но тогда гейт обязан сказать это, а не зеленеть."""
    fake(repo)
    (repo / "HISTORY.md").unlink()

    assert hm.main(["--root", str(repo), "--check"]) == 2


def test_нет_тегов_это_третий_исход(repo):
    """Мелкий клон тегов не приносит: без них сверять не с чем, и зелёное
    здесь означало бы «выпусков не было» (075)."""
    fake(repo)
    git(repo, "tag", "-d", "v1.0.0")

    assert hm.main(["--root", str(repo), "--check"]) == 2


def test_второй_строки_одному_выпуску_не_бывает(repo):
    """Номера не переиспользуются, и дописать выпуск дважды нельзя."""
    fake(repo)

    assert hm.main(["--root", str(repo), "--add", "v1.0.0",
                    "--key", "второй раз", "--at-tag"]) == 1


def test_дописанная_строка_проходит_свой_же_гейт(repo):
    """Пара «дописать» и «сверить» обязана сходиться: иначе выпуск оставлял бы
    после себя красное на общей ветке."""
    fake(repo, rows="")

    assert hm.main(["--root", str(repo), "--add", "v1.0.0",
                    "--key", "первый выпуск", "--at-tag"]) == 0
    assert hm.main(["--root", str(repo), "--check"]) == 0
