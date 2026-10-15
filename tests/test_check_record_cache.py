"""Поле слияния записи изменения доказательством не служит (148): заслон и его исключения."""

from pathlib import Path

import pytest

import check_record_cache as rc


def дерево(tmp_path: Path, файлы: dict[str, str]) -> Path:
    """Дерево, где каждое законное место живо, плюс названные файлы поверх."""
    законные: dict[str, str] = {}
    for ф, в in rc.ЗАКОННЫЕ:
        законные[ф] = законные.get(ф, "") + f"y = {в}\n"
    for имя, текст in {**законные, **файлы}.items():
        (tmp_path / имя).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / имя).write_text(текст, encoding="utf-8")
    return tmp_path


# Перечень форм (210): каждая форма чтения и каждое место охвата — свой случай.
@pytest.mark.parametrize("файлы", [
    {"scripts/wait.py": 'if pr["merged"]:\n    go()\n'},                       # 2
    {"scripts/wait.py": "ok = pr.get('merged_at') is not None\n"},              # 2
    {"scripts/wait.py": "ok = pr.merged\n"},                                     # 1
    {".github/workflows/w.yml": "run: gh api pulls/1 --jq .merged\n"},           # 1
    {".github/workflows/w.yml": "run: gh api pulls --jq '.[] | {merged_by}'\n"}, # 3
    {".github/workflows/w.yml": "run: gh pr view 1 --json mergedAt\n"},          # 4
    {"scripts/wait.py": 'done = state == "MERGED"\n'},                           # 5
    {"scripts/wait.sh": "gh pr view 1 --json mergedBy\n"},                       # охват: .sh
    {"scripts/sub/wait.py": "ok = pr.merged_at\n"},                              # охват: вглубь
    {".github/actions/a/action.yml": "run: gh api pulls/1 --jq .merged\n"},      # охват: действия
    {".claude/hooks/h.sh": "gh pr view --json mergedAt\n"},                      # охват: хуки
    {"scripts/check_x.py": 'if pr["merged"]:\n    go()\n'},                      # гейты не исключены
    # Законное исключение — место, а не файл: новое чтение рядом не прикрыто.
    {"scripts/review_findings.py": "y = select(.merged_at != null)\nif pr.merged:\n    go()\n"},
])
def test_чтение_поля_отказ(tmp_path, capsys, файлы):
    assert rc.main(["--root", str(дерево(tmp_path, файлы))]) == 1
    assert "148" in capsys.readouterr().err


@pytest.mark.parametrize("файлы", [
    {"scripts/wait.py": "# ждём не поля merged, а коммита в main\n"},     # комментарий
    {".github/workflows/w.yml": "  # поле merged у записи отстаёт\n"},     # комментарий
    {"scripts/wait.py": "merged_into = 1\n"},                               # другое имя
    {"scripts/wait.py": "merged = sorted(a | b)\n"},                        # голое имя
    {"scripts/wait.py": "x = merged.values()\n"},                           # голое имя
    {"scripts/notes.md": "pr.merged\n"},                                    # не исполняется
])
def test_законное_проходит(tmp_path, файлы):
    assert rc.main(["--root", str(дерево(tmp_path, файлы))]) == 0


def test_сам_гейт_пропущен(tmp_path):
    файлы = {rc.САМ: 'ПОЛЕ = re.compile(r"\\.merged|mergedAt")\n'}
    assert rc.main(["--root", str(дерево(tmp_path, файлы))]) == 0


def test_законное_без_места_находка(tmp_path, capsys):
    (ф, в), *_ = rc.ЗАКОННЫЕ
    корень = дерево(tmp_path, {ф: "x = 1\n"})
    assert rc.main(["--root", str(корень)]) == 1
    assert в in capsys.readouterr().err


def test_законное_без_файла_находка(tmp_path, capsys):
    (tmp_path / "scripts").mkdir()
    assert rc.main(["--root", str(tmp_path)]) == 1
    assert "в дереве его нет" in capsys.readouterr().err


def test_живое_дерево_чисто():
    assert rc.main([]) == 0


def test_нет_каталога_третий_исход(tmp_path, capsys):
    assert rc.main(["--root", str(tmp_path / "нет")]) == 2
    assert "нет" in capsys.readouterr().err
