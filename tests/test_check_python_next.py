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


@pytest.mark.parametrize("находки", [["одна"], ["одна", "две"]])
def test_тело_несёт_маркер_и_источник(находки):
    текст = pn.тело(находки, "https://прогон")
    assert текст.startswith(pn.MARKER)
    assert pn.MANIFEST_URL in текст and all(f"- {н}" in текст for н in находки)


class Трекер:
    """Подделка трекера: задачи по номеру, поиск по маркеру — тот же, что у
    main_red.find_issue (тело содержит маркер). Источник формы — REST
    /repos/{o}/{r}/issues: PATCH body/state, POST title/body/labels[]."""

    def __init__(self, задачи: dict[int, str] | None = None, *, лежит: bool = False):
        self.задачи = dict(задачи or {})
        self.закрытые: set[int] = set()
        self.лежит = лежит

    def find(self, marker):
        if self.лежит:
            return None, "HTTP 503"
        for n, body in self.задачи.items():
            if n not in self.закрытые and marker in body:
                return n, None
        return None, None

    def run(self, *args):
        if self.лежит:
            return 1, "HTTP 503"
        поля = dict(a.split("=", 1) for a in args if "=" in a and not a.startswith("repos/"))
        if "PATCH" in args:
            n = int(args[3].rsplit("/", 1)[1])
            if поля.get("state") == "closed":
                self.закрытые.add(n)
            else:
                self.задачи[n] = поля["body"]
        else:
            n = max(self.задачи, default=0) + 1
            self.задачи[n] = поля["body"]
        return 0, "ok"


@pytest.fixture
def трекер(monkeypatch):
    def завести(**kw):
        т = Трекер(**kw)
        monkeypatch.setattr(pn.main_red, "find_issue", т.find)
        monkeypatch.setattr(pn.ghcli, "run", т.run)
        return т
    return завести


def test_находка_заводит_задачу_и_обновляет_её(tmp_path, трекер):
    т = трекер()
    корень = _прогон(tmp_path)
    манифест = _манифест(tmp_path, ВЫШЛА)
    assert pn.main(["--root", str(корень), "--manifest", манифест, "--apply"]) == 1
    assert pn.main(["--root", str(корень), "--manifest", манифест, "--apply"]) == 1
    assert list(т.задачи) == [1] and т.задачи[1].startswith(pn.MARKER)


def test_отказ_сверки_уходит_в_свою_задачу_а_не_в_цвет(tmp_path, трекер):
    """Находка обзора #692: отказ краснил прогон дежурного. Код 2 — записано,
    прогон его красным не делает."""
    т = трекер()
    корень = _прогон(tmp_path)
    assert pn.main(["--root", str(корень), "--manifest", _манифест(tmp_path, []), "--apply"]) == 2
    (тело,) = т.задачи.values()
    assert тело.startswith(pn.MARKER_ОТКАЗ) and "пуст или не список" in тело


def test_отказ_не_перетирает_открытую_находку(tmp_path, трекер):
    """Находка обзора #693: маркер был общий, и разовый сбой источника
    переписывал тело открытого расхождения."""
    находка = pn.MARKER + "\n- python-next гоняет 3.15, а площадка такой ветки не знает"
    т = трекер(задачи={1: находка})
    корень = _прогон(tmp_path)
    assert pn.main(["--root", str(корень), "--manifest", _манифест(tmp_path, []), "--apply"]) == 2
    assert т.задачи[1] == находка
    assert т.задачи[2].startswith(pn.MARKER_ОТКАЗ)


def test_сверка_отработала_закрывает_задачу_отказа(tmp_path, трекер):
    """Находка обзора #693: задачу, заведённую чужим сбоем, не закрывал никто.
    Находку при этом не трогает — её закрывает человек."""
    т = трекер(задачи={1: pn.MARKER + "\nнаходка", 2: pn.MARKER_ОТКАЗ + "\nсбой"})
    корень = _прогон(tmp_path)
    assert pn.main(["--root", str(корень), "--manifest", _манифест(tmp_path, СЕГОДНЯ), "--apply"]) == 0
    assert т.закрытые == {2}


def test_трекер_не_ответил_при_отказе_код_3(tmp_path, трекер):
    """Находка обзора #693: «причина в задаче» печаталось, когда задачи не было.
    Код 3 — адресата нет, и прогон его различает."""
    трекер(лежит=True)
    корень = _прогон(tmp_path)
    assert pn.main(["--root", str(корень), "--manifest", _манифест(tmp_path, []),
                    "--apply"]) == pn.НЕТ_АДРЕСАТА


def test_трекер_не_ответил_при_находке_код_3(tmp_path, трекер):
    трекер(лежит=True)
    корень = _прогон(tmp_path)
    assert pn.main(["--root", str(корень), "--manifest", _манифест(tmp_path, ВЫШЛА),
                    "--apply"]) == pn.НЕТ_АДРЕСАТА


def test_отказ_без_apply_в_трекер_не_пишет(tmp_path, monkeypatch):
    корень = _прогон(tmp_path)
    monkeypatch.setattr(pn, "записать", lambda *a: pytest.fail("писать без --apply нельзя"))
    assert pn.main(["--root", str(корень), "--manifest", _манифест(tmp_path, [])]) == 2
