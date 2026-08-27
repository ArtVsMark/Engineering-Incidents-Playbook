"""Тест не зависит от того, что случайно стоит у автора.

Инцидент: новый набор импортировал `yaml`, чтобы убедиться, что собранный
рабочий процесс вообще разбирается. У автора библиотека стояла — набор был
зелёный. В конвейере её не было — прогон упал на `ModuleNotFoundError`.
Классика 107: «у автора работает» означает «проверено на выборке автора».

Отдельный случай держит тонкость, на которой гейт споткнулся при первом же
прогоне: **имя пакета и имя модуля — разные вещи**. `pyyaml` даёт `yaml`.
Таблица синонимов здесь была бы запретительным списком наоборот (068); имена
спрашиваются у метаданных.
"""

from __future__ import annotations

import check_test_deps as td
from conftest import write


def tree(repo, test_src: str, reqs: str = "pytest\n"):
    write(repo / "scripts" / "own_module.py", "x = 1\n")
    write(repo / "tests" / "test_a.py", test_src)
    write(repo / "requirements-test.txt", reqs)
    return repo


def run(repo) -> int:
    return td.main(["--root", str(repo)])


# ── здоровые предметы: гейт обязан пропустить ──────────────────────────────

def test_стандартная_библиотека_объявления_не_требует(repo):
    assert run(tree(repo, "import json\nimport pathlib\n")) == 0


def test_свой_модуль_объявления_не_требует(repo):
    assert run(tree(repo, "import own_module\n")) == 0


def test_соседний_тест_объявления_не_требует(repo):
    assert run(tree(repo, "from conftest import write\n")) == 0


def test_объявленная_зависимость_проходит(repo):
    assert run(tree(repo, "import pytest\n", "pytest\n")) == 0


def test_версия_в_объявлении_не_мешает(repo):
    """Предмет у границы: в файле зависимостей пишут не только имена."""
    assert run(tree(repo, "import pytest\n", "pytest>=8.0  # с версией\n")) == 0


def test_имя_модуля_объявляется_рядом_с_пакетом(repo):
    """`pyyaml` даёт модуль `yaml` — и это объявляется, а не выясняется.

    Первая версия проверки спрашивала метаданные УСТАНОВЛЕННОГО пакета и тем
    самым зависела от того, что уже установлено, — то есть болела ровно той
    болезнью, которую ловит. Она прошла у автора и упала в конвейере, где
    библиотеки на момент проверки ещё нет.
    """
    assert run(tree(repo, "import yaml\n", "pyyaml  # модуль: yaml\n")) == 0


def test_без_объявления_модуля_имя_пакета_не_спасает(repo, capsys):
    """Граница ровно здесь: `pyyaml` объявлен, `yaml` — нет."""
    assert run(tree(repo, "import yaml\n", "pyyaml\n")) == 1
    assert "yaml" in capsys.readouterr().err


def test_объявить_можно_несколько_модулей(repo):
    assert run(tree(repo, "import a\nimport b\n", "pkg  # модули: a, b\n")) == 0


def test_проверка_не_трогает_установленное(repo):
    """Гейт обязан работать на голом дереве, без единой установки.

    Он читает только файлы: ни импортов, ни метаданных. Иначе он зависел бы
    от порядка шагов в конвейере — а порядок шагов невидим из кода гейта.
    """
    import inspect
    src = inspect.getsource(td)
    assert "importlib" not in src and "packages_distributions" not in src


def test_подмодуль_считается_по_верхнему_имени(repo):
    assert run(tree(repo, "from pathlib import Path\nimport os.path\n")) == 0


# ── предмет, который гейт обязан отвергнуть ────────────────────────────────

def test_необъявленный_импорт_это_находка(repo, capsys):
    assert run(tree(repo, "import requests\n")) == 1
    err = capsys.readouterr().err
    assert "requests" in err and "выборке автора" in err


def test_находка_называет_файл_и_модуль(repo, capsys):
    tree(repo, "import requests\n")
    assert run(repo) == 1
    assert "test_a.py" in capsys.readouterr().err


# ── три исхода ─────────────────────────────────────────────────────────────

def test_нет_тестов_это_третий_исход(repo, capsys):
    write(repo / "requirements-test.txt", "pytest\n")
    (repo / "tests").mkdir(parents=True, exist_ok=True)
    assert run(repo) == 2
    assert "смотреть нечего" in capsys.readouterr().err


def test_нет_файла_зависимостей_это_третий_исход(repo, capsys):
    write(repo / "tests" / "test_a.py", "import json\n")
    assert run(repo) == 2
    assert "не прочитан" in capsys.readouterr().err


def test_неразбираемый_тест_это_третий_исход(repo, capsys):
    assert run(tree(repo, "import (((\n")) == 2
    assert "не разобран" in capsys.readouterr().err
