"""Хук старта облачного окна: выход 0 всегда, отказ назван словами.

Хук гоняется настоящим bash в каталоге-подделке проекта. Источник подделки
(правило 170): форма снята с дерева каталога — pyproject.toml с
requires-python, scripts/check_python_version.py, requirements-test.txt.
Планкой ставится версия интерпретатора, который гоняет набор: он уже стоит,
и хук не ходит за ним в сеть.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / ".claude" / "hooks" / "session-start.sh"
ПЛАНКА = f"{sys.version_info[0]}.{sys.version_info[1]}"

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None or shutil.which(f"python{ПЛАНКА}") is None,
    reason=f"нужны bash и python{ПЛАНКА} в PATH — хук зовёт интерпретатор планки по имени")


def проект(tmp_path: Path, pyproject: str = f'requires-python = ">={ПЛАНКА}"\n',
           зависимости: str = "") -> Path:
    корень = tmp_path / "проект"
    (корень / "scripts").mkdir(parents=True)
    shutil.copy(ROOT / "scripts" / "check_python_version.py", корень / "scripts")
    (корень / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    (корень / "requirements-test.txt").write_text(зависимости, encoding="utf-8")
    return корень


def запуск(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    окружение = {k: v for k, v in os.environ.items()
                 if not k.startswith("CLAUDE_")}
    окружение.update(env)
    return subprocess.run(["bash", str(HOOK)], env=окружение, capture_output=True,
                          text=True, encoding="utf-8", timeout=300)


def test_вне_облака_молчит():
    итог = запуск({})
    assert итог.returncode == 0 and итог.stderr == ""


def test_без_каталога_проекта_выход_0_и_причина():
    """Находка #473 (46061c1): при `set -u` незаданная переменная площадки
    роняла хук ненулевым кодом мимо обещания «выход 0 всегда»."""
    итог = запуск({"CLAUDE_CODE_REMOTE": "true"})
    assert итог.returncode == 0 and "CLAUDE_PROJECT_DIR" in итог.stderr


def test_без_планки_причина_словами_а_не_трассировка(tmp_path):
    """Находка #473 (5a37026): floor() is None давал TypeError."""
    корень = проект(tmp_path, pyproject="[project]\nname = 'x'\n")
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(tmp_path / "env")})
    assert итог.returncode == 0
    assert "нет requires-python" in итог.stderr and "Traceback" not in итог.stderr


def test_окружение_собирается_и_выставляется(tmp_path):
    корень = проект(tmp_path)
    env_file = tmp_path / "env"
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(env_file)})
    assert итог.returncode == 0, итог.stderr
    assert f"{корень}/.venv/bin" in env_file.read_text(encoding="utf-8")


def test_сбой_pip_не_отнимает_собранное_окружение(tmp_path):
    """Находка #473 (b4d11dd): сбой сети при обновлении зависимостей оставлял
    окно без PATH, хотя окружение на планке уже было."""
    корень = проект(tmp_path, зависимости="такого-пакета-нет-ни-где==0\n")
    env_file = tmp_path / "env"
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(env_file),
                   "PIP_INDEX_URL": "http://127.0.0.1:9/", "PIP_RETRIES": "0",
                   "PIP_TIMEOUT": "1"})
    assert итог.returncode == 0
    assert "зависимости не обновлены" in итог.stderr
    assert f"{корень}/.venv/bin" in env_file.read_text(encoding="utf-8")


def test_без_файла_окружения_выход_0_и_причина(tmp_path):
    корень = проект(tmp_path)
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень)})
    assert итог.returncode == 0 and "CLAUDE_ENV_FILE" in итог.stderr


def test_версия_uv_закреплена_и_интерпретатор_по_планке():
    """Находки #473 (2c380f8, 1ee9a42): uv без пина и прошитая 3.14."""
    текст = HOOK.read_text(encoding="utf-8")
    assert 'pip install -q "uv==$UV_VERSION"' in текст
    assert "python install 3.14" not in текст and 'python install "$floor"' in текст
