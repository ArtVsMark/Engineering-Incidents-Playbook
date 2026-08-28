"""Задача-«входящие»: открыта ровно тогда, когда в ней есть работа.

Открытая задача — это УТВЕРЖДЕНИЕ «здесь есть работа», а не оформление. При нуле
нерассмотренных оно ложно, и ежедневная неправда в трекере приучает листать его
мимо — тем самым способом, каким ломается 091: трекер и есть первый источник
работы, и единственный, в который окно смотрит обязательно.

До этой правки закрыть задачу было НЕЛЬЗЯ: поиск шёл среди открытых, и следующий
прогон её не находил, а заводил вторую. Потребитель это и наблюдал —
`ArtVsMark/ArtVsMark#52` висел открытым с нулём нерассмотренных именно потому,
что иначе раздвоился бы. Поэтому пара «закрывается пустой» / «находится закрытой
и не дублируется» стоит здесь вместе: порознь каждая из них проходила бы и на
сломанном механизме.

Граница, которую эти случаи держат: закрывает МЕХАНИЗМ, потому что пустота —
проверяемый факт. Там, где закрытие означало бы «я посмотрел», решает человек
(142), и такого случая здесь нет намеренно.

Сеть не трогается: экспорт и `gh` подменяются.
"""

from __future__ import annotations

import sync_inbox as si


def arm(monkeypatch, rules, answered, issue=None):
    """Подменяет экспорт, ответ проекта и `gh`; возвращает журнал вызовов."""
    calls: list[tuple] = []

    def fake_gh(*args):
        calls.append(args)
        if args[:2] == ("issue", "list"):
            return 0, (f"{issue[0]} {issue[1]}" if issue else "")
        if args[:2] == ("issue", "create"):
            return 0, "https://example/issues/99"
        return 0, ""

    monkeypatch.setattr(si, "fetch_rules", lambda c, r: (rules, None))
    monkeypatch.setattr(si, "gh", fake_gh)
    monkeypatch.setenv("GH_TOKEN", "x")
    import json, pathlib, tempfile
    path = pathlib.Path(tempfile.mkdtemp()) / "bindings.json"
    path.write_text(json.dumps({"rules": answered}), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["sync_inbox.py", "--bindings", str(path)])
    return calls


def verbs(calls):
    return [c[1] for c in calls if c[0] == "issue"]


RULES = [{"id": "001", "title": {"ru": "первое"}},
         {"id": "002", "title": {"ru": "второе"}}]
ANSWERED_ALL = {"001": {"status": "active"}, "002": {"status": "active"}}


def test_pustaya_zadacha_zakryvaetsya(monkeypatch, capsys):
    calls = arm(monkeypatch, RULES, ANSWERED_ALL, issue=("52", "OPEN"))
    assert si.main() == 0
    assert "close" in verbs(calls)
    assert "закрыта" in capsys.readouterr().out


def test_zakrytaya_zadacha_nahoditsya_i_ne_dublitsya(monkeypatch, capsys):
    """Вторая половина пары: поиск идёт среди ВСЕХ состояний."""
    calls = arm(monkeypatch, RULES, ANSWERED_ALL, issue=("52", "CLOSED"))
    assert si.main() == 0
    assert "create" not in verbs(calls)
    assert "close" not in verbs(calls)      # уже закрыта — трогать нечего
    listing = next(c for c in calls if c[:2] == ("issue", "list"))
    assert "all" in listing


def test_poyavilos_nerassmotrennoe_zadacha_otkryvaetsya_zanovo(monkeypatch, capsys):
    calls = arm(monkeypatch, RULES, {"001": {"status": "active"}}, issue=("52", "CLOSED"))
    assert si.main() == 1
    assert "reopen" in verbs(calls)
    assert "открыта заново" in capsys.readouterr().out


def test_otkrytaya_s_rabotoy_ostayotsya_otkrytoy(monkeypatch, capsys):
    """Ложное срабатывание здесь дороже пропуска: закрыть задачу с работой —
    значит спрятать её от того, кто обязан её увидеть."""
    calls = arm(monkeypatch, RULES, {"001": {"status": "unreviewed"}, "002": {"status": "active"}},
                issue=("52", "OPEN"))
    assert si.main() == 1
    assert "close" not in verbs(calls)
    assert "reopen" not in verbs(calls)


def test_zadachi_net_i_rabotu_net_ne_zavodim(monkeypatch, capsys):
    """Завести задачу, чтобы тут же закрыть, — шум без адресата."""
    calls = arm(monkeypatch, RULES, ANSWERED_ALL, issue=None)
    assert si.main() == 0
    assert "create" not in verbs(calls)
    assert "заводить нечего" in capsys.readouterr().out


def test_zadachi_net_a_rabota_est_zavodim(monkeypatch, capsys):
    calls = arm(monkeypatch, RULES, {}, issue=None)
    assert si.main() == 1
    assert "create" in verbs(calls)


def test_lishniy_otvet_tozhe_derzhit_zadachu_otkrytoy(monkeypatch, capsys):
    """Ответ по правилу, которого в каталоге нет, — работа, а не фон."""
    answered = dict(ANSWERED_ALL, **{"143": {"status": "active"}})
    calls = arm(monkeypatch, RULES, answered, issue=("52", "CLOSED"))
    assert si.main() == 1
    assert "reopen" in verbs(calls)


def test_treker_ne_otvetil_eto_tretiy_ishod(monkeypatch, capsys):
    monkeypatch.setattr(si, "fetch_rules", lambda c, r: (RULES, None))
    monkeypatch.setattr(si, "gh", lambda *a: (1, "HTTP 403"))
    monkeypatch.setenv("GH_TOKEN", "x")
    import json, pathlib, tempfile
    path = pathlib.Path(tempfile.mkdtemp()) / "b.json"
    path.write_text(json.dumps({"rules": ANSWERED_ALL}), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["sync_inbox.py", "--bindings", str(path)])
    assert si.main() == 2
    assert "не отработала" in capsys.readouterr().err
