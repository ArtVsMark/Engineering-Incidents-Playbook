"""Стиль на планке: гейт проверяется тем, что обязан отвергнуть, и тем, что
обязан пропустить.

Источник подделки (правило 170): подделывается свой же манифест и свои же
файлы — `pyproject.toml` с `requires-python` и модули с формой из дерева
каталога. Загрузочный список сверяется с настоящим деревом: он обязан быть
замыканием от стража толчка, а не списком по памяти.
"""

import ast
import re
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


# ── загрузочные файлы: требование наоборот ─────────────────────────────────

def test_загрузочный_без_future_находка():
    путь = sorted(st.ЗАГРУЗОЧНЫЕ)[0]
    assert any("__future__" in н for н in st.находки_стиля(путь, "x = 1\n", P314))


def test_загрузочный_с_синтаксисом_планки_находка():
    путь = sorted(st.ЗАГРУЗОЧНЫЕ)[0]
    текст = FUT + "try:\n    pass\nexcept OSError, ValueError:\n    pass\n"
    assert any("не разбирается" in н for н in st.находки_стиля(путь, текст, P314))


def test_загрузочный_в_старом_стиле_чист():
    путь = sorted(st.ЗАГРУЗОЧНЫЕ)[0]
    assert st.находки_стиля(путь, FUT + EXC, P314) == []


def test_загрузочные_настоящего_дерева_разбираются_грамматикой_окна():
    for путь in st.ЗАГРУЗОЧНЫЕ:
        ast.parse((ROOT / путь).read_text(encoding="utf-8"), feature_version=st.ОКНО)


def _замыкание() -> set[str]:
    """От стража толчка и чтеца планки: импорты из scripts/ и запуски
    `scripts/<имя>.py`, названные в коде, — транзитивно."""
    очередь = [".claude/hooks/push_guard.py", "scripts/check_python_version.py"]
    видели: set[str] = set()
    while очередь:
        путь = очередь.pop()
        if путь in видели:
            continue
        видели.add(путь)
        текст = (ROOT / путь).read_text(encoding="utf-8")
        имена = set(re.findall(r'"scripts"\s*/\s*"(\w+)\.py"', текст))
        for узел in ast.walk(ast.parse(текст)):
            if isinstance(узел, ast.Import):
                имена |= {a.name.split(".")[0] for a in узел.names}  # не проза: путь модуля
            elif isinstance(узел, ast.ImportFrom) and узел.module:
                имена.add(узел.module.split(".")[0])  # не проза: путь модуля
        очередь += [f"scripts/{и}.py" for и in имена if (SCRIPTS / f"{и}.py").exists()]
    return видели


def test_загрузочный_список_равен_замыканию_от_стража():
    """Страж начнёт запускать ещё один скрипт — список обязан вырасти, иначе
    тот уедет в стиле планки и уронит стража на python окна."""
    assert set(st.ЗАГРУЗОЧНЫЕ) == _замыкание()


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
