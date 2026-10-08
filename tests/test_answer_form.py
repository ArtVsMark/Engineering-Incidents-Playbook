"""Форма записи ответа — контракт 1.9: одна на каталог, сводку и потребителя.

Случаи спрашивают модуль формы и проверку, которую каталог отдаёт проекту
(`check_answer.py`), на подделке: живой корпус зеленел бы и при сломанной
проверке (146). Каждое «отвергается» ниже — предмет, ради которого поле
заведено, а «пропускается» — законная форма, ложный отказ на которой
приучил бы читать красное как фон (051).
"""


import json
from pathlib import Path

import pytest

import answer_form as af
import check_answer as ca

ИСТОЧНИК = "o/r:scripts/x.py@0123abc"


# ── происхождение: обязательно с 1.9 у gate/pipeline ──────────────────────

@pytest.mark.parametrize("rec", [
    {"status": "active", "mechanism": "gate", "origin_kind": "own"},
    {"status": "active", "mechanism": "pipeline", "origin_kind": "adapted", "origin": ИСТОЧНИК},
    {"status": "active", "mechanism": "document"},
    {"status": "not-applicable", "why": "нет"},
])
def test_происхождение_19_законно(rec):
    assert af.происхождение(rec, "1.9") is None


@pytest.mark.parametrize("rec, слово", [
    ({"status": "active", "mechanism": "gate"}, "обязательно"),
    ({"status": "active", "mechanism": "gate", "origin_kind": "own", "origin": ИСТОЧНИК}, "противоречит"),
    ({"status": "active", "mechanism": "gate", "origin_kind": "called"}, "без `origin`"),
    ({"status": "active", "mechanism": "none", "origin_kind": "own"}, "при механизме `none`"),
])
def test_происхождение_19_отвергается(rec, слово):
    что = af.происхождение(rec, "1.9")
    assert что is not None and слово in что


def test_ответ_18_задним_числом_не_спрашивается():
    """Требование 1.9 к ответу 1.8 не предъявляется — подъём схемы и есть
    перечитывание (157)."""
    assert af.происхождение({"status": "active", "mechanism": "gate"}, "1.8") is None
    assert "1.9" in af.происхождение(
        {"status": "active", "mechanism": "gate", "origin_kind": "own"}, "1.8")


# ── проба «не применимо»: одна форма и три диалекта ───────────────────────

def test_диалекты_пробы_читаются_одной_формой():
    assert af.проба({"refuted_by": "a/*.yml"}) == {"globs": ["a/*.yml"], "contains": []}
    assert af.проба({"absent": {"substring": "x", "globs": ["*.md"]}}) == {
        "globs": ["*.md"], "contains": ["x"]}
    assert af.проба({"refuted_by": {"globs": ["*.md"], "contains": ["x"]}}) == {
        "globs": ["*.md"], "contains": ["x"]}


@pytest.mark.parametrize("rec, схема, слово", [
    ({"status": "active", "refuted_by": {"globs": ["*"]}}, "1.9", "опровергать нечего"),
    ({"status": "not-applicable", "refuted_by": "a/*.yml"}, "1.9", "диалект до 1.9"),
    ({"status": "not-applicable", "absent": {"globs": ["*"]}}, "1.9", "диалект до 1.9"),
    ({"status": "not-applicable", "refuted_by": {"globs": []}}, "1.9", "непустой список"),
])
def test_проба_не_по_форме(rec, схема, слово):
    что = af.проба_неверна(rec, схема)
    assert что is not None and слово in что


def test_проба_находит_предмет(tmp_path):
    (tmp_path / "w").mkdir()
    (tmp_path / "w" / "a.yml").write_text("strategy:\n  matrix: [1]\n")
    rec = {"status": "not-applicable",
           "refuted_by": {"globs": ["w/*.yml"], "contains": ["matrix:"]}}
    assert "matrix:" in af.прогнать_пробу(rec, tmp_path)
    rec["refuted_by"]["contains"] = ["flock"]
    assert af.прогнать_пробу(rec, tmp_path) is None


# ── заметка и замер; закрытая форма ───────────────────────────────────────

@pytest.mark.parametrize("rec, слово", [
    ({"note": "  "}, "`note`"),
    ({"metric": 5}, "объект"),
    ({"metric": {"what": "x", "value": True, "measured": "2026-10-08"}}, "value"),
    ({"metric": {"what": "x", "value": 3, "measured": "8 октября"}}, "measured"),
])
def test_заметка_и_замер_не_по_форме(rec, слово):
    что = af.заметка_неверна(rec)
    assert что is not None and слово in что


def test_закрытая_форма_с_19_и_пояснения_через_подчёркивание():
    rec = {"status": "active", "mechanism": "document", "code_ref": "x", "_пояснение": "y"}
    assert af.незнакомые(rec, "1.9") == ["code_ref"]
    assert af.незнакомые(rec, "1.8") == []


# ── проверка, которую каталог отдаёт проекту ──────────────────────────────

def ответ(tmp_path: Path, rules: dict, схема: str = "1.9") -> Path:
    p = tmp_path / "bindings.json"
    p.write_text(json.dumps({"schema": схема, "rules": rules}), encoding="utf-8")
    return p


def test_проект_по_форме_проходит(tmp_path, capsys):
    p = ответ(tmp_path, {"001": {"status": "active", "mechanism": "gate",
                                 "where": "s.py", "origin_kind": "own",
                                 "note": "мысль",
                                 "metric": {"what": "x", "value": 1,
                                            "measured": "2026-10-08"}}})
    assert ca.main(["--bindings", str(p), "--root", str(tmp_path)]) == 0


@pytest.mark.parametrize("rec, слово", [
    ({"status": "active", "mechanism": "code", "origin_kind": "own"}, "вне словаря"),
    ({"status": "rejected"}, "без причины"),
    ({"status": "active", "mechanism": "gate"}, "origin_kind"),
])
def test_проект_не_по_форме_отвергается(tmp_path, capsys, rec, слово):
    p = ответ(tmp_path, {"001": rec})
    assert ca.main(["--bindings", str(p), "--root", str(tmp_path)]) == 1
    assert слово in capsys.readouterr().err


def test_опровергнутая_проба_это_находка(tmp_path, capsys):
    (tmp_path / "ci.yml").write_text("matrix: [a, b]\n")
    p = ответ(tmp_path, {"015": {"status": "not-applicable", "why": "одна ОС",
                                 "refuted_by": {"globs": ["*.yml"],
                                                "contains": ["matrix:"]}}})
    assert ca.main(["--bindings", str(p), "--root", str(tmp_path)]) == 1
    assert "опровергнуто" in capsys.readouterr().err


def test_нечитаемый_ответ_это_третий_исход(tmp_path, capsys):
    p = tmp_path / "bindings.json"
    p.write_text("{битый", encoding="utf-8")
    assert ca.main(["--bindings", str(p), "--root", str(tmp_path)]) == 2
