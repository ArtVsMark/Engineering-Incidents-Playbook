"""Хук окна исполняется интерпретатором планки (217): отказ, чисто, третий исход."""

import json
from pathlib import Path

import pytest

import check_hook_interpreter as hi

НАСТРОЙКИ = {
    "hooks": {
        "SessionStart": [{"hooks": [{"command": '"$CLAUDE_PROJECT_DIR/.claude/hooks/start.sh"'}]}],
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [{"command": '"$CLAUDE_PROJECT_DIR/.claude/hooks/guard.sh"'}],
            }
        ],
    }
}
ПЛАНКА = 'floor=$(planka_floor x)\npy=$(command -v "python$floor")\nexec "$py" "$dir/guard.py"\n'


def дерево(
    tmp_path: Path,
    guard: str,
    настройки: dict = НАСТРОЙКИ,
    start: str = "python3 -m venv /opt/uv\n",
) -> Path:
    хуки = tmp_path / ".claude" / "hooks"
    хуки.mkdir(parents=True)
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps(настройки), encoding="utf-8")
    (хуки / "guard.sh").write_text(guard, encoding="utf-8")
    (хуки / "start.sh").write_text(start, encoding="utf-8")
    return tmp_path


# Перечень форм (210): каждая форма голого вызова — свой случай.
@pytest.mark.parametrize(
    "guard",
    [
        ПЛАНКА + '[ -z "$py" ] && py=$(command -v python3 2>/dev/null)\n',  # запасной, #869
        ПЛАНКА + '[ -x "$py" ] || py=python3\n',  # глоссарий
        'exec python3 "$dir/guard.py"\n',  # прямой вызов
        'python "$dir/guard.py"\n',  # без тройки
        'out=$(python3 -c "print(1)")\n',  # в подстановке
    ],
)
def test_голый_интерпретатор_отказ(tmp_path, capsys, guard):
    assert hi.main(["--root", str(дерево(tmp_path, guard))]) == 1
    assert "guard.sh" in capsys.readouterr().err


def test_команда_хука_интерпретатором_отказ(tmp_path, capsys):
    настройки = {
        "hooks": {
            **НАСТРОЙКИ["hooks"],
            "PostToolUse": [
                {"hooks": [{"command": 'python "$CLAUDE_PROJECT_DIR/.claude/hooks/x.py"'}]}
            ],
        }
    }
    assert hi.main(["--root", str(дерево(tmp_path, ПЛАНКА, настройки))]) == 1
    assert "PostToolUse" in capsys.readouterr().err


@pytest.mark.parametrize(
    "guard",
    [
        ПЛАНКА,
        ПЛАНКА + "# без планки голый python3 не зовём\n",  # комментарий
        ПЛАНКА + 'echo "нет python$floor, python3 не зовём" >&2\n',  # проза в echo
        '"$UV_HOME/bin/uv" python install "$floor"\n',  # подкоманда uv
        'ln -sf x "$BIN_DIR/python$floor"\n',  # имя с планкой
        "p=/usr/bin/python3.14\n",  # путь с версией
    ],
)
def test_по_планке_чисто(tmp_path, guard):
    assert hi.main(["--root", str(дерево(tmp_path, guard))]) == 0


def test_стартовый_хук_исключён_по_роли(tmp_path):
    """Хук старта ставит планку сам и до неё зовёт системный python3."""
    assert hi.main(["--root", str(дерево(tmp_path, ПЛАНКА, start="python3 -m venv x\n"))]) == 0


def test_стартовый_определяется_настройками_а_не_именем(tmp_path):
    """Тот же файл, не зарегистрированный на старт, — находка."""
    настройки = {"hooks": {"PreToolUse": НАСТРОЙКИ["hooks"]["PreToolUse"]}}
    корень = дерево(tmp_path, ПЛАНКА, настройки, start="python3 -m venv x\n")
    assert hi.main(["--root", str(корень)]) == 1


def test_нет_настроек_третий_исход(tmp_path):
    assert hi.main(["--root", str(tmp_path)]) == 2


def test_нет_хуков_третий_исход(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
    assert hi.main(["--root", str(tmp_path)]) == 2


def test_живое_дерево_чисто():
    assert hi.main([]) == 0


# Обзор #878: формы, которые первая редакция пропускала.
@pytest.mark.parametrize(
    "guard",
    [
        '[ $# -gt 0 ] && python3 "$dir/guard.py"\n',  # `$#` не комментарий
        'n=${#args[@]}; python3 "$dir/guard.py"\n',  # `${#x}` не комментарий
        'echo run; python3 "$dir/guard.py"\n',  # echo снимает только себя
        'echo x && python3 "$dir/guard.py"\n',
    ],
)
def test_обход_комментарием_и_echo_отказ(tmp_path, capsys, guard):
    assert hi.main(["--root", str(дерево(tmp_path, guard))]) == 1
    assert "guard.sh" in capsys.readouterr().err


@pytest.mark.parametrize(
    "команда",
    [
        '/usr/bin/python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/x.py"',  # путём
        'env python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/x.py"',  # через env
        'bash -c "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/x.py"',  # через bash -c
    ],
)
def test_команда_хука_интерпретатором_в_любой_позиции_отказ(tmp_path, capsys, команда):
    настройки = {
        "hooks": {**НАСТРОЙКИ["hooks"], "PostToolUse": [{"hooks": [{"command": команда}]}]}
    }
    assert hi.main(["--root", str(дерево(tmp_path, ПЛАНКА, настройки))]) == 1
    assert "PostToolUse" in capsys.readouterr().err


def test_echo_с_решёткой_чисто(tmp_path):
    """`#` внутри слова и echo без вызова после него — не находка."""
    guard = ПЛАНКА + 'echo "шаг #2: python$floor" >&2\n'
    assert hi.main(["--root", str(дерево(tmp_path, guard))]) == 0


def test_обёртка_с_именем_на_python_чисто(tmp_path):
    """`python-guard.sh` — имя обёртки, а не интерпретатор (обзор #906)."""
    настройки = {
        "hooks": {
            **НАСТРОЙКИ["hooks"],
            "PostToolUse": [
                {"hooks": [{"command": '"$CLAUDE_PROJECT_DIR/.claude/hooks/python-guard.sh"'}]}
            ],
        }
    }
    assert hi.main(["--root", str(дерево(tmp_path, ПЛАНКА, настройки))]) == 0
