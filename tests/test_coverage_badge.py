"""Значок покрытия: порог цвета, форма и три исхода.

Скрипт закрывает правило 035 — число в витрине переписывает сборка, а не рука.
Проверяется то, ради чего он есть: значок, который **устарел**, обязан быть
находкой, а не молчанием, иначе витрина уверенно показывает вчерашнее число.

Отдельно держатся границы порогов. Они названы в самом скрипте («значок,
зелёный при любом числе, перестают читать»), и ошибка в сравнении — `>` вместо
`>=` — не видна ни чтением, ни зелёным прогоном: цвет просто съезжает на
ступень, и заметить это может только тот, кто помнит границу.
"""

from __future__ import annotations

import pytest

import coverage_badge as cb


# ── порог цвета: граница проверяется с обеих сторон ────────────────────────

@pytest.mark.parametrize("percent,want", [
    (100, "brightgreen"), (90, "brightgreen"), (89.9, "green"),
    (75, "green"), (74.9, "yellow"),
    (50, "yellow"), (49.9, "orange"),
    (25, "orange"), (24.9, "red"), (0, "red"),
])
def test_цвет_на_границе_порога(percent, want):
    assert cb.color(percent) == want


def test_значок_по_форме_endpoint():
    text = cb.render(13.4)
    assert '"schemaVersion": 1' in text
    assert '"label": "coverage"' in text
    # Округление до целого — тоже часть формы: витрина не показывает доли.
    assert '"message": "13%"' in text


# ── три исхода ─────────────────────────────────────────────────────────────

def test_без_замера_это_третий_исход(monkeypatch, repo, capsys):
    monkeypatch.setattr(cb, "DATA", repo / "нет-замера")
    monkeypatch.setattr("sys.argv", ["coverage_badge.py", "--check"])
    assert cb.main() == 2
    assert "замер не отработал" in capsys.readouterr().err


def test_актуальный_значок_проходит(monkeypatch, repo, capsys):
    badge = repo / "badge.json"
    badge.write_text(cb.render(42), encoding="utf-8")
    monkeypatch.setattr(cb, "BADGE", badge)
    monkeypatch.setattr(cb, "measured", lambda: 42.0)
    monkeypatch.setattr("sys.argv", ["coverage_badge.py", "--check"])
    assert cb.main() == 0
    assert "актуален" in capsys.readouterr().out


def test_устаревший_значок_это_находка(monkeypatch, repo, capsys):
    badge = repo / "badge.json"
    badge.write_text(cb.render(90), encoding="utf-8")
    monkeypatch.setattr(cb, "BADGE", badge)
    monkeypatch.setattr(cb, "measured", lambda: 42.0)
    monkeypatch.setattr("sys.argv", ["coverage_badge.py", "--check"])
    assert cb.main() == 1
    assert "устарел" in capsys.readouterr().err


def test_отсутствующий_значок_тоже_находка(monkeypatch, repo, capsys):
    monkeypatch.setattr(cb, "BADGE", repo / "нет" / "badge.json")
    monkeypatch.setattr(cb, "measured", lambda: 42.0)
    monkeypatch.setattr("sys.argv", ["coverage_badge.py", "--check"])
    assert cb.main() == 1


def test_сборка_кладёт_значок_рядом_с_недостающими_каталогами(
        monkeypatch, repo, capsys):
    badge = repo / "нет" / "такого" / "badge.json"
    monkeypatch.setattr(cb, "BADGE", badge)
    monkeypatch.setattr(cb, "measured", lambda: 77.0)
    monkeypatch.setattr("sys.argv", ["coverage_badge.py"])
    assert cb.main() == 0
    assert '"message": "77%"' in badge.read_text(encoding="utf-8")
