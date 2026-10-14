"""Поле слияния записи изменения доказательством не служит (148): заслон и его исключения."""

from pathlib import Path

import pytest

import check_record_cache as rc


def дерево(tmp_path: Path, файлы: dict[str, str]) -> Path:
    for имя, текст in {"scripts/review_findings.py": "x = 1\n", **файлы}.items():
        (tmp_path / имя).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / имя).write_text(текст, encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("файлы", [
    {"scripts/wait.py": 'if pr["merged"]:\n    go()\n'},
    {"scripts/wait.py": "ok = pr.get('merged_at') is not None\n"},
    {".github/workflows/w.yml": "run: gh api pulls/1 --jq .merged\n"},
])
def test_чтение_поля_отказ(tmp_path, capsys, файлы):
    assert rc.main(["--root", str(дерево(tmp_path, файлы))]) == 1
    assert "148" in capsys.readouterr().err


@pytest.mark.parametrize("файлы", [
    {"scripts/wait.py": "# ждём не поля merged, а коммита в main\n"},     # комментарий
    {".github/workflows/w.yml": "  # поле merged у записи отстаёт\n"},     # комментарий
    {"scripts/check_x.py": 'ПОЛЕ = re.compile(r"\\.merged")\n'},          # сам гейт
    {"scripts/review_findings.py": "select(.merged_at != null)\n"},        # законное
    {"scripts/wait.py": "merged_into = 1\n"},                               # другое имя
])
def test_законное_проходит(tmp_path, файлы):
    assert rc.main(["--root", str(дерево(tmp_path, файлы))]) == 0


def test_законное_без_файла_находка(tmp_path, capsys):
    (tmp_path / "scripts").mkdir()
    assert rc.main(["--root", str(tmp_path)]) == 1
    assert "файла нет" in capsys.readouterr().err


def test_нет_каталога_третий_исход(tmp_path, capsys):
    assert rc.main(["--root", str(tmp_path / "нет")]) == 2
    assert "нет" in capsys.readouterr().err
