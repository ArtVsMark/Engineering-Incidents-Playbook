"""Языковые деревья: английская запись — перевод, а не копия.

Случаи спрашивают гейт через `main()` на поддельном дереве (правило 150).
Пороги в подделке те же, что в бою: подмена порога проверяла бы арифметику
сравнения, а не решение гейта.
"""

from __future__ import annotations

from pathlib import Path

import check_locale as cl
from conftest import write

РУССКИЙ = ("# Правило одной строкой\n\n**Область.** гейты\n\n"
           "Запись целиком по-русски: инцидент, механизм поломки и граница.\n")
АНГЛИЙСКИЙ = ("# A rule in one line\n\n**Area.** gates\n\n"
              "The record in English: the incident, the mechanism and the boundary.\n")


def подделка(repo: Path, ru: str = РУССКИЙ, en: str = АНГЛИЙСКИЙ) -> Path:
    write(repo / "rules/ru/001-a-rule.md", ru)
    write(repo / "rules/en/001-a-rule.md", en)
    return repo


def test_perevedennaya_para_prohodit(repo):
    assert cl.main(["--root", str(подделка(repo))]) == 0


def test_russkiy_tekst_v_angliyskom_dereve_eto_otkaz(repo, capsys):
    """Ровно тот случай, которого не видит структурная сверка: разделы на
    месте, имена совпадают, а запись не переведена."""
    подделка(repo, en=РУССКИЙ)

    assert cl.main(["--root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "en/001-a-rule.md" in err and "непереведённой" in err


def test_angliyskiy_tekst_v_russkom_dereve_eto_otkaz(repo, capsys):
    """Обратная сторона: русское дерево — канон, и английский текст в нём
    означает, что перевод положили не туда."""
    подделка(repo, ru=АНГЛИЙСКИЙ)

    assert cl.main(["--root", str(repo)]) == 1
    assert "ru/001-a-rule.md" in capsys.readouterr().err


def test_imena_i_kod_v_znamenatel_ne_idut(repo):
    """Английская запись цитирует русские имена файлов и терминов — это не
    делает её непереведённой: порог стоит с запасом в разы."""
    подделка(repo, en=АНГЛИЙСКИЙ + "\nSee `rules/ru/001-правило.md` for the original.\n")

    assert cl.main(["--root", str(repo)]) == 0


def test_net_derevev_eto_tretiy_ishod(repo, capsys):
    assert cl.main(["--root", str(repo)]) == 2
    assert "не отработала" in capsys.readouterr().err
