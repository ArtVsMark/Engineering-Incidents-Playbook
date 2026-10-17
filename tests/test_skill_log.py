"""Журнал навыков (#866): вызов пишется строкой, текст запроса — никогда.

Случаи спрашивают САМ ХУК через `main()` с событием на stdin в том виде, в
каком его подаёт площадка (правило 150). Подключение проверяется отдельно, по
`.claude/settings.json`: писатель без вызова — ровно поломка ECC #2463 (211).
"""

import importlib.util
import io
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

КОРЕНЬ = Path(__file__).resolve().parent.parent
ХУК = КОРЕНЬ / ".claude" / "hooks" / "skill_log.py"
_spec = importlib.util.spec_from_file_location("skill_log", ХУК)
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)
СЕЙЧАС = datetime(2026, 10, 16, 12, 0, tzinfo=UTC)


def вызвать(tmp_path, monkeypatch, событие: str, исход: str = "ok") -> list[dict]:
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    assert sl.main([исход], io.StringIO(событие), СЕЙЧАС) == 0
    журнал = tmp_path / sl.ЖУРНАЛ
    if not журнал.exists():
        return []
    return [json.loads(с) for с in журнал.read_text(encoding="utf-8").splitlines()]


def test_вызов_записан_без_аргументов(tmp_path, monkeypatch):
    событие = json.dumps({"tool_name": "Skill", "session_id": "s1",
                          "tool_input": {"skill": "close-a-finding", "args": "слова владельца"}})
    строки = вызвать(tmp_path, monkeypatch, событие)
    assert строки == [{"ts": "2026-10-16T12:00:00+00:00", "skill": "close-a-finding",
                       "outcome": "ok", "session": "s1"}]
    assert "слова владельца" not in (tmp_path / sl.ЖУРНАЛ).read_text(encoding="utf-8")


def test_отказ_навыка_записан_отказом(tmp_path, monkeypatch):
    событие = json.dumps({"tool_name": "Skill", "tool_input": {"skill": "plugin:x"}})
    assert вызвать(tmp_path, monkeypatch, событие, "fail")[0]["outcome"] == "fail"


@pytest.mark.parametrize("событие", [
    "не json",
    "[]",
    json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    json.dumps({"tool_name": "Skill", "tool_input": "close-a-finding"}),
    json.dumps({"tool_name": "Skill", "tool_input": {"skill": "имя с пробелом и; rm -rf"}}),
    json.dumps({"tool_name": "Skill", "tool_input": {"skill": "x" * 101}}),
])
def test_не_та_форма_ничего_не_пишет_и_не_падает(tmp_path, monkeypatch, событие):
    assert вызвать(tmp_path, monkeypatch, событие) == []


def test_вход_больше_предела_не_разбирается(tmp_path, monkeypatch, capsys):
    событие = json.dumps({"tool_name": "Skill", "tool_input": {"skill": "a"},
                          "tool_response": "x" * (sl.ПРЕДЕЛ + 1)})
    assert вызвать(tmp_path, monkeypatch, событие) == []
    assert "больше предела" in capsys.readouterr().err


def test_журнал_не_записан_код_ноль(tmp_path, monkeypatch, capsys):
    (tmp_path / ".claude").write_text("", encoding="utf-8")   # каталог занят файлом
    событие = json.dumps({"tool_name": "Skill", "tool_input": {"skill": "a"}})
    assert вызвать(tmp_path, monkeypatch, событие) == []
    assert "не записан" in capsys.readouterr().err


def test_хук_подключён_на_оба_события():
    """Писатель без вызова — ECC #2463: сводка годами показывала ноль (211)."""
    хуки = json.loads((КОРЕНЬ / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]
    for событие, исход in (("PostToolUse", "ok"), ("PostToolUseFailure", "fail")):
        записи = [h for g in хуки[событие] if g.get("matcher") == "Skill" for h in g["hooks"]]
        assert any(h["command"].endswith(f"skill_log.sh\" {исход}") for h in записи)


def test_журнал_вне_дерева():
    assert ".claude/state/" in (КОРЕНЬ / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_путь_целиком_через_обёртку(tmp_path):
    """settings.json → skill_log.sh → floor.sh → интерпретатор планки → skill_log.py (211).

    Без этого случая набор звал `main()` напрямую, и поломка обёртки или
    разбора планки оставляла журнал пустым при зелёном наборе (находка #868).
    """
    import shutil
    import subprocess

    (tmp_path / "pyproject.toml").write_text(
        (КОРЕНЬ / "pyproject.toml").read_text(encoding="utf-8"), encoding="utf-8")
    событие = json.dumps({"tool_name": "Skill", "tool_input": {"skill": "close-a-finding"}})
    итог = subprocess.run(
        ["sh", str(КОРЕНЬ / ".claude" / "hooks" / "skill_log.sh"), "ok"],
        input=событие, capture_output=True, text=True, encoding="utf-8", timeout=30,
        env={"PATH": os.environ["PATH"], "CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert итог.returncode == 0
    журнал = tmp_path / sl.ЖУРНАЛ
    # Планка — из `requires-python` самим `floor.sh`, а не из версии, на которой
    # идёт набор (на прогоне 3.15 они расходятся), и не своим выражением: второй
    # разбор того же поля уже́ sed'а в floor.sh (обзор #877, 214).
    планка = subprocess.run(
        ["sh", "-c", '. "$1"; planka_floor "$2"', "sh",
         str(КОРЕНЬ / ".claude" / "hooks" / "floor.sh"), str(КОРЕНЬ / "pyproject.toml")],
        capture_output=True, text=True, encoding="utf-8", timeout=10).stdout.strip()
    assert планка, "floor.sh не прочитал планку из pyproject.toml"
    if shutil.which(f"python{планка}") is None:
        assert "Перезапустите окно" in итог.stderr and not журнал.exists()
    else:
        assert json.loads(журнал.read_text(encoding="utf-8"))["skill"] == "close-a-finding"


def test_без_планки_системный_python3_не_зовётся(tmp_path):
    """Хук окна исполняется только интерпретатором планки (217): запасного нет."""
    import subprocess

    bin_ = tmp_path / "bin"
    bin_.mkdir()
    системный = bin_ / "python3"
    системный.write_text("#!/bin/sh\necho ЗАПУЩЕН >&2\n", encoding="utf-8")
    системный.chmod(0o755)
    (tmp_path / "pyproject.toml").write_text('[project]\nrequires-python = ">=9.99"\n',
                                             encoding="utf-8")
    итог = subprocess.run(
        ["sh", str(КОРЕНЬ / ".claude" / "hooks" / "skill_log.sh"), "ok"],
        input="{}", capture_output=True, text=True, encoding="utf-8", timeout=30,
        env={"PATH": f"{bin_}:/usr/bin:/bin", "CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert итог.returncode == 0
    assert "ЗАПУЩЕН" not in итог.stderr and "python9.99" in итог.stderr
