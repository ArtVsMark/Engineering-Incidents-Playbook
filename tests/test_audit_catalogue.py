"""Поворотные моменты в HISTORY.md: форма и разрешимая ссылка.

`HISTORY.md` отвечает на «почему решили именно так», и до критерия он собирал
то, что вспомнилось. Здесь держится главное из критерия: **раздел
«Альтернативы» обязателен**. Решение без отвергнутой альтернативы — это не
решение, а ход работы, и ему место в журнале (правило 026). Второе —
«Во что превратилось» обязано вести в артефакт: без ссылки поворот остаётся
рассказом, ровно как правило без следа.

Набор двусторонний, и здоровые предметы взяты у границы: образец формы внутри
самого критерия лежит в заборе кода и находкой считаться не должен — иначе
гейт краснел бы на собственном описании.

ВТОРОЙ ПРЕДМЕТ НАБОРА — полнота необязательного поля переносимости.

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

TURN = """## Поворотный момент: номер присуждается здесь · 27 августа 2026

**Ситуация.** Замер показал перекос.

**Альтернативы.** Раздавать номера в проектах — отвергнуто, займут один.

**Решение.** Номер присуждается здесь.

**Во что превратилось.** Задача [#91](https://github.com/o/r/issues/91).
"""


def history(root: Path, text: str) -> Path:
    return write(root / "HISTORY.md", text)
RU = "# Правило\n\n**Область.** процесс\n\n**Правило.** Что-то.\n\n{f}## Инцидент\n\nБыло.\n"
EN = "# A rule\n\n**Area.** process\n\n**The rule.** Something.\n\n{f}## The incident\n\nHappened.\n"
P_RU = "**Переносится вне Claude Code.** да — не зависит от площадки.\n\n"
P_EN = "**Portable beyond Claude Code.** yes — platform-independent.\n\n"


def slot(repo: Path, ru: str, en: str) -> dict:
    return {"ru": write(repo / "ru.md", ru), "en": write(repo / "en.md", en)}


# ── здоровые предметы ──────────────────────────────────────────────────────

def test_поворот_по_форме_проходит(repo):
    history(repo, TURN)
    assert ac.check_history(repo) == []


def test_документа_нет_это_не_находка(repo):
    assert ac.check_history(repo) == []


def test_ссылка_задачей_без_адреса_тоже_разрешается(repo):
    history(repo, TURN.replace("[#91](https://github.com/o/r/issues/91)", "o/r#91"))
    assert ac.check_history(repo) == []


def test_образец_формы_в_заборе_кода_находкой_не_считается(repo):
    """Предмет у самой границы: критерий описывает форму и сам ей не следует."""
    history(repo, "# История\n\n```\n" + TURN.replace(
        "номер присуждается здесь", "<название>") + "```\n" + TURN)
    assert ac.check_history(repo) == []


def test_обычные_разделы_истории_поворотами_не_считаются(repo):
    history(repo, "# История\n\n## Как он появился\n\nтекст без разделов\n")
    assert ac.check_history(repo) == []


# ── предметы, которые гейт обязан отвергнуть ───────────────────────────────

def test_поворот_без_альтернатив_это_находка(repo):
    history(repo, TURN.replace("**Альтернативы.**", "**Что ещё думали.**"))
    out = ac.check_history(repo)
    assert out and "Альтернативы" in out[0]


def test_поворот_без_решения_это_находка(repo):
    history(repo, TURN.replace("**Решение.**", "**Итог.**"))
    assert any("Решение" in p for p in ac.check_history(repo))


def test_во_что_превратилось_без_ссылки_это_находка(repo):
    history(repo, TURN.replace("Задача [#91](https://github.com/o/r/issues/91).",
                               "Из этого много чего выросло."))
    out = ac.check_history(repo)
    assert out and "рассказом" in out[0]


def test_второй_поворот_проверяется_отдельно_от_первого(repo):
    history(repo, TURN + "\n" + TURN.replace(
        "номер присуждается здесь", "второй поворот").replace(
        "**Альтернативы.** Раздавать номера в проектах — отвергнуто, займут один.\n\n", ""))
    out = ac.check_history(repo)
    assert len(out) == 1 and "второй поворот" in out[0]
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
