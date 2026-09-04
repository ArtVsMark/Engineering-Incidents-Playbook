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
    код = ("import subprocess\n"
           "subprocess.run(['git', 'log'], capture_output=True, text=True)")
    assert [n for n, _ in cs.offenders(код)] == [2]


def test_s_kodirovkoy_chisto():
    код = 'subprocess.run(["git"], text=True, encoding="utf-8")'
    assert cs.offenders(код) == []


def test_dvoichnyy_vyzov_ne_nahodka():
    """ГРАНИЦА: у двоичного вызова кодировки нет по построению."""
    assert cs.offenders("subprocess.run(['git'], capture_output=True)") == []


def test_errors_bez_encoding_tozhe_nahodka():
    """Самый коварный случай: `errors=` включает текстовый режим и берёт ту же
    локаль, а выглядит предусмотрительностью."""
    код = 'import subprocess\nsubprocess.run(["git"], errors="replace")'
    assert len(cs.offenders(код)) == 1


def test_universal_newlines_schitaetsya_tekstovym():
    код = ("import subprocess\n"
           "subprocess.run(['git'], universal_newlines=True)")
    assert len(cs.offenders(код)) == 1


def test_slovo_v_dokstroke_ne_vyzov():
    """Поиск подстрокой дал бы находку здесь; разбор дерева не даёт (166)."""
    assert cs.offenders('"""Пример: subprocess.run(..., text=True)."""\n') == []


def test_vyzov_razlozhennyy_po_strokam_naydetsya():
    """И обратная сторона того же: поиск по строке пропустил бы это."""
    код = ("import subprocess\n"
           "subprocess.run(\n"
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


# ── правило 180: предмет разрешается по импортам, а не по хвосту имени ──────

def test_svoya_funktsiya_s_tem_zhe_imenem_ne_nahodka():
    """ГЛАВНЫЙ СЛУЧАЙ 180, и он про ложную находку, а не про пропуск.

    В дереве каталога двенадцать своих функций с именем `run`. По последнему
    звену имени они неотличимы от subprocess.run, и автоматическая правка у
    потребителя дописала таким несуществующий параметр — пятнадцать тестов
    упали. Ложная находка здесь дороже пропуска: она чинит работающий код.
    """
    код = ("import subprocess\n"
           "def run(cmd, text=True): ...\n"
           "run(['x'], text=True)\n")
    assert cs.offenders(код) == []


def test_psevdonim_funktsii_nahoditsya():
    """ОБРАТНАЯ ПОЛОВИНА ТОГО ЖЕ, и у каталога она была открыта полностью:
    до разрешения по импортам такой вызов не находился вовсе — гейт зеленел
    за отсутствие того, чего не умел увидеть (146)."""
    код = ("from subprocess import run as запустить\n"
           "запустить(['x'], text=True)\n")
    assert [n for n, _ in cs.offenders(код)] == [2]


def test_psevdonim_modulya_nahoditsya():
    код = "import subprocess as sp\nsp.run(['x'], text=True)\n"
    assert [n for n, _ in cs.offenders(код)] == [2]


def test_chuzhoy_modul_s_tem_zhe_imenem_metoda_ne_nahodka():
    """ГРАНИЦА: `pool.run(..., text=True)` — не subprocess, и звено имени об
    этом не сообщает ничего."""
    код = ("import subprocess\n"
           "import pool\n"
           "pool.run(['x'], text=True)\n")
    assert cs.offenders(код) == []


def test_import_vnutri_funktsii_tozhe_schitaetsya():
    """Импорт бывает не только в шапке; разбор идёт по всему дереву."""
    код = ("def f():\n"
           "    import subprocess\n"
           "    subprocess.run(['x'], text=True)\n")
    assert [n for n, _ in cs.offenders(код)] == [3]


# ── правила 017 и 058: площадку зовут через одну дверь ─────────────────────

def test_gh_naprjamuyu_nahodka():
    """Мимо ghcli «лимит кончился» снова становится неотличимо от «ничего не
    нашлось»: площадка отдаёт 1 в обоих случаях. Цена известна — 2 сентября
    четыре изменения подряд не открылись, и никто не покраснел."""
    код = 'import subprocess\nsubprocess.run(["gh", "issue", "list"])\n'
    assert cs.мимо_двери(код) == [2]


def test_gh_kortezhem_tozhe_nahodka():
    код = 'import subprocess\nsubprocess.run(("gh", "pr", "view"))\n'
    assert cs.мимо_двери(код) == [2]


def test_which_ne_vyzov_podprotsessa():
    """ГРАНИЦА: `shutil.which("gh")` спрашивает, есть ли инструмент, и площадку
    не трогает вовсе. Красное на нём — ложный отказ (051)."""
    assert cs.мимо_двери('import shutil\nshutil.which("gh")\n') == []


def test_sosednyaya_komanda_ne_trogaetsya():
    """Предмет — ПЕРВОЕ слово списка, а не наличие строки «gh» в вызове:
    проверка отношения через подстроку краснела бы там, где отношения нет
    (166)."""
    assert cs.мимо_двери('import subprocess\nsubprocess.run(["git", "log"])\n') == []


def test_cherez_dver_chisto():
    assert cs.мимо_двери('import ghcli\nghcli.run("issue", "list")\n') == []

