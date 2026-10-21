"""Один счёт правил: каждый счётчик каталога на живом дереве даёт одно число.

Правило 214 для числа. «Сколько правил» отвечает одна точка —
`build_rules_index.действующие()` и её вариант по выгрузке. 17–21.10 девять
мест отвечали своей формулировкой, длиной списка всех записей, и после
слияний #645 печатали 226 вместо 214 четверо суток (#916, #917). Литерал
`len(...)` машине от законного не отличить, поэтому держит это не запрет
формы, а инвариант: каждый счётчик запускается и сверяется с одним источником.

У СЕМЬИ СПРОСИЛИ (162). Ответы по 214 у пяти проектов: механизмы и ArtVsMark
держат литеральные копии регулярных выражений — счёт им не виден; грейдер и
глоссарий — документом. Приём взят у Token: названный предмет держит набор
(ArtVsMark/Claude-Code_Usage-Token, `tests/test_workflow_on.py`). Сверки
«счётчики сходятся» не нашлось ни у кого.

ГРАНИЦА. Новый счётчик набор не найдёт сам — его вписывают сюда же. Сборка
указателя проверяется по её производным (`active` выгрузки, маркер README):
их свежесть держит `build_rules_index.py --check`, а её `main` требует
полного клона.
"""

import json
import re
from pathlib import Path

import pytest

import aggregate_bindings as ab
import audit_catalogue as ac
import build_rules_index as b
import check_bindings as cb
import check_duplicates as cd
import consumers_picture as cp
import history_metrics as hm
import onboard_consumer as oc
import project_badge as pb
import sync_inbox as si
from conftest import write
from test_sync_inbox import arm

ROOT = Path(__file__).resolve().parent.parent
ВЫГРУЗКА = ROOT / "export" / "rules.json"
ОТВЕТ = ROOT / ".rules" / "bindings.json"


@pytest.fixture(scope="module")
def n() -> int:
    """Источник: действующие записи дерева. Замещённые в дереве есть — иначе набор пуст."""
    found, _, _ = b.collect()
    assert len(found) > len(b.действующие(found)), (
        "замещённых нет — сверять нечего, и зелёное ничего бы не значило (146)")
    return len(b.действующие(found))


def число(текст: str, образец: str) -> int:
    m = re.search(образец, текст)
    assert m, f"счётчик не напечатал число по образцу {образец!r}:\n{текст}"
    return int(m.group(1))


def test_производные_сборки(n):
    выгрузка = json.loads(ВЫГРУЗКА.read_text(encoding="utf-8"))
    assert выгрузка["active"] == n
    assert len(b.действующие_в_выгрузке(выгрузка)) == n
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert число(readme, r"<!--m:rules-->(\d+)<!--/m:rules-->") == n


def test_гейт_ответа(n, capsys):
    cb.main()
    assert число(capsys.readouterr().out, r"полон: (\d+) правил") == n


def test_гейт_соседей(n, capsys):
    cd.mode_check(ROOT)
    assert число(capsys.readouterr().out, r"правил (\d+) \(") == n


def test_аудит(n, capsys):
    ac.main([])
    assert число(capsys.readouterr().out, r"действующих правил (\d+)") == n


def test_сводка_где_действует(n):
    rule_ids, в_силе = ab.правила_выгрузки(ВЫГРУЗКА)
    assert число(ab.census([], rule_ids, в_силе)[0], r"правил в каталоге: (\d+)") == n


def test_метрики_выпуска(n):
    files = {str(p.relative_to(ROOT)): p.read_text(encoding="utf-8")
             for p in (ROOT / "rules" / "ru").glob("*.md")}
    files[".rules/bindings.json"] = ОТВЕТ.read_text(encoding="utf-8")
    assert int(hm.snapshot(files)["правил"]) == n


def test_значок(n, tmp_path):
    svg, _ = pb.собрать(ROOT, tmp_path / "нет.json", tmp_path / "нет.json")
    assert число(svg, r"machine \d+/(\d+)") == n


def test_картинка_потребителей(n, tmp_path, capsys):
    write(tmp_path / "export" / "rules.json", ВЫГРУЗКА.read_text(encoding="utf-8"))
    write(tmp_path / "export" / "where.json", json.dumps({"consumers": [
        {"repo": "o/a", "state": "подключён", "rules": {}, "answered": 0,
         "by_mechanism": {}}]}))
    assert cp.main(["--root", str(tmp_path), "--out-dir", str(tmp_path / "svg")]) == 0
    assert число(capsys.readouterr().out, r"правил (\d+);") == n


def test_заготовка_потребителя(n, tmp_path, capsys):
    oc.main(["--repo", "owner/name", "--out", str(tmp_path / "out"),
             "--export", str(ВЫГРУЗКА), "--contract", str(ROOT / "export" / "README.md")])
    assert число(capsys.readouterr().out, r"правил (\d+),") == n


def test_входящие_потребителя(n, monkeypatch, capsys):
    выгрузка = json.loads(ВЫГРУЗКА.read_text(encoding="utf-8"))
    ответ = json.loads(ОТВЕТ.read_text(encoding="utf-8"))["rules"]
    arm(monkeypatch, выгрузка["rules"], ответ, issue=("52", "OPEN"))
    si.main()
    assert число(capsys.readouterr().out, r"правил (\d+), разобрано") == n
