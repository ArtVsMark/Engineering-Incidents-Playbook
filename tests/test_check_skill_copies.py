"""Копия навыка каталога у потребителя: совпадает, расходится, или сверять нечего.

Подделка — настоящие деревья тех форм, которые читает скрипт: каталог с
плагином и проект с `.claude/skills/`. Сети у проверки нет по построению —
эталон лежит в дереве, из которого она запущена.
"""

from __future__ import annotations

from pathlib import Path

import check_skill_copies as csc
from conftest import write

НАВЫК = "---\nname: answer-a-rule\ndescription: Звать, когда отвечают.\n---\n\n# Навык\n"


def каталог(root: Path) -> Path:
    корень = root / "cat"
    write(корень / "plugins/catalogue/skills/answer-a-rule/SKILL.md", НАВЫК)
    return корень


def прогон(repo: Path, *ключи: str) -> int:
    return csc.main(["--repo", str(repo / "proj"),
                     "--catalogue-root", str(repo / "cat"), *ключи])


def сверка(repo: Path, *имена: str) -> int:
    """Сверка с объявленным списком — так её зовёт действие."""
    return прогон(repo, "--skills", *(имена or ("answer-a-rule",)))


def test_совпадающая_копия_чиста(repo, capsys):
    каталог(repo)
    write(repo / "proj/.claude/skills/answer-a-rule/SKILL.md", НАВЫК)
    assert сверка(repo) == 0
    assert "совпадают с каталогом: 1 — answer-a-rule" in capsys.readouterr().out


def test_правка_копии_это_находка_с_номером_строки(repo, capsys):
    """Замер 01.10: у проекта механизмов копия разошлась с третьей строки."""
    каталог(repo)
    write(repo / "proj/.claude/skills/answer-a-rule/SKILL.md",
          НАВЫК.replace("Звать, когда отвечают.", "Своё описание."))
    assert сверка(repo) == 1
    out = capsys.readouterr().out
    assert "SKILL.md расходится с каталогом, первая разная строка 3" in out
    assert "kind: skill" in out


def test_лишний_файл_в_копии_это_находка(repo, capsys):
    каталог(repo)
    write(repo / "proj/.claude/skills/answer-a-rule/SKILL.md", НАВЫК)
    write(repo / "proj/.claude/skills/answer-a-rule/notes.md", "своё\n")
    assert сверка(repo) == 1
    assert "лишний файл notes.md" in capsys.readouterr().out


def test_чужой_навык_проекта_не_копия(repo, capsys):
    """Объявление копии — список: свой навык, не названный в нём, не сверяется."""
    каталог(repo)
    write(repo / "proj/.claude/skills/answer-a-rule/SKILL.md", НАВЫК)
    write(repo / "proj/.claude/skills/build-a-gate/SKILL.md", "своё\n")
    assert сверка(repo) == 0


def test_без_списка_это_третий_исход(repo, capsys):
    """Без списка объявлением была бы папка, а по ней пропажа копии не видна."""
    каталог(repo)
    write(repo / "proj/.claude/skills/answer-a-rule/SKILL.md", НАВЫК)
    assert прогон(repo) == 2
    assert "список --skills" in capsys.readouterr().err


def test_пустой_список_это_третий_исход_а_не_зелёное(repo, capsys):
    """Находка ревью #638: `--skills` без имён давал «совпадают: 0» (075)."""
    каталог(repo)
    write(repo / "proj/.claude/skills/answer-a-rule/SKILL.md", НАВЫК)
    assert прогон(repo, "--skills") == 2
    assert "не назван ни один навык" in capsys.readouterr().err


def test_удалённая_копия_из_нескольких_это_находка(repo, capsys):
    """Находка ревью #638: при двух копиях удаление одной проходило зелёным."""
    корень = каталог(repo)
    write(корень / "plugins/catalogue/skills/second/SKILL.md",
          НАВЫК.replace("answer-a-rule", "second"))
    write(repo / "proj/.claude/skills/answer-a-rule/SKILL.md", НАВЫК)
    assert сверка(repo, "answer-a-rule", "second") == 1
    assert "second: копии нет" in capsys.readouterr().out


def test_навык_удалённый_в_каталоге_не_выпадает_молча(repo, capsys):
    """Находка ревью #638: копия навыка, которого у каталога больше нет."""
    каталог(repo)
    write(repo / "proj/.claude/skills/old-name/SKILL.md", "было\n")
    assert сверка(repo, "old-name") == 2
    assert "удалён или переименован" in capsys.readouterr().err


def test_названная_копия_которой_нет_это_находка(repo, capsys):
    каталог(repo)
    (repo / "proj").mkdir()
    assert прогон(repo, "--skills", "answer-a-rule") == 1
    assert "копии нет" in capsys.readouterr().out


def test_неизвестное_имя_это_третий_исход(repo, capsys):
    каталог(repo)
    (repo / "proj").mkdir()
    assert прогон(repo, "--skills", "нет-такого") == 2
    assert "нет навыков нет-такого" in capsys.readouterr().err


def test_каталог_без_навыков_это_третий_исход(repo, capsys):
    (repo / "cat").mkdir()
    (repo / "proj").mkdir()
    assert сверка(repo) == 2
    assert "сверять не с чем" in capsys.readouterr().err


def test_apply_кладёт_копию_и_она_сверяется_чистой(repo, capsys):
    каталог(repo)
    write(repo / "proj/.claude/skills/answer-a-rule/old.md", "устаревшее\n")
    assert прогон(repo, "--apply", "answer-a-rule") == 0
    копия = repo / "proj/.claude/skills/answer-a-rule"
    assert (копия / "SKILL.md").read_text(encoding="utf-8") == НАВЫК
    assert not (копия / "old.md").exists()
    assert сверка(repo) == 0


def test_apply_неизвестного_имени_ничего_не_пишет(repo, capsys):
    каталог(repo)
    (repo / "proj").mkdir()
    assert прогон(repo, "--apply", "нет-такого") == 2
    assert not (repo / "proj/.claude").exists()


def test_эталон_по_умолчанию_дерево_самого_каталога():
    """Без --catalogue-root сверка идёт с деревом, откуда запущен скрипт."""
    assert "answer-a-rule" in csc.навыки_каталога(csc.ROOT)
