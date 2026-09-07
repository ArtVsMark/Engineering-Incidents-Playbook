"""Выбор коммита спрашивается на выдуманной истории, а не на настоящей ветке.

Прежний выбор жил строкой оболочки в agent-pr.yml, и единственной пробой был
толчок ветки — то есть проверка ПОСЛЕ того, как заголовок уехал (018). Здесь
история собирается в тесте: каждый случай — три-четыре коммита, и ответ виден
до того, как что-либо открыто.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import pr_source_commit as psc  # noqa: E402


def git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, encoding="utf-8", check=True)
    return done.stdout.strip()


def commit(root: Path, subject: str, name: str = "f",
           content: str | None = None) -> str:
    """Содержимое задаётся отдельно от заголовка НЕ для красоты: два коммита с
    одним родителем, деревом, заголовком и секундой — один и тот же объект git,
    и «слитая уплотнением соседка» тихо становилась предком общей ветки. Тогда
    случай проверял бы не то, ради чего заведён (140)."""
    (root / name).write_text(content or subject, encoding="utf-8")
    git(root, "add", name)
    git(root, "commit", "-q", "-m", subject)
    return git(root, "rev-parse", "HEAD")


@pytest.fixture
def дерево(tmp_path: Path) -> Path:
    """Пустое дерево с общей веткой `main` и одним коммитом на ней."""
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "проба")
    git(root, "config", "user.email", "проба@example.com")
    commit(root, "chore: начало")
    return root


def test_svoy_pervyy_kommit_i_dayot_zagolovok(дерево):
    """Обычный случай: ветка от общей, заголовок берётся у первого коммита."""
    git(дерево, "checkout", "-q", "-b", "agent/своя")
    свой = commit(дерево, "feat(rules): своя тема (200)")
    commit(дерево, "chore: пересобрать производные")

    sha, code, why = psc.choose(дерево, "main")

    assert code == 0
    assert sha == свой, why


def test_chuzhoy_kommit_slitoy_vetki_propuskaetsya(дерево):
    """РОВНО ПРЕДМЕТ ПРАВИЛА, ЗАМЕР 7 сентября (#368, #376). Ветка начата
    поверх соседней; соседняя слита уплотнением — её коммита в предках общей
    ветки НЕТ, но её заголовок в общей ветке стоит. Прежний выбор отдавал
    именно этот коммит, и #368 повторил заголовок #367 слово в слово."""
    git(дерево, "checkout", "-q", "-b", "agent/соседняя")
    commit(дерево, "fix(bindings): отложенное — не долг (177)", name="a")

    # Уплотняющее слияние: в общей ветке один НОВЫЙ коммит с тем же заголовком.
    git(дерево, "checkout", "-q", "main")
    commit(дерево, "fix(bindings): отложенное — не долг (177)", name="a",
           content="слито уплотнением")

    git(дерево, "checkout", "-q", "agent/соседняя")
    git(дерево, "checkout", "-q", "-b", "agent/своя")
    свой = commit(дерево, "feat(gates): своя тема (201)", name="b")

    sha, code, why = psc.choose(дерево, "main")

    assert code == 0
    assert sha == свой, why


def test_neskolko_chuzhih_kommitov_propuskayutsya_podryad(дерево):
    """НАЙДЕНО РЕВЬЮ, А НЕ РАССУЖДЕНИЕМ, И ЭТО ОБЫЧНЫЙ ВХОД. Соседняя ветка
    редко состоит из одного коммита: уплотнение схлопывает её целиком, и в
    общей ветке стоит заголовок ПЕРВОГО из них. Второй («chore: пересобрать
    производные») не совпадает заголовком ни с чем — и первая редакция выбора
    отдавала его. Случай при этом ЗАПИСЫВАЛ эту ошибку ожидаемым результатом,
    и набор зеленел на дефекте (146).

    Держит теперь признак по содержимому: второй чужой коммит на своих путях
    не отличается от общей ветки, потому что уплотнение унесло туда обе его
    правки."""
    git(дерево, "checkout", "-q", "-b", "agent/соседняя")
    commit(дерево, "fix(export): чужая тема (049)", name="a")
    вторая = commit(дерево, "chore: пересобрать производные", name="a2")

    # Уплотнение несёт в общую ветку ОБА файла соседки одним коммитом, и
    # содержимое там то же самое: иначе случай проверял бы не уплотнение.
    git(дерево, "checkout", "-q", "main")
    (дерево / "a").write_text("fix(export): чужая тема (049)", encoding="utf-8")
    (дерево / "a2").write_text("chore: пересобрать производные", encoding="utf-8")
    git(дерево, "add", "a", "a2")
    git(дерево, "commit", "-q", "-m", "fix(export): чужая тема (049)")

    git(дерево, "checkout", "-q", вторая)
    git(дерево, "checkout", "-q", "-b", "agent/своя")
    свой = commit(дерево, "feat(rules): своя тема (202)", name="b")

    sha, code, why = psc.choose(дерево, "main")

    assert code == 0
    assert sha == свой, why


def test_chuzhoy_kommit_bez_sovpadeniya_zagolovka_lovitsya_soderzhimym(дерево):
    """Граница с другой стороны: признак по содержимому работает и БЕЗ
    заголовка в общей ветке. Уплотнение могло уехать под другим именем —
    заголовок изменения правится руками, и правился сегодня трижды."""
    git(дерево, "checkout", "-q", "-b", "agent/соседняя")
    commit(дерево, "fix(export): чужая тема (049)", name="a")

    git(дерево, "checkout", "-q", "main")
    commit(дерево, "совсем другой заголовок", name="a",
           content="fix(export): чужая тема (049)")

    git(дерево, "checkout", "-q", "agent/соседняя")
    git(дерево, "checkout", "-q", "-b", "agent/своя")
    свой = commit(дерево, "feat(rules): своя тема (204)", name="b")

    sha, code, why = psc.choose(дерево, "main")

    assert (sha, code) == (свой, 0), why


def test_svoy_kommit_ne_propuskaetsya_iz_za_sosedney_pravki(дерево):
    """ЛОЖНЫЙ ПРОПУСК ЗДЕСЬ ДОРОЖЕ ЛИШНЕГО: он уносит заголовок вперёд, к
    производным. Свой коммит трогает файл, которого в общей ветке нет вовсе, —
    признак по содержимому обязан молчать, даже когда рядом стоит слитая
    соседка (051)."""
    git(дерево, "checkout", "-q", "-b", "agent/своя")
    свой = commit(дерево, "feat(rules): своя тема (205)", name="новый")
    commit(дерево, "chore: пересобрать производные", name="ещё")

    sha, code, why = psc.choose(дерево, "main")

    assert (sha, code) == (свой, 0), why


def test_vetka_bez_kommitov_eto_ishod_1(дерево):
    """Открывать нечего — отдельный ответ, а не отказ и не пустой отпечаток."""
    git(дерево, "checkout", "-q", "-b", "agent/пустая")

    sha, code, why = psc.choose(дерево, "main")

    assert (sha, code) == (None, 1)
    assert "main" in why


def test_vsya_vetka_opoznana_kak_slitaya_beryot_pervyy(дерево):
    """«Неизвестно» и «чужое» — разные ответы (051). Своей работы не видно,
    но изменение всё равно обязано открыться (147): выбор называет первый
    коммит и говорит, что это запасной путь."""
    git(дерево, "checkout", "-q", "-b", "agent/своя")
    первый = commit(дерево, "chore: повтор", name="a")

    git(дерево, "checkout", "-q", "main")
    commit(дерево, "chore: повтор", name="a", content="иное содержимое")
    git(дерево, "checkout", "-q", "agent/своя")

    sha, code, why = psc.choose(дерево, "main")

    assert (sha, code) == (первый, 0)
    assert "запасной" in why


def test_git_ne_otvetil_eto_tretiy_ishod_s_predmetom(дерево):
    """Третий исход называет команду, которая не ответила (158)."""
    sha, code, why = psc.choose(дерево, "origin/такой-ветки-нет")

    assert (sha, code) == (None, 2)
    assert "git rev-list" in why and "такой-ветки-нет" in why


def test_main_pechataet_otpechatok_v_stdout(дерево, capsys):
    """Прогон подставляет ответ в переменную оболочки: объяснение обязано
    уехать в stderr, иначе оно попадёт в заголовок изменения."""
    git(дерево, "checkout", "-q", "-b", "agent/своя")
    свой = commit(дерево, "feat(rules): своя тема (203)")

    assert psc.main(["--root", str(дерево), "--base", "main"]) == 0
    напечатано = capsys.readouterr()
    assert напечатано.out.strip() == свой
    assert "заголовок даёт" in напечатано.err
