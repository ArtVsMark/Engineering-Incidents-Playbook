"""Гейт атрибуции: трейлеры, список согласованных имён и три исхода.

Самый важный скрипт каталога — на нём держится правило 123. Тесты строят
НАСТОЯЩИЕ репозитории во временном каталоге, а не подсовывают разбор строк:
проверка ходит в git, и подделка её входа проверяла бы регулярку, а не гейт.

Отдельно закрыт краевой случай, ради которого скрипт и переписывали: пустой
диапазон — это исход 2, а не «чисто». Проверка, которой нечего смотреть, не
подтверждает ничего (правило 075).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import check_attribution as ca
from conftest import write

AGREED = "Claude <noreply@anthropic.com>"


def run(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True)


def commit(repo: Path, subject: str, body: str = "",
           author: tuple[str, str] = ("Владелец", "owner@example.com")) -> None:
    write(repo / "f.txt", subject)
    run(repo, "add", "-A")
    message = f"{subject}\n\n{body}" if body else subject
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message],
                   check=True, capture_output=True, text=True,
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin",
                        "HOME": str(repo),
                        "GIT_AUTHOR_NAME": author[0],
                        "GIT_AUTHOR_EMAIL": author[1],
                        "GIT_COMMITTER_NAME": "Владелец",
                        "GIT_COMMITTER_EMAIL": "owner@example.com"})


def make_repo(repo: Path) -> Path:
    run(repo, "init", "-q", "-b", "main")
    run(repo, "config", "user.name", "Владелец")
    run(repo, "config", "user.email", "owner@example.com")
    return repo


def authors_file(repo: Path, text: str = AGREED) -> Path:
    return write(repo / ".github" / "authors.txt", text + "\n")


OWNER = "Владелец <owner@example.com>"
BOT = ("claude[bot]", "209825114+claude[bot]@users.noreply.github.com")


def test_список_имён_без_комментариев_и_пустых(repo):
    path = authors_file(repo, f"# комментарий\n\n{AGREED}\n")
    co, people = ca.agreed(path)
    assert co == {AGREED} and people == set()


# ── разрешительный список авторов ─────────────────────────────────────────
#
# Проверка автора была ЗАПРЕТИТЕЛЬНОЙ: «автором не должен стоять известный
# соавтор». Она ловит ровно одно написание и молчит на `claude[bot]`, у
# которого другое имя и другая почта. Так изменение #78 и уехало в общую ветку
# авторства бота, а переписать там нечем (068, 114, задача #79).
#
# Ключ отдельный и по умолчанию выключен: у проекта раздела «[авторы]» может
# не быть, и требовать его тогда — отказ на пустом месте.

def test_раздел_авторов_читается_отдельно_от_соавторов(repo):
    path = authors_file(repo, f"{AGREED}\n\n[авторы]\n{OWNER}\n")
    co, people = ca.agreed(path)
    assert co == {AGREED} and people == {OWNER}


def test_объявленный_автор_проходит(repo, capsys, monkeypatch):
    make_repo(repo)
    commit(repo, "первый", f"Co-Authored-By: {AGREED}")
    commit(repo, "второй", f"Co-Authored-By: {AGREED}")
    path = authors_file(repo, f"{AGREED}\n\n[авторы]\n{OWNER}\n")
    monkeypatch.setattr("sys.argv", [
        "check_attribution.py", "--repo", str(repo), "--range", "HEAD~1..HEAD",
        "--authors", str(path), "--require-declared-author"])
    assert ca.main() == 0


def test_бот_автором_это_находка(repo, capsys, monkeypatch):
    """Тот самый случай: имя и почта другие, запрет молчал."""
    make_repo(repo)
    commit(repo, "первый", f"Co-Authored-By: {AGREED}")
    commit(repo, "от бота", f"Co-Authored-By: {AGREED}", author=BOT)
    path = authors_file(repo, f"{AGREED}\n\n[авторы]\n{OWNER}\n")
    monkeypatch.setattr("sys.argv", [
        "check_attribution.py", "--repo", str(repo), "--range", "HEAD~1..HEAD",
        "--authors", str(path), "--require-declared-author"])
    assert ca.main() == 1
    assert "не объявлен в разделе" in capsys.readouterr().err


def test_без_ключа_бот_автором_проходит_как_раньше(repo, monkeypatch):
    """Здоровый предмет у границы: ключ не должен ломать старых потребителей."""
    make_repo(repo)
    commit(repo, "первый", f"Co-Authored-By: {AGREED}")
    commit(repo, "от бота", f"Co-Authored-By: {AGREED}", author=BOT)
    path = authors_file(repo, f"{AGREED}\n\n[авторы]\n{OWNER}\n")
    monkeypatch.setattr("sys.argv", [
        "check_attribution.py", "--repo", str(repo), "--range", "HEAD~1..HEAD",
        "--authors", str(path)])
    assert ca.main() == 0


def test_ключ_без_раздела_авторов_это_третий_исход(repo, capsys, monkeypatch):
    make_repo(repo)
    commit(repo, "первый", f"Co-Authored-By: {AGREED}")
    commit(repo, "второй", f"Co-Authored-By: {AGREED}")
    path = authors_file(repo, AGREED)
    monkeypatch.setattr("sys.argv", [
        "check_attribution.py", "--repo", str(repo), "--range", "HEAD~1..HEAD",
        "--authors", str(path), "--require-declared-author"])
    assert ca.main() == 2
    assert "требовать нечем" in capsys.readouterr().err


def test_чистая_история_проходит(repo, capsys):
    make_repo(repo)
    commit(repo, "первый", f"Co-Authored-By: {AGREED}")
    commit(repo, "второй", f"Co-Authored-By: {AGREED}")
    assert ca.first_parents(repo, "main", None, {AGREED}) == 0
    assert "без атрибуции 0" in capsys.readouterr().out


def test_коммит_без_трейлера_это_находка(repo, capsys):
    make_repo(repo)
    commit(repo, "с подписью", f"Co-Authored-By: {AGREED}")
    commit(repo, "без подписи")
    assert ca.first_parents(repo, "main", None, {AGREED}) == 1
    err = capsys.readouterr().err
    assert "без атрибуции 1" in err
    assert "без подписи" in err


def test_соавтор_вне_списка_это_находка(repo, capsys):
    make_repo(repo)
    commit(repo, "чужой", "Co-Authored-By: Кто-то Другой <x@example.com>")
    assert ca.first_parents(repo, "main", None, {AGREED}) == 1
    assert "вне списка" in capsys.readouterr().err


def test_объявленное_начало_подрезает_долг(repo, capsys):
    make_repo(repo)
    commit(repo, "старый без подписи")
    old = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()
    commit(repo, "новый", f"Co-Authored-By: {AGREED}")
    # Без --since долг виден числом; с ним — спрашивается только новое.
    assert ca.first_parents(repo, "main", None, {AGREED}) == 1
    assert ca.first_parents(repo, "main", old, {AGREED}) == 0


def test_недоступная_ветка_это_третий_исход(repo, capsys):
    make_repo(repo)
    commit(repo, "один", f"Co-Authored-By: {AGREED}")
    assert ca.first_parents(repo, "такой-ветки-нет", None, {AGREED}) == 2
    assert "не отработала" in capsys.readouterr().err


def test_пустой_диапазон_это_третий_исход(repo, capsys):
    make_repo(repo)
    commit(repo, "один", f"Co-Authored-By: {AGREED}")
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    # Диапазон от головы до головы пуст. Зелёное здесь означало бы, что гейт
    # подтвердил историю, которую не смотрел.
    assert ca.first_parents(repo, "main", head, {AGREED}) == 2
    assert "подтверждать нечего" in capsys.readouterr().err
