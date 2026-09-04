"""У подделки назван источник: гейт проверяется тем, что обязан отвергнуть,
и тем, что обязан пропустить.

Ложный отказ здесь дороже пропуска, и потому граница «свои константы под
правило не подпадают» стоит отдельным случаем: набор подменяет и путь к файлу,
и корень дерева, и argv — требовать от них источника значило бы краснеть на
верном (051).

Источник подделки (правило 170): подделывается не чужая сторона, а СВОЙ разбор
— тексты наборов сочиняются здесь нарочно, и настоящей стороны у них нет по
построению. Это законный случай границы: гейт разбирает исходники своего же
дерева, см. `scripts/check_forgeries.py`.
"""

from __future__ import annotations

import check_forgeries as cf


# ── что гейт обязан отвергнуть ─────────────────────────────────────────────

ПОДМЕНА = ('def test_x(monkeypatch):\n'
           '    monkeypatch.setattr(mod.ghcli, "run", lambda *a: (0, "[]"))\n')


def test_shov_bez_istochnika_nahodka():
    assert cf.швы(ПОДМЕНА) == ["run"]
    assert not cf.назван_источник(ПОДМЕНА)


def test_slovo_bez_adresa_ne_schitaetsya():
    """ГЛАВНАЯ ПОЛОВИНА: «источник» без адреса отвечает на вопрос «сказано ли»,
    а не «с чем сверять». Проверка отношения без отношения зеленеет там, где
    отношения нет (166)."""
    текст = '"""Источник подделки: снято с площадки."""\n' + ПОДМЕНА
    assert not cf.назван_источник(текст)


def test_adres_bez_slova_ne_schitaetsya():
    """Обратная половина: путь в тексте сам по себе источником не объявляет —
    их в наборе десятки."""
    текст = '"""Разбор идёт по rules/ru/001-x.md."""\n' + ПОДМЕНА
    assert not cf.назван_источник(текст)


# ── что гейт обязан пропустить ─────────────────────────────────────────────

def test_komanda_v_kavychkah_eto_adres():
    текст = ('"""Источник подделки: снято с `gh pr list --json number`."""\n'
             + ПОДМЕНА)
    assert cf.назван_источник(текст)


def test_ssylka_eto_adres():
    текст = ('"""Форма снята с https://raw.githubusercontent.com/x/y/main/e.json"""\n'
             + ПОДМЕНА)
    assert cf.назван_источник(текст)


def test_nomer_zadachi_eto_adres():
    текст = '"""Форма снята с живого случая: ArtVsMark/ArtVsMark#52."""\n' + ПОДМЕНА
    assert cf.назван_источник(текст)


def test_obyavlenie_v_dve_stroki():
    """Объявление в докстроке переносится; окно в две строки — та же граница,
    что у разбора прозы (144)."""
    текст = ('"""Источник подделки:\n'
             '`gh issue list --json number,body`.\n"""\n' + ПОДМЕНА)
    assert cf.назван_источник(текст)


def test_svoi_konstanty_pod_pravilo_ne_podpadayut():
    """ГРАНИЦА: подмена своего пути, корня и argv — не подделка чужой стороны."""
    текст = ('def test_x(monkeypatch):\n'
             '    monkeypatch.setattr(mod, "LABELS", path)\n'
             '    monkeypatch.setattr(mod, "ROOT", repo)\n'
             '    monkeypatch.setattr("sys.argv", ["x.py"])\n')
    assert cf.швы(текст) == []


def test_nabor_bez_shva_ne_sprashivaetsya():
    assert cf.швы("def test_x():\n    assert 1 == 1\n") == []


# ── исходы через main ──────────────────────────────────────────────────────

def дерево(tmp_path, файлы: dict[str, str]):
    (tmp_path / "tests").mkdir(exist_ok=True)
    for имя, текст in файлы.items():
        (tmp_path / "tests" / имя).write_text(текст, encoding="utf-8")
    return ["--root", str(tmp_path)]


def test_glavnyy_otvet_gejta_otkaz(tmp_path):
    """Решение гейта, а не повторение его условия (150)."""
    assert cf.main(дерево(tmp_path, {"test_a.py": ПОДМЕНА})) == 1


def test_s_istochnikom_chisto(tmp_path):
    текст = '"""Снято с `gh pr list --json number`."""\n' + ПОДМЕНА
    assert cf.main(дерево(tmp_path, {"test_a.py": текст})) == 0


def test_net_naborov_eto_tretiy_ishod(tmp_path):
    (tmp_path / "tests").mkdir()
    assert cf.main(["--root", str(tmp_path)]) == 2


def test_ni_odnogo_shva_eto_tretiy_ishod(tmp_path):
    """Гейт, не нашедший предмета, обязан упасть, а не зазеленеть (075): набор
    без единого шва наружу означает, что искали не там."""
    argv = дерево(tmp_path, {"test_a.py": "def test_x():\n    assert 1\n"})
    assert cf.main(argv) == 2
