"""Пропущенный тест называет причину: формы пропуска и форма причины.

Случаи спрашивают гейт через `main()` на поддельном наборе (правило 150), а не
разбор строки: предмет здесь — доезжает ли находка до отказа.
"""

from __future__ import annotations

from pathlib import Path

import check_skips as cs
from conftest import write

ЖИВОЙ = "def test_живой():\n    assert True\n"


def подделка(repo: Path, тело: str = ЖИВОЙ) -> Path:
    write(repo / "tests" / "test_подделка.py", тело)
    return repo


def test_nabor_bez_propuskov_prohodit(repo):
    assert cs.main(["--root", str(подделка(repo))]) == 0


def test_metka_bez_prichiny_eto_otkaz(repo, capsys):
    подделка(repo, "import pytest\n\n@pytest.mark.skip\ndef test_x():\n    pass\n")

    assert cs.main(["--root", str(repo)]) == 1
    assert "без причины" in capsys.readouterr().err


def test_metka_s_prichinoy_prohodit(repo):
    подделка(repo, 'import pytest\n\n@pytest.mark.skip(reason="ждём #12")\n'
                   "def test_x():\n    pass\n")

    assert cs.main(["--root", str(repo)]) == 0


def test_skipif_bez_prichiny_eto_otkaz(repo, capsys):
    подделка(repo, "import pytest, sys\n\n@pytest.mark.skipif(sys.platform == 'win32')\n"
                   "def test_x():\n    pass\n")

    assert cs.main(["--root", str(repo)]) == 1
    assert "test_подделка.py" in capsys.readouterr().err


def test_vyzov_s_prichinoy_prohodit(repo):
    подделка(repo, 'import pytest\n\ndef test_x():\n    pytest.skip("нет сети")\n')

    assert cs.main(["--root", str(repo)]) == 0


def test_prichina_na_sleduyushchey_stroke_zaschityvaetsya(repo):
    """Вызов переносят: окно разбора берётся абзацем, а не строкой (144)."""
    подделка(repo, 'import pytest\n\n@pytest.mark.skip(\n    reason="перенос строки"\n)\n'
                   "def test_x():\n    pass\n")

    assert cs.main(["--root", str(repo)]) == 0


def test_net_nabora_eto_tretiy_ishod(repo, capsys):
    assert cs.main(["--root", str(repo)]) == 2
    assert "не отработала" in capsys.readouterr().err


def test_pustaya_papka_nabora_eto_tretiy_ishod(repo, capsys):
    """Ноль пропусков при нуле тестов не значит ничего (075)."""
    (repo / "tests").mkdir()

    assert cs.main(["--root", str(repo)]) == 2
    assert "ни одного модуля" in capsys.readouterr().err


def test_nabor_ne_razobralsya_eto_tretiy_ishod(repo, capsys):
    """Разбор — сам механизм: не разобрав файл, гейт не проверил его, а не
    признал чистым (039, 145: объявленный исход прогоняется)."""
    подделка(repo, "def test_x(:\n    pass\n")

    assert cs.main(["--root", str(repo)]) == 2
    assert "не разобрался" in capsys.readouterr().err
