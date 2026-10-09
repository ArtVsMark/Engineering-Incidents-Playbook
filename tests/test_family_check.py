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


def test_опережение_не_отставание():
    """Моё новее опубликованного — серый с причиной, а не красный (обзор #807)."""
    связь = fc.сверить("family", "p", "bindings", "1.10", "1.9", "x")
    assert связь.state == "unknown" and "опережает" in связь.why
    assert fc.сверить("family", "p", "release", "v1.9.0", "v1.10.0", "x").state == "behind"


def test_неполная_запись_takes_данные_а_не_падение(tmp_path):
    связи = fc.пары(tmp_path, сводка(), {"takes": [{"from": "o/g", "contract": "form"}]})
    assert [(с.state, "неполна" in с.why) for с in связи] == [("unknown", True)]


def _манифест(root: Path, tag: str | None, **поверх) -> None:
    (root / family.MANIFEST).parent.mkdir(parents=True, exist_ok=True)
    doc = {"schema": "1.0", "project": "o/p", "takes": [], "gives": {"x": "1.0"},
           "release": {"tag": tag, "sha": SHA} if tag else None, **поверх}
    (root / family.MANIFEST).write_text(json.dumps(doc), encoding="utf-8")


@pytest.mark.parametrize("тег_манифеста, в_сводке, итог", [
    ("v2.0.0", True, "ok"),
    ("v1.9.0", True, "behind"),     # манифест называет не последний тег дерева
    ("v2.0.0", False, "unknown"),   # до сводки не дошёл
])
def test_сегмент_отдаю(tmp_path, monkeypatch, тег_манифеста, в_сводке, итог):
    monkeypatch.setattr(fc, "latest_tag", lambda root: "v2.0.0")
    _манифест(tmp_path, тег_манифеста)
    свод = сводка(издатель("o/p", tag=тег_манифеста)) if в_сводке else сводка()
    связи = fc.отдаю(tmp_path, свод, "o/p", json.loads(
        (tmp_path / family.MANIFEST).read_text(encoding="utf-8")))
    assert fc.итог(связи) == итог


def test_отдаю_чужой_формы_красный(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "latest_tag", lambda root: "v2.0.0")
    манифест = {"schema": "2.0", "project": "o/p", "takes": [], "gives": {},
                "release": {"tag": "v2.0.0", "sha": SHA}}
    связи = fc.отдаю(tmp_path, сводка(издатель("o/p", tag="v2.0.0")), "o/p", манифест)
    assert [с.state for с in связи if с.what == "form"] == ["behind"]


def test_main_пишет_значок_и_разбор(tmp_path, capsys):
    root = дерево(tmp_path / "p", f"{МЕХ}/.github/workflows/step-x.yml@v1.4.0")
    файл = tmp_path / "family.json"
    файл.write_text(json.dumps(сводка(издатель(МЕХ))), encoding="utf-8")
    (root / ".github" / "badges").mkdir(parents=True)
    assert fc.main(["--root", str(root), "--family", str(файл), "--repo", "o/p"]) == 0
    разбор = json.loads((root / fc.РАЗБОР).read_text(encoding="utf-8"))
    assert разбор["segments"]["family"]["state"] == "behind"
    assert "family 1 behind" in (root / fc.SVG).read_text(encoding="utf-8")
    assert "v1.4.0" in capsys.readouterr().out
