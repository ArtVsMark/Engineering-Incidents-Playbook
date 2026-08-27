"""Локальные ссылки и якоря.

Скрипт закрывает правило 002: разовая проверка ссылок руками ничего не
гарантирует. Здесь проверяется, что он действительно ловит битое, и — не менее
важно — что он различает ТРИ исхода (правило 039): чисто, находки и
«проверять было нечего», причём последнее не зеленеет (правило 075).
"""

from __future__ import annotations

from pathlib import Path

import check_links as cl
from conftest import write


def prepare(monkeypatch, repo: Path) -> None:
    monkeypatch.setattr(cl, "ROOT", repo)


def test_якорь_из_заголовка(repo):
    doc = write(repo / "a.md", "# Простой Заголовок\n\n## С Двумя Словами\n")
    assert "простой-заголовок" in cl.anchors(doc)
    assert "с-двумя-словами" in cl.anchors(doc)


def test_якорь_теряет_пунктуацию_но_не_кириллицу(repo):
    doc = write(repo / "a.md", "# Гейты: три исхода, а не два!\n")
    assert "гейты-три-исхода-а-не-два" in cl.anchors(doc)


def test_строки_без_решётки_якорями_не_становятся(repo):
    doc = write(repo / "a.md", "просто текст\n# Заголовок\n")
    assert cl.anchors(doc) == {"заголовок"}


def test_живая_ссылка_проходит(monkeypatch, repo, capsys):
    write(repo / "a.md", "см. [цель](b.md)\n")
    write(repo / "b.md", "# Цель\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 0
    assert "ссылки в порядке" in capsys.readouterr().out


def test_ссылка_в_никуда_это_находка(monkeypatch, repo, capsys):
    write(repo / "a.md", "см. [цель](нет-такого.md)\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 1
    # Отказ обязан назвать, ЧТО именно битое, а не только сколько.
    assert "нет-такого.md" in capsys.readouterr().err


def test_живой_файл_но_мёртвый_якорь_это_находка(monkeypatch, repo, capsys):
    write(repo / "a.md", "см. [цель](b.md#которого-нет)\n")
    write(repo / "b.md", "# Совсем другое\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 1
    assert "якоря нет" in capsys.readouterr().err


def test_внешние_ссылки_не_проверяются(monkeypatch, repo):
    write(repo / "a.md", "[вовне](https://example.com/x.md) и [свой](b.md)\n")
    write(repo / "b.md", "# Свой\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 0


def test_нет_документов_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo)
    assert cl.main() == 2
    assert "проверять нечего" in capsys.readouterr().err


def test_документы_без_локальных_ссылок_это_третий_исход(monkeypatch, repo, capsys):
    write(repo / "a.md", "текст без единой ссылки\n")
    prepare(monkeypatch, repo)
    # Ноль проверенных ссылок — это «вход подозрителен», а не «всё хорошо»:
    # зелёное здесь означало бы, что гейт проспал пустой каталог (правило 075).
    assert cl.main() == 2
    assert "подозрителен" in capsys.readouterr().err
