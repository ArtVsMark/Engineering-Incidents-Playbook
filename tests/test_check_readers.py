"""Разведение документов по читателю: объявление, словарь и полнота.

Случаи спрашивают ГЕЙТ через `main()` на поддельном дереве: разбор строки,
проверенный отдельно, не говорит, доедет ли находка до отказа (правило 150).

Подделка держит по одному документу на каждого читателя — меньше нельзя:
пустой читатель сам по себе находка, и без полного набора любой случай краснел
бы по чужой причине.
"""

from __future__ import annotations

from pathlib import Path

import check_readers as cr
from conftest import write

ВОПРОС = {
    "посетитель": "что это такое",
    "подключающийся": "как подключить",
    "участник": "как внести правку",
    "агент": "как здесь принято работать",
    "историк": "как оно было раньше",
}


def документ(читатель: str, вопрос: str | None = None, отступ: int = 1) -> str:
    строка = f"> **Читатель:** {читатель} — {вопрос if вопрос is not None else ВОПРОС.get(читатель, 'зачем-то')}."
    пусто = "\n".join(["текст"] * (отступ - 1))
    return f"# Заголовок\n\n{пусто}\n{строка}\n\nдальше текст\n"


def подделка(repo: Path, **правки: str | None) -> Path:
    """Полный набор: по документу на читателя. Правки подменяют или убирают."""
    файлы = {f"{r}.md": документ(r) for r in cr.READERS}
    for имя, тело in правки.items():
        ключ = f"{имя}.md"
        if тело is None:
            файлы.pop(ключ, None)
        else:
            файлы[ключ] = тело
    for имя, тело in файлы.items():
        write(repo / имя, тело)
    return repo


def test_polnyy_nabor_prohodit(repo):
    assert cr.main(["--root", str(подделка(repo))]) == 0


def test_dokument_bez_stroki_eto_otkaz(repo, capsys):
    """Документ, о котором не сказано, кто его читает, и есть та свалка, от
    которой правило 021 и родилось."""
    подделка(repo, посетитель="# Заголовок\n\nпросто текст без объявления\n")

    assert cr.main(["--root", str(repo)]) == 1
    assert "посетитель.md" in capsys.readouterr().err


def test_chitatel_vne_slovarya_eto_otkaz(repo, capsys):
    """Опечатка иначе заводит шестую аудиторию молча (099)."""
    подделка(repo, посетитель=документ("посититель", "что это такое"))

    assert cr.main(["--root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "посититель" in err and "словаря" in err


def test_chitatel_bez_voprosa_eto_otkaz(repo, capsys):
    """«Кому» без «зачем» не разводит два документа одного читателя."""
    подделка(repo, участник="# Заголовок\n\n> **Читатель:** участник —\n")

    assert cr.main(["--root", str(repo)]) == 1
    assert "вопрос" in capsys.readouterr().err


def test_chitatel_bez_dokumenta_eto_otkaz(repo, capsys):
    """ГЛАВНЫЙ СЛУЧАЙ. Ровно это и вскрылось у каталога: аудитория объявлена,
    а прийти ей некуда — у подключающегося проекта документа не было вовсе."""
    подделка(repo, подключающийся=None)

    assert cr.main(["--root", str(repo)]) == 1
    assert "подключающийся" in capsys.readouterr().err


def test_angliyskaya_stroka_zaschityvaetsya(repo):
    """Каталог двуязычен: у английской страницы русская строка была бы
    разрывом в её собственном тексте."""
    подделка(repo, посетитель="# Title\n\n> **Reader:** visitor — what this is.\n")

    assert cr.main(["--root", str(repo)]) == 0


def test_stroka_v_seredine_obyavleniem_ne_schitaetsya(repo, capsys):
    """Объявление стоит под заголовком, а не там, где попалось: строка в
    середине текста — это цитата или пример, а не декларация документа."""
    подделка(repo, историк=документ("историк", отступ=cr.HEAD + 3))

    assert cr.main(["--root", str(repo)]) == 1
    assert "историк" in capsys.readouterr().err


def test_readme_papki_schitaetsya_dokumentom(repo):
    """Документ папки — её README: читатель у содержимого папки от него."""
    подделка(repo, историк=None)
    write(repo / "архив" / "README.md", документ("историк"))

    assert cr.main(["--root", str(repo)]) == 0


def test_pustoy_koren_eto_tretiy_ishod(repo, capsys):
    assert cr.main(["--root", str(repo)]) == 2
    assert "не отработала" in capsys.readouterr().err
