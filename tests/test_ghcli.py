"""Один вызов `gh` на весь каталог: отсутствие инструмента — третий исход.

Помощник был у четырёх скриптов, и все четыре написали его по-своему: два
падали трассировкой, третий возвращал код 2 — занятый у самого `gh`, —
четвёртый отдавал 127. Расхождение не косметическое: у потребителя действие
каталога разбирает код возврата, и 1 означает «очередь, всё в порядке».
Скрипт без `gh` умирал и отдавал 1 — механизм не работал ВООБЩЕ и рапортовал
успех (правило 075).

Здесь проверяется и сам помощник, и то, ради чего он заведён: **все четыре
скрипта отдают ровно 2**, когда `gh` нет. Случай стоит для каждого отдельно,
а не для одного «представителя»: расходились они именно поодиночке.
"""

from __future__ import annotations

import pytest

import ghcli


@pytest.fixture(autouse=True)
def свежий_замер(monkeypatch):
    """Замер квоты держится один на процесс, и это состояние МОДУЛЯ. Между
    случаями его надо сбрасывать: иначе второй случай читает ответ первого, и
    набор проверяет не то, что написано (149 — площадку набор забирает себе)."""
    monkeypatch.setattr(ghcli, "_замер", None)


def no_gh(monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError(2, "No such file or directory", "gh")
    monkeypatch.setattr(ghcli.subprocess, "run", boom)


# ── сам помощник ───────────────────────────────────────────────────────────

def test_нет_инструмента_это_свой_код(monkeypatch):
    no_gh(monkeypatch)
    code, why = ghcli.run("issue", "list")
    assert code == ghcli.NO_GH and "gh" in why


def test_код_отсутствия_не_совпадает_с_кодами_gh():
    """Совпади он с 1 или 2 — «инструмента нет» снова стало бы находкой."""
    assert ghcli.NO_GH not in (0, 1, 2)


def test_причина_называется_целиком(monkeypatch):
    no_gh(monkeypatch)
    _, why = ghcli.run("x")
    assert "не должен зеленеть" in why


def test_обычный_отказ_gh_отсутствием_не_считается(monkeypatch):
    """Здоровый предмет у границы: gh есть и вернул 1 — это находка, не сбой.

    К сообщению теперь приписан факт о квоте (017), и здесь он не измерился:
    подделка отвечает единицей и на rate_limit тоже. Это ЗАКОННЫЙ исход и он
    не превращает находку в исчерпание — неизмеренное не выдаётся за нулевое.
    """
    class Done:
        returncode, stdout, stderr = 1, "", "нет такой задачи"
    monkeypatch.setattr(ghcli.subprocess, "run", lambda *a, **k: Done())
    code, out = ghcli.run("issue", "view", "1")
    assert code == 1 and not ghcli.failed(code)
    assert out.startswith("нет такой задачи")
    assert "остаток не измерен" in out


def test_успех_проходит(monkeypatch):
    class Done:
        returncode, stdout, stderr = 0, "[]", ""
    monkeypatch.setattr(ghcli.subprocess, "run", lambda *a, **k: Done())
    assert ghcli.run("issue", "list") == (0, "[]")


# ── ради чего заведён: четыре скрипта, четыре отдельных случая ────────────

@pytest.mark.parametrize("module,argv", [
    ("sync_inbox", ["--bindings", "нет-такого.json"]),
    ("collect_proposals", []),
    ("sync_labels", ["--repo", "o/r"]),
    ("main_red", []),
])
def test_без_инструмента_скрипт_отдаёт_третий_исход(module, argv, monkeypatch, tmp_path):
    """1 у потребителя означает «очередь, всё в порядке» — отдавать его нельзя."""
    import importlib
    mod = importlib.import_module(module)
    no_gh(monkeypatch)
    monkeypatch.setenv("GH_TOKEN", "x")
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setattr("sys.argv", [f"{module}.py", *argv])
    assert mod.main() == 2


# ── правила 017 и 058: квота мерится, исчерпание останавливает ─────────────

class Ответ:
    """Подделка ответа subprocess. Подделка нарочная и с источником: форма
    снята с живого ответа `gh api rate_limit` (170)."""

    def __init__(self, code: int, out: str = "", err: str = ""):
        self.returncode, self.stdout, self.stderr = code, out, err


КВОТА_ЕСТЬ = ('{"resources":{"core":{"remaining":4980,"limit":5000},'
              '"graphql":{"remaining":4900,"limit":5000},'
              '"search":{"remaining":30,"limit":30}}}')
КВОТА_ПУСТА = ('{"resources":{"core":{"remaining":0,"limit":5000},'
               '"graphql":{"remaining":4900,"limit":5000}}}')


def подменить(monkeypatch, ответы):
    """Отдаёт ответы по порядку вызовов: сперва рабочая команда, потом
    rate_limit."""
    очередь = list(ответы)
    monkeypatch.setattr(ghcli, "_замер", None)

    def поддельный(argv, **kw):
        return очередь.pop(0)

    monkeypatch.setattr(ghcli.subprocess, "run", поддельный)


def test_ostatok_razbiraetsya_po_schetchikam(monkeypatch):
    подменить(monkeypatch, [Ответ(0, КВОТА_ЕСТЬ)])
    факт, пусто = ghcli.остаток()
    assert "core 4980/5000" in факт and "graphql 4900/5000" in факт
    assert пусто is False


def test_nulevoy_schetchik_eto_ischerpanie(monkeypatch):
    подменить(monkeypatch, [Ответ(0, КВОТА_ПУСТА)])
    _, пусто = ghcli.остаток()
    assert пусто is True


def test_neizmerennoe_ne_vydayotsya_za_izmerennoe(monkeypatch):
    """ГРАНИЦА: подставить ноль вместо неизмеренного значило бы выдать гипотезу
    за факт (037). Говорится «не измерен», и это не считается исчерпанием."""
    подменить(monkeypatch, [Ответ(1, "", "boom")])
    факт, пусто = ghcli.остаток()
    assert "не измерен" in факт and пусто is False


def test_pri_otkaze_snachala_fakt_o_kvote(monkeypatch):
    """ГЛАВНЫЙ СЛУЧАЙ 017: диагностика начинается с фактов, а не с гипотез —
    остаток спрашивается при первом же отказе, без решения «похоже ли»."""
    подменить(monkeypatch, [Ответ(1, "", "not found"), Ответ(0, КВОТА_ЕСТЬ)])
    код, вывод = ghcli.run("issue", "view", "999999")
    assert код == 1
    assert "остаток квоты: core 4980/5000" in вывод


def test_ischerpanie_eto_svoy_terminalnyy_kod(monkeypatch):
    """ГЛАВНЫЙ СЛУЧАЙ 058: до этого gh отдавал 1, и «лимит кончился» было
    неотличимо от «ничего не нашлось» — вызывающий шёл дальше."""
    подменить(monkeypatch,
              [Ответ(1, "", "API rate limit exceeded"), Ответ(0, КВОТА_ПУСТА)])
    код, _ = ghcli.run("issue", "list")
    assert код == ghcli.QUOTA_OUT
    assert ghcli.failed(код)


def test_otkaz_bez_ischerpaniya_ostayotsya_nahodkoy(monkeypatch):
    """Обратная половина: живой отказ — находка, и выдавать её за исчерпание
    нельзя, иначе работа встанет там, где встать не должна (051)."""
    подменить(monkeypatch, [Ответ(1, "", "not found"), Ответ(0, КВОТА_ЕСТЬ)])
    код, _ = ghcli.run("issue", "view", "999999")
    assert not ghcli.failed(код)


def test_zamer_derzhitsya_odin_na_protsess(monkeypatch):
    """«Смотреть первым шагом» не значит «смотреть на каждом»: цена ограничена
    одним лишним вызовом, а следующим отказам факт отдаётся с отметкой."""
    подменить(monkeypatch, [Ответ(1, "", "not found"), Ответ(0, КВОТА_ЕСТЬ),
                            Ответ(1, "", "not found")])
    ghcli.run("issue", "view", "1")
    _, вывод = ghcli.run("issue", "view", "2")
    assert "замер этого процесса" in вывод

