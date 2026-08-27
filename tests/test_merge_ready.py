"""Готовность к слиянию: пустое множество проверок — не «всё зелено».

Скрипт закрывает правило 010 дословно: условие «нет красных» истинно на ПУСТОМ
множестве, и сторож слияния проверял только его — изменение без единого
прогона проходило как чистое.

Пустой список не редкость и не сбой. Изменение с конфликтом НЕ ПОЛУЧАЕТ
прогонов вовсе: площадка не собирает ссылку слияния, событие `pull_request`
не рождается, ci не запускается ни разу. Замер этого дня — три изменения
простояли так с утра, выглядя при этом здоровыми.

Набор двусторонний (правило 140 во второй редакции), и здоровые предметы взяты
у границы: посторонняя зелёная работа обязана НЕ считаться за обязательную, а
обязательная зелёная — обязана пропускать, даже если рядом идёт что-то ещё...
нет, не обязана: идущая проверка это ожидание, и случай стоит отдельно.
"""

from __future__ import annotations

import json

import merge_ready as mr


def run(runs, required=("catalogue",), monkeypatch=None):
    return mr.verdict(runs, list(required))


def ok(name="catalogue", conclusion="success"):
    return {"name": name, "status": "completed", "conclusion": conclusion}


# ── предметы, которые сторож обязан отвергнуть ─────────────────────────────

def test_пустой_список_это_не_зелено():
    allowed, why = run([])
    assert not allowed and "НИ ОДНОЙ" in why


def test_красная_проверка_отвергается():
    allowed, why = run([ok(), ok("other", "failure")])
    assert not allowed and "other" in why


def test_отменённая_проверка_отвергается():
    allowed, why = run([ok(), ok("other", "cancelled")])
    assert not allowed


def test_идущая_проверка_это_ожидание_а_не_разрешение():
    allowed, why = run([ok(), {"name": "slow", "status": "in_progress"}])
    assert not allowed and "ещё идут" in why


def test_посторонняя_зелёная_за_обязательную_не_считается():
    """Разрешительный список вместо запретительного (068)."""
    allowed, why = run([ok("open")])
    assert not allowed and "catalogue" in why


def test_обязательная_красная_отвергается_даже_рядом_с_зелёными():
    allowed, _ = run([ok("open"), ok("catalogue", "failure")])
    assert not allowed


# ── здоровые предметы: сторож обязан пропустить ────────────────────────────

def test_обязательная_зелёная_пропускает():
    allowed, why = run([ok()])
    assert allowed and "все зелёные" in why


def test_лишние_зелёные_не_мешают():
    allowed, _ = run([ok(), ok("open"), ok("arm")])
    assert allowed


def test_нейтральный_исход_зелёным_не_считается_но_и_не_роняет():
    """Граница: `neutral` — не успех и не отказ; обязательной он не закрывает."""
    allowed, why = run([ok("catalogue", "neutral")])
    assert not allowed


def test_без_обязательных_достаточно_отсутствия_красных():
    allowed, _ = run([ok("open")], required=())
    assert allowed


# ── три исхода у командной строки ──────────────────────────────────────────

def test_пустой_ввод_это_третий_исход(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", type("S", (), {"read": staticmethod(lambda: "  ")})())
    assert mr.main(["--required", "catalogue"]) == 2
    assert "не отработала" in capsys.readouterr().err


def test_битый_json_это_третий_исход(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", type("S", (), {"read": staticmethod(lambda: "{не json")})())
    assert mr.main([]) == 2


def test_ответ_без_списка_это_третий_исход(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin",
                        type("S", (), {"read": staticmethod(lambda: '{"message":"нет"}')})())
    assert mr.main([]) == 2
    assert "нет списка проверок" in capsys.readouterr().err


def test_голый_список_тоже_принимается(monkeypatch):
    monkeypatch.setattr("sys.stdin",
                        type("S", (), {"read": staticmethod(lambda: json.dumps([ok()]))})())
    assert mr.main(["--required", "catalogue"]) == 0


def test_нельзя_сливать_это_код_один(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin",
                        type("S", (), {"read": staticmethod(lambda: '{"check_runs":[]}')})())
    assert mr.main(["--required", "catalogue"]) == 1
    assert "сливать нельзя" in capsys.readouterr().err
