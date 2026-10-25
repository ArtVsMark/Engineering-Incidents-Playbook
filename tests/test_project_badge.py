"""Значок проекта в две строки (#844): счёт правил, общая сетка, серое с причиной."""

import json
import re
from pathlib import Path

import pytest

import project_badge as pb
import python_badge


def ответ(**правила: dict) -> dict:
    return {"schema": "1.9", "rules": правила}


def test_счёт_правил_по_всем_и_одна_зона():
    """Знаменатель — все правила, правила и механизмы — одна зона (владелец 15.10)."""
    зоны, почему = pb.зоны_правил(
        ответ(
            **{
                "001": {"status": "active", "mechanism": "gate", "origin_kind": "own"},
                "002": {"status": "active", "mechanism": "pipeline", "origin_kind": "called"},
                "003": {"status": "active", "mechanism": "document"},
                "004": {"status": "not-applicable", "mechanism": "none"},
            }
        ),
        {"001", "002", "003", "004"},
    )
    assert почему == "" and len(зоны) == 1
    надписи = [т for т, _, _ in зоны[0]]
    assert надписи == ["rules", "machine 2/4 · 50%", "own 1", "taken 1"]


@pytest.mark.parametrize("плохой", [None, [], {"rules": []}, {"schema": "1.9"}])
def test_нет_ответа_серое_с_причиной(плохой):
    зоны, почему = pb.зоны_правил(плохой, {"001"})
    assert почему and any(цвет == pb.СЕРЫЙ for з in зоны for _, цвет, _ in з)


def test_замещённое_в_долю_механизмов_не_входит():
    """Ответ о замещённом в знаменатель и в «machine» не идёт (17.10)."""
    зоны, почему = pb.зоны_правил(
        ответ(
            **{
                "001": {"status": "active", "mechanism": "gate", "origin_kind": "own"},
                "002": {"status": "active", "mechanism": "gate", "origin_kind": "own"},
                "003": {"status": "active", "mechanism": "none"},
            }
        ),
        {"002", "003"},
    )
    assert почему == ""
    assert [т for т, _, _ in зоны[0]][1:3] == ["machine 1/2 · 50%", "own 1"]


def test_выгрузка_не_прочитана_серое_с_причиной():
    """Действующих не отличить — серое с причиной, а не счёт по всем (075)."""
    зоны, почему = pb.зоны_правил(ответ(**{"001": {"status": "active"}}), None)
    assert "выгрузка" in почему and any(цвет == pb.СЕРЫЙ for з in зоны for _, цвет, _ in з)


def test_без_знаменателя_процента_нет():
    assert pb.доля(0, 0) == "0/0 · —" and pb.цвет_доли(0, 0) == pb.СЕРЫЙ


def _зоны(*надписи_по_зонам: tuple[str, ...]) -> list[list[tuple[str, str, str]]]:
    return [[(т, "#000", "") for т in з] for з in надписи_по_зонам]


def _конец(зоны, растяжки, i) -> int:
    w = pb.ширины(зоны)
    return sum(w[: i + 1]) + sum(растяжки.get(x, 0) for x in range(i + 1)) + i * python_badge.ЗАЗОР


ВЕРХ = _зоны(
    ("CI", "Python", "3.14"),
    ("linux", "windows", "mac"),
    ("coverage", "76%"),
    ("version", "1.13.19"),
)


@pytest.mark.parametrize(
    "правила", [("rules", "m"), ("rules", "machine 170/217 · 78%", "own 150", "taken 20 и ещё")]
)
def test_rules_кончается_под_ос_пустотой(правила):
    """Одна граница (владелец 16.10): конец rules — под концом ОС."""
    низ = _зоны(правила, ("family", "gives ✓"), ("EIP ✓",))
    о1, о2 = pb.выровнять(ВЕРХ, низ)
    assert _конец(ВЕРХ, о1, pb.ЗОНА_ОС) == _конец(низ, о2, 0)
    # Растягивается только одна из двух зон границы.
    assert set(о1) <= {pb.ЗОНА_ОС} and set(о2) <= {0} and not (о1 and о2)


def test_растяжка_поровну_на_части():
    """Разница делится на все части зоны, а не уходит в последнюю (16.10)."""
    зоны = [[("a", "#000", ""), ("b", "#000", ""), ("c", "#000", "")]]
    svg = python_badge.рисунок(зоны, 0, {0: 10})
    ширины = [
        int(w)
        for w in re.findall(
            r'<rect x="[\d.]+" width="(\d+)" height="20" fill="[^"]+" clip-path', svg
        )
    ]
    свои = [python_badge._ширина(т) for т in "abc"]
    assert sum(ширины) - sum(свои) == 10
    assert max(a - b for a, b in zip(ширины, свои)) - min(a - b for a, b in zip(ширины, свои)) <= 1


def test_без_зон_выравнивать_нечего():
    assert pb.выровнять(_зоны(("CI",)), _зоны(("rules",), ("x",))) == ({}, {})


def _дерево(tmp_path: Path) -> tuple[Path, Path, Path]:
    (tmp_path / ".rules").mkdir()
    (tmp_path / ".rules" / "bindings.json").write_text(
        json.dumps(ответ(**{"001": {"status": "active", "mechanism": "gate"}})), encoding="utf-8"
    )
    зоны = tmp_path / "python.zones.json"
    зоны.write_text(
        json.dumps([[["CI", "#444d56", ""], ["ok", "#2da44e", "CI пройден"]]]), encoding="utf-8"
    )
    разбор = tmp_path / "family-check.json"
    разбор.write_text(
        json.dumps(
            {
                "segments": {"gives": {"state": "ok", "why": "", "links": []}},
                "publishers": [{"code": "EIP", "state": "ok", "why": ""}],
            }
        ),
        encoding="utf-8",
    )
    return tmp_path, зоны, разбор


def test_две_строки_без_трансформаций(tmp_path):
    svg, серое = pb.собрать(*_дерево(tmp_path))
    assert серое == []
    assert 'height="44"' in svg.split(">", 1)[0]
    assert "transform" not in svg and svg.count("<svg") == 1
    assert re.search(r'<clipPath id="z\w+"><rect y="24"', svg)
    assert "machine 1/1 · 100%" in svg and "EIP" in svg


def test_зоны_рядом_с_картинкой():
    """python_badge кладёт зоны рядом с картинкой: python.svg → python.zones.json."""
    assert Path("python.svg").with_name("python" + python_badge.ЗОНЫ).name == "python.zones.json"


def test_нет_частей_серое_а_не_битая_картинка(tmp_path, capsys):
    out = tmp_path / "out" / "project.svg"
    код = pb.main(
        [
            "--root",
            str(tmp_path),
            "--python-zones",
            str(tmp_path / "нет.json"),
            "--family-json",
            str(tmp_path / "нет2.json"),
            "--out",
            str(out),
        ]
    )
    assert код == 1
    svg = out.read_text(encoding="utf-8")
    # Видимая надпись части — текст без тени: три серые части, по одной на источник.
    assert len(re.findall(r'y="(?:14|38)">n/a<', svg)) == 3
    assert "нет.json" in capsys.readouterr().err


@pytest.mark.parametrize("зоны", ["{}", "[]", '[["a"]]', '[[["a", "b"]]]'])
def test_зоны_не_той_формы_серое(tmp_path, зоны):
    путь = tmp_path / "python.zones.json"
    путь.write_text(зоны, encoding="utf-8")
    _, почему = pb.зоны_состояния(путь)
    assert почему


def test_файл_не_записан_третий_исход(tmp_path):
    root, зоны, разбор = _дерево(tmp_path)
    занято = tmp_path / "файл"
    занято.write_text("", encoding="utf-8")
    код = pb.main(
        [
            "--root",
            str(root),
            "--python-zones",
            str(зоны),
            "--family-json",
            str(разбор),
            "--out",
            str(занято / "project.svg"),
        ]
    )
    assert код == 2


def test_рисунок_без_сдвига_и_отступов_прежний():
    """Новые входы по умолчанию не меняют python.svg и family.svg ни на байт."""
    зоны = [[("a", "#000", "w")]]
    assert (
        python_badge.рисунок(зоны)
        == python_badge.рисунок(зоны, 0, None)
        == python_badge.рисунок(зоны, 0, {})
    )


@pytest.mark.parametrize("выгрузка", ['{"schema": "1.8"}', "[]", "не json"])
def test_выгрузка_без_правил_серая_а_не_ноль(tmp_path, monkeypatch, выгрузка):
    """Прочитанная выгрузка без списка «rules» — серое с причиной, а не «0/0» (обзор #917)."""
    путь = tmp_path / "rules.json"
    путь.write_text(выгрузка, encoding="utf-8")
    monkeypatch.setattr(pb, "ВЫГРУЗКА", путь)
    (tmp_path / ".rules").mkdir()
    (tmp_path / ".rules" / "bindings.json").write_text(
        json.dumps(ответ(**{"001": {"status": "active", "mechanism": "gate"}})), encoding="utf-8"
    )
    svg, почему = pb.собрать(tmp_path, tmp_path / "нет.json", tmp_path / "нет.json")
    assert any("выгрузка" in п for п in почему)
    assert "0/0" not in svg
