"""Витрина плагинов сходится с деревом, версию выводит коммит.

Случаи спрашивают гейт через `main()` на поддельном дереве (150). Последний
идёт по настоящему дереву: витрина каталога обязана проходить свой же гейт.

Источник формы витрины: `.claude-plugin/marketplace.json` и
`plugins/<имя>/.claude-plugin/plugin.json` — раскладка, которую
`claude plugin validate` 2.1.282 принял 25 сентября; адрес описания —
https://code.claude.com/docs/en/plugins/marketplace-reference.md
"""

from __future__ import annotations

import json
from pathlib import Path

import check_plugins as cp
from conftest import write

ВИТРИНА = {"name": "incidents-playbook", "owner": {"name": "o"},
           "plugins": [{"name": "catalogue", "source": "./plugins/catalogue"}]}


def дерево(repo: Path, витрина: dict | None = ВИТРИНА,
           манифест: dict | None = None) -> Path:
    if витрина is not None:
        write(repo / ".claude-plugin" / "marketplace.json", json.dumps(витрина))
    write(repo / "plugins" / "catalogue" / ".claude-plugin" / "plugin.json",
          json.dumps(манифест or {"name": "catalogue"}))
    return repo


def прогон(repo: Path) -> int:
    return cp.main(["--root", str(repo)])


def test_soshedshayasya_vitrina(repo, capsys):
    assert прогон(дерево(repo)) == 0
    assert "плагинов 1" in capsys.readouterr().out


def test_vpisannaya_versiya_v_manifeste_nahodka(repo, capsys):
    """Кеш ключуется версией: вписанную некому поднять (035)."""
    assert прогон(дерево(repo, манифест={"name": "catalogue", "version": "1.0.0"})) == 1
    assert "вписана версия" in capsys.readouterr().err


def test_vpisannaya_versiya_v_vitrine_nahodka(repo, capsys):
    витрина = {**ВИТРИНА, "plugins": [{**ВИТРИНА["plugins"][0], "version": "1.0.0"}]}
    assert прогон(дерево(repo, витрина=витрина)) == 1
    assert "вписана версия" in capsys.readouterr().err


def test_tri_imeni_odnogo_plagina_nahodka(repo, capsys):
    assert прогон(дерево(repo, манифест={"name": "other"})) == 1
    assert "три имени" in capsys.readouterr().err


def test_source_mimo_papki_nahodka(repo, capsys):
    витрина = {**ВИТРИНА, "plugins": [{"name": "catalogue", "source": "./catalogue"}]}
    assert прогон(дерево(repo, витрина=витрина)) == 1
    assert "./plugins/catalogue" in capsys.readouterr().err


def test_papka_o_kotoroy_molchit_vitrina_nahodka(repo, capsys):
    дерево(repo)
    (repo / "plugins" / "forgotten").mkdir()
    assert прогон(repo) == 1
    assert "plugins/forgotten/" in capsys.readouterr().err


def test_plaginy_bez_vitriny_tretiy_iskhod(repo, capsys):
    """Плагины лежат, а площадка их не найдёт — это не «чисто» (075)."""
    assert прогон(дерево(repo, витрина=None)) == 2
    assert "не отработала" in capsys.readouterr().err


def test_ni_vitriny_ni_plaginov_tretiy_iskhod(repo, capsys):
    assert прогон(repo) == 2
    assert "без предмета" in capsys.readouterr().err


def test_vitrina_ne_razobrana_tretiy_iskhod(repo, capsys):
    write(repo / ".claude-plugin" / "marketplace.json", "{не json")
    assert прогон(repo) == 2


def test_samoproverka():
    assert cp.main(["--selftest"]) == 0


def test_nastoyashchaya_vitrina_kataloga():
    assert cp.main([]) == 0
