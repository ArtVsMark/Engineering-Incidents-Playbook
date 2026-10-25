"""Новый механизм называет, у кого из семьи спросили (162): отказ, чисто, третий исход."""

import subprocess
from pathlib import Path

import pytest

import check_asked_family as af


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=True,
    ).stdout.strip()


@pytest.fixture
def репо(tmp_path):
    """Репозиторий с базой: в ней один старый гейт без записи о семье."""
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "check_old.py").write_text('"""Старый гейт."""\n', encoding="utf-8")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "база")
    return tmp_path, git(tmp_path, "rev-parse", "HEAD")


def запуск(root: Path, base: str, пути: list[str]) -> int:
    список = root / "paths.txt"
    список.write_text("\n".join(пути) + "\n", encoding="utf-8")
    return af.main(["--root", str(root), "--paths-from", str(список), "--base", base])


@pytest.mark.parametrize(
    "путь",
    [
        "scripts/check_new.py",
        ".claude/hooks/guard.sh",
        ".claude/hooks/guard.py",
        ".github/workflows/w.yml",
        ".github/actions/a/action.yml",
        ".claude/skills/s/SKILL.md",
    ],
)
def test_новый_механизм_без_записи_отказ(репо, capsys, путь):
    root, base = репо
    (root / путь).parent.mkdir(parents=True, exist_ok=True)
    (root / путь).write_text("# новый механизм\n", encoding="utf-8")
    assert запуск(root, base, [путь]) == 1
    assert путь in capsys.readouterr().err


def test_новый_механизм_с_записью_чисто(репо):
    root, base = репо
    (root / "scripts" / "check_new.py").write_text(
        '"""СПЕРВА СПРОСИЛИ СЕМЬЮ (162): у соседей нет."""\n', encoding="utf-8"
    )
    assert запуск(root, base, ["scripts/check_new.py"]) == 0


def test_правка_старого_механизма_не_спрашивается(репо):
    """Задним числом не спрашивается: путь есть на базе."""
    root, base = репо
    (root / "scripts" / "check_old.py").write_text('"""Старый гейт, правка."""\n', encoding="utf-8")
    assert запуск(root, base, ["scripts/check_old.py"]) == 0


@pytest.mark.parametrize("путь", ["scripts/helper.py", "tests/test_x.py", "docs/x.md"])
def test_не_механизм_не_спрашивается(репо, путь):
    root, base = репо
    (root / путь).parent.mkdir(parents=True, exist_ok=True)
    (root / путь).write_text("x\n", encoding="utf-8")
    assert запуск(root, base, [путь]) == 0


def test_номер_внутри_числа_не_запись(репо):
    root, base = репо
    (root / "scripts" / "check_new.py").write_text('"""Замер: 1620 строк."""\n', encoding="utf-8")
    assert запуск(root, base, ["scripts/check_new.py"]) == 1


def test_база_не_разобрана_третий_исход(репо, capsys):
    root, _ = репо
    (root / "scripts" / "check_new.py").write_text("x\n", encoding="utf-8")
    assert запуск(root, "deadbeef" * 5, ["scripts/check_new.py"]) == 2
    assert "deadbeef" in capsys.readouterr().err


def test_список_не_прочитан_третий_исход(tmp_path):
    assert (
        af.main(
            ["--root", str(tmp_path), "--paths-from", str(tmp_path / "нет.txt"), "--base", "HEAD"]
        )
        == 2
    )


def test_голое_число_не_запись(репо):
    """«162» в замере или списке правил — не запись о семье (обзор #884)."""
    root, base = репо
    (root / "scripts" / "check_new.py").write_text(
        '"""Реализует правила: 001, 162, 214."""\n', encoding="utf-8"
    )
    assert запуск(root, base, ["scripts/check_new.py"]) == 1


@pytest.mark.parametrize(
    "путь, виден",
    [
        (".github/workflows/deps-pins.yml", True),  # свой прогон подъёма закреплений
        ("scripts/check_hook_interpreter.py", True),  # гейт интерпретатора хуков
        ("scripts/check_old.py", False),  # расширение старого: граница
    ],
)
def test_три_случая_16_10(репо, путь, виден):
    """Охват сверен со случаями, ради которых гейт заведён (обзор #884)."""
    root, base = репо
    (root / путь).parent.mkdir(parents=True, exist_ok=True)
    (root / путь).write_text("# без записи\n", encoding="utf-8")
    assert запуск(root, base, [путь]) == (1 if виден else 0)


@pytest.mark.parametrize(
    "строка",
    [
        '"""Реализует правила: 162, 214 — семь проверок."""\n',  # числительное
        '"""162 — спрос на гейт велик."""\n',  # потребность
    ],
)
def test_соседнее_слово_не_запись(репо, строка):
    """«Семь» и «спрос» рядом с 162 — не запись о семье (обзор #888)."""
    root, base = репо
    (root / "scripts" / "check_new.py").write_text(строка, encoding="utf-8")
    assert запуск(root, base, ["scripts/check_new.py"]) == 1
