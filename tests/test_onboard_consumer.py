"""Набор подключения: собирается механизмом и принимается обеими сторонами.

Подключение — три файла с точным содержимым, и «скопируйте из контракта» уже
дало то, что дало: канал построен с обеих сторон, а подключено меньше половины
объявленных потребителей и адрес предложений не назван ни одним. Шаг, который
надо помнить, пропускают (правило 002).

Главное, что здесь держится, — **собранный набор принимается теми самыми
скриптами, которые будут его читать**. Проверять генератор сверкой строк
значило бы проверять его самим собой; предмет проверки — согласие сторон.
"""

from __future__ import annotations

import json

import onboard_consumer as oc
from conftest import write

EXPORT = {"rules": [{"id": "001"}, {"id": "002"}]}
CONTRACT = "текст\n\n`uses: X@<!--m:ref-->v1.2.0<!--/m:ref-->`\n"


def prepare(repo):
    e = write(repo / "export" / "rules.json", json.dumps(EXPORT))
    c = write(repo / "export" / "README.md", CONTRACT)
    return e, c


def run(repo, name="owner/name"):
    e, c = prepare(repo)
    return oc.main(["--repo", name, "--out", str(repo / "out"),
                    "--export", str(e), "--contract", str(c)])


# ── собранное принимается обеими сторонами ────────────────────────────────

def test_ответ_собран_по_каждому_правилу(repo):
    assert run(repo) == 0
    d = json.loads((repo / "out" / ".rules" / "bindings.json").read_text(encoding="utf-8"))
    assert set(d["rules"]) == {"001", "002"}
    assert all(v["status"] == "unreviewed" for v in d["rules"].values())


def test_предложения_пусты_но_это_валидный_файл(repo):
    assert run(repo) == 0
    d = json.loads((repo / "out" / ".rules" / "proposals.json").read_text(encoding="utf-8"))
    assert d["proposals"] == [] and d["schema"] == "1.0"


def test_в_предложениях_нет_поля_номера(repo):
    """Номер присваивает каталог; поле здесь — ошибка, и заготовка её не сеет."""
    assert run(repo) == 0
    d = json.loads((repo / "out" / ".rules" / "proposals.json").read_text(encoding="utf-8"))
    assert not any(k in d for k in ("id", "number", "rule"))


def test_тег_берётся_из_контракта_а_не_вписан(repo):
    """Второе место для версии разошлось бы с первым молча (035, 022)."""
    assert run(repo) == 0
    wf = (repo / "out" / ".github" / "workflows" / "rules-inbox.yml").read_text(encoding="utf-8")
    assert "@v1.2.0" in wf and "@main" not in wf


def test_рабочий_процесс_разбирается_как_yaml(repo):
    import yaml
    assert run(repo) == 0
    doc = yaml.safe_load(
        (repo / "out" / ".github" / "workflows" / "rules-inbox.yml").read_text(encoding="utf-8"))
    assert doc["name"] == "rules-inbox"
    assert doc["permissions"]["issues"] == "write"
    assert "workflow_dispatch" in doc[True]


# ── предметы, которые генератор обязан отвергнуть ──────────────────────────

def test_имя_не_по_форме_это_третий_исход(repo, capsys):
    assert run(repo, name="просто-имя") == 2
    assert "владелец/имя" in capsys.readouterr().err


def test_нет_экспорта_это_третий_исход(repo, capsys):
    _, c = prepare(repo)
    assert oc.main(["--repo", "o/n", "--out", str(repo / "out"),
                    "--export", str(repo / "нет.json"), "--contract", str(c)]) == 2


def test_контракт_без_маркера_это_третий_исход(repo, capsys):
    e, _ = prepare(repo)
    c = write(repo / "export" / "README.md", "текст без маркера\n")
    assert oc.main(["--repo", "o/n", "--out", str(repo / "out"),
                    "--export", str(e), "--contract", str(c)]) == 2
    assert "маркера" in capsys.readouterr().err


def test_пустой_экспорт_это_находка(repo, capsys):
    e = write(repo / "export" / "rules.json", json.dumps({"rules": []}))
    c = write(repo / "export" / "README.md", CONTRACT)
    assert oc.main(["--repo", "o/n", "--out", str(repo / "out"),
                    "--export", str(e), "--contract", str(c)]) == 1
