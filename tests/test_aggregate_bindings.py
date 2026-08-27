"""Сводка «где действует»: ответы потребителей, три исхода и согласованность.

Скрипт закрывает правила 049 и 075: таблица вычисляется из ответов, а не
ведётся руками, и объявленный потребитель, чей ответ не читается, роняет
сборку — иначе «не смогли прочитать» неотличимо от «у него всё хорошо».

Здесь же держится граница, которую легко потерять при правке: **отсутствие
связи и нечитаемый ответ — разные вещи**. Первое объявленное состояние и
проходит молча, второе находка. Тест на пару стоит рядом нарочно: они
отличаются одним полем реестра, и слить их в одну ветку можно случайно.

Сеть не трогается ни одним случаем: у всех потребителей ответ локальный. Это
не удобство теста, а то же требование, что и у `--check` в конвейере —
обязательная проверка не зависит от чужого сервера.
"""

from __future__ import annotations

import json
from pathlib import Path

import aggregate_bindings as ab
from conftest import write


def prepare(monkeypatch, repo: Path, consumers, rules=("001", "002")) -> None:
    registry = repo / ".rules" / "consumers.json"
    write(registry, json.dumps({"schema": "1.0", "consumers": consumers},
                               ensure_ascii=False))
    write(repo / "export" / "rules.json",
          json.dumps({"rules": [{"id": i} for i in rules]}))
    monkeypatch.setattr(ab, "ROOT", repo)
    monkeypatch.setattr(ab, "CONSUMERS", registry)
    monkeypatch.setattr(ab, "EXPORT_JSON", repo / "export" / "where.json")
    monkeypatch.setattr(ab, "EXPORT_MD", repo / "export" / "where.md")
    monkeypatch.setattr(ab, "RULES", repo / "export" / "rules.json")


def cli(monkeypatch, *argv: str) -> None:
    monkeypatch.setattr("sys.argv", ["aggregate_bindings.py", *argv])


def answer(repo: Path, where: str, **rules) -> str:
    """Кладёт ответ потребителя и возвращает путь ОТНОСИТЕЛЬНО корня."""
    write(repo / where,
          json.dumps({"rules": {k: {"status": v} for k, v in rules.items()}}))
    return where


# ── третий исход: сверять нечего ───────────────────────────────────────────

def test_нет_реестра_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, [])
    ab.CONSUMERS.unlink()
    cli(monkeypatch)
    assert ab.main() == 2
    assert "не отработала" in capsys.readouterr().err


def test_пустой_реестр_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, [])
    cli(monkeypatch)
    assert ab.main() == 2
    assert "не отработала" in capsys.readouterr().err


# ── состояния, которые находкой НЕ являются ────────────────────────────────

def test_потребитель_без_связи_это_состояние(monkeypatch, repo):
    slices, problems = ab.collect([{"repo": "owner/one"}])
    assert problems == []
    assert slices[0]["state"] == ab.NOT_CONNECTED
    assert slices[0]["why"]


def test_приватный_ответ_называется_неизвестным(monkeypatch, repo):
    slices, problems = ab.collect([{"repo": "owner/one", "access": "private"}])
    assert problems == []
    assert slices[0]["state"] == ab.UNKNOWN


# ── находка: объявленный потребитель, чей ответ не читается ────────────────

def test_нечитаемый_ответ_объявленного_потребителя_это_находка(
        monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            [{"repo": "owner/one", "bindings": ".rules/нет-такого.json"}])
    cli(monkeypatch)
    assert ab.main() == 1
    assert "не читается" in capsys.readouterr().err


def test_живой_ответ_собирается_в_срез(monkeypatch, repo):
    prepare(monkeypatch, repo, [])
    monkeypatch.setattr(ab, "ROOT", repo)
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    slices, problems = ab.collect([{"repo": "owner/one", "bindings": src}])
    assert problems == []
    assert slices[0]["state"] == "подключён"
    assert slices[0]["rules"] == {"001": "active"}


# ── сверка собранного: --check ─────────────────────────────────────────────

def test_собранная_сводка_согласована(monkeypatch, repo):
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    cli(monkeypatch, "--check")
    assert ab.main() == 0


def test_реестр_ушёл_вперёд_сводки_это_находка(monkeypatch, repo, capsys):
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    # Потребитель приехал в реестр, сводку не пересобрали.
    write(ab.CONSUMERS, json.dumps(
        {"schema": "1.0", "consumers": [{"repo": "owner/one", "bindings": src},
                                        {"repo": "owner/two"}]},
        ensure_ascii=False))
    cli(monkeypatch, "--check")
    assert ab.main() == 1
    assert "owner/two" in capsys.readouterr().err


def test_несобранной_сводки_достаточно_для_находки(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, [{"repo": "owner/one"}])
    cli(monkeypatch, "--check")
    assert ab.main() == 1
    assert "Соберите" in capsys.readouterr().err


def test_ответ_потребителя_уехал_вперёд_сводки_это_находка(monkeypatch, repo, capsys):
    """Расхождение, которое до #122 ловил только НОЧНОЙ прогон с сетью.

    Изменение правит ответ и не пересобирает сводку; обязательная проверка
    убеждалась, что сводка согласована сама с собой, и зеленела. Сети для
    этого не нужно: местный ответ лежит на диске.
    """
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    answer(repo, ".rules/bindings.json", **{"001": "rejected"})
    cli(monkeypatch, "--check")
    assert ab.main() == 1
    err = capsys.readouterr().err
    assert "отстала от ответа" in err and "001 (active → rejected)" in err


def test_сводка_в_ногу_с_ответом_проходит(monkeypatch, repo):
    """Здоровый предмет у самой границы: ответ менялся, сводку пересобрали."""
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    answer(repo, ".rules/bindings.json", **{"001": "rejected"})
    cli(monkeypatch)
    assert ab.main() == 0
    cli(monkeypatch, "--check")
    assert ab.main() == 0


def test_местный_ответ_пропал_после_сборки_это_находка(monkeypatch, repo, capsys):
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    (repo / src).unlink()
    cli(monkeypatch, "--check")
    assert ab.main() == 1
    assert "не читается" in capsys.readouterr().err


# ── производная таблица ────────────────────────────────────────────────────

def test_таблица_перечисляет_правила_поимённо(repo):
    slices = [{"repo": "owner/one", "state": "подключён", "answered": 1,
               "rules": {"001": "active"}}]
    text = ab.as_markdown(slices, ["001", "002"])
    assert "| 001 |" in text and "| 002 |" in text
    assert "не правится руками" in text


def test_без_подключённых_таблица_правил_объявлена_пустой(repo):
    slices = [{"repo": "owner/one", "state": ab.NOT_CONNECTED, "why": "нет"}]
    text = ab.as_markdown(slices, ["001"])
    assert "| 001 |" not in text
    assert "объявленное состояние" in text


def test_отставший_ответ_это_предупреждение_а_не_отказ():
    old = (__import__("datetime").date.today()
           - __import__("datetime").timedelta(days=ab.TTL_DAYS + 1)).isoformat()
    assert ab.stale([{"repo": "owner/one", "read_at": old}])
    assert ab.stale([{"repo": "owner/one", "read_at": "не дата"}]) == []


# ── объявленный и не подключившийся: срок делает адресата ─────────────────
#
# Замер, из которого это выросло: из шести объявленных потребителей пятеро не
# отдают ответа, шестеро не отдают предложений. Канал построен с обеих сторон
# и не пронёс НИ ОДНОГО предложения. «Не подключён» при этом печаталось
# спокойно как законное состояние — и потому не читалось никем, ровно как
# красное по расписанию без адресата (142).
#
# Срок делает адресата. Набор двусторонний: свежий и подключённый обязаны
# проходить, иначе состояние станет находкой на пустом месте.

def days_ago(n: int) -> str:
    import datetime as dt
    return (dt.date.today() - dt.timedelta(days=n)).isoformat()


def test_свежий_неподключённый_это_состояние():
    assert ab.unconnected([{"repo": "o/a", "since": days_ago(1)}]) == []


def test_просроченный_неподключённый_это_находка():
    out = ab.unconnected([{"repo": "o/a", "since": days_ago(ab.UNCONNECTED_DAYS + 1)}])
    assert out and "объявлен потребителем" in out[0]


def test_на_границе_срока_ещё_состояние():
    """Здоровый предмет у самой границы: ровно срок — ещё не находка."""
    assert ab.unconnected([{"repo": "o/a", "since": days_ago(ab.UNCONNECTED_DAYS)}]) == []


def test_подключённый_срока_не_знает():
    assert ab.unconnected([{"repo": "o/a", "since": days_ago(999),
                            "bindings": "x.json"}]) == []


def test_приватный_подключения_не_требует():
    """Его ответ недоступен по объявленной причине — требовать нечего."""
    assert ab.unconnected([{"repo": "o/a", "since": days_ago(999),
                            "access": "private"}]) == []


def test_без_начала_отсчёта_это_находка():
    """Срок без начала не считается, и молчать об этом нельзя (075)."""
    out = ab.unconnected([{"repo": "o/a"}])
    assert out and "since" in out[0]


def test_неразбираемая_дата_это_находка():
    out = ab.unconnected([{"repo": "o/a", "since": "вчера"}])
    assert out and "не разбирается" in out[0]


def test_отказ_живёт_в_сборке_а_не_в_проверке_изменения(monkeypatch, repo, capsys):
    """Разные предметы — разные исходы, и это главное в этой паре.

    Сборку запускает ночной прогон, и его отказ заводит задачу: у находки
    появляется адресат (142). Проверку `--check` запускает изменение, и там
    тот же список только печатается: автор изменения чужой репозиторий
    подключить не может, а красить его работу за это значит приучать к
    красному (051).
    """
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [
        {"repo": "owner/one", "bindings": src, "since": days_ago(1)},
        {"repo": "owner/two", "since": days_ago(ab.UNCONNECTED_DAYS + 1)},
    ])
    cli(monkeypatch)
    assert ab.main() == 1
    assert "owner/two" in capsys.readouterr().err
    cli(monkeypatch, "--check")
    assert ab.main() == 0
    assert "owner/two" in capsys.readouterr().out


def test_сводка_всё_равно_записана_при_находке(monkeypatch, repo):
    """Отказ не отменяет работу: сводка собрана, иначе чинить было бы нечем."""
    prepare(monkeypatch, repo, [{"repo": "owner/two",
                                 "since": days_ago(ab.UNCONNECTED_DAYS + 1)}])
    cli(monkeypatch)
    assert ab.main() == 1
    assert ab.EXPORT_MD.exists() and ab.EXPORT_JSON.exists()
