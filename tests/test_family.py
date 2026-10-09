"""Контракт семьи: манифест проекта и сводка манифестов по реестру.

Набор держит три вещи: манифест каталога отдаёт ровно номера выгрузки, а не
вторую их копию (049); у соседа в сводке три состояния, и «не прочитан» не
сливается ни с «нет файла», ни с «есть» (039); чужая форма не проходит как
своя.
"""

import json

import pytest

import build_rules_index as bri
import family

ХОРОШИЙ = {"schema": "1.0", "project": "o/a", "release": None,
           "gives": {"x": "1.0"}, "takes": []}


def test_манифест_отдаёт_номера_выгрузки_и_свой():
    м = family.манифест()
    assert м["gives"] == bri.contracts_now()
    assert м["gives"]["family"] == family.FAMILY_SCHEMA
    assert м["project"] == bri.CATALOGUE_URL.removeprefix("https://github.com/")
    assert family.изъян_формы(м) is None


@pytest.mark.parametrize("doc, изъян", [
    ([], "не объект"),
    ({**ХОРОШИЙ, "gives": None}, "«gives» не того типа"),
    ({k: v for k, v in ХОРОШИЙ.items() if k != "takes"}, "нет ключа «takes»"),
    ({**ХОРОШИЙ, "schema": "2.0"}, "формат 2.0"),
])
def test_чужая_форма_называется(doc, изъян):
    assert изъян in family.изъян_формы(doc)


def test_минор_формата_читается():
    """Минор добавляет поля, а не ломает старые — читатель 1.0 берёт 1.3."""
    assert family.изъян_формы({**ХОРОШИЙ, "schema": "1.3"}) is None


@pytest.mark.parametrize("err, состояние", [
    ("не прочитан: HTTP Error 404: Not Found", "absent"),
    ("не прочитан: <urlopen error timed out> — и так 3 раза подряд", "unreadable"),
    ("не прочитан: HTTP Error 403: Forbidden", "unreadable"),
])
def test_нет_файла_и_не_прочитан_различаются(err, состояние):
    строка = family.запись("o/a", None, err)
    assert строка["state"] == состояние and строка["why"] == err


def test_манифест_под_чужим_именем_не_принимается():
    строка = family.запись("o/b", ХОРОШИЙ, None)
    assert строка["state"] == "unreadable" and "o/a" in строка["why"]


def test_сводка_берёт_свой_без_сети_а_соседей_по_адресу():
    """Источник подделки (правило 170) — scripts/aggregate_bindings.py, форма
    возврата `fetch`: пара «данные, ошибка», текст ошибки 404 — её же
    `f"не прочитан: {e}"` над `urllib.error.HTTPError` 404."""
    прочитано: list[str] = []

    def прочесть(url: str):
        прочитано.append(url)
        return ({**ХОРОШИЙ, "project": "o/a"}, None) if "/o/a/" in url else (
            None, "не прочитан: HTTP Error 404: Not Found")

    свой = {**ХОРОШИЙ, "project": "o/self"}
    doc = family.сводка([{"repo": "o/self"}, {"repo": "o/a"}, {"repo": "o/b"}],
                        свой, прочесть)
    assert [p["state"] for p in doc["projects"]] == ["published", "published", "absent"]
    assert прочитано == [family.АДРЕС.format(repo=r) for r in ("o/a", "o/b")]
    assert doc["schema"] == family.FAMILY_SCHEMA


def test_main_пишет_сводку_по_реестру(tmp_path, monkeypatch, capsys):
    """Источник подделки (правило 170): та же форма возврата `fetch`, что
    выше, — `(None, "не прочитан: HTTP Error 404: Not Found")`."""
    (tmp_path / ".rules").mkdir()
    (tmp_path / ".rules" / "consumers.json").write_text(json.dumps(
        {"consumers": [{"repo": family.своё_имя()}, {"repo": "o/b"}]}),
        encoding="utf-8")
    monkeypatch.setattr(family, "fetch",
                        lambda url: (None, "не прочитан: HTTP Error 404: Not Found"))
    assert family.main(["--root", str(tmp_path), "--summary"]) == 0
    doc = json.loads((tmp_path / family.SUMMARY).read_text(encoding="utf-8"))
    assert [p["state"] for p in doc["projects"]] == ["published", "absent"]
    assert "published 1, absent 1, unreadable 0" in capsys.readouterr().out


def test_main_без_реестра_третий_исход_с_адресом(tmp_path, capsys):
    assert family.main(["--root", str(tmp_path), "--summary"]) == 2
    assert str(tmp_path / family.REGISTRY) in capsys.readouterr().err


def test_выпуск_берётся_из_того_же_дерева(tmp_path):
    """Выпуск и номера одного манифеста — из одного дерева (обзор #801):
    в клоне без тегов выпуска нет, хотя у каталога рядом он есть."""
    import subprocess
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    assert family.выпуск(tmp_path) is None
    assert family.манифест(tmp_path)["release"] is None


def test_выпуск_свой_тег_у_своего_дерева(tmp_path):
    """Положительный случай (обзор #802): в дереве с тегом выпуск — его тег и
    его коммит, а не тег каталога, рядом с которым лежит скрипт."""
    import subprocess

    def git(*a: str) -> str:
        return subprocess.run(["git", "-C", str(tmp_path), *a], check=True,
                              capture_output=True, text=True,
                              encoding="utf-8").stdout.strip()
    git("init", "-q")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
        "--allow-empty", "-m", "первый")
    git("tag", "v7.3.0")
    assert family.выпуск(tmp_path) == {"tag": "v7.3.0", "sha": git("rev-parse", "HEAD")}
