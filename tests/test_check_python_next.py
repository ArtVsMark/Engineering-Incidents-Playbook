"""Сверка предрелизной версии прогона python-next с площадкой (203).

Источник подделки (правило 170): форма записей манифеста снята 02.10 с
https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json
— список словарей с ключами `version` («3.15.0-rc.2», «3.14.7») и `stable`
(bool); 254 записи, стабильная ветка 3.14, предрелизная 3.15. Подделки ниже —
та же форма, урезанная до веток, о которых спрашивает случай.
"""


import json

import pytest

import check_python_next as pn
import main_red

from conftest import SCRIPTS

#: Снимок 02.10 по существу: 3.14 стабильна, 3.15 — только пробные.
СЕГОДНЯ = [
    {"version": "3.15.0-rc.2", "stable": False},
    {"version": "3.15.0-beta.4", "stable": False},
    {"version": "3.14.7", "stable": True},
    {"version": "3.13.9", "stable": True},
]
#: 3.15 вышла, 3.16 — первая альфа.
ВЫШЛА = [
    {"version": "3.16.0-alpha.1", "stable": False},
    {"version": "3.15.0", "stable": True},
    {"version": "3.15.0-rc.2", "stable": False},
    {"version": "3.14.7", "stable": True},
]


def _прогон(tmp_path, версия: str = "3.15"):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "python-next.yml").write_text(
        "jobs:\n  tests:\n    steps:\n      - uses: actions/setup-python@v6\n"
        f"        with:\n          python-version: \"{версия}\"\n"
        "          allow-prereleases: true\n", encoding="utf-8")
    return tmp_path


def _манифест(tmp_path, записи) -> str:
    путь = tmp_path / "manifest.json"
    путь.write_text(json.dumps(записи), encoding="utf-8")
    return str(путь)


def test_сегодня_сходится():
    assert pn.расхождения((3, 15), СЕГОДНЯ) == []


def test_вышла_стабильной_называет_следующую_ветку():
    """Предмет 203: пометка «предрелиз» устарела от события в CPython."""
    найдено = pn.расхождения((3, 15), ВЫШЛА)
    assert len(найдено) == 1
    assert "3.15 уже стабильна" in найдено[0] and "навести python-next на 3.16" in найдено[0]


def test_вышла_а_следующей_ещё_нет():
    манифест = [{"version": "3.15.0", "stable": True}]
    assert "следующей предрелизной ветки у площадки пока нет" in pn.расхождения((3, 15), манифест)[0]


def test_предрелизная_у_площадки_новее():
    манифест = [*СЕГОДНЯ, {"version": "3.16.0-alpha.1", "stable": False}]
    assert pn.расхождения((3, 15), манифест) == [
        "предрелизная у площадки уже 3.16, а python-next держит 3.15"]


def test_ветки_которой_площадка_не_знает():
    assert "площадка такой ветки не знает" in pn.расхождения((3, 99), СЕГОДНЯ)[0]


def test_непонятные_записи_пропускаются_а_не_роняют():
    манифест = [*СЕГОДНЯ, "строка", {"version": "pypy3.10"}, {"stable": True}]
    assert pn.расхождения((3, 15), манифест) == []


def test_нет_стабильной_ветки_третий_исход(tmp_path):
    корень = _прогон(tmp_path)
    манифест = _манифест(tmp_path, [{"version": "3.15.0-rc.2", "stable": False}])
    assert pn.main(["--root", str(корень), "--manifest", манифест]) == 2


def test_пустой_манифест_третий_исход(tmp_path):
    корень = _прогон(tmp_path)
    assert pn.main(["--root", str(корень), "--manifest", _манифест(tmp_path, [])]) == 2


def test_нет_предрелизного_прогона_третий_исход(tmp_path):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    assert pn.main(["--root", str(tmp_path), "--manifest", _манифест(tmp_path, СЕГОДНЯ)]) == 2


def test_исходы_0_и_1(tmp_path, capsys):
    корень = _прогон(tmp_path)
    assert pn.main(["--root", str(корень), "--manifest", _манифест(tmp_path, СЕГОДНЯ)]) == 0
    assert pn.main(["--root", str(корень), "--manifest", _манифест(tmp_path, ВЫШЛА)]) == 1
    assert "--apply не задан" in capsys.readouterr().out


def test_настоящее_дерево_на_снимке_сходится(tmp_path):
    assert pn.main(["--root", str(SCRIPTS.parent),
                    "--manifest", _манифест(tmp_path, СЕГОДНЯ)]) == 0


def test_задача_находится_своим_маркером_а_не_дежурного(monkeypatch):
    """find_issue принимал маркер и не читал его: сверка нашла бы задачу
    дежурного по красной ветке и переписала бы её тело (214)."""
    задачи = [{"number": 7, "body": main_red.MARKER},
              {"number": 9, "body": pn.MARKER + "\nтекст"}]
    monkeypatch.setattr(main_red.ghcli, "список", lambda *a, **k: (0, задачи, ""))
    assert main_red.find_issue(pn.MARKER) == (9, None)
    assert main_red.find_issue() == (7, None)


def test_запись_обновляет_найденную_и_заводит_новую(monkeypatch):
    вызовы: list[tuple[str, ...]] = []
    monkeypatch.setattr(pn.ghcli, "run", lambda *a: (вызовы.append(a), (0, "ok"))[1])
    monkeypatch.setattr(pn.main_red, "find_issue", lambda m: (9, None))
    assert pn.записать("тело") == (1, "задача #9 обновлена")
    assert "PATCH" in вызовы[-1]
    monkeypatch.setattr(pn.main_red, "find_issue", lambda m: (None, None))
    assert pn.записать("тело") == (1, "задача заведена")
    assert f"title={pn.TITLE}" in вызовы[-1]


def test_трекер_не_ответил_третий_исход(monkeypatch):
    monkeypatch.setattr(pn.main_red, "find_issue", lambda m: (None, "403"))
    код, что = pn.записать("тело")
    assert код == 2 and "403" in что


@pytest.mark.parametrize("находки", [["одна"], ["одна", "две"]])
def test_тело_несёт_маркер_и_источник(находки):
    текст = pn.тело(находки, "https://прогон")
    assert текст.startswith(pn.MARKER)
    assert pn.MANIFEST_URL in текст and all(f"- {н}" in текст for н in находки)
