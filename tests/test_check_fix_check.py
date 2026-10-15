"""Починка приносит проверку (014): отказ, пропуск и проза, которая проверки не требует.

Набор двусторонний (140): рядом с предметом, который гейт обязан отвергнуть,
стоит законный — прозаическая правка, удалённый скрипт, названный выход.
Дерево — настоящий репозиторий git во временном каталоге: гейт сравнивает
файл на базе с рабочим, и подделка без истории проверяла бы не его решение.
"""

import subprocess
from pathlib import Path

import pytest

import check_fix_check as fc

СКРИПТ = '''"""Модуль."""


def f(x):
    """Возвращает удвоенное."""
    return x * 2
'''


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


@pytest.fixture
def дерево(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "a.py").write_text(СКРИПТ, encoding="utf-8")
    (root / "scripts" / "gone.py").write_text("X = 1\n", encoding="utf-8")
    git(root, "init", "-q")
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "add", ".")
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
    return root, git(root, "rev-parse", "HEAD")


def прогон(tmp_path: Path, root: Path, base: str, пути: list[str], тело: str = "") -> int:
    (tmp_path / "paths.txt").write_text("\n".join(пути) + "\n", encoding="utf-8")
    (tmp_path / "body.md").write_text(тело, encoding="utf-8")
    return fc.main(["--root", str(root), "--base", base,
                    "--paths-from", str(tmp_path / "paths.txt"),
                    "--body-file", str(tmp_path / "body.md")])


ПОЧИНКА = "changelog.d/x.fixed.md"


def код(root: Path) -> None:
    (root / "scripts" / "a.py").write_text(СКРИПТ.replace("x * 2", "x * 3"), encoding="utf-8")


# ── обязан отвергнуть ────────────────────────────────────────────────────

def test_починка_кода_без_проверки_отказ(tmp_path, дерево, capsys):
    root, base = дерево
    код(root)
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/a.py"]) == 1
    assert "scripts/a.py" in capsys.readouterr().err


def test_новый_скрипт_в_починке_без_проверки_отказ(tmp_path, дерево):
    root, base = дерево
    (root / "scripts" / "new.py").write_text("def g():\n    return 1\n", encoding="utf-8")
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/new.py"]) == 1


def test_выход_без_причины_не_выход(tmp_path, дерево):
    root, base = дерево
    код(root)
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/a.py"],
                  "Проверка: не требуется —   \n") == 1


# ── обязан пропустить ────────────────────────────────────────────────────

def test_починка_с_проверкой_проходит(tmp_path, дерево):
    root, base = дерево
    код(root)
    (root / "tests").mkdir()
    (root / "tests" / "test_a.py").write_text("def test_a():\n    pass\n", encoding="utf-8")
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/a.py", "tests/test_a.py"]) == 0


def test_не_починка_не_спрашивается(tmp_path, дерево):
    root, base = дерево
    код(root)
    assert прогон(tmp_path, root, base, ["changelog.d/x.added.md", "scripts/a.py"]) == 0


@pytest.mark.parametrize("правка", [
    lambda s: s.replace("Возвращает удвоенное.", "Удваивает число."),       # докстрока
    lambda s: s.replace('"""Модуль."""', '"""Модуль о числах."""'),          # докстрока модуля
    lambda s: s.replace("    return x * 2", "    # удвоение\n    return x * 2"),  # комментарий
    lambda s: s.replace("return x * 2", "return x*2"),                      # пробелы
])
def test_правка_прозы_проверки_не_требует(tmp_path, дерево, правка, capsys):
    root, base = дерево
    (root / "scripts" / "a.py").write_text(правка(СКРИПТ), encoding="utf-8")
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/a.py"]) == 0
    assert "только проза" in capsys.readouterr().out


def test_удалённый_скрипт_проверки_не_требует(tmp_path, дерево):
    root, base = дерево
    (root / "scripts" / "gone.py").unlink()
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/gone.py"]) == 0


def test_названный_выход_пропускает(tmp_path, дерево, capsys):
    root, base = дерево
    код(root)
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/a.py"],
                  "Проверка: не требуется — правится текст сообщения, поведение то же\n") == 0
    assert "выход назван" in capsys.readouterr().out


# ── не отработала ────────────────────────────────────────────────────────

def test_неразбираемый_скрипт_третий_исход_с_предметом(tmp_path, дерево, capsys):
    root, base = дерево
    (root / "scripts" / "a.py").write_text("def (:\n", encoding="utf-8")
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/a.py"]) == 2
    assert "scripts/a.py не разбирается" in capsys.readouterr().err


def test_нет_списка_путей_третий_исход(tmp_path, дерево, capsys):
    root, base = дерево
    assert fc.main(["--root", str(root), "--base", base,
                    "--paths-from", str(tmp_path / "нет.txt"),
                    "--body-file", str(tmp_path / "нет.md")]) == 2
    assert "нет.txt" in capsys.readouterr().err


# ── находки обзора #830 ──────────────────────────────────────────────────

def test_пустая_причина_не_берёт_следующую_строку(tmp_path, дерево):
    root, base = дерево
    код(root)
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/a.py"],
                  "Проверка: не требуется —\nPart of #816\n") == 1


def test_удалённый_тест_не_проверка(tmp_path, дерево):
    root, base = дерево
    код(root)
    assert прогон(tmp_path, root, base, [ПОЧИНКА, "scripts/a.py", "tests/test_gone.py"]) == 1


def test_неизвестная_база_третий_исход(tmp_path, дерево, capsys):
    root, _ = дерево
    код(root)
    assert прогон(tmp_path, root, "0" * 40, [ПОЧИНКА, "scripts/a.py"]) == 2
    assert "не найдена" in capsys.readouterr().err
