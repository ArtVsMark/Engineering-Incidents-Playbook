"""Явная кодировка у текстового вызова: гейт проверяется тем, что обязан
отвергнуть, и тем, что обязан пропустить.

Ложный отказ здесь дороже пропуска: двоичный вызов кодировки не принимает
вовсе, и красное на нём заставило бы обходить гейт (051). Поэтому обе стороны
стоят случаями, а не одна.

Разбор — чистая функция над текстом: ни площадка, ни файловая система не
трогаются.
"""

from __future__ import annotations

import check_subprocess as cs


def test_tekstovyy_vyzov_bez_kodirovki_nahodka():
    """Ровно тот случай, что дал 32 находки на живом дереве."""
    код = "subprocess.run(['git', 'log'], capture_output=True, text=True)"
    assert [n for n, _ in cs.offenders(код)] == [1]


def test_s_kodirovkoy_chisto():
    код = 'subprocess.run(["git"], text=True, encoding="utf-8")'
    assert cs.offenders(код) == []


def test_dvoichnyy_vyzov_ne_nahodka():
    """ГРАНИЦА: у двоичного вызова кодировки нет по построению."""
    assert cs.offenders("subprocess.run(['git'], capture_output=True)") == []


def test_errors_bez_encoding_tozhe_nahodka():
    """Самый коварный случай: `errors=` включает текстовый режим и берёт ту же
    локаль, а выглядит предусмотрительностью."""
    код = 'subprocess.run(["git"], errors="replace")'
    assert len(cs.offenders(код)) == 1


def test_universal_newlines_schitaetsya_tekstovym():
    код = "subprocess.run(['git'], universal_newlines=True)"
    assert len(cs.offenders(код)) == 1


def test_slovo_v_dokstroke_ne_vyzov():
    """Поиск подстрокой дал бы находку здесь; разбор дерева не даёт (166)."""
    assert cs.offenders('"""Пример: subprocess.run(..., text=True)."""\n') == []


def test_vyzov_razlozhennyy_po_strokam_naydetsya():
    """И обратная сторона того же: поиск по строке пропустил бы это."""
    код = ("subprocess.run(\n"
           "    ['git', 'log'],\n"
           "    text=True,\n"
           ")\n")
    assert len(cs.offenders(код)) == 1


def test_tretiy_ishod_bez_ishodnikov(tmp_path):
    """Ноль просмотренных файлов — отказ, а не чистый прогон (075)."""
    assert cs.main(["--root", str(tmp_path)]) == 2


def test_gejt_otvechaet_otkazom_cherez_main(tmp_path):
    """Случай спрашивает РЕШЕНИЕ гейта, а не повторяет его условие (150)."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "x.py").write_text(
        "import subprocess\nsubprocess.run(['git'], text=True)\n", encoding="utf-8")
    assert cs.main(["--root", str(tmp_path)]) == 1


# ── список путей читается по NUL (165) ─────────────────────────────────────

def test_spisok_putey_bez_z_nahodka():
    """Ровно тот случай, что дал семь мест на живом дереве."""
    код = 'subprocess.run(["git", "ls-files"], capture_output=True)'
    assert [n for n, _ in cs.unseparated(код)] == [1]


def test_s_z_chisto():
    код = 'subprocess.run(["git", "ls-files", "-z"], capture_output=True)'
    assert cs.unseparated(код) == []


def test_quotepath_prinimaetsya_kak_ravnosilnyy():
    """ГРАНИЦА, НАЙДЕННАЯ ЖИВЫМ ОТКАЗОМ: `core.quotePath=false` снимает ту же
    поломку с другой стороны, и два места в дереве отвечали именно так."""
    код = ('subprocess.run(["git", "-c", "core.quotePath=false", "status",'
           ' "--porcelain"])')
    assert cs.unseparated(код) == []


def test_vyzov_bez_spiska_putey_ne_nahodka():
    """У `git describe` списка нет — требовать от него разделитель значило бы
    краснеть на верном вызове."""
    assert cs.unseparated('subprocess.run(["git", "describe", "--tags"])') == []


def test_ne_git_ne_trogaetsya():
    assert cs.unseparated('subprocess.run(["ls", "--name-only"])') == []

