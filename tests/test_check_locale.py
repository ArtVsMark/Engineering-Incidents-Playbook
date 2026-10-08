"""Языковые деревья: английская запись — перевод, а не копия.

Случаи спрашивают гейт через `main()` на поддельном дереве (правило 150).
Пороги в подделке те же, что в бою: подмена порога проверяла бы арифметику
сравнения, а не решение гейта.
"""


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


# ── запас порога — проверяемое утверждение (правило 070) ──────────────────

def test_английское_у_самого_потолка_это_находка(repo, capsys):
    """Ниже потолка, но выше половины: порог прошёл бы, запас — нет."""
    англ = АНГЛИЙСКИЙ + "Цитата: " + "щ" * 2 + "\n"
    доля = cl.share(англ)
    assert cl.EN_MARGIN < доля <= cl.EN_CEIL
    assert cl.main(["--root", str(подделка(repo, en=англ))]) == 1
    assert "без запаса" in capsys.readouterr().err


def test_русское_у_самого_пола_это_находка(repo, capsys):
    рус = РУССКИЙ + "English quote kept as is in the original wording.\n"
    доля = cl.share(рус)
    assert cl.RU_FLOOR <= доля < cl.RU_MARGIN
    assert cl.main(["--root", str(подделка(repo, ru=рус))]) == 1
    assert "без запаса" in capsys.readouterr().err


def test_сдвиг_порога_запас_не_двигает(repo, capsys):
    """Поднять потолок «под корпус» правкой числа В ИСХОДНИКЕ — ровно то
    ослабление, о котором 070. Подмена атрибута после импорта этого не
    воспроизводит: производное от порога уже вычислено, и тест зеленел бы на
    коде, где запас едет вместе с порогом."""
    import importlib.util
    исходник = Path(cl.__file__).read_text(encoding="utf-8")
    assert "EN_CEIL = 0.15" in исходник
    правка = repo / "check_locale_ослаблен.py"
    правка.write_text(исходник.replace("EN_CEIL = 0.15", "EN_CEIL = 0.30"),
                      encoding="utf-8")
    spec = importlib.util.spec_from_file_location("ослаблен", правка)
    ослаблен = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ослаблен)
    англ = АНГЛИЙСКИЙ + "Цитата: " + "щ" * 2 + "\n"
    assert ослаблен.main(["--root", str(подделка(repo, en=англ))]) == 1
    assert "без запаса" in capsys.readouterr().err
