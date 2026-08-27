"""Каркас записи собирается механизмом, содержание — нет.

Порядок добавления правила — семь шагов, и все семь делались руками: номер,
два файла с одинаковым именем, область из закрытого словаря, вопрос о соседях,
ответ в bindings, фрагмент журнала, пересборка. Шаг, который надо помнить,
пропускают (правило 002). Измерено на этом же каталоге: за одно окно дважды
поставлены НЕСУЩЕСТВУЮЩИЕ имена файлов в перекрёстных ссылках.

Главное, что здесь держится, — **граница между механическим и суждением**.
Номер вычисляется однозначно, инцидент — нет. Сгенерированный инцидент был бы
выдумкой, а выдуманный инцидент хуже отсутствующего: он выглядит как
основание. Поэтому отдельный случай требует, чтобы в собранном каркасе
остались МЕСТА для суждения, а не заполненные поля.
"""

from __future__ import annotations

import json

import new_rule as nr
from conftest import write


def tree(repo, rules=("001-a", "002-b"), consumers=None, proposals=None):
    for name in rules:
        write(repo / "rules" / "ru" / f"{name}.md", "# Правило\n")
        write(repo / "rules" / "en" / f"{name}.md", "# A rule\n")
    write(repo / "templates" / "rule-template.md",
          "# `<Правило одной строкой>`\n\n**Область.** `<область>`\n\n"
          "**Правило.** `<что делать>`\n\n## Инцидент\n\n`<что сломалось>`\n\n"
          "## Применимость\n\n**Не работает** `<где>`.\n\n"
          "## След\n\n`<разрешимый след>`\n")
    write(repo / ".rules" / "bindings.json", json.dumps({"rules": {}}))
    write(repo / ".rules" / "consumers.json",
          json.dumps(consumers or {"consumers": [{"repo": "o/one"}]}, ensure_ascii=False))
    if proposals is not None:
        write(repo / ".rules" / "incoming.json", json.dumps(proposals, ensure_ascii=False))
    (repo / "changelog.d").mkdir(parents=True, exist_ok=True)
    return repo


def run(repo, *argv):
    return nr.main([*argv, "--root", str(repo)])


OK = ("--slug", "a-new-thing", "--area", "процесс",
      "--trail", "owner/repo#12")


# ── номер: вычисляется однозначно и не переиспользуется ────────────────────

def test_номер_берётся_выше_максимума(repo):
    """Дыра от удалённой записи остаётся дырой: номера не переиспользуются."""
    assert nr.next_number({"001": "a", "005": "b"}) == "006"


def test_каркас_кладётся_в_оба_дерева(repo):
    assert run(tree(repo), *OK) == 0
    assert (repo / "rules" / "ru" / "003-a-new-thing.md").exists()
    assert (repo / "rules" / "en" / "003-a-new-thing.md").exists()


def test_ответ_каталога_заводится_нерассмотренным(repo):
    assert run(tree(repo), *OK) == 0
    d = json.loads((repo / ".rules" / "bindings.json").read_text(encoding="utf-8"))
    assert d["rules"]["003"] == {"status": "unreviewed"}


def test_фрагмент_журнала_кладётся(repo):
    assert run(tree(repo), *OK) == 0
    assert (repo / "changelog.d" / "rule-003-a-new-thing.added.md").exists()


def test_след_подставлен_целиком(repo):
    assert run(tree(repo), *OK) == 0
    ru = (repo / "rules" / "ru" / "003-a-new-thing.md").read_text(encoding="utf-8")
    assert "owner/repo#12" in ru


# ── граница: суждение остаётся человеку ────────────────────────────────────

def test_места_для_суждения_остаются_пустыми(repo):
    """Сгенерированный инцидент был бы выдумкой, а она выглядит как основание."""
    assert run(tree(repo), *OK) == 0
    ru = (repo / "rules" / "ru" / "003-a-new-thing.md").read_text(encoding="utf-8")
    assert "<что сломалось>" in ru
    en = (repo / "rules" / "en" / "003-a-new-thing.md").read_text(encoding="utf-8")
    assert "<What broke" in en or "<" in en


# ── предметы, которые генератор обязан отвергнуть ──────────────────────────

def test_занятый_слаг_это_находка(repo, capsys):
    assert run(tree(repo, rules=("001-a-new-thing",)), *OK) == 1
    assert "Пересмотр" in capsys.readouterr().err


def test_область_вне_словаря_это_находка(repo, capsys):
    assert run(tree(repo), "--slug", "x", "--area", "выдуманная",
               "--trail", "owner/repo#12") == 1
    assert "вне словаря" in capsys.readouterr().err


def test_след_прозой_это_находка(repo, capsys):
    assert run(tree(repo), "--slug", "x", "--area", "процесс",
               "--trail", "где-то там") == 1
    assert "не разрешается" in capsys.readouterr().err


def test_слаг_кириллицей_это_находка(repo, capsys):
    assert run(tree(repo), "--slug", "правило", "--area", "процесс",
               "--trail", "owner/repo#12") == 1
    assert "не по форме" in capsys.readouterr().err


# ── круг: предложение из проекта → каркас здесь ────────────────────────────

def connected(slug="a-real-incident", incident="Сломалось вот это."):
    return ({"consumers": [{"repo": "o/one", "proposals": ".rules/incoming.json"}]},
            {"proposals": [{"slug": slug, "claim": "Делать так.",
                            "incident": incident, "trail": "scripts/x.py"}]})


def test_предложение_становится_каркасом(repo):
    c, p = connected()
    assert run(tree(repo, consumers=c, proposals=p),
               "--from-proposal", "o/one:a-real-incident", "--area", "процесс") == 0
    ru = (repo / "rules" / "ru" / "003-a-real-incident.md").read_text(encoding="utf-8")
    assert "o/one — scripts/x.py" in ru


def test_номер_присваивает_каталог_а_не_проект(repo):
    """У предложения номера нет и быть не может: независимый выбор двух
    проектов уже нечем починить."""
    c, p = connected()
    assert run(tree(repo, consumers=c, proposals=p),
               "--from-proposal", "o/one:a-real-incident", "--area", "процесс") == 0
    assert (repo / "rules" / "ru" / "003-a-real-incident.md").exists()


def test_предложение_без_инцидента_это_находка(repo, capsys):
    c, p = connected(incident="")
    assert run(tree(repo, consumers=c, proposals=p),
               "--from-proposal", "o/one:a-real-incident", "--area", "процесс") == 1
    assert "без инцидента" in capsys.readouterr().err


def test_предложение_от_необъявленного_проекта_это_находка(repo, capsys):
    c, p = connected()
    assert run(tree(repo, consumers=c, proposals=p),
               "--from-proposal", "чужой/проект:a-real-incident", "--area", "процесс") == 1
    assert "не объявлен потребителем" in capsys.readouterr().err


def test_канал_в_эту_сторону_не_подключён_это_находка(repo, capsys):
    _, p = connected()
    assert run(tree(repo, proposals=p),
               "--from-proposal", "o/one:a-real-incident", "--area", "процесс") == 1
    assert "не назван адрес предложений" in capsys.readouterr().err


# ── третий исход ───────────────────────────────────────────────────────────

def test_пустой_каталог_это_третий_исход(repo, capsys):
    assert run(tree(repo, rules=()), *OK) == 2
    assert "нумеровать не от чего" in capsys.readouterr().err
