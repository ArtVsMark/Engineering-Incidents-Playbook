"""Договор фактов держит каталог (#843): проверка издателя и её исходы."""

import json
import subprocess
import sys
from pathlib import Path

import check_facts as cf

ПРИМЕР = cf.EXAMPLE_PATH


def запуск(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(Path(cf.__file__)), *args],
                          capture_output=True, text=True, encoding="utf-8", timeout=600)


def test_самопроверка_двусторонняя():
    assert cf.selftest() == 0


def test_номер_договора_сходится_с_прозой_и_схемой():
    assert запуск("--contract").returncode == 0


def test_образец_отвечает():
    assert запуск("--file", str(ПРИМЕР), "--repo", "Owner/Project").returncode == 0


def test_чужой_репозиторий_находка(tmp_path):
    assert запуск("--file", str(ПРИМЕР), "--repo", "Owner/Other").returncode == 1


def test_мажор_1_принят_с_советом_о_переезде(tmp_path):
    f = tmp_path / "facts.json"
    f.write_text(json.dumps({**json.loads(ПРИМЕР.read_text(encoding="utf-8")),
                             "schema": "1.6"}), encoding="utf-8")
    run = запуск("--file", str(f), "--repo", "Owner/Project")
    assert run.returncode == 0
    assert "facts-v2.0.0" in run.stdout


def test_без_файла_третий_исход():
    run = запуск()
    assert run.returncode == 2
    assert "--file" in run.stderr


def test_нечитаемый_файл_третий_исход(tmp_path):
    f = tmp_path / "facts.json"
    f.write_text("{", encoding="utf-8")
    assert запуск("--file", str(f), "--repo", "Owner/Project").returncode == 2


def test_номер_разошёлся_с_прозой_отказ(tmp_path, monkeypatch):
    """Гейт `--contract` отвергает прозу на прежнем номере, а не только пропускает верную."""
    проза = cf.CONTRACT_PATH.read_text(encoding="utf-8").replace(
        "FACTS_CONTRACT: facts-v2.0.0", "FACTS_CONTRACT: facts-v1.6.0")
    старая = tmp_path / "facts-contract.md"
    старая.write_text(проза, encoding="utf-8")
    monkeypatch.setattr(cf, "CONTRACT_PATH", старая)
    monkeypatch.setattr(sys, "argv", ["check_facts.py", "--contract"])
    assert cf.main() == 1
