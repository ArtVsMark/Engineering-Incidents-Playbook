"""Кандидаты в правила: граница с корпусом и три исхода.

Скрипт держит то, ради чего папка вообще опасна: `candidates/` — готовый обход
требования инцидента, и обход происходит СПОЛЗАНИЕМ, а не решением. Сперва на
кандидата ссылается правило, потом свод, потом никто не помнит, что это
гипотеза. Поэтому случай «правило сослалось на кандидата» стоит здесь наравне
с проверками формы, а не после них.

Набор двусторонний (правило 140 во второй редакции): рядом с каждым предметом,
который гейт обязан отвергнуть, стоит здоровый — и здоровые взяты у границы.
Пустая папка проверяется отдельно: это объявленное законное состояние, и гейт,
краснеющий на ней, был бы хуже отсутствующего.
"""

from __future__ import annotations

from pathlib import Path

import check_candidates as cc
from conftest import write

GOOD = """# Модель выбирается под задачу, а не берётся самая большая

**Область.** процесс

**Гипотеза.** Дешёвая модель на механической правке экономит бюджет окна.

## Источник

https://github.com/owner/other-project#12

## Предполагаемая причина

У них это описано как правило и, по-видимому, держится сознательно.

## Чем подтвердится

У нас кончится бюджет окна на механической работе, и цена будет названа.

## Применимость

**Работает**, по-видимому, там, где правка механическая.

**Не работает** там, где задача требует разбора.
"""


def prepare(root: Path, files: dict[str, str], rules: dict[str, str] | None = None):
    """Кладёт минимальное дерево: rules/ru обязательно, иначе исход 2."""
    write(root / "rules" / "ru" / "001-a.md", "# Правило\n")
    (root / "rules" / "en").mkdir(parents=True, exist_ok=True)
    for name, text in (rules or {}).items():
        write(root / "rules" / "ru" / name, text)
    for name, text in files.items():
        write(root / "candidates" / name, text)


def run(root: Path) -> int:
    return cc.main(["--root", str(root)])


# ── здоровые предметы: гейт обязан пропустить ──────────────────────────────

def test_кандидат_по_форме_проходит(repo, capsys):
    prepare(repo, {"model-per-task.md": GOOD})
    assert run(repo) == 0
    assert "в порядке" in capsys.readouterr().out


def test_пустая_папка_это_объявленное_состояние(repo, capsys):
    prepare(repo, {})
    assert run(repo) == 0
    assert "объявленное состояние" in capsys.readouterr().out


def test_папки_нет_вовсе_тоже_чисто(repo):
    write(repo / "rules" / "ru" / "001-a.md", "# Правило\n")
    (repo / "rules" / "en").mkdir(parents=True, exist_ok=True)
    assert run(repo) == 0


def test_readme_кандидатом_не_считается(repo):
    prepare(repo, {"README.md": "# как это устроено\n"})
    assert run(repo) == 0


def test_источник_задачей_тоже_разрешается(repo):
    prepare(repo, {"a.md": GOOD.replace("https://github.com/owner/other-project#12",
                                        "owner/repo#12")})
    assert run(repo) == 0


def test_правило_рядом_с_похожим_именем_ссылкой_не_считается(repo):
    """Здоровый предмет у самой границы: имя совпало, папка другая."""
    prepare(repo, {"a.md": GOOD},
            rules={"002-b.md": "# Правило\n\nСм. [соседа](001-a.md) и [a.md](../en/a.md).\n"})
    assert run(repo) == 0


# ── предметы, которые гейт обязан отвергнуть ───────────────────────────────

def test_ссылка_из_правила_на_кандидата_это_находка(repo, capsys):
    prepare(repo, {"a.md": GOOD},
            rules={"002-b.md": "# Правило\n\nСм. [гипотезу](../../candidates/a.md).\n"})
    assert run(repo) == 1
    assert "ссылается на кандидата" in capsys.readouterr().err


def test_номер_в_имени_это_находка(repo, capsys):
    prepare(repo, {"149-model-per-task.md": GOOD})
    assert run(repo) == 1
    assert "номера нет" in capsys.readouterr().err


def test_раздел_след_это_находка(repo, capsys):
    prepare(repo, {"a.md": GOOD + "\n## След\n\nowner/repo#1\n"})
    assert run(repo) == 1
    assert "притворяется правилом" in capsys.readouterr().err


def test_нет_строки_гипотезы_это_находка(repo, capsys):
    prepare(repo, {"a.md": GOOD.replace("**Гипотеза.**", "**Правило.**")})
    assert run(repo) == 1
    assert "Гипотеза" in capsys.readouterr().err


def test_нет_раздела_чем_подтвердится_это_находка(repo, capsys):
    prepare(repo, {"a.md": GOOD.replace("## Чем подтвердится", "## Заметки")})
    assert run(repo) == 1
    assert "Чем подтвердится" in capsys.readouterr().err


def test_пустой_обязательный_раздел_это_находка(repo, capsys):
    prepare(repo, {"a.md": GOOD.replace(
        "У нас кончится бюджет окна на механической работе, и цена будет названа.", "")})
    assert run(repo) == 1
    assert "пуст" in capsys.readouterr().err


def test_источник_прозой_это_находка(repo, capsys):
    prepare(repo, {"a.md": GOOD.replace("https://github.com/owner/other-project#12",
                                        "видел в каком-то проекте")})
    assert run(repo) == 1
    assert "не разрешается" in capsys.readouterr().err


def test_имя_не_по_форме_это_находка(repo, capsys):
    prepare(repo, {"Модель.md": GOOD})
    assert run(repo) == 1
    assert "не по форме" in capsys.readouterr().err


# ── третий исход ───────────────────────────────────────────────────────────

def test_нет_дерева_правил_это_третий_исход(repo, capsys):
    (repo / "candidates").mkdir(parents=True, exist_ok=True)
    assert run(repo) == 2
    assert "не отработала" in capsys.readouterr().err


# ── выгрузка гипотез: помечена, без номера, с «чем подтвердится» ───────────
#
# Гипотеза едет потребителям, чтобы её мог подтвердить ЧУЖОЙ инцидент. Вместе с
# ней уезжает и риск, ради которого написан этот гейт: у соседа нашей проверки
# нет, и там кандидат легче всего тихо станет правилом. Набор двусторонний
# (140) и стережёт именно то, что этому мешает.

def test_кандидат_в_выгрузке_помечен_гипотезой(repo, monkeypatch):
    import build_rules_index as bri
    prepare(repo, {"model-per-task.md": GOOD})
    monkeypatch.setattr(bri, "ROOT", repo)

    вышло = bri.candidates_export()

    assert len(вышло) == 1
    assert вышло[0]["kind"] == "hypothesis"
    assert вышло[0]["slug"] == "model-per-task"


def test_у_кандидата_в_выгрузке_нет_поля_номера(repo, monkeypatch):
    """Ни пустого, ни null.

    Пустой ключ той же формы, что у правила, есть приглашение его заполнить, а
    номер занимать нельзя: корпус состоит из инцидентов, и переиспользовать
    номера запрещено. Проверяется ОТСУТСТВИЕ ключа, а не его значение.
    """
    import build_rules_index as bri
    prepare(repo, {"model-per-task.md": GOOD})
    monkeypatch.setattr(bri, "ROOT", repo)

    запись = bri.candidates_export()[0]

    assert "id" not in запись
    assert not any(k for k in запись if "id" == k.lower() or k.endswith("_id"))


def test_чем_подтвердится_едет_вместе_с_гипотезой(repo, monkeypatch):
    """Без этого раздела гипотеза не подтвердится и не отвергнется.

    Она просто придаст уверенности самим фактом существования — и тем скорее,
    чем дальше от места, где её записали.
    """
    import build_rules_index as bri
    prepare(repo, {"model-per-task.md": GOOD})
    monkeypatch.setattr(bri, "ROOT", repo)

    запись = bri.candidates_export()[0]

    assert "кончится бюджет окна" in запись["confirmed_by"]
    assert "**Не работает**" in запись["applicability"]


def test_пустая_папка_даёт_пустой_список_а_не_отказ(repo, monkeypatch):
    """Кандидатов может не быть — это объявленное состояние (091)."""
    import build_rules_index as bri
    prepare(repo, {})
    monkeypatch.setattr(bri, "ROOT", repo)

    assert bri.candidates_export() == []
