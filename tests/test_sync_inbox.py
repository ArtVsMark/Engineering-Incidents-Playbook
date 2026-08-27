"""Входящие потребителя: перепись, находка и очередь — разные вещи.

Прогон живёт у ПОТРЕБИТЕЛЯ и ведёт одну задачу в его трекере. До этого он
перечислял только очередь: правила без ответа и записанные `unreviewed`. Двух
вопросов он не задавал вовсе.

**Сколько правил сейчас и сколько разобрано** — число печаталось лишь при
находке, то есть отвечало на «что сломалось» и не отвечало на «куда мы
движемся».

**Ответ о правиле, которого в каталоге нет.** У себя каталог такой ответ
отвергает гейтом; у потребителя тот же вопрос не задавался. Замер: у витрины
лежит ответ о правиле 143, снятом как дубль, и лежит с самого снятия. Чинится
это только здесь — файл принадлежит проекту, — потому и называется здесь.

Набор двусторонний (140): очередь находкой становиться не должна, а находка
обязана переживать зелёный.

Сеть не трогается: `gh` не зовётся ни одним случаем, всё идёт через --dry-run.
"""

from __future__ import annotations

import json

import sync_inbox as si
from conftest import write


def rule(rid: str, title: str = "правило") -> dict:
    return {"id": rid, "slug": "s", "title": {"ru": title, "en": title}}


RULES = [rule("001"), rule("002"), rule("003")]


# ── находка: ответ о снятом правиле ───────────────────────────────────────

def test_ответ_о_снятом_правиле_это_находка():
    assert si.stale_here({"001": {}, "143": {}}, RULES) == ["143"]


def test_очередь_находкой_не_становится():
    """«Не дошли руки» решится решением; лишний ответ не решится никогда."""
    assert si.stale_here({"001": {}}, RULES) == []


def test_пустой_ответ_это_не_находка():
    """Проект ещё не подключён — упрекать не в чем."""
    assert si.stale_here({}, RULES) == []


def test_находка_названа_в_теле_и_сказано_что_делать():
    тело = si.body_for([], [], "o/к", stale=["143"], total=3, answered=3)

    assert "которого в каталоге нет" in тело
    assert "**143**" in тело
    assert "удаляется из `.rules/bindings.json`" in тело


def test_находка_переживает_зелёную_очередь():
    """Очередь пуста, а лишний ответ есть — тело обязано об этом сказать."""
    тело = si.body_for([], [], "o/к", stale=["143"], total=3, answered=3)

    assert "Нерассмотренных нет" in тело and "**143**" in тело


# ── перепись ──────────────────────────────────────────────────────────────

def test_перепись_есть_и_на_зелёном():
    тело = si.body_for([], [], "o/к", stale=[], total=3, answered=3)

    assert "Правил в каталоге: 3. Разобрано здесь: 3." in тело


def test_перепись_различает_нет_ответа_и_не_рассмотрено():
    тело = si.body_for([rule("002")], [rule("003")], "o/к", stale=[],
                       total=3, answered=1)

    assert "Ответа нет вовсе у 1, записано `unreviewed` у 1" in тело


def test_без_переписи_тело_не_ломается():
    """Старый вызов без новых полей обязан остаться рабочим."""
    тело = si.body_for([rule("002")], [], "o/к")

    assert "Ответа нет вовсе" in тело and "Правил в каталоге" not in тело


# ── исходы ────────────────────────────────────────────────────────────────

def _подготовить(monkeypatch, repo, answers: dict, rules=RULES):
    """Экспорт подменяется на входе, а не скачивается: сеть тесту не нужна."""
    bindings = write(repo / "bindings.json", json.dumps({"rules": answers}))
    monkeypatch.setattr(si, "fetch_rules", lambda *a: (rules, None))
    monkeypatch.setattr(si, "gh", lambda *a: (_ for _ in ()).throw(
        AssertionError("сеть не должна опрашиваться")))
    return bindings


def test_лишний_ответ_роняет_прогон(monkeypatch, repo, capsys):
    bindings = _подготовить(
        monkeypatch, repo, {r["id"]: {"status": "active"} for r in RULES}
        | {"143": {"status": "active"}})
    monkeypatch.setattr("sys.argv", [
        "sync_inbox.py", "--dry-run", "--bindings", str(bindings)])

    код = si.main()

    assert код == 1
    assert "**143**" in capsys.readouterr().out


def test_всё_разобрано_и_лишнего_нет_это_ноль(monkeypatch, repo):
    bindings = _подготовить(
        monkeypatch, repo, {r["id"]: {"status": "active"} for r in RULES})
    monkeypatch.setattr("sys.argv", [
        "sync_inbox.py", "--dry-run", "--bindings", str(bindings)])

    assert si.main() == 0


def test_неразобранный_ответ_это_не_третий_исход(monkeypatch, repo):
    """Очередь — единица, а не двойка: механизм отработал и нашёл предмет."""
    bindings = _подготовить(monkeypatch, repo, {"001": {"status": "unreviewed"}})
    monkeypatch.setattr("sys.argv", [
        "sync_inbox.py", "--dry-run", "--bindings", str(bindings)])

    assert si.main() == 1
