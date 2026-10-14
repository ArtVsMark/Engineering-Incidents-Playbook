"""Зелёное со второй попытки записано (124): что считается повторным и что записью.

Подделка — список прогонов формы `actions/runs` площадки (поля `id`,
`conclusion`, `run_attempt`, `name`, `html_url`, `head_sha`), журнал — дерево
`changelog.d/` во временном каталоге. Площадка подменяется на шве `ghcli.список`.
Источник формы — ответ `gh api repos/{owner}/{repo}/actions/runs`, массив
`workflow_runs`; снято 14.10 с прогона 38568475045 этого каталога.
"""

from pathlib import Path

import pytest

import flaky_reruns as fr


def прогон(id_: int, попытка: int, исход: str = "success") -> dict:
    return {"id": id_, "run_attempt": попытка, "conclusion": исход, "name": "ci",
            "html_url": f"https://example.invalid/runs/{id_}", "head_sha": "a" * 40}


def журнал(root: Path, текст: str) -> Path:
    (root / "changelog.d").mkdir(parents=True, exist_ok=True)
    (root / "changelog.d" / "x.fixed.md").write_text(текст, encoding="utf-8")
    return root


@pytest.mark.parametrize("прогоны, текст, незаписано", [
    ([прогон(1, 1)], "", []),                                    # с первой попытки — не предмет
    ([прогон(2, 2)], "", [2]),                                   # повторный, не записан
    ([прогон(3, 2)], "нестабильность, прогон 3 упал на checkout", []),  # записан номером
    ([прогон(4, 3, "failure")], "", []),                         # красный — не этот случай
    ([прогон(5, 2), прогон(6, 1), прогон(7, 2)], "прогон 7", [5]),  # смесь
])
def test_незаписанные(tmp_path, прогоны, текст, незаписано):
    root = журнал(tmp_path, текст)
    assert [п["id"] for п in fr.незаписанные(прогоны, fr.журнал(root))] == незаписано


def test_номер_ищется_и_в_вышедших_фрагментах(tmp_path):
    (tmp_path / "changelog.d" / "released").mkdir(parents=True)
    (tmp_path / "changelog.d" / "released" / "y.fixed.md").write_text("прогон 9", encoding="utf-8")
    assert fr.незаписанные([прогон(9, 2)], fr.журнал(tmp_path)) == []


def test_main_находка_без_записи_трекера(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(fr.ghcli, "список", lambda *a, **k: (0, [прогон(11, 2)], ""))
    assert fr.main(["--root", str(журнал(tmp_path, ""))]) == 1
    assert "runs/11" in capsys.readouterr().out


def test_main_всё_записано_чисто(tmp_path, monkeypatch):
    monkeypatch.setattr(fr.ghcli, "список", lambda *a, **k: (0, [прогон(12, 2)], ""))
    assert fr.main(["--root", str(журнал(tmp_path, "прогон 12"))]) == 0


def test_main_площадка_молчит_третий_исход(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(fr.ghcli, "список", lambda *a, **k: (1, [], "HTTP 502"))
    assert fr.main(["--root", str(tmp_path)]) == 2
    assert "HTTP 502" in capsys.readouterr().err


def test_main_задачи_нет_и_находок_нет_не_заводит(tmp_path, monkeypatch):
    monkeypatch.setattr(fr.ghcli, "список", lambda *a, **k: (0, [], ""))
    monkeypatch.setattr(fr.main_red, "find_issue", lambda m: (None, None))
    вызовы = []
    monkeypatch.setattr(fr.ghcli, "run", lambda *a: вызовы.append(a) or (0, ""))
    assert fr.main(["--root", str(журнал(tmp_path, "")), "--apply"]) == 0
    assert вызовы == []
