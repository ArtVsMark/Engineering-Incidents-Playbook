"""Фрагменты журнала: разбор, находки и порядок сборки.

Проверяется то, ради чего скрипт написан (правило 030): фрагмент с неверным
именем, пустой фрагмент и фрагмент с ведущим «-» — находки, а не мелочи. Пустой
особенно: файл, в котором ничего не написано, выглядит сделанной работой.
"""

from __future__ import annotations

from pathlib import Path

import collect_changelog as cc
from conftest import write


def prepare(monkeypatch, repo: Path, files: dict[str, str]) -> None:
    fragments = repo / "changelog.d"
    fragments.mkdir()
    for name, text in files.items():
        write(fragments / name, text)
    monkeypatch.setattr(cc, "FRAGMENTS", fragments)


def test_читает_годный_фрагмент(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.added.md": "Гейт покрытия (#1).\n"})
    found, problems = cc.validate()
    assert problems == []
    assert found["added"] == ["Гейт покрытия (#1)."]


def test_readme_фрагментом_не_считается(monkeypatch, repo):
    prepare(monkeypatch, repo, {"README.md": "как класть фрагменты"})
    found, problems = cc.validate()
    assert problems == []
    assert all(not lines for lines in found.values())


def test_имя_не_по_форме_это_находка(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.wontfix.md": "текст"})
    _, problems = cc.validate()
    assert len(problems) == 1
    # Отказ обязан называть предмет, а не только факт (правило 083).
    assert "gate.wontfix.md" in problems[0]
    assert "added" in problems[0]


def test_пустой_фрагмент_это_находка(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.added.md": "   \n"})
    found, problems = cc.validate()
    assert len(problems) == 1
    assert "gate.added.md" in problems[0]
    assert found["added"] == []


def test_ведущий_дефис_это_находка(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.added.md": "- уже со списком"})
    _, problems = cc.validate()
    assert len(problems) == 1
    assert "gate.added.md" in problems[0]


def test_перенос_строк_схлопывается(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.fixed.md": "длинная\nстрока   в   две"})
    found, _ = cc.validate()
    assert found["fixed"] == ["длинная строка в две"]


def test_секции_идут_объявленным_порядком(monkeypatch, repo):
    prepare(monkeypatch, repo, {
        "z.internal.md": "внутреннее",
        "a.fixed.md": "починка",
        "m.added.md": "новое",
    })
    found, problems = cc.validate()
    assert problems == []
    out = cc.render(found)
    assert out.index("Добавлено") < out.index("Починено") < out.index("Внутреннее")
    assert "- новое" in out


def test_записи_внутри_секции_отсортированы(monkeypatch, repo):
    prepare(monkeypatch, repo, {"b.added.md": "яблоко", "a.added.md": "апельсин"})
    found, _ = cc.validate()
    lines = [s for s in cc.render(found).splitlines() if s.startswith("- ")]
    assert lines == ["- апельсин", "- яблоко"]


def test_пустая_сборка_это_пустая_строка(monkeypatch, repo):
    prepare(monkeypatch, repo, {})
    found, _ = cc.validate()
    assert cc.render(found) == ""


# ─── командные режимы ───────────────────────────────────────────────────────
# Разбор фрагментов проверен выше; здесь — что скрипт делает с разобранным:
# три исхода (039), сборка в [Unreleased] и удаление собранных фрагментов (030).

def cli(monkeypatch, repo: Path, files: dict[str, str], changelog: str | None,
        *argv: str) -> None:
    prepare(monkeypatch, repo, files)
    monkeypatch.setattr(cc, "ROOT", repo)
    path = repo / "CHANGELOG.md"
    if changelog is not None:
        write(path, changelog)
    monkeypatch.setattr(cc, "CHANGELOG", path)
    monkeypatch.setattr("sys.argv", ["collect_changelog.py", *argv])


HEADER = "# Журнал\n\n## [Unreleased]\n\n## [0.1.0]\n\n- старое\n"


def test_проверка_чистых_фрагментов(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое"}, HEADER, "--check")
    assert cc.main() == 0
    assert "в порядке" in capsys.readouterr().out


def test_находка_красит_проверку(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": ""}, HEADER, "--check")
    assert cc.main() == 1
    assert "не в порядке" in capsys.readouterr().err


def test_нет_каталога_фрагментов_это_третий_исход(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {}, HEADER, "--check")
    monkeypatch.setattr(cc, "FRAGMENTS", repo / "нет-такого")
    assert cc.main() == 2
    assert "не отработала" in capsys.readouterr().err


def test_нет_журнала_это_третий_исход(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое"}, None, "--check")
    assert cc.main() == 2
    assert "собирать некуда" in capsys.readouterr().err


def test_показ_сборки_ничего_не_меняет(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое"}, HEADER, "--preview")
    assert cc.main() == 0
    assert "- новое" in capsys.readouterr().out
    assert (repo / "changelog.d" / "a.added.md").exists()


def test_сборка_кладёт_записи_и_убирает_фрагменты(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое", "b.fixed.md": "починка"},
        HEADER, "--collect")
    assert cc.main() == 0
    text = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "- новое" in text and "- починка" in text
    # Старый раздел не затёрт: сборка вставляет, а не переписывает.
    assert "- старое" in text
    assert not list((repo / "changelog.d").glob("*.md"))
    assert "собрано записей: 2" in capsys.readouterr().out


def test_сборка_без_раздела_это_третий_исход(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое"}, "# Журнал без раздела\n",
        "--collect")
    assert cc.main() == 2
    assert "нет раздела" in capsys.readouterr().err
    # Фрагмент уцелел: не собрали — значит не удалили.
    assert (repo / "changelog.d" / "a.added.md").exists()


def test_сборка_пустого_не_трогает_журнал(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {}, HEADER, "--collect")
    assert cc.main() == 0
    assert (repo / "CHANGELOG.md").read_text(encoding="utf-8") == HEADER


# ── вердикт починки: момент, которого не было ──────────────────────────────
#
# Фильтр «тянет ли это на правило» есть и работает машинно, но срабатывает для
# того, кто УЖЕ решил писать. Здесь стоит момент, в который решают: фрагмент
# пишут ровно тогда, когда починка сделана и инцидент ещё цел (правило 138).
#
# Набор двусторонний, и здоровые предметы взяты у границы: секции, кроме
# `fixed`, вердикта не требуют — иначе вопрос задавался бы там, где починки
# не было.

def frag(repo: Path, name: str, text: str) -> Path:
    return write(repo / "changelog.d" / name, text)


def test_починка_без_вердикта_это_находка(repo):
    out = cc.verdict_problems([frag(repo, "a.fixed.md", "Починили.\n")])
    assert out and "не ответила" in out[0]


def test_отказ_с_причиной_проходит(repo):
    assert cc.verdict_problems([frag(
        repo, "a.fixed.md",
        "Починили.\n\n> правилом не становится, потому что это местная настройка.\n")]) == []


def test_отказ_без_причины_это_находка(repo):
    out = cc.verdict_problems([frag(repo, "a.fixed.md", "Починили.\n\n> не правило.\n")])
    assert out and "не разбирается" in out[0]


def test_ссылка_на_правило_проходит(repo):
    assert cc.verdict_problems([frag(
        repo, "a.fixed.md", "Починили.\n\n> правило 145 — тот же класс.\n")]) == []


def test_ссылка_путём_в_дерево_тоже_проходит(repo):
    assert cc.verdict_problems([frag(
        repo, "a.fixed.md",
        "Починили.\n\n> см. rules/ru/145-every-declared-outcome-is-run.md\n")]) == []


def test_у_остальных_секций_вердикта_не_спрашивают(repo):
    """Здоровый предмет у границы: вопрос адресован починке, а не всякой работе."""
    assert cc.verdict_problems([
        frag(repo, "a.added.md", "Завели.\n"),
        frag(repo, "b.changed.md", "Поменяли.\n"),
        frag(repo, "c.internal.md", "Внутреннее.\n"),
    ]) == []


def test_имя_не_по_форме_вердиктом_не_проверяется(repo):
    """Форму имени судит validate(); дважды об одном не сообщают."""
    assert cc.verdict_problems([frag(repo, "a.md", "Что-то.\n")]) == []


def test_вердикт_в_журнал_не_едет(repo):
    body, verdict = cc.split_verdict(
        "Починили гонку.\n\n> правило 148 — тот же класс.\n")
    assert body == "Починили гонку."
    assert "148" in verdict


def test_фрагмент_из_одного_вердикта_считается_пустым(monkeypatch, repo):
    """Вердикт — не запись журнала: строка «>» одна оставляет тело пустым."""
    prepare(monkeypatch, repo, {"a.fixed.md": "> правило 148 — связано.\n"})
    _, problems = cc.validate()
    assert problems and "пуст" in problems[0]
