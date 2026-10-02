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


НЕТ_ИНДЕКСА = {"PIP_INDEX_URL": "http://127.0.0.1:9/", "PIP_RETRIES": "0",
               "PIP_TIMEOUT": "1"}


def test_сбой_pip_на_собранном_окружении_не_отнимает_его(tmp_path):
    """Находка #473 (b4d11dd): сбой сети при ОБНОВЛЕНИИ зависимостей оставлял
    окно без PATH, хотя окружение на планке уже было. Окружение собирается
    первым запуском, сбой — вторым (находка обзора #660)."""
    корень = проект(tmp_path)
    env_file = tmp_path / "env"
    база = {"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
            "CLAUDE_ENV_FILE": str(env_file)}
    assert запуск(база).returncode == 0
    env_file.unlink()
    (корень / "requirements-test.txt").write_text("такого-пакета-нет-ни-где==0\n",
                                                  encoding="utf-8")
    итог = запуск({**база, **НЕТ_ИНДЕКСА})
    assert итог.returncode == 0
    assert "оставлено как было" in итог.stderr
    assert f"{корень}/.venv/bin" in env_file.read_text(encoding="utf-8")


def test_сбой_pip_на_свежем_окружении_не_выставляет_пустое(tmp_path):
    """Находка обзора #660: только что собранный .venv без зависимостей в PATH
    окну не нужен, и «оставлено как было» про него неправда."""
    корень = проект(tmp_path, зависимости="такого-пакета-нет-ни-где==0\n")
    env_file = tmp_path / "env"
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(env_file), **НЕТ_ИНДЕКСА})
    assert итог.returncode == 0
    assert "не поставлены — в PATH не выставлено" in итог.stderr
    assert not env_file.exists()


def test_без_файла_окружения_выход_0_и_причина(tmp_path):
    корень = проект(tmp_path)
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень)})
    assert итог.returncode == 0 and "CLAUDE_ENV_FILE" in итог.stderr


ПОДДЕЛЬНЫЙ_PYTHON312 = """#!/bin/bash
# python3.12 -m venv DIR: кладёт в DIR/bin подставные pip и uv, пишущие журнал.
dir="$3"; mkdir -p "$dir/bin"
cat > "$dir/bin/pip" <<'S'
#!/bin/bash
echo "pip $*" >> "$JOURNAL"
S
cat > "$dir/bin/uv" <<'S'
#!/bin/bash
echo "uv $*" >> "$JOURNAL"
if [ "$1 $2" = "python find" ]; then echo "$REAL_PYTHON"; fi
S
chmod +x "$dir/bin/pip" "$dir/bin/uv"
"""


def test_нет_интерпретатора_планки_ставится_закреплённым_uv(tmp_path):
    """Находки #473 (2c380f8, 1ee9a42) и обзора #660: ветка установки
    ИСПОЛНЯЕТСЯ, а не читается. Планка — версия, которой на машине нет;
    python3.12 и uv подставные и пишут журнал вызовов."""
    корень = проект(tmp_path, pyproject='requires-python = ">=3.99"\n')
    подмена = tmp_path / "bin"
    подмена.mkdir()
    (подмена / "python3.12").write_text(ПОДДЕЛЬНЫЙ_PYTHON312, encoding="utf-8")
    (подмена / "python3.12").chmod(0o755)
    журнал = tmp_path / "журнал"
    ссылки = tmp_path / "ссылки"
    ссылки.mkdir()
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(tmp_path / "env"),
                   "PATH": f"{подмена}:{ссылки}:{os.environ['PATH']}",
                   "SESSION_START_UV_HOME": str(tmp_path / "uv"),
                   "SESSION_START_BIN_DIR": str(ссылки),
                   "JOURNAL": str(журнал), "REAL_PYTHON": sys.executable})
    assert итог.returncode == 0
    вызовы = журнал.read_text(encoding="utf-8")
    assert "pip install -q uv==0.12.21" in вызовы
    assert "uv python install 3.99" in вызовы
    assert (ссылки / "python3.99").resolve() == Path(sys.executable).resolve()
