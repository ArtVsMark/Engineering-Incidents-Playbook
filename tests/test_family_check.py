"""Семейный значок: сверка проекта со сводкой семьи по сегментам.

Набор держит цвет по решению владельца 09.10: отставание на минор — красный,
нечего сверять или не прочитано — серый, и серый в зелёный не засчитывается.
Сводка здесь — подделка формы `scripts/family.py`, а дерево проекта — своё,
во временном каталоге.
"""

import json
from pathlib import Path

import pytest

import family
import family_check as fc

КАТАЛОГ = family.своё_имя()
МЕХ = "ArtVsMark/Engineering-Pipeline-Mechanisms"
SHA = "a" * 40


def сводка(*проекты: dict) -> dict:
    """Источник подделки (правило 170): форма — `family.сводка` из
    scripts/family.py, проект — строка `family.запись`."""
    return {"schema": family.FAMILY_SCHEMA, "projects": list(проекты)}


def издатель(repo: str, tag: str | None = "v1.5.0", **gives: str) -> dict:
    return {"repo": repo, "state": "published", "schema": "1.0", "takes": [],
            "release": {"tag": tag, "sha": SHA} if tag else None, "gives": gives}


def дерево(tmp_path: Path, uses: str = "", ответ: dict | None = None) -> Path:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "a.yml").write_text(f"jobs:\n  x:\n    uses: {uses}\n" if uses else "on: push\n",
                              encoding="utf-8")
    if ответ is not None:
        (tmp_path / ".rules").mkdir()
        (tmp_path / ".rules" / "bindings.json").write_text(json.dumps(ответ), encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("ссылка, состояние", [
    ("v1.5.0", "ok"),
    ("v1.4.0", "behind"),          # минор — красный, а не жёлтый
    (SHA, "ok"),                   # SHA последнего выпуска
    ("b" * 40, "behind"),          # SHA не последнего выпуска
])
def test_прибитый_тег_семьи(tmp_path, ссылка, состояние):
    root = дерево(tmp_path, f"{МЕХ}/.github/workflows/step-x.yml@{ссылка}")
    связи = fc.семья(root, сводка(издатель(МЕХ)), КАТАЛОГ)
    assert [с.state for с in связи] == [состояние]


def test_издатель_без_манифеста_неизвестен_а_не_сходится(tmp_path):
    root = дерево(tmp_path, f"{МЕХ}/.github/workflows/step-x.yml@v1.5.0")
    связи = fc.семья(root, сводка({"repo": МЕХ, "state": "absent", "why": "404"}), КАТАЛОГ)
    assert [с.state for с in связи] == ["unknown"] and fc.итог(связи) == "unknown"


def test_вне_семьи_и_своё_не_сверяются(tmp_path):
    root = дерево(tmp_path, "actions/checkout@v5")
    assert fc.семья(root, сводка(издатель(МЕХ)), КАТАЛОГ) == []


def test_ответ_каталогу_сверяется_с_его_номерами(tmp_path):
    root = дерево(tmp_path, ответ={"schema": "1.8", "answers_to": "1.7"})
    связи = fc.семья(root, сводка(издатель(КАТАЛОГ, bindings="1.9", export="1.7")), "o/p")
    assert {с.what: с.state for с in связи} == {"bindings": "behind", "export": "ok"}


def test_пара_читает_номер_из_названного_файла(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "source.json").write_text('{"form": "6.0"}', encoding="utf-8")
    манифест = {"takes": [{"from": "o/glossary", "contract": "form",
                           "where": "src/source.json", "field": "form"}]}
    связи = fc.пары(tmp_path, сводка(издатель("o/glossary", form="6.1")), манифест)
    assert [(с.mine, с.latest, с.state) for с in связи] == [("6.0", "6.1", "behind")]


@pytest.mark.parametrize("состояния, итог", [
    ([], "unknown"),
    (["ok", "ok"], "ok"),
    (["ok", "unknown"], "unknown"),
    (["unknown", "behind"], "behind"),
])
def test_цвет_сегмента(состояния, итог):
    связи = [fc.Связь("family", "p", "w", "1", "1", "x", s) for s in состояния]
    assert fc.итог(связи) == итог


def test_значок_рисует_общая_функция_и_называет_отставание(tmp_path):
    root = дерево(tmp_path, f"{МЕХ}/.github/workflows/step-x.yml@v1.4.0")
    разбор = fc.разобрать(root, сводка(издатель(МЕХ)), КАТАЛОГ)
    svg = fc.значок(разбор)
    assert "family 1 behind" in svg and fc.ЦВЕТ["behind"] in svg
    assert разбор["segments"]["external"]["state"] == "unknown"
    assert разбор["segments"]["gives"]["why"]          # не издатель — названо


def test_main_без_сводки_третий_исход_с_адресом(tmp_path, capsys):
    assert fc.main(["--root", str(tmp_path), "--family", str(tmp_path / "нет.json")]) == 2
    assert str(tmp_path / "нет.json") in capsys.readouterr().err
