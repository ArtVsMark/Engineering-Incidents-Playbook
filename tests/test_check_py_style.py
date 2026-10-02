"""Стиль на планке: гейт проверяется тем, что обязан отвергнуть, и тем, что
обязан пропустить.

Источник подделки (правило 170): подделывается свой же манифест и свои же
файлы — `pyproject.toml` с `requires-python` и модули с формой из дерева
каталога. Загрузочный список сверяется с настоящим деревом: он обязан быть
замыканием от стража толчка, а не списком по памяти.
"""

import subprocess

import pytest

import check_py_style as st
from conftest import SCRIPTS, write

ROOT = SCRIPTS.parent
P314, P313 = (3, 14), (3, 13)
FUT = "from __future__ import annotations\n"
EXC = "try:\n    pass\nexcept (OSError, ValueError):\n    pass\n"


# ── требования планки ──────────────────────────────────────────────────────

def test_future_на_планке_314_находка():
    assert any("PEP 649" in н for н in st.находки_стиля("a.py", FUT, P314))


def test_future_ниже_планки_не_предмет():
    """Требование действует с версии, где доступно: на 3.13 импорт нужен."""
    assert st.находки_стиля("a.py", FUT + EXC, P313) == []


def test_except_в_скобках_без_as_находка():
    assert st.except_в_скобках(EXC) == [3]


def test_except_в_скобках_с_as_не_предмет():
    """С `as` скобки обязательны и на 3.14."""
    assert st.except_в_скобках(EXC.replace("):", ") as e:")) == []


def test_одно_исключение_в_скобках_не_предмет():
    assert st.except_в_скобках("try:\n    pass\nexcept (OSError):\n    pass\n") == []


def test_except_в_строке_и_комментарии_не_предмет():
    текст = 's = "except (A, B):"\n# except (A, B):\n'
    assert st.except_в_скобках(текст) == []


def test_вложенные_скобки_в_кортеже_исключений():
    текст = "try:\n    pass\nexcept (errors.get('a', OSError), ValueError):\n    pass\n"
    assert st.except_в_скобках(текст) == [3]


def test_except_звёздочка_в_скобках_находка():
    """PEP 758 снимает скобки и у групп исключений."""
    assert st.except_в_скобках("try:\n    pass\nexcept* (A, B):\n    pass\n") == [3]


def test_одноэлементный_кортеж_с_запятой_не_предмет():
    """`except A,:` не пишется — находка требовала бы невозможного."""
    assert st.except_в_скобках("try:\n    pass\nexcept (OSError,):\n    pass\n") == []


# ── исходы ─────────────────────────────────────────────────────────────────

def _дерево(repo, pyproject: str, файлы: dict[str, str]):
    write(repo / "pyproject.toml", pyproject)
    for путь, текст in файлы.items():
        write(repo / путь, текст)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    return repo


def test_настоящее_дерево_чисто():
    assert st.main(["--root", str(ROOT)]) == 0


def test_отстающий_файл_это_находка(repo, capsys):
    _дерево(repo, 'requires-python = ">=3.14"\n', {"scripts/a.py": FUT + "x = 1\n"})
    assert st.main(["--root", str(repo)]) == 1
    assert "PEP 649" in capsys.readouterr().out


def test_без_планки_третий_исход(repo, capsys):
    _дерево(repo, "[project]\nname = 'x'\n", {"scripts/a.py": "x = 1\n"})
    assert st.main(["--root", str(repo)]) == 2
    assert "requires-python" in capsys.readouterr().err


def test_без_ruff_третий_исход(repo, capsys, monkeypatch):
    """Ruff не найден — отказ, а не «чисто» без половины проверки (075)."""
    _дерево(repo, 'requires-python = ">=3.14"\n', {"scripts/a.py": "x = 1\n"})
    monkeypatch.setattr(st.shutil, "which", lambda _: None)
    monkeypatch.setattr(st.sys, "executable", str(repo / "нет" / "python"))
    assert st.main(["--root", str(repo)]) == 2
    assert "ruff не найден" in capsys.readouterr().err


@pytest.mark.parametrize("планка", [P313, P314])
def test_ruff_получает_цель_из_планки(repo, планка):
    """`str.format` с `%` ruff ловит на любой цели; цель же видна в разборе:
    `typing.Callable` устарел для любой планки выше 3.9 — находка на обеих."""
    _дерево(repo, f'requires-python = ">={планка[0]}.{планка[1]}"\n',
            {"scripts/a.py": "from typing import Callable\nf: Callable\n"})
    assert any("UP035" in н for н in st.находки_ruff(repo, ["scripts/a.py"], планка))
