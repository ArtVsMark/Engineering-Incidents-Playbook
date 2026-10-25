"""Семейный значок: сверка проекта со сводкой семьи по сегментам.

Набор держит цвет по решению владельца 09.10: отставание на минор — красный,
нечего сверять или не прочитано — серый, и серый в зелёный не засчитывается.
Сводка здесь — подделка формы `scripts/family.py`, а дерево проекта — своё,
во временном каталоге.
"""

import json
from pathlib import Path

import family
import family_check as fc
import pytest

КАТАЛОГ = family.своё_имя()
МЕХ = "ArtVsMark/Engineering-Pipeline-Mechanisms"
SHA = "a" * 40


def сводка(*проекты: dict) -> dict:
    """Источник подделки (правило 170): форма — `family.сводка` из
    scripts/family.py, проект — строка `family.запись`."""
    return {"schema": family.FAMILY_SCHEMA, "projects": list(проекты)}


def издатель(repo: str, tag: str | None = "v1.5.0", **gives: str) -> dict:
    return {
        "repo": repo,
        "state": "published",
        "schema": "1.0",
        "takes": [],
        "release": {"tag": tag, "sha": SHA} if tag else None,
        "gives": gives,
    }


def дерево(tmp_path: Path, uses: str = "", ответ: dict | None = None) -> Path:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "a.yml").write_text(
        f"jobs:\n  x:\n    uses: {uses}\n" if uses else "on: push\n", encoding="utf-8"
    )
    if ответ is not None:
        (tmp_path / ".rules").mkdir()
        (tmp_path / ".rules" / "bindings.json").write_text(json.dumps(ответ), encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize(
    "ссылка, состояние",
    [
        ("v1.5.0", "ok"),
        ("v1.4.0", "behind"),  # минор — красный, а не жёлтый
        (SHA, "ok"),  # SHA последнего выпуска
        ("b" * 40, "behind"),  # SHA не последнего выпуска
    ],
)
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
    манифест = {
        "takes": [
            {"from": "o/glossary", "contract": "form", "where": "src/source.json", "field": "form"}
        ]
    }
    связи = fc.пары(tmp_path, сводка(издатель("o/glossary", form="6.1")), манифест)
    assert [(с.mine, с.latest, с.state) for с in связи] == [("6.0", "6.1", "behind")]


@pytest.mark.parametrize(
    "состояния, итог",
    [
        ([], "unknown"),
        (["ok", "ok"], "ok"),
        (["ok", "unknown"], "unknown"),
        (["unknown", "behind"], "behind"),
    ],
)
def test_цвет_сегмента(состояния, итог):
    связи = [fc.Связь("family", "p", "w", "1", "1", "x", s) for s in состояния]
    assert fc.итог(связи) == итог


def test_значок_рисует_общая_функция_и_называет_отставание(tmp_path):
    root = дерево(tmp_path, f"{МЕХ}/.github/workflows/step-x.yml@v1.4.0")
    разбор = fc.разобрать(root, сводка(издатель(МЕХ)), КАТАЛОГ)
    svg = fc.значок(разбор)
    assert "family ✗1" in svg and fc.ЦВЕТ["behind"] in svg
    assert разбор["segments"]["external"]["state"] == "unknown"
    assert разбор["segments"]["gives"]["why"]  # не издатель — названо


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
    doc = {
        "schema": "1.0",
        "project": "o/p",
        "takes": [],
        "gives": {"x": "1.0"},
        "release": {"tag": tag, "sha": SHA} if tag else None,
        **поверх,
    }
    (root / family.MANIFEST).write_text(json.dumps(doc), encoding="utf-8")


@pytest.mark.parametrize(
    "тег_манифеста, в_сводке, итог",
    [
        ("v2.0.0", True, "ok"),
        ("v1.9.0", True, "behind"),  # манифест называет не последний тег дерева
        ("v2.0.0", False, "unknown"),  # до сводки не дошёл
    ],
)
def test_сегмент_отдаю(tmp_path, monkeypatch, тег_манифеста, в_сводке, итог):
    monkeypatch.setattr(fc, "latest_tag", lambda root: "v2.0.0")
    _манифест(tmp_path, тег_манифеста)
    свод = сводка(издатель("o/p", tag=тег_манифеста, x="1.0")) if в_сводке else сводка()
    связи = fc.отдаю(
        tmp_path, свод, "o/p", json.loads((tmp_path / family.MANIFEST).read_text(encoding="utf-8"))
    )
    assert fc.итог(связи) == итог


def test_отдаю_чужой_формы_красный(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "latest_tag", lambda root: "v2.0.0")
    манифест = {
        "schema": "2.0",
        "project": "o/p",
        "takes": [],
        "gives": {},
        "release": {"tag": "v2.0.0", "sha": SHA},
    }
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
    assert "family ✗1" in (root / fc.SVG).read_text(encoding="utf-8")
    assert "v1.4.0" in capsys.readouterr().out


def test_main_кладёт_значок_и_разбор_по_out(tmp_path):
    """Действие `family-badge` у соседа: имя — своё, путь — его вход `out`,
    а разбор ложится рядом с картинкой, а не в папку значков каталога."""
    root = дерево(tmp_path / "p", f"{МЕХ}/.github/workflows/step-x.yml@v1.5.0")
    файл = tmp_path / "family.json"
    файл.write_text(json.dumps(сводка(издатель(МЕХ))), encoding="utf-8")
    out = root / "img" / "семья.svg"
    assert (
        fc.main(["--root", str(root), "--family", str(файл), "--repo", "o/p", "--out", str(out)])
        == 0
    )
    разбор = json.loads((root / "img" / fc.РАЗБОР.name).read_text(encoding="utf-8"))
    assert разбор["project"] == "o/p"
    assert разбор["segments"]["family"]["state"] == "ok"
    assert "family ✓" in out.read_text(encoding="utf-8")
    assert not (root / fc.SVG).exists()


def test_номер_разошёлся_со_сводкой_серый(tmp_path, monkeypatch):
    """Сводка ещё не перечитала манифест — видно, но это не отставание (обзор #808)."""
    monkeypatch.setattr(fc, "latest_tag", lambda root: "v2.0.0")
    манифест = {
        "schema": "1.1",
        "project": "o/p",
        "takes": [],
        "gives": {"x": "1.1"},
        "release": {"tag": "v2.0.0", "sha": SHA},
    }
    связи = fc.отдаю(tmp_path, сводка(издатель("o/p", tag="v2.0.0", x="1.0")), "o/p", манифест)
    assert [(с.state, с.why) for с in связи if с.what == "x"] == [
        ("unknown", "сводка ещё не перечитала манифест")
    ]


def _издатели(root, свод, свой="o/p", манифест=None):
    if манифест is not None:
        _манифест(root, None, **манифест)
    return {и["code"]: и["state"] for и in fc.разобрать(root, свод, свой)["publishers"]}


def test_блок_издателей(tmp_path):
    """Свежий шаг механизмов без `.pipeline.yml` — частичная связь `◐` (решение
    владельца 14.10), каталог без манифеста в сводке — нет связи. Блока `AVM`
    нет: с facts 2.0 витрина — читатель фактов, а не издатель (#843)."""
    root = дерево(tmp_path, f"{МЕХ}/.github/workflows/step-x.yml@v1.5.0")
    состояния = _издатели(root, сводка(издатель(МЕХ)))
    assert состояния == {"EIP": "none", "EPM": "partial"}


def test_отставший_пин_без_конвейера_остаётся_красным(tmp_path):
    """◐ решает, когда ставить ✓, а не прячет ✗ (обзор #839)."""
    root = дерево(tmp_path, f"{МЕХ}/.github/workflows/step-x.yml@v1.4.0")
    assert _издатели(root, сводка(издатель(МЕХ)))["EPM"] == "behind"


@pytest.mark.parametrize(
    "пин, steps, итог_",
    [
        ("v1.5.0", "0.7", "ok"),  # конвейер подключён, всё свежее
        ("v1.4.0", "0.7", "behind"),  # конвейер подключён, пин отстал
        ("v1.5.0", "0.9", "behind"),  # конвейер подключён, диапазон отстал
    ],
)
def test_механизмы_с_конвейером_судятся_по_свежести(tmp_path, пин, steps, итог_):
    root = дерево(tmp_path, f"{МЕХ}/.github/workflows/step-x.yml@{пин}")
    _конвейер(root, 'contract: ">=0.5,<0.9"\n')
    состояния = _издатели(root, сводка(издатель(МЕХ, steps=steps)))
    assert состояния["EPM"] == итог_


def test_частичная_связь_называет_число_связей(tmp_path):
    root = дерево(tmp_path, f"{МЕХ}/.github/workflows/step-x.yml@v1.5.0")
    блок = {и["code"]: и for и in fc.разобрать(root, сводка(издатель(МЕХ)), "o/p")["publishers"]}
    assert блок["EPM"]["state"] == "partial" and "связей с механизмами 1" in блок["EPM"]["why"]
    assert "EPM ◐" in fc.значок(fc.разобрать(root, сводка(издатель(МЕХ)), "o/p"))


def test_отказ_с_причиной_серый_а_не_красный(tmp_path):
    root = дерево(tmp_path)
    состояния = _издатели(root, сводка(), манифест={"skips": {"EPM": "шаги не нужны: нет PR"}})
    assert состояния["EPM"] == "skipped" and "AVM" not in состояния


def test_свой_издатель_показывает_отдачу(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "latest_tag", lambda root: None)
    root = дерево(tmp_path)
    состояния = _издатели(root, сводка(), свой=МЕХ, манифест={"project": МЕХ})
    assert состояния["EPM"] != "none"


def test_пустая_причина_отказа_не_форма():
    doc = {
        "schema": "1.1",
        "project": "o/p",
        "release": None,
        "gives": {},
        "takes": [],
        "skips": {"EPM": " "},
    }
    assert "skips" in family.изъян_формы(doc)


def test_отказ_от_неизвестного_издателя_и_при_живой_связи(tmp_path):
    """Опечатка в skips и отказ при живой связи не работают молча (обзор #809)."""
    root = дерево(tmp_path, f"{МЕХ}/.github/workflows/step-x.yml@v1.5.0")
    _манифест(root, None, skips={"EMP": "опечатка", "EPM": "не нужны"})
    разбор = fc.разобрать(root, сводка(издатель(МЕХ)), "o/p")
    почему = [x["why"] for x in разбор["segments"]["gives"]["links"] if x["what"] == "skips"]
    assert any("такого издателя нет" in п for п in почему)
    assert any("связь с ним в дереве есть" in п for п in почему)


@pytest.mark.parametrize(
    "мои, договор, состояние, причина",
    [
        ("2.0", "2.0", "ok", ""),  # подняты на договор каталога
        ("2.0", "2.1", "behind", ""),  # отстали внутри мажора — красный
        ("1.6", "2.0", "unknown", "#845"),  # переезд: форма та же, ждёт витрину
        ("1.2", "2.0", "behind", ""),  # отставание внутри 1.x — красный (владелец 21.10)
        ("1.5", "2.0", "behind", ""),  # и у предпоследнего 1.x — красный
        ("1.6", None, "unknown", "не опубликовано"),  # каталог договора не отдаёт
    ],
)
def test_факты_сверяются_с_договором_каталога(tmp_path, мои, договор, состояние, причина):
    """С facts 2.0 договор отдаёт каталог (#843): связь facts — с ним, а не с витриной."""
    root = дерево(tmp_path)
    _факты(root, {"schema": мои})
    gives = {"facts": договор} if договор else {}
    с = сводка(издатель(КАТАЛОГ, **gives), издатель("ArtVsMark/ArtVsMark", facts="1.6"))
    (связь,) = [
        x
        for x in fc.разобрать(root, с, "o/p")["segments"]["family"]["links"]
        if x["what"] == "facts"
    ]
    assert связь["publisher"] == КАТАЛОГ
    assert связь["state"] == состояние and причина in связь["why"]


def test_витрина_с_facts_не_издатель():
    """Витрина, ещё отдающая facts 1.x в манифесте, роли издателя не получает (#843)."""
    коды = fc.издатели_семьи(сводка(издатель("ArtVsMark/ArtVsMark", facts="1.6")))
    assert set(коды.values()) == {"EIP", "EPM"}
    assert (
        fc.споры_издателей(сводка(издатель("o/a", facts="1.6"), издатель("o/b", facts="2.0"))) == []
    )


def _факты(root: Path, doc: object) -> None:
    (root / ".github" / "badges").mkdir(parents=True, exist_ok=True)
    (root / fc.ФАКТЫ).write_text(json.dumps(doc), encoding="utf-8")


@pytest.mark.parametrize(
    "факты, состояние, отстаёт, причина",
    [
        (None, "unknown", 0, "фактов нет"),  # файла нет
        ({"schema": "1.6"}, "unknown", 0, "нет python.os"),  # раздела нет
        ({"python": {"os": []}}, "unknown", 0, "нет python.os"),  # пусто
        ({"python": {"os": ["ubuntu-26.04"]}}, "ok", 0, ""),  # прибито
        (
            {"python": {"os": ["ubuntu-26.04", "windows-latest", "macos-latest"]}},
            "behind",
            2,
            "",
        ),  # грейдер на 14.10
        (["не объект"], "unknown", 0, "нет python.os"),  # не той формы
        ({"python": ["ubuntu-26.04"]}, "unknown", 0, "нет python.os"),  # python не объект
        ({"python": "3.14"}, "unknown", 0, "нет python.os"),  # python строкой
        ({"python": {"os": "ubuntu-26.04"}}, "unknown", 0, "нет python.os"),  # os не список
        ({"python": {"os": ["ubuntu-26.04", 42]}}, "unknown", 0, "не строка"),  # метка не строка
    ],
)
def test_ext_по_своим_фактам(tmp_path, факты, состояние, отстаёт, причина):
    """Все формы входа сегмента ext (решение владельца 14.10, #816): плавающая
    метка исполнителя — красный, нечего судить — серый с причиной."""
    root = дерево(tmp_path)
    if факты is not None:
        _факты(root, факты)
    ext = fc.разобрать(root, сводка(), "o/p")["segments"]["external"]
    assert ext["state"] == состояние
    assert sum(x["state"] == "behind" for x in ext["links"]) == отстаёт
    assert причина in ext["why"]
    if отстаёт:
        assert fc.надпись("external", ext) == f"ext ✗{отстаёт}"
        assert {x["what"] for x in ext["links"] if x["state"] == "behind"} == {
            "windows-latest",
            "macos-latest",
        }


@pytest.mark.parametrize("файл", [".rules/bindings.json", ".github/badges/facts.json"])
def test_файл_дерева_не_объект_не_роняет_разбор(tmp_path, файл):
    """Ответ и факты не той формы (список вместо объекта) — сверять нечего,
    а не исключение: значок соседа собирается и с битым файлом."""
    root = дерево(tmp_path)
    (root / файл).parent.mkdir(parents=True, exist_ok=True)
    (root / файл).write_text("[1]", encoding="utf-8")
    разбор = fc.разобрать(root, сводка(издатель(КАТАЛОГ, bindings="1.9", export="1.9")), "o/p")
    assert not [x for x in разбор["segments"]["family"]["links"] if x["where"] == файл]


# ── диапазон контракта шагов механизмов (решение владельца 14.10, #816) ──


def _конвейер(root: Path, текст: str | None) -> None:
    if текст is not None:
        (root / ".pipeline.yml").write_text(текст, encoding="utf-8")


@pytest.mark.parametrize(
    "конвейер, steps, состояние, причина",
    [
        (None, "0.7", None, ""),  # шагов не берёт — связи нет
        ("checks: {}\n", "0.7", "unknown", "не объявлен"),  # строки нет
        ('contract: "0.5..0.9"\n', "0.7", "unknown", "не той формы"),  # форма не та
        ('contract: ">=0.5,<0.9"\n', None, "unknown", "не опубликовано"),  # издатель молчит
        ('contract: ">=0.5,<0.9"\n', "0.7", "ok", ""),  # свежий в диапазоне
        ("contract: '>=0.5,<0.9'  # окно перехода\n", "0.7", "ok", ""),  # кавычки и комментарий
        ('contract: ">=0.5,<0.7"\n', "0.7", "behind", "вне объявленного"),  # верх ниже свежего
        ('contract: "==0.6"\n', "0.7", "behind", "вне объявленного"),  # прибит к старому
        ('contract: ">=0.8,<0.9"\n', "0.7", "unknown", "опережает"),  # сводка отстала
        ('contract: "==0.8"\n', "0.7", "unknown", "опережает"),  # == выше — тоже нижняя (#831)
        ('contract: "==0.8"\n', "0.9", "behind", "вне"),  # == ниже свежего — отстаёт
    ],
)
def test_диапазон_шагов(tmp_path, конвейер, steps, состояние, причина):
    """Все формы входа (210): нет файла · нет строки · форма · молчание
    издателя · в диапазоне · вне сверху · вне снизу."""
    root = дерево(tmp_path)
    _конвейер(root, конвейер)
    gives = {"steps": steps} if steps else {}
    связи = [
        x
        for x in fc.разобрать(root, сводка(издатель(МЕХ, **gives)), "o/p")["segments"]["family"][
            "links"
        ]
        if x["what"] == "steps"
    ]
    if состояние is None:
        assert связи == []
        return
    assert [x["state"] for x in связи] == [состояние]
    assert причина in связи[0]["why"]


def test_диапазон_при_споре_о_механизмах_серый(tmp_path):
    root = дерево(tmp_path)
    _конвейер(root, 'contract: ">=0.5,<0.9"\n')
    с = сводка(издатель(МЕХ, steps="0.7"), издатель("o/мех-2", steps="0.8"))
    связи = [
        x
        for x in fc.разобрать(root, с, "o/p")["segments"]["family"]["links"]
        if x["what"] == "steps"
    ]
    assert связи[0]["state"] == "unknown" and "несколько проектов" in связи[0]["why"]


def test_uptake_у_издателя_по_связям_сводки():
    """Сколько проектов семьи перешли на издателя (владелец 15.10, #844)."""
    с = сводка(
        {**издатель(КАТАЛОГ), "links": {}},
        {**издатель("o/a"), "links": {"EIP": "ok"}},
        {**издатель("o/b"), "links": {"EIP": "partial", "EPM": "ok"}},
        {**издатель("o/c"), "links": {"EIP": "none"}},
        {**издатель("o/e"), "links": {"EIP": "unknown"}},  # связь есть, свежесть не сверена
        {**издатель("o/f"), "links": {"EIP": "skipped"}},  # отказ — не перешёл
        издатель("o/d"),
    )  # не прочитан
    п = fc.uptake(с, КАТАЛОГ, fc.издатели_семьи(с))
    assert п == {"code": "EIP", "taken": 3, "of": 6, "unread": 1, "by": ["o/a", "o/b", "o/e"]}
    подпись, число = fc.зона_uptake(п)
    assert число[0] == "3/6" and "не прочитано у 1" in число[2]


def test_uptake_нет_у_не_издателя(tmp_path):
    root = дерево(tmp_path)
    разбор = fc.разобрать(root, сводка({**издатель("o/a"), "links": {"EIP": "ok"}}), "o/p")
    assert "uptake" not in разбор
    assert all(з[0][0] != "uptake" for з in fc.зоны(разбор))


def test_uptake_все_не_прочитаны_серый():
    с = сводка(издатель(КАТАЛОГ), издатель("o/a"))
    п = fc.uptake(с, КАТАЛОГ, fc.издатели_семьи(с))
    assert fc.зона_uptake(п)[1][1] == fc.ЦВЕТ["unknown"]


def test_одно_отставание_названо_один_раз_с_числом_и_файлом():
    """Два uses: на одном старом выпуске — одна строка подсказки, а не повтор (21.10)."""
    связь = {
        "what": "release",
        "mine": "v1.5.0",
        "latest": "v1.8.0",
        "where": ".github/workflows/mechanisms.yml",
        "state": "behind",
    }
    свежая = {**связь, "mine": "v1.8.0", "where": "a.yml", "state": "ok"}
    другая = {**связь, "where": "b.yml", "mine": "v1.4.0"}
    assert fc.отставание([связь, dict(связь), свежая]) == (
        "release: v1.5.0 → v1.8.0 (связей 2, .github/workflows/mechanisms.yml)"
    )
    assert fc.отставание([связь, другая]) == (
        "release: v1.5.0 → v1.8.0 (.github/workflows/mechanisms.yml); "
        "release: v1.4.0 → v1.8.0 (b.yml)"
    )
