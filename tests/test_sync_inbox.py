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
            # ПОДДЕЛКА ОТДАЁТ ТО, ЧТО ОТДАЁТ ПЛОЩАДКА, А НЕ ТО, ЧТО ЗАДУМАНО.
            # Раньше здесь стояла пустая строка — и четыре теста «задачи нет»
            # гонялись на значении, которого `gh --jq` не возвращает никогда:
            # индексация пустого набора печатается словом «null null». Тесты
            # были зелёными, а механизм не мог завести первую задачу вовсе.
            return 0, (f"{issue[0]} {issue[1]}" if issue else "null null")
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


# ── «у соседей это уже решено» (доставка сводки во входящие) ────────────────

def сосед(repo: str, rid: str, mechanism: str = "gate", where: str = "s/g.py") -> dict:
    return {"repo": repo, "holds": {rid: {"mechanism": mechanism, "where": where}}}


НИЧЕМ = {"001": {"status": "active", "mechanism": "none", "why": "не дошли руки"}}


def test_sosedskiy_mehanizm_popadaet_s_adresom():
    out = si.solved_next_door(НИЧЕМ, [сосед("o/grader", "001")], "o/me")

    assert out == [{"rule": "001",
                    "held": [{"repo": "o/grader", "mechanism": "gate",
                              "where": "s/g.py"}]}]


def test_svoy_mehanizm_sosedskim_ne_schitaetsya():
    """Проект не должен видеть собственный ответ как чужой совет."""
    assert si.solved_next_door(НИЧЕМ, [сосед("o/me", "001")], "o/me") == []


def test_pravilo_derzhitsya_zdes_v_razdel_ne_idyot():
    свой = {"001": {"status": "active", "mechanism": "gate", "where": "s/x.py"}}

    assert si.solved_next_door(свой, [сосед("o/grader", "001")], "o/me") == []


def test_sosed_bez_adresa_ne_pomogaet():
    """ГРАНИЦА, ТА ЖЕ ЧТО У ПОЛЯ `where`: пересказ механизма помогает не больше,
    чем его отсутствие — открыть его нечем."""
    без = [{"repo": "o/grader", "holds": {"001": {"mechanism": "gate", "where": ""}}}]

    assert si.solved_next_door(НИЧЕМ, без, "o/me") == []


def test_sosed_u_kotorogo_tozhe_nichem_ne_schitaetsya():
    оба = [{"repo": "o/grader",
            "holds": {"001": {"mechanism": "none", "where": "нигде"}}}]

    assert si.solved_next_door(НИЧЕМ, оба, "o/me") == []


def test_nedeystvuyushchee_pravilo_v_razdel_ne_idyot():
    """`rejected` здесь — решение, а не пробел: советовать по нему нечего."""
    отклонено = {"001": {"status": "rejected", "why": "нет предмета"}}

    assert si.solved_next_door(отклонено, [сосед("o/grader", "001")], "o/me") == []


def test_razdel_pechataetsya_v_tele_zadachi():
    body = si.body_for([], [], "o/cat", solved=[
        {"rule": "001", "held": [{"repo": "o/grader", "mechanism": "gate",
                                  "where": "s/g.py — что делает"}]}])

    assert "У соседей это уже решено" in body
    assert "s/g.py" in body and "grader" in body


def test_pustoy_razdel_ne_pechataetsya():
    """Заголовок без строк читается как «мы посмотрели и там пусто», а посмотреть
    могли и не суметь: пустое состояние объявляется, когда оно измерено (027)."""
    assert "У соседей" not in si.body_for([], [], "o/cat", solved=[])


# ── разбор ответа трекера ─────────────────────────────────────────────────


def test_pustota_ot_jq_eto_null_null():
    """`gh --jq` на пустом наборе печатает «null null», а не пустоту.

    Строка «null» непустая, то есть истинная: ветка «завести задачу» не
    выполнялась никогда, вместо неё уходил `gh issue edit null`.
    """
    assert si.found_issue("null null") == ("", "")


def test_pustaya_stroka_tozhe_otsutstvie():
    assert si.found_issue("") == ("", "")


def test_nayidennaya_zadacha_razbiraetsya():
    assert si.found_issue("52 OPEN") == ("52", "OPEN")
