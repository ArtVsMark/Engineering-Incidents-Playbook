"""Полнота необязательного поля переносимости.

Поле `**Переносится вне Claude Code.**` заполнять не обязаны — задним числом
его не проставляют. Но заполненное проверяется на ПОЛНОТУ, а не на непустоту
(правило 128): «частично» без причины выглядит осторожным ответом и не
сообщает ничего, а через месяц его нечем ни проверить, ни оспорить.

Второе, что здесь держится, — паритет деревьев. Деревья расходятся именно так:
не целой записью, а одним полем, добавленным на одной стороне.

Набор двусторонний, и здоровые предметы взяты у границы: запись БЕЗ поля обязана
проходить, иначе необязательное поле станет обязательным молча.
"""

from __future__ import annotations

from pathlib import Path

import audit_catalogue as ac
from conftest import write

RU = "# Правило\n\n**Область.** процесс\n\n**Правило.** Что-то.\n\n{f}## Инцидент\n\nБыло.\n"
EN = "# A rule\n\n**Area.** process\n\n**The rule.** Something.\n\n{f}## The incident\n\nHappened.\n"
P_RU = "**Переносится вне Claude Code.** да — не зависит от площадки.\n\n"
P_EN = "**Portable beyond Claude Code.** yes — platform-independent.\n\n"


def slot(repo: Path, ru: str, en: str) -> dict:
    return {"ru": write(repo / "ru.md", ru), "en": write(repo / "en.md", en)}


# ── здоровые предметы ──────────────────────────────────────────────────────

def test_записи_без_поля_проходят(repo):
    assert ac.check_portable("001", slot(repo, RU.format(f=""), EN.format(f=""))) == []


def test_поле_с_причиной_проходит(repo):
    assert ac.check_portable("001", slot(repo, RU.format(f=P_RU), EN.format(f=P_EN))) == []


def test_частично_с_причиной_проходит(repo):
    assert ac.check_portable("001", slot(
        repo,
        RU.format(f="**Переносится вне Claude Code.** частично — приём да, лекарство нет.\n\n"),
        EN.format(f="**Portable beyond Claude Code.** partly — device yes, remedy no.\n\n"))) == []


def test_одно_дерево_отсутствует_паритет_не_судится(repo):
    """Расхождение по составу файлов — предмет сборки указателя, не этой проверки."""
    only = {"ru": write(repo / "ru.md", RU.format(f=P_RU)), "en": None}
    assert ac.check_portable("001", only) == []


# ── предметы, которые проверка обязана отвергнуть ──────────────────────────

def test_поле_только_в_одном_дереве_это_находка(repo):
    out = ac.check_portable("001", slot(repo, RU.format(f=P_RU), EN.format(f="")))
    assert out and "только в дереве ru" in out[0]


def test_значение_вне_набора_это_находка(repo):
    out = ac.check_portable("001", slot(
        repo,
        RU.format(f="**Переносится вне Claude Code.** наверное — кто знает.\n\n"),
        EN.format(f=P_EN)))
    assert out and "вне набора" in out[0]


def test_ответ_без_причины_это_находка(repo):
    out = ac.check_portable("001", slot(
        repo,
        RU.format(f="**Переносится вне Claude Code.** частично\n\n"),
        EN.format(f=P_EN)))
    assert out and "без причины" in out[0]
