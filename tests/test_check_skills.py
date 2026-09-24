"""Навыки окна: список сходится с деревом, у навыка форма заготовки.

Случаи спрашивают ГЕЙТ через `main()` на поддельном дереве, а не его функции:
разбор, проверенный отдельно, ничего не говорит о том, доедет ли находка до
отказа (правило 150). Подделка нарочно маленькая — один навык, одна заготовка
с двумя разделами, — чтобы «отверг» означало «отверг именно это».

Последний случай идёт по НАСТОЯЩЕМУ дереву и полным разбором YAML: гейт
читает заголовок узким разбором без библиотеки (её нет в шаге конвейера), а
площадка — настоящим. Расхождение двух прочтений видно только так.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import check_skills as cs
from conftest import write

ЗАГОТОВКА = """# Навык

```markdown
---
name: <имя>
description: <когда звать>
---

# <Заголовок>

> **Читатель:** <кто зовёт>

## Зачем это существует

## Чего навык НЕ делает
```
"""

СПИСОК = """# Навыки

> **Читатель:** участник — какие навыки есть у окна и как их звать.

| Навык | Когда |
|---|---|
| `triage` | когда что-то покраснело |
"""

НАВЫК = """---
name: triage
description: Звать, когда общая ветка покраснела.
---

# Первичный разбор

> **Читатель:** агент — окно, у которого покраснело.

## Зачем это существует

Инцидент.

## Чего навык НЕ делает

Не краснеет.
"""


def подделка(repo: Path, список: str = СПИСОК, навык: str = НАВЫК,
             заготовка: str = ЗАГОТОВКА, имя: str = "triage") -> Path:
    write(repo / "templates" / "skill-template.md", заготовка)
    write(repo / ".claude" / "skills" / "README.md", список)
    write(repo / ".claude" / "skills" / имя / "SKILL.md", навык)
    return repo


def прогон(repo: Path) -> int:
    return cs.main(["--root", str(repo)])


def test_vsyo_na_meste(repo, capsys):
    assert прогон(подделка(repo)) == 0
    assert "в списке 1, в дереве 1" in capsys.readouterr().out


def test_nazvan_a_kataloga_net_eto_otkaz(repo, capsys):
    подделка(repo, список=СПИСОК + "| `postmortem` | после починки |\n")
    assert прогон(repo) == 1
    assert "postmortem" in capsys.readouterr().err


def test_est_a_v_spiske_ne_nazvan_eto_otkaz(repo, capsys):
    """Ровно тот случай, ради которого гейт заведён: навык в дереве, о котором
    не знает никто, кроме площадки."""
    подделка(repo)
    write(repo / ".claude" / "skills" / "review" / "SKILL.md",
          НАВЫК.replace("name: triage", "name: review"))
    assert прогон(repo) == 1
    assert "review есть" in capsys.readouterr().err


def test_dvazhdy_nazvannyy_eto_otkaz(repo, capsys):
    подделка(repo, список=СПИСОК + "| `triage` | ещё раз |\n")
    assert прогон(repo) == 1
    assert "дважды" in capsys.readouterr().err


def test_imya_ne_sovpadaet_s_katalogom_eto_otkaz(repo, capsys):
    подделка(repo, навык=НАВЫК.replace("name: triage", "name: incident-triage"))
    assert прогон(repo) == 1
    assert "incident-triage" in capsys.readouterr().err


@pytest.mark.parametrize("пустое", ["description:", "description: >-", "description: ''"])
def test_pustoe_opisanie_eto_otkaz(repo, capsys, пустое):
    """Разбор заголовка — у check_bindings; здесь проверяется, что его находка
    доезжает до отказа ЭТОГО гейта, в том числе на блочном скаляре."""
    подделка(repo, навык=НАВЫК.replace(
        "description: Звать, когда общая ветка покраснела.", пустое))
    assert прогон(repo) == 1
    assert "description" in capsys.readouterr().err


def test_razdela_zagotovki_net_eto_otkaz(repo, capsys):
    подделка(repo, навык=НАВЫК.replace("## Чего навык НЕ делает", "## Прочее"))
    assert прогон(repo) == 1
    assert "## Чего навык НЕ делает" in capsys.readouterr().err


def test_razdely_berutsya_iz_zagotovki_a_ne_iz_skripta(repo, capsys):
    """Заготовка потребовала третий раздел — навык без него отвергается, хотя
    в гейте о нём ни слова (155: канон один, и он в заготовке)."""
    подделка(repo, заготовка=ЗАГОТОВКА.replace(
        "## Чего навык НЕ делает", "## Что сделать\n\n## Чего навык НЕ делает"))
    assert прогон(repo) == 1
    assert "## Что сделать" in capsys.readouterr().err


@pytest.mark.parametrize("строка", [
    "",
    "> **Читатель:** прохожий — кто-то.",
    "> **Читатель:** агент —",
])
def test_chitatel_navyka_ne_nazvan_eto_otkaz(repo, capsys, строка):
    подделка(repo, навык=НАВЫК.replace(
        "> **Читатель:** агент — окно, у которого покраснело.", строка))
    assert прогон(repo) == 1
    assert "Читатель" in capsys.readouterr().err


def test_chitatel_spiska_ne_nazvan_eto_otkaz(repo, capsys):
    подделка(repo, список=СПИСОК.replace(
        "> **Читатель:** участник — какие навыки есть у окна и как их звать.\n", ""))
    assert прогон(repo) == 1
    assert "README.md: не назван читатель" in capsys.readouterr().err


def test_tablitsa_putey_strokoy_spiska_ne_schitaetsya(repo):
    """В том же документе законно стоят таблицы с путями и командами: они не
    навыки, и ложный отказ на них приучил бы читать красное как фон."""
    подделка(repo, список=СПИСОК + "\n| Файл | Что |\n|---|---|\n"
                                   "| `scripts/check_skills.py` | гейт |\n")
    assert прогон(repo) == 0


def test_net_kataloga_navykov_eto_tretiy_ishod(repo, capsys):
    write(repo / "templates" / "skill-template.md", ЗАГОТОВКА)
    assert прогон(repo) == 2
    assert ".claude/skills" in capsys.readouterr().err


def test_net_spiska_eto_tretiy_ishod(repo, capsys):
    подделка(repo)
    (repo / ".claude" / "skills" / "README.md").unlink()
    assert прогон(repo) == 2
    assert "README.md" in capsys.readouterr().err


def test_spisok_ne_razobralsya_eto_tretiy_ishod(repo, capsys):
    """Ноль строк — ошибка разбора, а не пустой список (075)."""
    подделка(repo, список="# Навыки\n\n> **Читатель:** участник — навыки.\n\nодна проза\n")
    assert прогон(repo) == 2
    assert "не разобралось" in capsys.readouterr().err


def test_zagotovka_bez_formy_eto_tretiy_ishod(repo, capsys):
    подделка(repo, заготовка="# Навык\n\nформы нет, одна проза\n")
    assert прогон(repo) == 2
    assert "skill-template.md" in capsys.readouterr().err


def test_nastoyashchie_navyki_chitayutsya_polnym_razborom():
    """Живой предмет, а не подделка: каждый навык дерева разбирается PyYAML так
    же, как его прочтёт площадка, и прочтение сходится с узким разбором гейта."""
    folder = cs.ROOT / cs.SKILLS
    навыки = sorted(p for p in folder.iterdir() if p.is_dir())
    assert навыки, f"в {folder} нет ни одного навыка — проверять нечего (075)"
    for каталог in навыки:
        текст = (каталог / "SKILL.md").read_text(encoding="utf-8")
        голова = текст.split("---", 2)[1]
        поля = yaml.safe_load(голова)
        assert поля["name"] == каталог.name
        assert isinstance(поля["description"], str) and поля["description"].strip()
