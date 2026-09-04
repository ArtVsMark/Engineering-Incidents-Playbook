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

RELEASE = """## v1.0.0 · 27 августа 2026 · конвейер стал автором

**Контекст.** Замер показал перекос: правила рождались в других проектах.

**Что вошло.** Номер присуждается здесь — задача
[#91](https://github.com/o/r/issues/91).

**Решения.** Раздавать номера в проектах отвергнуто: займут один.

**Итог.** Каталог перестал быть складом.
"""


def history(root: Path, text: str) -> Path:
    return write(root / "docs" / "HISTORY.md", text)
RU = "# Правило\n\n**Область.** процесс\n\n**Правило.** Что-то.\n\n{f}## Инцидент\n\nБыло.\n"
EN = "# A rule\n\n**Area.** process\n\n**The rule.** Something.\n\n{f}## The incident\n\nHappened.\n"
P_RU = "**Переносится вне Claude Code.** да — не зависит от площадки.\n\n"
P_EN = "**Portable beyond Claude Code.** yes — platform-independent.\n\n"


def slot(repo: Path, ru: str, en: str) -> dict:
    return {"ru": write(repo / "ru.md", ru), "en": write(repo / "en.md", en)}


# ── здоровые предметы ──────────────────────────────────────────────────────

def test_раздел_выпуска_по_форме_проходит(repo):
    history(repo, RELEASE)
    assert ac.check_history(repo) == []


def test_документа_нет_это_не_находка(repo):
    assert ac.check_history(repo) == []


def test_незакрытый_выпуск_проверяется_той_же_меркой(repo):
    """До тега раздел живёт под «Не выпущено» и формы не теряет."""
    history(repo, RELEASE.replace("## v1.0.0 · 27 августа 2026 ·", "## Не выпущено ·"))
    assert ac.check_history(repo) == []


def test_ссылка_задачей_без_адреса_тоже_разрешается(repo):
    history(repo, RELEASE.replace("[#91](https://github.com/o/r/issues/91)", "o/r#91"))
    assert ac.check_history(repo) == []


def test_образец_формы_в_заборе_кода_находкой_не_считается(repo):
    """Предмет у самой границы: критерий описывает форму и сам ей не следует."""
    history(repo, "# История\n\n```\n" + RELEASE.replace(
        "конвейер стал автором", "<чем этот выпуск был>") + "```\n" + RELEASE)
    assert ac.check_history(repo) == []


def test_обычные_разделы_истории_выпусками_не_считаются(repo):
    history(repo, "# История\n\n## Как он появился\n\nтекст без разделов\n")
    assert ac.check_history(repo) == []


# ── предметы, которые гейт обязан отвергнуть ───────────────────────────────

def test_раздел_без_решений_это_находка(repo):
    history(repo, RELEASE.replace("**Решения.**", "**Что ещё думали.**"))
    out = ac.check_history(repo)
    assert out and "Решения" in out[0]


def test_раздел_без_итога_это_находка(repo):
    history(repo, RELEASE.replace("**Итог.**", "**Хвост.**"))
    assert any("Итог" in p for p in ac.check_history(repo))


def test_что_вошло_без_ссылки_это_находка(repo):
    history(repo, RELEASE.replace(
        "Номер присуждается здесь — задача\n[#91](https://github.com/o/r/issues/91).",
        "Из этого много чего выросло."))
    out = ac.check_history(repo)
    assert out and "рассказом" in out[0]


def test_ссылка_в_итоге_вместо_что_вошло_не_спасает(repo):
    """Граница спроса названа: ссылка живёт там, где перечислено вошедшее.

    В «Итоге» ссылке делать нечего — он про смысл, а не про артефакт, и
    зачёт ссылки где угодно превратил бы проверку в поиск ссылки по разделу.
    """
    history(repo, RELEASE.replace(
        "Номер присуждается здесь — задача\n[#91](https://github.com/o/r/issues/91).",
        "Номер присуждается здесь.").replace(
        "**Итог.** Каталог перестал быть складом.",
        "**Итог.** Склад кончился — [#91](https://github.com/o/r/issues/91)."))
    out = ac.check_history(repo)
    assert out and "рассказом" in out[0]


def test_второй_выпуск_проверяется_отдельно_от_первого(repo):
    history(repo, RELEASE + "\n" + RELEASE.replace(
        "## v1.0.0 · 27 августа 2026 · конвейер стал автором",
        "## v1.1.0 · 28 августа 2026 · контракт с потребителями").replace(
        "**Решения.** Раздавать номера в проектах отвергнуто: займут один.\n\n", ""))
    out = ac.check_history(repo)
    assert len(out) == 1 and "v1.1.0" in out[0]


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


# ── предел, выраженный числом (правило 108) ───────────────────────────────
#
# Растущий документ без предела перестаёт отвечать на вопрос «что было
# недавно» и не сообщает об этом. Гейт держит только СЧЁТ: дословность
# переноса в архив машинно не проверить, и это сказано в самом скрипте.

def releases(n: int) -> str:
    return "\n".join(RELEASE.replace("## v1.0.0 · 27 августа 2026 ·",
                                     f"## v2.{i}.0 · 1 сентября 2026 ·")
                     for i in range(n))


def test_окно_не_переполнено_проходит(repo):
    history(repo, releases(ac.HISTORY_WINDOW))
    assert ac.check_history(repo) == []


def test_переполненное_окно_это_находка(repo):
    history(repo, releases(ac.HISTORY_WINDOW + 1))
    out = ac.check_history(repo)
    assert out and "окно" in out[0]


def test_находка_называет_СТАРШИЕ_выпуски_поимённо(repo):
    """Не «слишком много», а что именно переносить — и с какого края."""
    history(repo, releases(ac.HISTORY_WINDOW + 2))
    out = [p for p in ac.check_history(repo) if "окно" in p]
    assert out
    assert "«v2.0.0»" in out[0] and "«v2.1.0»" in out[0]
    assert f"«v2.{ac.HISTORY_WINDOW + 1}.0»" not in out[0]


def test_находка_называет_куда_переносить(repo):
    history(repo, releases(ac.HISTORY_WINDOW + 1))
    out = [p for p in ac.check_history(repo) if "окно" in p]
    assert out and ac.HISTORY_ARCHIVE in out[0]


def test_предел_выражен_числом_а_не_наречием():
    """Само требование 108: предел ЧИСЛОМ. «Много» проверить нельзя."""
    assert isinstance(ac.HISTORY_WINDOW, int) and ac.HISTORY_WINDOW > 0
