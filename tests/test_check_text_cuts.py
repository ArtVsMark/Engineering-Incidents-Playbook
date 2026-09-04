"""Разрез текста объявляет, что режет: гейт проверяется тем, что обязан
отвергнуть, и тем, что обязан пропустить.

Гейт держит НЕ СУЖДЕНИЕ, а то, что вопрос задан: различить путь модуля и абзац
по коду нельзя, и попытка различать дала бы ложные находки чаще верных — ровно
то возражение, из-за которого правило 144 долго стояло без механизма. Поэтому
случаев на «пометка стоит» здесь столько же, сколько на «не стоит».

Источник подделки (правило 170): подделывается свой же исходник — тексты
сочинены здесь нарочно, настоящей стороны у них нет по построению; см.
`scripts/check_text_cuts.py`.
"""

from __future__ import annotations

import check_text_cuts as ct


# ── что гейт обязан отвергнуть ─────────────────────────────────────────────

def test_razrez_po_tochke_bez_pometki_nahodka():
    код = 'куски = текст.split(".")\n'
    assert ct.разрезы(код) == [(1, "split")]
    assert not ct.объявлено(код.splitlines(), 1)


def test_regulyarka_po_predlozheniyam_tozhe_razrez():
    """`[.!?]` режет ровно по предложениям — тем способом, о котором правило."""
    код = 'import re\nкуски = re.split("[.!?]", текст)\n'
    assert [n for n, _ in ct.разрезы(код)] == [2]


def test_partition_eto_tozhe_rezak():
    код = 'голова, _, хвост = текст.partition(".")\n'
    assert ct.разрезы(код) == [(1, "partition")]


# ── что гейт обязан пропустить ─────────────────────────────────────────────

def test_pometka_na_svoey_stroke():
    код = 'путь = имя.split(".")[0]  # не проза: путь модуля\n'
    assert ct.объявлено(код.splitlines(), 1)


def test_pometka_strokoy_vyshe():
    """Вызов часто переносят, и пометка оказывается над ним."""
    код = ("# не проза: номер версии\n"
           'major, minor, _ = tag.split(".")\n')
    assert ct.объявлено(код.splitlines(), 2)


def test_pometka_dalshe_dvuh_strok_ne_schitaetsya():
    """ГРАНИЦА: больше двух строк — уже не «рядом», и пометка начала бы
    засчитываться от ЧУЖОГО разреза."""
    код = ("# не проза: номер версии\n"
           "пусто = 1\n"
           "ещё = 2\n"
           'куски = текст.split(".")\n')
    assert not ct.объявлено(код.splitlines(), 4)


def test_razrez_po_drugomu_razdelitelyu_ne_predmet():
    """ГРАНИЦА: по запятой, пробелу и переводу строки режут свободно —
    правило про точку, и красное на прочем было бы ложным отказом (051)."""
    assert ct.разрезы('куски = текст.split(",")\n') == []
    assert ct.разрезы('куски = текст.split()\n') == []
    assert ct.разрезы('абзацы = текст.split("\\n\\n")\n') == []


def test_stroka_v_dokstroke_ne_vyzov():
    """Поиск подстрокой нашёл бы `split(".")` в прозе о самом гейте (166)."""
    assert ct.разрезы('"""Резать по split(".") нельзя."""\n') == []


# ── исходы через main ──────────────────────────────────────────────────────

def дерево(tmp_path, текст: str):
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "x.py").write_text(текст, encoding="utf-8")
    return ["--root", str(tmp_path)]


def test_glavnyy_otvet_gejta_otkaz(tmp_path):
    assert ct.main(дерево(tmp_path, 'куски = текст.split(".")\n')) == 1


def test_s_pometkoy_chisto(tmp_path):
    argv = дерево(tmp_path, 'куски = имя.split(".")  # не проза: расширение\n')
    assert ct.main(argv) == 0


def test_net_ishodnikov_eto_tretiy_ishod(tmp_path):
    (tmp_path / "scripts").mkdir()
    assert ct.main(["--root", str(tmp_path)]) == 2
