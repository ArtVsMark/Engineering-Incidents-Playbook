"""Хук старта облачного окна: выход 0 всегда, отказ назван словами.

Хук гоняется настоящим bash в каталоге-подделке проекта. Источник подделки
(правило 170): форма снята с дерева каталога — pyproject.toml с
requires-python, scripts/check_python_version.py, requirements-test.txt.
Планкой ставится версия интерпретатора, который гоняет набор: он уже стоит,
и хук не ходит за ним в сеть.

Звено окна в правиле 217: хук переключает python3 окна на планку, потому что
хуки площадки исполняются в окружении процесса, а не в PATH команд.
"""


import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / ".claude" / "hooks" / "session-start.sh"
ПЛАНКА = f"{sys.version_info[0]}.{sys.version_info[1]}"

def требует(*имена: str) -> pytest.MarkDecorator:
    """Пропуск по отсутствующей программе — только там, где она нужна, и
    только вне CI. На конвейере отсутствие — отказ, а не зелёный набор без
    исполненных случаев (140, 146; находка обзора #660)."""
    нет = [и for и in имена if shutil.which(и) is None]
    if нет and os.environ.get("CI"):
        pytest.fail(f"на CI нет {', '.join(нет)} — набор хука не исполнился бы вовсе",
                    pytrace=False)
    return pytest.mark.skipif(bool(нет), reason=f"нет в PATH: {', '.join(нет)}")


НУЖНА_ПЛАНКА = требует("bash", f"python{ПЛАНКА}")
НУЖЕН_BASH = требует("bash")


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
    # Каталог ссылок — временный, если случай не задал свой: хук переключает
    # `python3` окна, и набор не вправе переключить его машине, где идёт.
    окружение["SESSION_START_BIN_DIR"] = tempfile.mkdtemp(prefix="ссылки-")
    окружение.update(env)
    return subprocess.run(["bash", str(HOOK)], env=окружение, capture_output=True,
                          text=True, encoding="utf-8", timeout=300)


@НУЖЕН_BASH
def test_вне_облака_молчит():
    итог = запуск({})
    assert итог.returncode == 0 and итог.stderr == ""


@НУЖЕН_BASH
def test_без_каталога_проекта_выход_0_и_причина():
    """Находка #473 (46061c1): при `set -u` незаданная переменная площадки
    роняла хук ненулевым кодом мимо обещания «выход 0 всегда»."""
    итог = запуск({"CLAUDE_CODE_REMOTE": "true"})
    assert итог.returncode == 0 and "CLAUDE_PROJECT_DIR" in итог.stderr


@НУЖНА_ПЛАНКА
def test_без_планки_причина_словами_а_не_трассировка(tmp_path):
    """Находка #473 (5a37026): floor() is None давал TypeError."""
    корень = проект(tmp_path, pyproject="[project]\nname = 'x'\n")
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(tmp_path / "env")})
    assert итог.returncode == 0
    assert "нет requires-python" in итог.stderr and "Traceback" not in итог.stderr


@НУЖНА_ПЛАНКА
def test_окружение_собирается_и_выставляется(tmp_path):
    корень = проект(tmp_path)
    env_file = tmp_path / "env"
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(env_file)})
    assert итог.returncode == 0, итог.stderr
    assert f"{корень}/.venv/bin" in env_file.read_text(encoding="utf-8")


НЕТ_ИНДЕКСА = {"PIP_INDEX_URL": "http://127.0.0.1:9/", "PIP_RETRIES": "0",
               "PIP_TIMEOUT": "1"}


@НУЖНА_ПЛАНКА
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


@НУЖНА_ПЛАНКА
def test_сбой_pip_на_свежем_окружении_не_выставляет_пустое(tmp_path):
    """Находка обзора #660: только что собранный .venv без зависимостей в PATH
    окну не нужен, и «оставлено как было» про него неправда."""
    корень = проект(tmp_path, зависимости="такого-пакета-нет-ни-где==0\n")
    env_file = tmp_path / "env"
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(env_file), **НЕТ_ИНДЕКСА})
    assert итог.returncode == 0
    assert "не поставлены ни разу — в PATH не выставлено" in итог.stderr
    assert not env_file.exists()
    # Второй старт с тем же сбоем: .venv уже на планке, но зависимостей в нём
    # не было никогда — признак живёт в дереве и переживает перезапуск.
    повтор = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                     "CLAUDE_ENV_FILE": str(env_file), **НЕТ_ИНДЕКСА})
    assert "не поставлены ни разу" in повтор.stderr and not env_file.exists()


def поставь_без_сети(корень: Path) -> None:
    """Установленный пакет без сети: запись dist-info — то, по чему его видит pip."""
    сайт = next((корень / ".venv" / "lib").glob("python*/site-packages"))
    дист = сайт / "prezhnyaya_zavisimost-1.0.dist-info"
    дист.mkdir()
    (дист / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: prezhnyaya-zavisimost\nVersion: 1.0\n",
        encoding="utf-8")


@НУЖНА_ПЛАНКА
def test_сбой_pip_на_окружении_до_метки_не_отнимает_его(tmp_path):
    """Находка обзора #664: .venv, собранный прежним хуком, метки не несёт, хотя
    зависимости в нём стоят. Первый же сбой pip не должен отнять у него PATH."""
    корень = проект(tmp_path)
    env_file = tmp_path / "env"
    база = {"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
            "CLAUDE_ENV_FILE": str(env_file)}
    assert запуск(база).returncode == 0
    env_file.unlink()
    # Прежний хук не клал ни одной метки.
    (корень / ".venv" / ".deps-installed").unlink()
    (корень / ".venv" / ".built-by-hook").unlink()
    поставь_без_сети(корень)
    (корень / "requirements-test.txt").write_text("такого-пакета-нет-ни-где==0\n",
                                                  encoding="utf-8")
    итог = запуск({**база, **НЕТ_ИНДЕКСА})
    assert итог.returncode == 0
    assert "оставлено как было" in итог.stderr
    assert f"{корень}/.venv/bin" in env_file.read_text(encoding="utf-8")
    assert (корень / ".venv" / ".deps-installed").exists()


@НУЖНА_ПЛАНКА
def test_частичная_установка_на_своём_окружении_не_выставляет_его(tmp_path):
    """Находка обзора #665: freeze не пуст и после ЧАСТИЧНОЙ установки на .venv
    этого хука — исключение «до метки» ему не положено, целых зависимостей
    там не было никогда. Случай защитный: сбой сети его не даёт (pip ставит
    после того, как всё скачал), даёт сбой в фазе установки — его и
    изображает dist-info, положенный рукой."""
    корень = проект(tmp_path, зависимости="такого-пакета-нет-ни-где==0\n")
    env_file = tmp_path / "env"
    база = {"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
            "CLAUDE_ENV_FILE": str(env_file), **НЕТ_ИНДЕКСА}
    assert "ни разу" in запуск(база).stderr
    поставь_без_сети(корень)
    итог = запуск(база)
    assert "не поставлены ни разу" in итог.stderr and not env_file.exists()
    assert not (корень / ".venv" / ".deps-installed").exists()


def test_требует_на_ci_отказывает_а_вне_ci_пропускает(monkeypatch, tmp_path):
    """Находка обзора #664: гейт против пустого набора сам не был проверен."""
    нет = "такой-программы-нет-ни-где"
    monkeypatch.setenv("CI", "true")
    with pytest.raises(pytest.fail.Exception, match="на CI нет"):
        требует(нет)
    # «Заведомо найденная» программа заводится здесь же: имя интерпретатора
    # в PATH может и не лежать (находка обзора #665).
    каталог = tmp_path / "bin"
    каталог.mkdir()
    есть = каталог / "zavedomo-est"
    есть.write_text("#!/bin/sh\n", encoding="utf-8")
    есть.chmod(0o755)
    monkeypatch.setenv("PATH", str(каталог))
    assert требует("zavedomo-est").args == (False,)
    monkeypatch.delenv("CI")
    assert требует(нет).args == (True,)


@НУЖНА_ПЛАНКА
def test_без_файла_окружения_выход_0_и_причина(tmp_path):
    корень = проект(tmp_path)
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень)})
    assert итог.returncode == 0 and "CLAUDE_ENV_FILE" in итог.stderr


ПОДДЕЛЬНЫЙ_PYTHON3 = """#!/bin/bash
# python3 -m venv DIR: кладёт в DIR/bin подставные pip и uv, пишущие журнал.
# Прочие вызовы (сверка версии хуком) — молча: подделка изображает установщик.
[ "$1 $2" = "-m venv" ] || exit 0
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


@НУЖЕН_BASH
def test_нет_интерпретатора_планки_ставится_закреплённым_uv(tmp_path):
    """Находки #473 (2c380f8, 1ee9a42) и обзора #660: ветка установки
    ИСПОЛНЯЕТСЯ, а не читается. Планка — версия, которой на машине нет;
    python3 образа и uv подставные и пишут журнал вызовов. Номера у
    установщика нет: прошитый python3.12 умер бы вместе с образом (005)."""
    корень = проект(tmp_path, pyproject='requires-python = ">=3.99"\n')
    подмена = tmp_path / "bin"
    подмена.mkdir()
    (подмена / "python3").write_text(ПОДДЕЛЬНЫЙ_PYTHON3, encoding="utf-8")
    (подмена / "python3").chmod(0o755)
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


# ── переезд целиком: планка без Python, python3 окна, страж на планке ─────

FLOOR_SH = ROOT / ".claude" / "hooks" / "floor.sh"
GUARD_SH = ROOT / ".claude" / "hooks" / "push_guard.sh"


def планка_sed(pyproject: Path) -> str:
    return subprocess.run(["sh", "-c", f'. "{FLOOR_SH}"; planka_floor "$1"', "_", str(pyproject)],
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


@НУЖЕН_BASH
@pytest.mark.parametrize("строка", [
    'requires-python = ">=3.14"', 'requires-python=">=3.14.1"', '  requires-python = "~=3.13"',
    'requires-python = ">= 3.12, <4"', 'name = "x"',
])
def test_разбор_планки_в_оболочке_совпадает_с_питоновым(tmp_path, строка):
    """floor.sh — второй разбор той же территории (214), и держится он только
    этим тестом: тот же ответ, что у check_python_version.floor."""
    import check_python_version as cv
    манифест = tmp_path / "pyproject.toml"
    манифест.write_text(строка + "\n", encoding="utf-8")
    ждём = cv.floor(манифест.read_text(encoding="utf-8"))
    assert планка_sed(манифест) == (f"{ждём[0]}.{ждём[1]}" if ждём else "")


@НУЖЕН_BASH
def test_разбор_планки_на_настоящем_манифесте():
    import check_python_version as cv
    ждём = cv.floor((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert планка_sed(ROOT / "pyproject.toml") == f"{ждём[0]}.{ждём[1]}"


@НУЖНА_ПЛАНКА
def test_python3_окна_переключается_на_планку(tmp_path):
    """Замер 02.10: python3 окна — 3.11 при поставленном 3.14 рядом. Хуки
    площадки видят именно его."""
    корень = проект(tmp_path)
    старый = tmp_path / "образ"
    старый.mkdir()
    (старый / "python3").write_text("#!/bin/sh\necho 3.11\n", encoding="utf-8")
    (старый / "python3").chmod(0o755)
    ссылки = tmp_path / "ссылки"
    ссылки.mkdir()
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(tmp_path / "env"),
                   "PATH": f"{старый}:{os.environ['PATH']}",
                   "SESSION_START_BIN_DIR": str(ссылки)})
    assert итог.returncode == 0, итог.stderr
    assert (ссылки / "python3").resolve() == Path(shutil.which(f"python{ПЛАНКА}")).resolve()


@НУЖНА_ПЛАНКА
def test_строка_окружения_не_копится(tmp_path):
    """Замер 02.10: .venv/bin в PATH окна десять раз подряд."""
    корень = проект(tmp_path)
    env_file = tmp_path / "env"
    база = {"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
            "CLAUDE_ENV_FILE": str(env_file)}
    assert запуск(база).returncode == 0
    assert запуск(база).returncode == 0
    assert env_file.read_text(encoding="utf-8").count(".venv/bin") == 2  # одна строка, два упоминания
    путь = subprocess.run(["bash", "-c", f'. "{env_file}"; . "{env_file}"; echo "$PATH"'],
                          capture_output=True, text=True, encoding="utf-8").stdout
    assert путь.count(f"{корень}/.venv/bin") == 1


def _страж(tmp_path, планка: str, команда: str) -> subprocess.CompletedProcess[str]:
    корень = проект(tmp_path, pyproject=f'requires-python = ">={планка}"\n')
    вход = json.dumps({"tool_name": "Bash", "tool_input": {"command": команда}})
    return subprocess.run(["sh", str(GUARD_SH)], input=вход, capture_output=True, text=True,
                          encoding="utf-8", env={**os.environ, "CLAUDE_PROJECT_DIR": str(корень)})


@НУЖЕН_BASH
def test_без_интерпретатора_планки_толчок_закрыт(tmp_path):
    """Ненулевой код, кроме 2, площадка не считает отказом: страж, упавший на
    старой версии, открыл бы толчок молча."""
    итог = _страж(tmp_path, "3.99", "git push -u origin agent/x")
    assert итог.returncode == 2 and "python3.99" in итог.stderr


@НУЖЕН_BASH
@pytest.mark.parametrize("команда", [
    "git -C . push origin main", "git p''ush origin main", 'git "push" origin main',
    "git\tpush origin main", "cd x && git --no-pager push", "git pu\\sh origin main",
])
def test_без_интерпретатора_планки_закрыты_и_непрямые_толчки(tmp_path, команда):
    """Находка обзора #672: запасной разбор ловил только литерал «git push»,
    а страж видит больше форм — каждая из них уходила непроверенной."""
    итог = _страж(tmp_path, "3.99", команда)
    assert итог.returncode == 2, команда


@НУЖЕН_BASH
def test_без_интерпретатора_планки_прочее_открыто(tmp_path):
    """Сбой сети на старте не обездвиживает окно: закрыт только толчок."""
    assert _страж(tmp_path, "3.99", "ls -la").returncode == 0


@НУЖНА_ПЛАНКА
def test_страж_зовётся_интерпретатором_планки(tmp_path):
    итог = _страж(tmp_path, ПЛАНКА, "ls -la")
    assert итог.returncode == 0, итог.stderr


# --- строка статуса (217) ----------------------------------------------------
#
# stdout хука старта площадка кладёт в контекст окна: это единственное, что
# окно узнаёт о своём Python, не спрашивая. Строка одна при любом исходе.

ПОЛНАЯ = ".".join(map(str, sys.version_info[:3]))


def _python3_ниже_планки(tmp_path: Path) -> str:
    """Каталог с `python3`, отвечающим 3.11.15, — ровно то, что было в окне
    2 октября: системный python3 ниже планки при планке, стоящей рядом."""
    каталог = tmp_path / "система"
    каталог.mkdir()
    подделка = каталог / "python3"
    подделка.write_text("#!/bin/sh\necho 3.11.15\n", encoding="utf-8")
    подделка.chmod(0o755)
    return str(каталог)


@НУЖНА_ПЛАНКА
def test_статус_на_планке_одной_строкой_в_stdout(tmp_path):
    корень = проект(tmp_path)
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(tmp_path / "env")})
    assert итог.returncode == 0, итог.stderr
    assert итог.stdout.splitlines() == [
        f"окно на {ПОЛНАЯ}: python3, .venv и страж толчка — на планке"]


@НУЖЕН_BASH
def test_статус_без_планки_называет_причину(tmp_path):
    корень = проект(tmp_path, pyproject="[project]\nname = 'x'\n")
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(tmp_path / "env")})
    assert итог.stdout.splitlines() == [
        "окно НЕ на планке: в pyproject.toml нет requires-python"]


@НУЖНА_ПЛАНКА
def test_статус_называет_python3_ниже_планки(tmp_path):
    """Хук переключает python3 в своём каталоге ссылок, а PATH окна смотрит
    раньше — в системный: строка говорит, что вышло, а не что хук сделал."""
    корень = проект(tmp_path)
    путь = f"{_python3_ниже_планки(tmp_path)}:{os.environ['PATH']}"
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(tmp_path / "env"), "PATH": путь})
    assert итог.returncode == 0, итог.stderr
    assert итог.stdout.splitlines() == [f"окно НЕ на планке {ПЛАНКА}: python3 — 3.11.15"]


@НУЖЕН_BASH
def test_статус_вне_облака_не_печатается():
    assert запуск({}).stdout == ""


@НУЖЕН_BASH
def test_статус_без_каталога_проекта_не_молчит():
    """Находка обзора #675: ловушка стояла после этого раннего выхода, и окно
    не узнавало ничего — строка обещала «при любом исходе»."""
    итог = запуск({"CLAUDE_CODE_REMOTE": "true"})
    assert итог.returncode == 0
    assert итог.stdout.splitlines() == [
        "окно НЕ на планке: нет каталога проекта (CLAUDE_PROJECT_DIR) — Python окна не проверен"]


@НУЖНА_ПЛАНКА
def test_статус_без_файла_окружения_называет_path(tmp_path):
    """Находка обзора #675: .venv собран и с зависимостями, но в PATH окна не
    выставлен — строка была зелёной, а голый pytest брался не из .venv."""
    корень = проект(tmp_path)
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень)})
    assert итог.returncode == 0, итог.stderr
    assert итог.stdout.splitlines() == [
        f"окно НЕ на планке {ПЛАНКА}: .venv не выставлен в PATH окна"]


@НУЖНА_ПЛАНКА
def test_статус_называет_необновлённые_зависимости(tmp_path):
    """Находка обзора #675: «оставлено как было» видел человек, а строка
    оставалась зелёной — метка зависимостей стоит с прошлого старта."""
    корень = проект(tmp_path)
    env_file = tmp_path / "env"
    база = {"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
            "CLAUDE_ENV_FILE": str(env_file)}
    assert запуск(база).returncode == 0
    (корень / "requirements-test.txt").write_text("такого-пакета-нет-ни-где==0\n",
                                                  encoding="utf-8")
    итог = запуск({**база, **НЕТ_ИНДЕКСА})
    assert итог.stdout.splitlines() == [
        f"окно НЕ на планке {ПЛАНКА}: тестовые зависимости .venv не обновлены"]


@НУЖНА_ПЛАНКА
def test_статус_сверяет_записанную_строку_а_не_подстроку_пути(tmp_path):
    """Находка обзора #676: статус искал в файле окружения подстроку пути
    .venv/bin — её выполняет и посторонняя строка, а провал собственной
    записи хука оставался зелёным. Файл с чужой строкой закрыт на запись."""
    корень = проект(tmp_path)
    env_file = tmp_path / "env"
    env_file.write_text(f"# {корень}/.venv/bin — чужой комментарий\n", encoding="utf-8")
    env_file.chmod(0o444)
    if os.access(env_file, os.W_OK):
        pytest.skip("под root права на запись не отнимаются — случай исполняется на CI")
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(env_file)})
    assert итог.returncode == 0, итог.stderr
    assert итог.stdout.splitlines() == [
        f"окно НЕ на планке {ПЛАНКА}: .venv не выставлен в PATH окна"]


ПОДДЕЛЬНЫЙ_PYTHON3_БЕЗ_VENV = """#!/bin/bash
# python3 без venv: запускается, но `import venv, ensurepip` падает — как
# висячая ссылка или образ без пакета venv. Каждый вызов пишется в журнал
# ДО ответа: проверка хука должна в нём остаться (обзор #683).
echo "$*" >> "$JOURNAL"
[ "$1" = "-c" ] && [ "$2" = "import venv, ensurepip" ] && exit 1
exit 0
"""


@НУЖЕН_BASH
def test_python3_без_venv_установщик_берётся_системный(tmp_path):
    """Находки обзоров #679 и #683: откат на /usr/bin/python3 должен
    ИСПОЛНЯТЬСЯ, и доказывать это положительный признак, а не отсутствие
    вызова. Признаков три: хук спросил у python3 впереди PATH то, что нужно
    установщику; получив отказ, не звал его с `-m venv`; окружение установщика
    собрал системный интерпретатор — это пишет `home` в его pyvenv.cfg.
    Сеть закрыта: дальше venv хук не идёт, и это не предмет случая."""
    системный = Path("/usr/bin/python3")
    if not системный.exists():
        pytest.skip("нет /usr/bin/python3 — откату некуда идти, случай про образ с ним")
    корень = проект(tmp_path, pyproject='requires-python = ">=3.99"\n')
    подмена = tmp_path / "bin"
    подмена.mkdir()
    журнал = tmp_path / "журнал"
    поддельный = подмена / "python3"
    поддельный.write_text(ПОДДЕЛЬНЫЙ_PYTHON3_БЕЗ_VENV, encoding="utf-8")
    поддельный.chmod(0o755)
    ссылки = tmp_path / "ссылки"
    ссылки.mkdir()
    установщик = tmp_path / "uv"
    итог = запуск({"CLAUDE_CODE_REMOTE": "true", "CLAUDE_PROJECT_DIR": str(корень),
                   "CLAUDE_ENV_FILE": str(tmp_path / "env"),
                   "PATH": f"{подмена}:{ссылки}:{os.environ['PATH']}",
                   "SESSION_START_UV_HOME": str(установщик),
                   "SESSION_START_BIN_DIR": str(ссылки),
                   "JOURNAL": str(журнал), **НЕТ_ИНДЕКСА})
    assert итог.returncode == 0
    вызовы = журнал.read_text(encoding="utf-8").splitlines()
    assert "-c import venv, ensurepip" in вызовы
    assert not any(в.startswith("-m venv") for в in вызовы)
    настройка = (установщик / "pyvenv.cfg").read_text(encoding="utf-8")
    дом = next(с.split("=", 1)[1].strip() for с in настройка.splitlines()
               if с.startswith("home"))
    # `home` — каталог того, чем venv запущен, а не цели ссылки: на образе,
    # где /usr/bin/python3 — ссылка в другой каталог, верный откат дал бы
    # /usr/bin, а resolve() цели — чужой каталог (обзор #688). Годится любой
    # из двух; каталог подделки (tmp_path/bin) в это множество не входит, и
    # отдельной проверки на него не нужно — она не покраснела бы никогда (#690).
    assert Path(дом) in {системный.parent, системный.resolve().parent}
