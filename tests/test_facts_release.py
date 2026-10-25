"""Выпуск договора фактов (#843): собирается и проверяется у издателя, тег не переставляется."""

import sys

import facts_release as fr


def test_самопроверка_двусторонняя():
    assert fr.selftest() == 0


def test_стоящий_тег_отказ(tmp_path, monkeypatch):
    monkeypatch.setattr(fr, "tag_exists", lambda _tag: True)
    monkeypatch.setattr(
        sys,
        "argv",
        ["facts_release.py", "--dist", str(tmp_path / "d"), "--notes", str(tmp_path / "n.md")],
    )
    assert fr.main() == 1


def test_без_каталога_выпуска_третий_исход(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["facts_release.py"])
    assert fr.main() == 2


def test_страница_называет_источник_у_каталога():
    текст = fr.notes("2.0.0", "ArtVsMark/Engineering-Incidents-Playbook")
    assert "export/facts/facts-contract.md" in текст
    assert "facts-v2.0.0" in текст
