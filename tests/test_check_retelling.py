"""Пересказ своей работы (215): машинная часть — полнота, и только предупреждением.

Случай #631 стоит здесь живым: «Две находки» в теле при трёх строках
«Разобрано:» и цитате обзора «находок 0» рядом. Источник тела — изменение
ArtVsMark/Engineering-Incidents-Playbook#631, слитое 27.09.
"""

from pathlib import Path

import pytest

import check_retelling as cr

ТЕЛО_631 = """Две находки по #629 закрыты ещё коммитом 18ca670 в самом #629 — ревью
его третьего прогона дало «находок 0», — а из списка не сняты.

Разобрано: d7f50f9
Разобрано: 1d578df
Разобрано: bf23959
"""


def прогон(tmp_path: Path, тело: str, пути: list[str] = ()) -> int:
    (tmp_path / "p.txt").write_text("\n".join(пути), encoding="utf-8")
    (tmp_path / "b.md").write_text(тело, encoding="utf-8")
    return cr.main(
        [
            "--root",
            str(tmp_path),
            "--paths-from",
            str(tmp_path / "p.txt"),
            "--body-file",
            str(tmp_path / "b.md"),
        ]
    )


@pytest.mark.parametrize(
    "тело, предупредить",
    [
        (ТЕЛО_631, True),  # 2 против 3
        ("Две находки.\nРазобрано: a\nРазобрано: b\n", False),  # сошлось
        ("3 находки.\nРазобрано: a\nРазобрано: b\n", True),  # цифрой
        ("ревью дало «находок 0».\nРазобрано: a\n", False),  # цитата не счёт
        ("Две другие находки закрыты раньше.\nРазобрано: a\nРазобрано: b\nРазобрано: c\n", False),
        ("Две находки и три находки.\nРазобрано: a\n", False),  # два числа — не судим
        ("Две находки, строк снятия нет.\n", False),  # снятий нет
    ],
)
def test_число_находок_против_снятий(tmp_path, capsys, тело, предупредить):
    assert прогон(tmp_path, тело) == 0
    assert ("::warning::" in capsys.readouterr().out) is предупредить


def test_путь_которого_нет_нигде_предупреждается(tmp_path, capsys):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "есть.py").write_text("", encoding="utf-8")
    тело = "Тронуты `scripts/есть.py`, `scripts/новый.py` и `scripts/выдумка.py`."
    assert прогон(tmp_path, тело, ["scripts/новый.py"]) == 0
    вывод = capsys.readouterr().out
    assert "scripts/выдумка.py" in вывод
    assert "scripts/есть.py" not in вывод.split("пересказ сверен")[0]
    assert "scripts/новый.py" not in вывод.split("пересказ сверен")[0]


def test_нет_тела_третий_исход(tmp_path, capsys):
    assert (
        cr.main(
            [
                "--root",
                str(tmp_path),
                "--paths-from",
                str(tmp_path / "нет.txt"),
                "--body-file",
                str(tmp_path / "нет.md"),
            ]
        )
        == 2
    )
    assert "нет.txt" in capsys.readouterr().err
