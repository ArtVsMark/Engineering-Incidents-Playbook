"""Общая обвязка тестов каталога.

Скрипты лежат в ``scripts/`` и пакетом не оформлены — импортировать их иначе
как через путь нечем. Оформлять пакет ради тестов значило бы перестроить
раскладку репозитория под удобство проверки, а не наоборот.

Каждый скрипт вычисляет свои пути **на импорте**, от ``__file__``. Поэтому
подменять предмет проверки приходится атрибутами модуля, а не переменными
окружения: так тест работает с настоящим кодом, а не с его параметризованной
копией.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Пустой каталог под поддельный репозиторий: предмет проверки задаёт тест."""
    return tmp_path


def write(path: Path, text: str) -> Path:
    """Кладёт файл вместе с недостающими каталогами и возвращает его путь."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
