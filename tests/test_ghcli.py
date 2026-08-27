"""Один вызов `gh` на весь каталог: отсутствие инструмента — третий исход.

Помощник был у четырёх скриптов, и все четыре написали его по-своему: два
падали трассировкой, третий возвращал код 2 — занятый у самого `gh`, —
четвёртый отдавал 127. Расхождение не косметическое: у потребителя действие
каталога разбирает код возврата, и 1 означает «очередь, всё в порядке».
Скрипт без `gh` умирал и отдавал 1 — механизм не работал ВООБЩЕ и рапортовал
успех (правило 075).

Здесь проверяется и сам помощник, и то, ради чего он заведён: **все четыре
скрипта отдают ровно 2**, когда `gh` нет. Случай стоит для каждого отдельно,
а не для одного «представителя»: расходились они именно поодиночке.
"""

from __future__ import annotations

import pytest

import ghcli


def no_gh(monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError(2, "No such file or directory", "gh")
    monkeypatch.setattr(ghcli.subprocess, "run", boom)


# ── сам помощник ───────────────────────────────────────────────────────────

def test_нет_инструмента_это_свой_код(monkeypatch):
    no_gh(monkeypatch)
    code, why = ghcli.run("issue", "list")
    assert code == ghcli.NO_GH and "gh" in why


def test_код_отсутствия_не_совпадает_с_кодами_gh():
    """Совпади он с 1 или 2 — «инструмента нет» снова стало бы находкой."""
    assert ghcli.NO_GH not in (0, 1, 2)


def test_причина_называется_целиком(monkeypatch):
    no_gh(monkeypatch)
    _, why = ghcli.run("x")
    assert "не должен зеленеть" in why


def test_обычный_отказ_gh_отсутствием_не_считается(monkeypatch):
    """Здоровый предмет у границы: gh есть и вернул 1 — это находка, не сбой."""
    class Done:
        returncode, stdout, stderr = 1, "", "нет такой задачи"
    monkeypatch.setattr(ghcli.subprocess, "run", lambda *a, **k: Done())
    code, out = ghcli.run("issue", "view", "1")
    assert code == 1 and not ghcli.failed(code)
    assert out == "нет такой задачи"


def test_успех_проходит(monkeypatch):
    class Done:
        returncode, stdout, stderr = 0, "[]", ""
    monkeypatch.setattr(ghcli.subprocess, "run", lambda *a, **k: Done())
    assert ghcli.run("issue", "list") == (0, "[]")


# ── ради чего заведён: четыре скрипта, четыре отдельных случая ────────────

@pytest.mark.parametrize("module,argv", [
    ("sync_inbox", ["--bindings", "нет-такого.json"]),
    ("collect_proposals", []),
    ("sync_labels", ["--repo", "o/r"]),
    ("main_red", []),
])
def test_без_инструмента_скрипт_отдаёт_третий_исход(module, argv, monkeypatch, tmp_path):
    """1 у потребителя означает «очередь, всё в порядке» — отдавать его нельзя."""
    import importlib
    mod = importlib.import_module(module)
    no_gh(monkeypatch)
    monkeypatch.setenv("GH_TOKEN", "x")
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setattr("sys.argv", [f"{module}.py", *argv])
    assert mod.main() == 2
