"""Вердикт после последнего случая: ранний выход прячет непроверенное.

Подделка — исходный текст, а не файл на диске: предмет гейта это ДЕРЕВО
РАЗБОРА, и подставлять ему текст значит спрашивать ровно то, что он смотрит
(правило 137).

Здоровые предметы взяты у самой границы: возврат третьего исхода внутри цикла
законен и обязан быть ранним — продолжать перебор, не прочитав источник,
значит копить находки о состоянии, которого не знаешь (039).
"""

from __future__ import annotations

import ast

import check_verdict_order as cv


def находки(src: str) -> list[str]:
    return cv.early(ast.parse(src), "подделка.py")


# ── здоровые предметы ──────────────────────────────────────────────────────

def test_verdikt_posle_cikla_prohodit():
    assert not находки("""
def check(items):
    out = []
    for i in items:
        if i:
            out.append(i)
    return out
""")


def test_tretiy_ishod_vnutri_cikla_zakonen():
    """Предмет у границы: `return 2` — отказ, а не вердикт."""
    assert not находки("""
def check(items):
    out = []
    for i in items:
        if i is None:
            return 2
        out.append(i)
    return out
""")


def test_tretiy_ishod_kortezhem_tozhe_zakonen():
    """Замер на живом дереве: `return 2, [], problems` — сборщика нет."""
    assert not находки("""
def refresh(builders):
    problems = []
    for b in builders:
        if not b:
            problems.append("сборщика нет")
            return 2, [], problems
        problems.append(b)
    return 0, [], problems
""")


def test_cikl_bez_nakopitelya_ne_predmet():
    assert not находки("""
def first(items):
    out = []
    for i in items:
        if i:
            return i
    return out
""")


def test_vozvrat_konstanty_ne_verdikt():
    """Ранний `return 1` без накопителя ничего не прячет: он не о находках."""
    assert not находки("""
def check(items):
    out = []
    for i in items:
        out.append(i)
        if i == "стоп":
            return 1
    return out
""")


# ── предметы, которые гейт обязан отвергнуть ───────────────────────────────

def test_ranniy_verdikt_eto_nahodka():
    """Ровно предмет правила: половина случаев осталась непроверенной."""
    out = находки("""
def check(items):
    problems = []
    for i in items:
        if not i:
            problems.append("пусто")
            return problems
    return problems
""")

    assert out and "ВНУТРИ цикла" in out[0]


def test_ranniy_verdikt_kortezhem_tozhe_nahodka():
    out = находки("""
def check(items):
    problems = []
    for i in items:
        problems.append(i)
        if problems:
            return 1, problems
    return 0, problems
""")

    assert out


def test_nahodka_nazyvaet_funkciyu_i_stroku():
    """«Где-то рано» чинить нечем: отказ называет предмет (158)."""
    out = находки("""
def проверка(items):
    находки = []
    for i in items:
        находки.append(i)
        return находки
""")

    assert out and "проверка" in out[0] and "строка" in out[0]


def test_vlozhennyy_cikl_tozhe_smotritsya():
    out = находки("""
def check(rows):
    problems = []
    for row in rows:
        for cell in row:
            problems.append(cell)
            return problems
    return problems
""")

    assert out


def test_gate_otvechaet_otkazom_na_poddelannom_dereve(repo, capsys):
    """Решение спрашивается у САМОГО ГЕЙТА через main(), а не у функции
    разбора: случай, повторяющий условие, проверяет условие (правило 150)."""
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "ранний.py").write_text("""
def check(items):
    problems = []
    for i in items:
        problems.append(i)
        return problems
    return problems
""", encoding="utf-8")

    assert cv.main(["--root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "посреди перебора" in err and "ранний.py" in err


def test_gate_propuskaet_zdorovoe_derevo(repo, capsys):
    """Вторая половина набора: гейт из одних отказов проверен наполовину
    (правило 140) — здоровый предмет обязан пройти."""
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "здоровый.py").write_text("""
def check(items):
    problems = []
    for i in items:
        if i is None:
            return 2
        problems.append(i)
    return problems
""", encoding="utf-8")

    assert cv.main(["--root", str(repo)]) == 0
    assert "ранних вердиктов нет" in capsys.readouterr().out


# ── третий исход: проверка не отработала ──────────────────────────────────

def test_nerazobrannyy_fayl_eto_tretiy_ishod(repo, capsys):
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "битый.py").write_text("def (\n", encoding="utf-8")

    assert cv.main(["--root", str(repo)]) == 2
    assert "не разобран" in capsys.readouterr().err


def test_nechego_prosmatrivat_eto_tretiy_ishod(repo, capsys):
    assert cv.main(["--root", str(repo)]) == 2
    assert "просматривать нечего" in capsys.readouterr().err
