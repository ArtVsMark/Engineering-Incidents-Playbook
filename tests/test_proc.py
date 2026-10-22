"""Обёртка вызова процесса: истёкший дедлайн — названный код, а не трасса (100, 039)."""

import subprocess
import sys

import pytest

import proc

СПИТ = [sys.executable, "-c", "import time; time.sleep(5)"]


def test_истечение_текстом_код_и_причина():
    done = proc.run(СПИТ, timeout=0.3, capture_output=True, text=True, encoding="utf-8")
    assert done.returncode == proc.TIMED_OUT
    assert "не ответил за 0.3 с" in done.stderr and "(100)" in done.stderr
    assert done.stdout == ""


def test_истечение_байтами_тот_же_род_вывода():
    done = proc.run(СПИТ, timeout=0.3, capture_output=True)
    assert done.returncode == proc.TIMED_OUT
    assert isinstance(done.stdout, bytes) and isinstance(done.stderr, bytes)
    assert "не ответил".encode() in done.stderr


def test_истечение_при_check_поднимает_отказ():
    """`check=True` обещает исключение — вызывающие его ловят, молчаливый код их обманул бы."""
    with pytest.raises(subprocess.CalledProcessError) as отказ:
        proc.run(СПИТ, timeout=0.3, capture_output=True, text=True, encoding="utf-8", check=True)
    assert отказ.value.returncode == proc.TIMED_OUT


def test_успех_как_у_subprocess():
    done = proc.run([sys.executable, "-c", "print('ок')"], timeout=60,
                    capture_output=True, text=True, encoding="utf-8")
    assert (done.returncode, done.stdout) == (0, "ок\n")


def test_дедлайн_обязателен():
    """Без значения по умолчанию и только по имени: вызов без дедлайна не соберётся."""
    import inspect
    срок = inspect.signature(proc.run).parameters["timeout"]
    assert срок.default is inspect.Parameter.empty
    assert срок.kind is inspect.Parameter.KEYWORD_ONLY
