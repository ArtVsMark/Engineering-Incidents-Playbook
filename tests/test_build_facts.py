"""Факты о каталоге: публикуется измеренное, пропуск называется вслух.

Проверяется то, ради чего файл существует (правило 174): числа берутся у тех,
кто их считает, а раздел, который не измерился, ОТСУТСТВУЕТ — не выставляется в
ноль. Ноль на месте пропуска читался бы как ответ: «проверок не создаётся»
вместо «замер не отработал» (039).
"""

from __future__ import annotations

import json
from pathlib import Path

import build_facts as bf
from conftest import write


ПРОГОН = """\
name: ci
on:
  pull_request:
    types: [opened]
  workflow_dispatch:
jobs:
  catalogue:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
"""

ТОЛЬКО_ТОЛЧОК = """\
name: badges
on:
  push:
    branches: [main]
jobs:
  publish:
    runs-on: macos-latest
    steps:
      - run: echo
"""


def дерево(repo: Path) -> None:
    """Подделка — настоящие файлы тех форм, которые скрипт читает."""
    write(repo / ".github/workflows/ci.yml", ПРОГОН)
    write(repo / ".github/workflows/badges.yml", ТОЛЬКО_ТОЛЧОК)
    write(repo / "pyproject.toml", 'requires-python = ">=3.12"\n')
    write(repo / "tests/test_a.py", "def test_one():\n    pass\n\n"
                                    "async def test_two():\n    pass\n")
    write(repo / "tests/test_b.py", "def test_three():\n    pass\n")


def подставить(monkeypatch, repo: Path) -> None:
    monkeypatch.setattr(bf, "ROOT", repo)
    monkeypatch.setattr(bf, "WORKFLOWS", repo / ".github/workflows")
    monkeypatch.setattr(bf, "WHERE", repo / "export/where.json")
    monkeypatch.setattr(bf, "FACTS", repo / ".github/badges/facts.json")


def test_считает_функции_и_модули_набора(monkeypatch, repo):
    дерево(repo)
    подставить(monkeypatch, repo)
    # Асинхронный тест считается наравне с обычным: pytest его запускает.
    assert bf.tests()[0] == {"functions": 3, "modules": 2}


def test_проверкой_на_изменении_считается_разбуженная_изменением(
        monkeypatch, repo):
    """Работа, которую будит толчок в ветку, проверкой ИЗМЕНЕНИЯ не является.

    Снаружи её видно в тех же проверках коммита, и медиана «по семи
    изменениям» именно так и промахивается. Контракт витрины запрещает
    публиковать оценки: издатель называет то, что знает точно.
    """
    дерево(repo)
    подставить(monkeypatch, repo)
    раздел, почему = bf.checks_per_pr()
    assert почему == ""
    assert раздел["count"] == 1 and раздел["names"] == ["catalogue"]
    # `publish` из прогона, просыпающегося только на толчок, сюда не попал.
    assert "publish" not in раздел["names"]


def test_нет_прогона_на_изменении_раздела_нет_и_причина_названа(
        monkeypatch, repo):
    """Вторая сторона (140): пустого раздела не возникает, возникает пропуск."""
    write(repo / ".github/workflows/badges.yml", ТОЛЬКО_ТОЛЧОК)
    подставить(monkeypatch, repo)
    раздел, почему = bf.checks_per_pr()
    assert раздел is None
    assert "pull_request" in почему


def test_версии_и_исполнители_берутся_у_прогонов(monkeypatch, repo):
    дерево(repo)
    подставить(monkeypatch, repo)
    раздел, _ = bf.python()
    assert раздел["supported"] == ["3.12"]
    assert раздел["floor"] == "3.12"
    assert раздел["os"] == ["macos-latest", "ubuntu-latest"]


def test_доли_правил_берутся_из_сводки_а_не_считаются_заново(monkeypatch, repo):
    дерево(repo)
    подставить(monkeypatch, repo)
    write(repo / "export/where.json", json.dumps({"consumers": [
        {"repo": "чужой/проект", "answered": 1, "by_mechanism": {"gate": 1}},
        {"repo": "свой/каталог", "answered": 9,
         "by_status": {"active": 5, "not-applicable": 4},
         "by_mechanism": {"gate": 3, "pipeline": 1, "document": 1, "none": 0}},
    ]}))
    раздел, почему = bf.rules("свой/каталог")
    assert почему == ""
    assert раздел == {"total": 9, "gate": 3, "pipeline": 1, "document": 1,
                      "none": 0, "not_applicable": 4}


def test_чужого_среза_не_берём(monkeypatch, repo):
    """Имя разошлось с реестром — это пропуск с причиной, а не чужие числа."""
    дерево(repo)
    подставить(monkeypatch, repo)
    write(repo / "export/where.json", json.dumps({"consumers": [
        {"repo": "чужой/проект", "answered": 1, "by_mechanism": {"gate": 1}}]}))
    раздел, почему = bf.rules("свой/каталог")
    assert раздел is None and "свой/каталог" in почему


def test_нет_сводки_нет_раздела_и_сказано_кто_её_собирает(monkeypatch, repo):
    дерево(repo)
    подставить(monkeypatch, repo)
    раздел, почему = bf.rules("свой/каталог")
    assert раздел is None and "aggregate_bindings" in почему


def test_покрытие_без_замера_это_пропуск_а_не_ноль(monkeypatch, repo):
    """Ноль здесь читался бы как «покрытия нет», а это «не мерили» (039)."""
    monkeypatch.setattr(bf.coverage_badge, "measured", lambda: None)
    значение, почему = bf.coverage()
    assert значение is None and почему
    # И главное: в собранном файле ключа нет вовсе.
    дерево(repo)
    подставить(monkeypatch, repo)
    monkeypatch.setattr(bf, "git", lambda *a: (0, "deadbeef"))
    monkeypatch.setattr(bf.check_own_name, "own_slug", lambda root: ("своё/имя", ""))
    факты, пропуски, беда = bf.build()
    assert беда == ""
    assert "coverage_percent" not in факты
    assert any(п.startswith("coverage_percent:") for п in пропуски)


def test_покрытие_берётся_замером_а_не_округлённым_значком(monkeypatch, repo):
    """99.2 обязано доехать как 99.2: значок рисует `{:.0f}%` и теряет точность."""
    monkeypatch.setattr(bf.coverage_badge, "measured", lambda: 99.1666)
    assert bf.coverage() == (99.2, "")


def test_обязательный_минимум_есть_всегда(monkeypatch, repo):
    дерево(repo)
    подставить(monkeypatch, repo)
    monkeypatch.setattr(bf, "git", lambda *a: (0, "deadbeef"))
    monkeypatch.setattr(bf.check_own_name, "own_slug", lambda root: ("своё/имя", ""))
    факты, _, беда = bf.build()
    assert беда == ""
    assert факты["schema"] == "1.0" and isinstance(факты["schema"], str)
    assert факты["repo"] == "своё/имя"
    assert факты["generated_at"].endswith("+00:00")
    assert факты["commit"] == "deadbeef"


def test_без_имени_репозитория_файл_не_пишется(monkeypatch, repo, capsys):
    """Пустой ответ хуже отсутствующего — это третий исход, а не пустой файл."""
    дерево(repo)
    подставить(monkeypatch, repo)
    monkeypatch.setattr(bf.check_own_name, "own_slug",
                        lambda root: ("", "origin не спросить"))
    assert bf.main([]) == 2
    assert "не отработал" in capsys.readouterr().err
    assert not (repo / ".github/badges/facts.json").exists()


def test_записанный_файл_разбирается_и_несёт_объявленную_схему(
        monkeypatch, repo):
    дерево(repo)
    подставить(monkeypatch, repo)
    monkeypatch.setattr(bf, "git", lambda *a: (0, "deadbeef"))
    monkeypatch.setattr(bf.check_own_name, "own_slug", lambda root: ("своё/имя", ""))
    assert bf.main([]) == 0
    записано = json.loads((repo / ".github/badges/facts.json")
                          .read_text(encoding="utf-8"))
    assert записано["schema"] == "1.0"
    # Номер схемы обязан сказать, ЧЕГО он: ключ `schema` носят четыре предмета.
    assert "164" in записано["schema_of"]
