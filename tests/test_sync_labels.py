"""Расстановка меток: разбор файла и три исхода.

Скрипт закрывает 064 с обеих сторон: объявленную метку заводит, неучтённую
называет и НЕ удаляет — удаление снимает метку со всех задач разом, и это
решение человека (051).

Источник подделки (правило 170): форма ответа снята с
`gh api repos/OWNER/REPO/labels?per_page=100`; запись метки — с тела запроса
`gh api -X POST repos/OWNER/REPO/labels`. Сверка требует сети и остаётся
человеку.

Отдельный случай — отсутствие самого `gh`. Он стоит здесь потому, что раньше
эта ветка не существовала: вылетала трассировка, оболочка отдавала код 1, и
«инструмента нет» становилось неотличимо от «нашли расхождение». Разница не
косметическая — находку чинит автор изменения, а отсутствующий инструмент тот,
кто запускает (правила 039, 145).
"""

from __future__ import annotations

import json
from pathlib import Path

import sync_labels as sl
from conftest import write

FILE = '''# комментарий
- name: "area/rules"
  color: "1d76db"
  description: "Зона: записи"
- name: "bug"
  color: "d73a4a"
  description: "Дефект"
'''


def prepare(monkeypatch, repo: Path, text: str = FILE) -> Path:
    path = write(repo / "labels.yml", text)
    monkeypatch.setattr(sl, "LABELS", path)
    monkeypatch.setattr(sl, "ROOT", repo)
    return path


def cli(monkeypatch, *argv: str) -> None:
    monkeypatch.setattr("sys.argv", ["sync_labels.py", *argv])


def fake_gh(monkeypatch, have: list[dict], code: int = 0) -> None:
    monkeypatch.setattr(sl, "gh_json",
                        lambda *a: (code, json.dumps(have) if code == 0 else "нет"))


# ── разбор файла ───────────────────────────────────────────────────────────

def test_разбор_читает_имя_цвет_и_описание(monkeypatch, repo):
    prepare(monkeypatch, repo)
    out, err = sl.declared()
    assert err is None
    assert [l["name"] for l in out] == ["area/rules", "bug"]
    assert out[0]["color"] == "1d76db"


def test_метка_без_цвета_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, '- name: "bug"\n  description: "Дефект"\n')
    cli(monkeypatch, "--dry-run", "--repo", "o/r")
    assert sl.main() == 2
    assert "без цвета" in capsys.readouterr().err


def test_пустой_файл_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, "# только комментарий\n")
    cli(monkeypatch, "--dry-run", "--repo", "o/r")
    assert sl.main() == 2
    assert "не объявляет" in capsys.readouterr().err


def test_репозиторий_не_назван_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    cli(monkeypatch, "--dry-run")
    assert sl.main() == 2
    assert "репозиторий не определён" in capsys.readouterr().err


# ── отсутствие инструмента: ветка, которой не было ─────────────────────────

def test_без_gh_это_третий_исход_а_не_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo)
    def boom(*a, **k):
        raise FileNotFoundError(2, "No such file or directory", "gh")
    monkeypatch.setattr(sl.subprocess, "run", boom)
    cli(monkeypatch, "--dry-run", "--repo", "o/r")
    assert sl.main() == 2
    assert "нет команды gh" in capsys.readouterr().err


def test_код_отсутствия_не_совпадает_с_кодами_находок():
    """Совпади он с 1 или 2 — «инструмента нет» снова стало бы находкой."""
    assert sl.NO_GH not in (0, 1, 2)


# ── чисто и находки ────────────────────────────────────────────────────────

def test_объявленные_на_месте_это_чисто(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo)
    fake_gh(monkeypatch, [
        {"name": "area/rules", "color": "1d76db", "description": "Зона: записи"},
        {"name": "bug", "color": "d73a4a", "description": "Дефект"}])
    cli(monkeypatch, "--dry-run", "--repo", "o/r")
    assert sl.main() == 0
    assert "на месте и совпадают" in capsys.readouterr().out


def test_цвет_в_другом_регистре_расхождением_не_считается(monkeypatch, repo):
    """Здоровый предмет у самой границы: площадка отдаёт цвет как угодно."""
    prepare(monkeypatch, repo)
    fake_gh(monkeypatch, [
        {"name": "area/rules", "color": "1D76DB", "description": "Зона: записи"},
        {"name": "bug", "color": "D73A4A", "description": "Дефект"}])
    cli(monkeypatch, "--dry-run", "--repo", "o/r")
    assert sl.main() == 0


def test_неучтённая_метка_это_находка_и_её_не_удаляют(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo)
    fake_gh(monkeypatch, [
        {"name": "area/rules", "color": "1d76db", "description": "Зона: записи"},
        {"name": "bug", "color": "d73a4a", "description": "Дефект"},
        {"name": "wontfix", "color": "ffffff", "description": ""}])
    cli(monkeypatch, "--dry-run", "--repo", "o/r")
    assert sl.main() == 1
    err = capsys.readouterr().err
    assert "wontfix" in err and "Не удаляю" in err


def test_недостающая_метка_показана_но_не_заведена_на_сухом_прогоне(
        monkeypatch, repo, capsys):
    prepare(monkeypatch, repo)
    fake_gh(monkeypatch, [
        {"name": "bug", "color": "d73a4a", "description": "Дефект"}])
    cli(monkeypatch, "--dry-run", "--repo", "o/r")
    assert sl.main() == 0
    assert "завелись бы: area/rules" in capsys.readouterr().out


def test_список_меток_не_прочитан_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo)
    fake_gh(monkeypatch, [], 1)
    cli(monkeypatch, "--dry-run", "--repo", "o/r")
    assert sl.main() == 2
    assert "не прочитан" in capsys.readouterr().err
