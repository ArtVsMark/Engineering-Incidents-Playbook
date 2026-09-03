"""Ответ каталога о самом себе: три исхода и находки по контракту.

Скрипт закрывает правила 128, 129 и 026. Тесты бьют в то, ради чего он есть:
ответ нужен по КАЖДОМУ правилу, «действует» без механизма и без места — не
ответ, а отрицательный статус без причины вернётся следующей ревизией.

Отдельно проверяется разделение отказа и предупреждения (правило 051):
несуществующий путь — факт и находка, число словом — подозрение и только
предупреждение. Смешать их значило бы либо ронять прогон на живой прозе, либо
пропускать разошедшуюся декларацию.
"""

from __future__ import annotations

import json
from pathlib import Path

import check_bindings as cb
from conftest import write


def prepare(monkeypatch, repo: Path, answer, export) -> None:
    b = repo / ".rules" / "bindings.json"
    e = repo / "export" / "rules.json"
    write(b, answer if isinstance(answer, str) else json.dumps(answer))
    write(e, export if isinstance(export, str) else json.dumps(export))
    monkeypatch.setattr(cb, "ROOT", repo)
    monkeypatch.setattr(cb, "BINDINGS", b)
    monkeypatch.setattr(cb, "EXPORT", e)


def export_of(*ids):
    return {"rules": [{"id": i} for i in ids]}


def test_полный_ответ_проходит(monkeypatch, repo):
    write(repo / "CLAUDE.md", "# свод\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "CLAUDE.md — раздел про гейты"}}},
            export_of("001"))
    assert cb.main() == 0


def test_нет_файла_ответа_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, {"rules": {}}, export_of("001"))
    cb.BINDINGS.unlink()
    assert cb.main() == 2
    assert "не отработала" in capsys.readouterr().err


def test_битый_json_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, "{не json", export_of("001"))
    assert cb.main() == 2
    assert "не разобрать JSON" in capsys.readouterr().err


def test_пустой_ответ_это_третий_исход(monkeypatch, repo, capsys):
    # Ноль записей — «сверять нечего», а не «всё сошлось»: зелёное на пустом
    # входе и есть тихо отключённый гейт (правило 075).
    prepare(monkeypatch, repo, {"rules": {}}, export_of("001"))
    assert cb.main() == 2
    assert "сверять нечего" in capsys.readouterr().err


def test_правило_без_ответа_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "нигде"}}},
            export_of("001", "002"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "002" in err and "unreviewed" in err


def test_ответ_на_несуществующее_правило_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "нигде"},
                       "999": {"status": "unreviewed"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "999" in capsys.readouterr().err


def test_статус_вне_набора_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "потом-разберёмся"}}}, export_of("001"))
    assert cb.main() == 1
    assert "вне набора" in capsys.readouterr().err


def test_действует_без_места_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "где именно" in capsys.readouterr().err


def test_отказ_без_причины_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "rejected"}}}, export_of("001"))
    assert cb.main() == 1
    assert "без причины" in capsys.readouterr().err


def test_заявленный_файл_обязан_существовать(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/выдумка.py"}}},
            export_of("001"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "выдумка.py" in err and "разошлась с фактом" in err


def test_живой_заявленный_файл_находкой_не_считается(monkeypatch, repo):
    write(repo / "scripts" / "живой.py",
          '"""Сторож.\n\nРеализует правила каталога:\n  001 — держит вот это.\n"""\n')
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/живой.py"}}},
            export_of("001"))
    assert cb.main() == 0


def test_число_словом_только_предупреждает(monkeypatch, repo):
    # Правило 051: «три гейта» устареет, но отказ здесь был бы ложным —
    # живая проза даёт достаточно законных сочетаний со словом-числом.
    write(repo / "CLAUDE.md", "# свод\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "CLAUDE.md",
                               "why": "держат три гейта"}}},
            export_of("001"))
    assert cb.main() == 0


# ── адрес механизма: рассказ вместо адреса — находка ──────────────────────
#
# «След» правила гейт требует РАЗРЕШИМЫМ (audit_catalogue), а `where` до сих
# пор проверялся только на непустоту. Набор двусторонний (140): у каждого
# исхода есть предмет, который обязан его дать, — иначе гейт, отвергающий
# всё подряд, выглядел бы так же зелено, как верный.

def test_механизм_без_адреса_это_находка(monkeypatch, repo, capsys):
    """Гейт, чей адрес нельзя назвать, обычно и не гейт."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "все скрипты различают исходы кодом"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "адреса нет" in capsys.readouterr().err


def test_образец_файлов_это_адрес(monkeypatch, repo):
    """Набор файлов — такой же адрес, как один файл.

    Требовать перечислить их поимённо значило бы требовать список, который
    устареет с первым новым прогоном.
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "document",
                               "where": ".github/workflows/*.yml — у всех есть "
                                        "ручная кнопка"}}},
            export_of("001"))
    assert cb.main() == 0


def test_корневой_документ_по_имени_это_адрес(monkeypatch, repo):
    """`CONTRIBUTING` без расширения называют в прозе, и это адрес."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "document",
                               "where": "CONTRIBUTING — раздел про ревью"}}},
            export_of("001"))
    assert cb.main() == 0


def test_у_отсутствия_механизма_адреса_не_требуют(monkeypatch, repo):
    """`none` — это «не держится ничем». Адрес тут нечему называть.

    Требовать его значило бы толкать к выдумыванию: ответ «ничем» честнее
    придуманного пути, и наказывать за честность гейт не должен.
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "намерение, за которым пока ничего",
                               "why": "не дошли руки: предмет счётный"}}},
            export_of("001"))
    assert cb.main() == 0


# ── «ничем» обязано назвать причину (правило 154) ─────────────────────────
#
# `none` без причины означает сразу две вещи — «пробовали, машинно нельзя» и
# «никто не пробовал». Замер при заведении правила: 41 запись не держалась
# ничем, причину называли 5. После заполнения вышло 14 «не дошли руки» —
# очередь на гейты, невидимая до этого. Набор двусторонний (140).

def test_ничем_без_причины_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "держится договорённостью"}}},
            export_of("001"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "не держится ничем, и почему" in err


def test_ничем_с_причиной_проходит(monkeypatch, repo):
    """Причина — обычная проза; замкнутый словарь был бы ярлыком вместо ответа."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "держится договорённостью",
                               "why": "требует суждения: что считать решением, "
                                      "решает читатель"}}},
            export_of("001"))
    assert cb.main() == 0


def test_у_обеспеченного_правила_причины_не_требуют(monkeypatch, repo):
    """154 спрашивает только у `none`: у механизма причина — его адрес."""
    write(repo / "scripts" / "живой.py",
          '"""Сторож.\n\nРеализует правила каталога:\n  001 — держит вот это.\n"""\n')
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/живой.py"}}},
            export_of("001"))
    assert cb.main() == 0


# ── механизм называет свои правила (задача #202) ──────────────────────────
#
# Две декларации одной территории существовали и не сверялись: 27 скриптов
# называли правила в докстроке, 23 были названы правилами. Замер 28 августа:
# 32 «скрипт без блока вовсе» и 25 «блок есть, правила в нём нет».
# Связь односторонняя — обратную требовать нельзя, см. комментарий в гейте.

def гейт(repo, текст: str):
    write(repo / "scripts" / "страж.py", текст)


def test_механизм_без_блока_правил_это_находка(monkeypatch, repo, capsys):
    гейт(repo, '"""Просто сторож."""\n')
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/страж.py"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "не объявляет своих правил" in capsys.readouterr().err


def test_блок_есть_а_правила_в_нём_нет_это_находка(monkeypatch, repo, capsys):
    гейт(repo, '"""Сторож.\n\nРеализует правила каталога:\n'
               '  002 — что-то другое.\n"""\n')
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/страж.py"}}},
            export_of("001"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "его не называет" in err and "002" in err


def test_обе_стороны_сошлись_проходит(monkeypatch, repo):
    гейт(repo, '"""Сторож.\n\nРеализует правила каталога:\n'
               '  001 — держит вот это.\n"""\n')
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/страж.py"}}},
            export_of("001"))
    assert cb.main() == 0


def test_у_ничем_блока_не_спрашивают(monkeypatch, repo):
    """`none` механизма не имеет, и спрашивать у него нечего."""
    гейт(repo, '"""Просто сторож."""\n')
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "scripts/страж.py",
                               "why": "не дошли руки: предмет счётный"}}},
            export_of("001"))
    assert cb.main() == 0


# ── разбивка «ничем» по причине (154 + решение владельца 31 августа) ────────

def правило(why: str) -> dict:
    return {"status": "active", "mechanism": "none", "where": "нигде", "why": why}


def test_prichiny_razobrany_po_klassam():
    rules = {"001": правило("требует суждения: из диффа не следует"),
             "002": правило("требует суждения: оценивает читатель"),
             "003": правило("не дошли руки: очередь не дошла")}

    counts, other = cb.why_split(rules)

    assert counts == {"суждением": 2, "очередь": 1} and other == 0


def test_neznakomaya_prichina_pechataetsya_prochim():
    """Список классов разрешительный: непопавшее считается «прочим» и остаётся
    числом, а не растворяется в соседних (068)."""
    counts, other = cb.why_split({"001": правило("проверка дороже нарушения")})

    assert counts == {} and other == 1


def test_pravilo_s_mehanizmom_v_razbivku_ne_popadaet():
    rules = {"001": {"status": "active", "mechanism": "gate", "where": "s/g.py"}}

    assert cb.why_split(rules) == ({}, 0)


def test_ne_deystvuyushchee_pravilo_ne_schitaetsya():
    """`rejected` и `not-applicable` тоже несут `why`, но это другая причина —
    почему правила здесь нет, а не почему оно не держится."""
    rules = {"001": {"status": "rejected", "why": "требует суждения: нет"}}

    assert cb.why_split(rules) == ({}, 0)


# ── очередь «ничем» называет, что уже решено у соседа (правило 162) ─────────
#
# Случаи спрашивают ГЕЙТ через main() и читают его вывод: свёртка сама по себе
# ответила бы согласием с собой, а предмет здесь — попадает ли ответ соседа в
# метрику, рядом с которой выбирают работу (правило 150).

СОСЕДИ = {
    "consumers": [
        {"repo": "мой/каталог", "holds": {}},
        {"repo": "чужой/грейдер", "holds": {
            "001": {"mechanism": "gate", "where": "scripts/check_docs.py"},
        }},
    ]
}


def с_соседями(monkeypatch, repo: Path, ответ: dict, соседи=СОСЕДИ) -> None:
    prepare(monkeypatch, repo, ответ, export_of(*ответ["rules"]))
    if соседи is not None:
        write(repo / "export" / "where.json", json.dumps(соседи))


def ничем(why: str = "требует суждения: пока так") -> dict:
    return {"project": "мой/каталог",
            "rules": {"001": {"status": "active", "mechanism": "none",
                              "where": "договорённостью, гейта нет",
                              "why": why}}}


def test_reshennoe_u_sosseda_nazvano_v_metrike(monkeypatch, repo, capsys):
    """Ровно инцидент 162: ответ соседа лежал в собранной сводке и молчал."""
    с_соседями(monkeypatch, repo, ничем())

    assert cb.main() == 0
    out = capsys.readouterr().out
    assert "решено у соседа 1" in out and "грейдер" in out and "001" in out


def test_u_sosseda_tozhe_nichem_eto_otvet(monkeypatch, repo, capsys):
    """«Ни одного» печатается: пустая строка неотличима от несчитанного (027)."""
    с_соседями(monkeypatch, repo, ничем(),
               соседи={"consumers": [{"repo": "чужой/грейдер", "holds": {
                   "001": {"mechanism": "none", "where": ""}}}]})

    assert cb.main() == 0
    assert "ни одного" in capsys.readouterr().out


def test_otvet_soseda_bez_adresa_ne_schitaetsya_reshennym(monkeypatch, repo, capsys):
    """Пересказ помогает не больше, чем молчание: адрес обязателен."""
    с_соседями(monkeypatch, repo, ничем(),
               соседи={"consumers": [{"repo": "чужой/грейдер", "holds": {
                   "001": {"mechanism": "gate", "where": "   "}}}]})

    assert cb.main() == 0
    assert "ни одного" in capsys.readouterr().out


def test_pravilo_s_mehanizmom_v_ocheredi_ne_stoit(monkeypatch, repo, capsys):
    """Очередь — это «ничем»; закрытое гейтом сюда попадать не должно, иначе
    метрика зовёт переделывать сделанное."""
    write(repo / "CLAUDE.md", "# свод\n")
    с_соседями(monkeypatch, repo,
               {"project": "мой/каталог",
                "rules": {"001": {"status": "active", "mechanism": "gate",
                                  "where": "CLAUDE.md — раздел про гейты"}}})

    assert cb.main() == 0
    assert "ни одного" in capsys.readouterr().out


def test_bez_svodki_metrika_govorit_chto_ne_schitalas(monkeypatch, repo, capsys):
    """Молчание вместо числа читалось бы как «у соседей ничего нет» (046)."""
    с_соседями(monkeypatch, repo, ничем(), соседи=None)

    assert cb.main() == 0
    assert "не считалось" in capsys.readouterr().out


# ── «не применимо» перечитывается пробой (175) ─────────────────────────────

def test_proba_oprovergaet_ne_primenimo(tmp_path):
    """Ровно тот случай, что нашёлся четырежды на живом ответе каталога:
    условия проекта изменились, а строка осталась и выглядит решением."""
    (tmp_path / "scripts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "scripts" / "s.py").write_text(
        "urllib.request.urlopen(url)\n", encoding="utf-8")
    assert "ходит наружу" in cb.refuted("001", tmp_path)


def test_bez_uliki_molchanie(tmp_path):
    """АСИММЕТРИЯ: не нашли опровержения — молчим. «Не нашли» и «нет» разные
    ответы, и в мелком клоне первое происходит постоянно."""
    (tmp_path / "scripts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "scripts" / "s.py").write_text("print('тихо')\n", encoding="utf-8")
    assert cb.refuted("001", tmp_path) == ""


def test_pravilo_bez_proby_ne_schitaetsya_provernnym(tmp_path):
    """Пробы нет — это НЕ «проверено»: такие обязаны считаться отдельно и
    называться числом, иначе непроверенное неотличимо от чистого (075)."""
    assert cb.refuted("019", tmp_path) == ""
    assert "019" not in cb.REFUTED_BY

