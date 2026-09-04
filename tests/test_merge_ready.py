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
    assert "нет ключа `check_runs`" in capsys.readouterr().err


def test_голый_список_тоже_принимается(monkeypatch):
    monkeypatch.setattr("sys.stdin",
                        type("S", (), {"read": staticmethod(lambda: json.dumps([ok()]))})())
    assert mr.main(["--required", "catalogue"]) == 0


def test_нельзя_сливать_это_код_один(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin",
                        type("S", (), {"read": staticmethod(lambda: '{"check_runs":[]}')})())
    assert mr.main(["--required", "catalogue"]) == 1
    assert "сливать нельзя" in capsys.readouterr().err


# ── заморозка очереди красным основанием (правило 053) ────────────────────
#
# Условие ВХОДА в очередь, а не одна из сортировок: спрашивается прежде
# проверок самого изменения. Инцидент — 2 сентября 2026: общая ветка
# покраснела, и за полчаса в неё уехали два изменения с зелёными проверками,
# снятыми на сломанном основании.

def прогон(name, conclusion, at="2026-09-02T09:00:00Z"):
    return {"name": name, "status": "completed", "conclusion": conclusion,
            "createdAt": at}


КРАСНОЕ = [прогон("ci", "success"),
           прогон("attribution-history", "success", "2026-09-02T08:53:00Z"),
           прогон("attribution-history", "failure", "2026-09-02T09:07:00Z")]
ЗЕЛЁНОЕ = [прогон("ci", "success"),
           прогон("attribution-history", "failure", "2026-09-02T09:07:00Z"),
           прогон("attribution-history", "success", "2026-09-02T09:31:00Z")]


def test_красное_основание_замораживает_очередь():
    why, state = mr.frozen(КРАСНОЕ, labels=[], thaw="blocker")

    assert "attribution-history" in why and "заморожена" in why
    assert state == ""


def test_метка_размораживает_очередь():
    why, state = mr.frozen(КРАСНОЕ, labels=["area/gates", "blocker"],
                           thaw="blocker")

    assert why == ""


def test_разморозка_не_выдаёт_основание_за_зелёное():
    """«Прошло, потому что метка» и «прошло, потому что чисто» — разные
    ответы, и подмена первого вторым была бы враньём в отчёте (158)."""
    _, state = mr.frozen(КРАСНОЕ, labels=["blocker"], thaw="blocker")

    assert "красное" in state and "blocker" in state


def test_зелёное_основание_очередь_не_держит():
    why, state = mr.frozen(ЗЕЛЁНОЕ, labels=[], thaw="blocker")

    assert why == "" and state == "основание зелёное"


def test_считается_последний_прогон_работы_а_не_любой():
    """Площадка отдаёт историю событий, а не состояние: рядом со свежим
    успехом висит вчерашний отказ, и он очередь морозить не должен (009)."""
    свежий_успех = [прогон("ci", "failure", "2026-09-01T10:00:00Z"),
                    прогон("ci", "success", "2026-09-02T10:00:00Z")]

    assert mr.frozen(свежий_успех, labels=[], thaw="blocker")[0] == ""


def test_идущий_прогон_основание_не_морозит():
    """«Ещё идёт» — не отказ: заморозка на состоянии, которое пройдёт само,
    останавливала бы очередь на ровном месте (051)."""
    идёт = [{"name": "ci", "status": "in_progress", "conclusion": None,
             "createdAt": "2026-09-02T10:00:00Z"}]

    assert mr.frozen(идёт, labels=[], thaw="blocker")[0] == ""


def test_исключение_принадлежит_потребителю():
    """Список исключений задаёт проект, а не инструмент."""
    assert mr.frozen(КРАСНОЕ, labels=[], thaw="blocker",
                     excluded=frozenset({"attribution-history"}))[0] == ""


def test_заморозка_спрашивается_до_проверок_изменения(tmp_path, monkeypatch, capsys):
    """Порядок — предмет правила: у изменения проверки зелёные, и всё равно
    нельзя. Спроси гейт их первыми — он ответил бы «сливать можно»."""
    base = tmp_path / "base.json"
    base.write_text(json.dumps(КРАСНОЕ), encoding="utf-8")
    monkeypatch.setattr("sys.stdin", type("S", (), {
        "read": staticmethod(lambda: json.dumps([ok()]))})())

    assert mr.main(["--required", "catalogue", "--base-runs", str(base)]) == 1
    assert "заморожена" in capsys.readouterr().err


def test_только_заморозка_проверок_изменения_не_читает(tmp_path, capsys):
    """Условие входа спрашивают до того, как у изменения появятся проверки."""
    base = tmp_path / "base.json"
    base.write_text(json.dumps(ЗЕЛЁНОЕ), encoding="utf-8")

    assert mr.main(["--freeze-only", "--base-runs", str(base)]) == 0
    assert "не заморожена" in capsys.readouterr().out


def test_только_заморозка_без_основания_это_третий_исход(capsys):
    assert mr.main(["--freeze-only"]) == 2
    assert "не отработала" in capsys.readouterr().err


def test_нечитаемое_основание_это_третий_исход(tmp_path, capsys):
    """«Основание красное» и «основание не спрошено» — разные ответы (039)."""
    assert mr.main(["--freeze-only",
                    "--base-runs", str(tmp_path / "нет.json")]) == 2
    assert "не прочитаны" in capsys.readouterr().err


def test_основание_не_список_это_третий_исход(tmp_path, capsys):
    base = tmp_path / "base.json"
    base.write_text('{"runs": []}', encoding="utf-8")

    assert mr.main(["--freeze-only", "--base-runs", str(base)]) == 2
    assert "нет списка" in capsys.readouterr().err
