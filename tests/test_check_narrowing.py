"""Сужение признака: находится убыль, пропускается прибыль и перенос.

Гейт спрашивается через `main()` на НАСТОЯЩЕМ дереве — с коммитами, диффом и
фрагментом журнала. Разбор диффа проверен самопроверкой скрипта; здесь предмет
другой: доезжает ли решение до кода возврата и различает ли гейт три исхода
(140, 146, 039).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import check_narrowing as cn
from conftest import write


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True, encoding="utf-8")


def дерево(repo: Path, было: str, стало: str, фрагмент: str | None) -> str:
    """Репозиторий с основанием и починкой. Возвращает отпечаток основания."""
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    write(repo / "scripts" / "предмет.py", было + "\n")
    write(repo / "changelog.d" / "older.added.md", "Было.\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "основание")
    основание = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                               check=True, capture_output=True, text=True,
                               encoding="utf-8").stdout.strip()
    write(repo / "scripts" / "предмет.py", стало + "\n")
    if фрагмент is not None:
        write(repo / "changelog.d" / "fix.fixed.md", фрагмент)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "починка")
    return основание


def настроить(monkeypatch, repo: Path) -> None:
    monkeypatch.setattr(cn, "ROOT", repo)
    monkeypatch.setattr(cn, "FRAGMENTS", repo / "changelog.d")


КЛАСС_БЫЛ = 'ПРЕФИКС = re.compile(r"^[ \\t>#-*]*")'
КЛАСС_СТАЛ = 'ПРЕФИКС = re.compile(r"^(?:[ \\t>#-]|\\*(?=\\s))*")'


def test_сужение_без_ответа_о_соседях_находка(monkeypatch, repo, capsys):
    """Инцидент 195 целиком: звёздочка ушла из класса, о соседях молчание.

    Ровно та правка, что уронила буллет разметки в #415. Гейт обязан ответить
    ОТКАЗОМ — иначе он подтверждает только собственную запускаемость (146).
    """
    основание = дерево(repo, КЛАСС_БЫЛ, КЛАСС_СТАЛ, "Починили.\n")
    настроить(monkeypatch, repo)
    assert cn.main(["--range", f"{основание}...HEAD"]) == 1
    сказано = capsys.readouterr().err
    assert "перестал принимать" in сказано
    assert "Соседи:" in сказано


def test_сужение_с_ответом_проходит(monkeypatch, repo):
    """Вторая сторона границы: вопрос задан — гейт молчит.

    Держится ЗАДАННЫЙ вопрос, а не ответ на него: судить об ответе машина не
    может, и требовать его форму значило бы получить форму (182).
    """
    основание = дерево(repo, КЛАСС_БЫЛ, КЛАСС_СТАЛ,
                       "Починили.\n\nСоседи: спросили — буллет `* ` терялся, закрыт случаем.\n")
    настроить(monkeypatch, repo)
    assert cn.main(["--range", f"{основание}...HEAD"]) == 0


def test_расширение_находкой_не_считается(monkeypatch, repo):
    """Прибыль — не убыль. Гейт, краснеющий на расширении, приучал бы к красному."""
    основание = дерево(repo, 'X = re.compile(r"[ab]")',
                       'X = re.compile(r"[abc]")', "Расширили.\n")
    настроить(monkeypatch, repo)
    assert cn.main(["--range", f"{основание}...HEAD"]) == 0


def test_перенос_множества_находкой_не_считается(monkeypatch, repo):
    """Убыло в одном месте, прибыло в другом — счёт по изменению целиком (051)."""
    основание = дерево(repo, 'S = {"a", "b"}',
                       '# переехало ниже\nS = {"a", "b"}', "Переставили.\n")
    настроить(monkeypatch, repo)
    assert cn.main(["--range", f"{основание}...HEAD"]) == 0


def test_нет_каталога_фрагментов_третий_исход(monkeypatch, repo, capsys):
    """Спрашивать ответ негде — это НЕ «ответа нет» (039, 075)."""
    основание = дерево(repo, КЛАСС_БЫЛ, КЛАСС_СТАЛ, "Починили.\n")
    настроить(monkeypatch, repo)
    monkeypatch.setattr(cn, "FRAGMENTS", repo / "нет-такого")
    assert cn.main(["--range", f"{основание}...HEAD"]) == 2
    assert "не отработала" in capsys.readouterr().err


def test_нечитаемый_диапазон_третий_исход(monkeypatch, repo, capsys):
    """Дифф не прочитан — предмет назван, а не спрятан за находкой (158)."""
    дерево(repo, КЛАСС_БЫЛ, КЛАСС_СТАЛ, "Починили.\n")
    настроить(monkeypatch, repo)
    assert cn.main(["--range", "нет-такой-ссылки...HEAD"]) == 2
    сказано = capsys.readouterr().err
    assert "не отработала" in сказано
    assert "нет-такой-ссылки" in сказано


def test_самопроверка_проходит():
    """Разбор диффа бьётся в оба конца — это предмет самопроверки скрипта."""
    assert cn.selftest() == 0
