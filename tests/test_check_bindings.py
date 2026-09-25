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

import datetime as _dt
import json
import re
from pathlib import Path

import pytest

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
    # Ответ «гейт» обязан назвать ИСПОЛНЯЕМОЕ (139), а названный скрипт —
    # объявить это правило своим: полный ответ и значит «оба конца сходятся».
    write(repo / "scripts/check_probe.py",
          '"""Проба.\n\nРеализует правила каталога:\n  001 — держит его целиком.\n"""\n')
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/check_probe.py — держит правило"}}},
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
            "holdable": "no",
                               "where": "нигде"}}},
            export_of("001", "002"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "002" in err and "unreviewed" in err


def test_ответ_на_несуществующее_правило_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
            "holdable": "no",
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
    # Адрес исполняемый, потому что механизм объявлен гейтом (139): предмет
    # этого случая — слово-число в прозе, и он не должен падать на соседнем
    # требовании.
    write(repo / "scripts/check_probe.py",
          '"""Проба.\n\nРеализует правила каталога:\n  001 — держит его целиком.\n"""\n')
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/check_probe.py",
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
                                        "ручная кнопка",
                               "holdable": "no",
                               "why": "предмет не в дереве"}}},
            export_of("001"))
    assert cb.main() == 0


def test_корневой_документ_по_имени_это_адрес(monkeypatch, repo):
    """`CONTRIBUTING` без расширения называют в прозе, и это адрес."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "document",
                               "where": "CONTRIBUTING — раздел про ревью",
                               "holdable": "no",
                               "why": "предмет не в дереве"}}},
            export_of("001"))
    assert cb.main() == 0


def test_у_отсутствия_механизма_адреса_не_требуют(monkeypatch, repo):
    """`none` — это «не держится ничем». Адрес тут нечему называть.

    Требовать его значило бы толкать к выдумыванию: ответ «ничем» честнее
    придуманного пути, и наказывать за честность гейт не должен.
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
            "holdable": "no",
                               "where": "намерение, за которым пока ничего",
                               "why": "не дошли руки: предмет счётный",
                               "machine_half": "есть, но нашла бы пустоту (182)"}}},
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
            "holdable": "no",
                               "where": "держится договорённостью"}}},
            export_of("001"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "не держится ничем, и почему" in err


def test_ничем_с_причиной_проходит(monkeypatch, repo):
    """Причина — обычная проза; замкнутый словарь был бы ярлыком вместо ответа."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
            "holdable": "no",
                               "where": "держится договорённостью",
                               "why": "требует суждения: что считать решением, "
                                      "решает читатель",
                               "machine_half": "нет: препятствие одно на обе "
                                               "половины (182)"}}},
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
            "holdable": "no",
                               "where": "scripts/страж.py",
                               "why": "не дошли руки: предмет счётный",
                               "machine_half": "есть, но нашла бы пустоту (182)"}}},
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
    """Ответ «держится ничем» — с разбором надвое, которого требует 182.

    Поле стоит в общем помощнике, а не в отдельном случае: без него КАЖДЫЙ
    случай, строящий такой ответ, отвечал бы отказом по другой причине, и набор
    проверял бы не то, что написано (150).
    """
    return {"project": "мой/каталог",
            "rules": {"001": {"status": "active", "mechanism": "none",
                              "where": "договорённостью, гейта нет",
                              "why": why,
                              # Слово держимости спрашивается у ВСЯКОГО ответа,
                              # которого не держит машина, — `none` в том числе.
                              "holdable": "no",
                              "machine_half": "нет: препятствие одно на обе "
                                              "половины (182)"}}}


def test_reshennoe_u_sosseda_nazvano_v_metrike(monkeypatch, repo, capsys):
    """Ровно инцидент 162: ответ соседа лежал в собранной сводке и молчал."""
    с_соседями(monkeypatch, repo, ничем())

    assert cb.main() == 0
    out = capsys.readouterr().out
    assert "решено у соседа: правил 1" in out
    assert "грейдер" in out and "001" in out


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
    write(repo / "scripts/check_probe.py",
          '"""Проба.\n\nРеализует правила каталога:\n  001 — держит его целиком.\n"""\n')
    с_соседями(monkeypatch, repo,
               {"project": "мой/каталог",
                "rules": {"001": {"status": "active", "mechanism": "gate",
                                  "where": "scripts/check_probe.py — держит правило"}}})

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


# ── два числа об одной величине печатаются вместе и названными (правило 178) ─

ДВОЕ = {
    "consumers": [
        {"repo": "мой/каталог", "holds": {}},
        {"repo": "чужой/грейдер", "holds": {
            "001": {"mechanism": "gate", "where": "scripts/check_docs.py"},
        }},
        {"repo": "чужой/счётчик", "holds": {
            "001": {"mechanism": "gate", "where": "scripts/other.py"},
        }},
    ]
}


def test_pravil_i_zapisey_nazvany_porozn(monkeypatch, repo, capsys):
    """ГЛАВНЫЙ СЛУЧАЙ 178, и он про СВОЁ чтение, а не про природу данных.

    Одно правило держат двое соседей: правил решено 1, а записей об этом 2.
    Читатель, сложивший числа по проектам, получит 2 и объяснит расхождение
    тем, что источники меряют разное, — самым дорогим объяснением из
    возможных. Дешёвая гипотеза «считаем одну величину дважды» закрывается
    печатью числа уникальных идентификаторов рядом с числом строк.
    """
    с_соседями(monkeypatch, repo, ничем(), ДВОЕ)

    assert cb.main() == 0
    out = capsys.readouterr().out
    assert "решено у соседа: правил 1" in out
    assert "записей 2" in out


def test_bez_rashozhdeniya_lishnego_ne_pechataetsya(monkeypatch, repo, capsys):
    """Обратная половина: когда чисел не два, а одно, второе не выдумывается.
    Лишняя скобка в каждой строке приучила бы её не читать (051)."""
    с_соседями(monkeypatch, repo, ничем())

    assert cb.main() == 0
    out = capsys.readouterr().out
    assert "решено у соседа: правил 1" in out
    assert "записей" not in out


# ── у «none» спрашивается разбор надвое (правило 182) ───────────────────────

def без_разбора(why: str = "требует суждения: понимание, а не форма") -> dict:
    return {"project": "мой/каталог",
            "rules": {"001": {"status": "active", "mechanism": "none",
            "holdable": "no",
                              "where": "нигде", "why": why}}}


def test_none_bez_razbora_nadvoe_otkaz(monkeypatch, repo, capsys):
    """ГЛАВНЫЙ СЛУЧАЙ 182, и он про ЧЕСТНЫЙ ответ, а не про отписку.

    Причина есть и она подробная — именно поэтому её никто не перепроверяет.
    Замер 4 сентября: 158, 170 и 144 простояли месяцами с такими причинами и
    закрылись за один заход, потому что лёгкая половина лежала рядом.
    """
    prepare(monkeypatch, repo, без_разбора(), export_of("001"))

    assert cb.main() == 1
    assert "разбора надвое нет" in capsys.readouterr().err


def test_s_razborom_chisto(monkeypatch, repo, capsys):
    ответ = без_разбора()
    ответ["rules"]["001"]["machine_half"] = (
        "есть, но нашла бы пустоту: предмета в дереве нет ни одного (146)")
    prepare(monkeypatch, repo, ответ, export_of("001"))

    assert cb.main() == 0


def test_mehanizm_est_razbor_ne_sprashivaetsya(monkeypatch, repo, capsys):
    """ГРАНИЦА: у ответа С механизмом делить нечего — вопрос «что из этого
    машинно» уже отвечен самим механизмом, и красное на нём было бы ложным
    отказом (051)."""
    гейт(repo, '"""Сторож. Реализует правила каталога:\n  001 — предмет.\n"""\n')
    ответ = без_разбора()
    ответ["rules"]["001"]["mechanism"] = "gate"
    ответ["rules"]["001"]["where"] = "scripts/страж.py"
    prepare(monkeypatch, repo, ответ, export_of("001"))

    assert cb.main() == 0



# ── `document` РАЗБИРАЕТСЯ НАДВОЕ ─────────────────────────────────────────

def документом(поля: dict | None = None) -> dict:
    """Ответ «держится документом» с произвольными добавками."""
    запись = {"status": "active", "mechanism": "document",
              "where": "AGENTS.md — сказано в своде"}
    запись.update(поля or {})
    return {"rules": {"001": запись}}


def test_document_bez_razbora_nadvoe_otkaz(monkeypatch, repo, capsys):
    """ГЛАВНЫЙ СЛУЧАЙ контракта 1.3: предмет тот же, что у `none`.

    Правило действует, машина его не держит — и до подъёма у `document` не
    спрашивалось ничего, хотя у `none` разбор обязателен с 4 сентября.
    """
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo, документом(), export_of("001"))

    assert cb.main() == 1
    assert "машина этого не держит, а можно ли" in capsys.readouterr().err


def test_document_chuzhoe_slovo_otkaz(monkeypatch, repo, capsys):
    """Словарь ЗАКРЫТЫЙ: счётчику семьи знаменатель надо разделить, а «почти
    невозможно» не складывается ни с чем."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            документом({"holdable": "почти невозможно", "why": "так вышло"}),
            export_of("001"))

    assert cb.main() == 1
    assert "машина этого не держит, а можно ли" in capsys.readouterr().err


def test_document_slovo_bez_prichiny_otkaz(monkeypatch, repo, capsys):
    """Слово из двух выбирается не думая — причину не написать, не подумав (154).

    Красная сторона показана подделкой: вердикт стоит, причины нет.
    """
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo, документом({"holdable": "not-yet"}),
            export_of("001"))

    assert cb.main() == 1
    assert "`holdable` есть, а причины нет" in capsys.readouterr().err


def test_document_s_razborom_chisto(monkeypatch, repo):
    """Зелёная сторона: оба слова законны и оба идут с причиной (140)."""
    write(repo / "AGENTS.md", "свод\n")
    for слово in ("no", "not-yet"):
        prepare(monkeypatch, repo,
                документом({"holdable": слово,
                            "why": "половина названа, а не выдана за отсутствие"}),
                export_of("001"))
        assert cb.main() == 0, слово


def test_razbor_ne_sprashivaetsya_u_sosednih_mehanizmov(monkeypatch, repo):
    """ГРАНИЦА: предмет поля — только `document`.

    У `gate` и `pipeline` вопрос «что здесь машинно» отвечен самим механизмом,
    и красное там было бы ложным отказом (051).
    """
    write(repo / ".github" / "workflows" / "ci.yml",
          "# держит правило 001\non: push\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "pipeline",
                               "where": ".github/workflows/ci.yml — прогон"}}},
            export_of("001"))
    assert cb.main() == 0


# ── ДВЕ ДАТЫ: ФОРМА И ПОРЯДОК ─────────────────────────────────────────────
#
# Набор двусторонний (140). `analysed` — когда запись сверяли с деревом;
# `decided` — когда вынесен НЫНЕШНИЙ вердикт. Перечитали и подтвердили —
# двигается первая и не двигается вторая; сменился вердикт — двигаются обе.
# Отсюда и то, что гейт обязан отвергнуть: дату, которой не бывает, дату из
# будущего и вердикт, вынесенный ПОЗЖЕ последнего взгляда на дерево.

def датой(поля: dict) -> dict:
    """Ответ «держится документом» с датами."""
    return документом({"holdable": "no", "why": "половина названа", **поля})


@pytest.mark.parametrize("значение", ["16.09.2026", "Sep 16 2026", "2026-9-16",
                                      "вчера", "2026-13-40"])
def test_data_ne_iso_otkaz(monkeypatch, repo, capsys, значение):
    """Даты сравнивает машина, а «16.09» и «Sep 16» она сравнить не может."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo, датой({"analysed": значение}), export_of("001"))

    assert cb.main() == 1
    assert "не дата вида ГГГГ-ММ-ДД" in capsys.readouterr().err


def test_data_iz_budushchego_otkaz(monkeypatch, repo, capsys):
    """Сверка, которой ещё не было, записана как бывшая."""
    write(repo / "AGENTS.md", "свод\n")
    завтра = (_dt.date.today() + _dt.timedelta(days=1)).isoformat()
    prepare(monkeypatch, repo, датой({"analysed": завтра}), export_of("001"))

    assert cb.main() == 1
    assert "в будущем" in capsys.readouterr().err


def test_verdikt_bez_sverki_otkaz(monkeypatch, repo, capsys):
    """Вынести вердикт, не посмотрев на дерево, нельзя."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo, датой({"decided": "2026-09-10"}), export_of("001"))

    assert cb.main() == 1
    assert "вердикт датирован, а сверка — нет" in capsys.readouterr().err


def test_verdikt_novee_sverki_otkaz(monkeypatch, repo, capsys):
    """Решают, посмотрев: `decided` не может быть позже `analysed`."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            датой({"analysed": "2026-09-10", "decided": "2026-09-16"}),
            export_of("001"))

    assert cb.main() == 1
    assert "новее сверки" in capsys.readouterr().err


def test_sverili_i_podtverdili_chisto(monkeypatch, repo):
    """ГЛАВНЫЙ ЗЕЛЁНЫЙ СЛУЧАЙ: перечитали сегодня, вердикт стоит с прошлого раза.

    Ровно это и разводит две даты: без них «сверено вчера» и «решено в августе
    и с тех пор никто не смотрел» выглядят одинаково.
    """
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            датой({"analysed": "2026-09-16", "decided": "2026-09-01"}),
            export_of("001"))

    assert cb.main() == 0


def test_bez_dat_chisto_no_nazvano(monkeypatch, repo, capsys):
    """Отсутствие даты — законный ответ «не сверяли», и он ПЕЧАТАЕТСЯ числом.

    Пустое поле не выдаётся за свежее: не спрошенное не идёт в чистое (039).
    """
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo, датой({}), export_of("001"))

    assert cb.main() == 0
    assert "дата есть у 0, нет у 1" in capsys.readouterr().out


def test_pri_uslovii_bez_sobytiya_otkaz(monkeypatch, repo, capsys):
    """«При условии» без предмета неотличимо от долга на «когда-нибудь» (146)."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            документом({"holdable": "conditional", "why": "предмета пока нет"}),
            export_of("001"))

    assert cb.main() == 1
    assert "без события" in capsys.readouterr().err


def test_pri_uslovii_s_sobytiem_chisto(monkeypatch, repo):
    """Зелёная сторона: событие названо, и это очередь с условием, а не долг."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            документом({"holdable": "conditional",
                        "why": "предмета пока нет: гейт зеленел бы вокруг пустоты",
                        "awaiting": "проектов с этим предметом сейчас 1, на одном признак не отличить от совпадения"}),
            export_of("001"))

    assert cb.main() == 0


# ── отказ по замеру — четвёртое слово (213, контракт 1.6) ─────────────────

def test_otkaz_bez_zamera_otkaz(monkeypatch, repo, capsys):
    """«Отказались» без замера неотличимо от «не смотрели» (213)."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            документом({"holdable": "refused",
                        "why": "решение 008 разрешает хвост мелких правок"}),
            export_of("001"))

    assert cb.main() == 1
    assert "без замера" in capsys.readouterr().err


def test_otkaz_s_zamerom_chisto_i_ne_dolg(monkeypatch, repo, capsys):
    """Зелёная сторона: замер назван, и отказ считается СВОИМ числом —
    не долгом «не построено» и не «держать нельзя»."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            документом({"holdable": "refused",
                        "why": "решение 008 разрешает хвост мелких правок одним изменением",
                        "machine_half": "компоненты связности по коммитам ветки: по 25 "
                                        "слитым распались 6, и каждое шестое разрешено 008"}),
            export_of("001"))

    assert cb.main() == 0
    вышло = capsys.readouterr().out
    assert "отказано по замеру у 1" in вышло
    assert "не построено у 0" in вышло
    assert "держать нельзя у 0" in вышло


def test_ne_postroennoe_pechataetsya_v_stupeni_nol(monkeypatch, repo, capsys):
    """Число видно СО СТОРОНЫ, иначе счёт по семье врёт молча.

    Печатается всегда — числа, видного лишь при поломке, здесь не бывает (027).
    """
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            документом({"holdable": "not-yet", "why": "построили бы счёт"}),
            export_of("001"))

    assert cb.main() == 0
    вышло = capsys.readouterr().out
    assert "не держится машиной: 1" in вышло
    assert "не построено у 1" in вышло


def test_nerazobrannoe_ne_zachislyaetsya_v_nevozmozhnoe(monkeypatch, repo, capsys):
    """Находка ревью #478: запись без ответа уезжала в «половины нет».

    Тот же прогон её ОТВЕРГАЕТ находкой — и тут же печатал число, в котором она
    стоит разобранной. Две половины одного прогона говорили о ней разное, а
    читают печатное (075). Не спрошенное не выдаётся за чистое (039).
    """
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo, документом(), export_of("001"))

    assert cb.main() == 1
    вышло = capsys.readouterr().out
    assert "держать нельзя у 0" in вышло
    assert "вердикт не разобран: 1" in вышло


def test_chuzhoe_slovo_tozhe_bez_razbora(monkeypatch, repo, capsys):
    """Слово вне словаря — тоже «не спрошено», а не «невозможно»."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            документом({"holdable": "почти", "why": "так вышло"}),
            export_of("001"))

    assert cb.main() == 1
    assert "вердикт не разобран: 1" in capsys.readouterr().out


def test_slovo_bez_prichiny_tozhe_bez_razbora(monkeypatch, repo, capsys):
    """Находка ревью #481: вторая половина того же расхождения.

    Гейт отвергает запись двумя условиями, а счёт смотрел только на первое:
    слово законное, причины нет — прогон отвергал её и тут же печатал
    разобранной. Приёмка теперь одна на обоих (022).
    """
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo, документом({"holdable": "no"}),
            export_of("001"))

    assert cb.main() == 1
    вышло = capsys.readouterr()
    assert "`holdable` есть, а причины нет" in вышло.err
    assert "держать нельзя у 0" in вышло.out
    assert "вердикт не разобран: 1" in вышло.out


def test_smeshannyy_sluchay_schitaetsya_po_zapisyam(monkeypatch, repo, capsys):
    """Разобранная и неразобранная рядом: счёт по каждой, а не по остатку."""
    write(repo / "AGENTS.md", "свод\n")
    ответ = {"rules": {
        "001": {"status": "active", "mechanism": "document",
                "where": "AGENTS.md — сказано в своде",
                "holdable": "not-yet", "why": "построили бы счёт"},
        "002": {"status": "active", "mechanism": "document",
                "where": "AGENTS.md — сказано в своде",
                "holdable": "no"},
    }}
    prepare(monkeypatch, repo, ответ, export_of("001", "002"))

    assert cb.main() == 1
    вышло = capsys.readouterr().out
    assert "не держится машиной: 2" in вышло
    assert "держать нельзя у 0" in вышло
    assert "не построено у 1" in вышло
    assert "вердикт не разобран: 1" in вышло


# ── ОТЛОЖЕННОЕ ПРОТИВ ДОЛГА ───────────────────────────────────────────────
# Поле `awaiting` выводит правило из ступени 0, а значит само становится
# лазейкой: припиской «построим потом» долг обнулялся бы даром. Три машинных
# правила заведены одним заходом — исключение из долга, запрет при названном
# механизме, требование замера — и каждое стоит здесь парой (140).
# Находка внешнего ревью на #367: первая редакция ушла БЕЗ этих случаев, и
# двусторонность держалась прогоном автора, а не механизмом.

ОТЛОЖЕНО = ("первого эпика: контейнеров ноль, открытых задач три, "
            "дочерних нет ни у одной")


def test_otlozhennoe_vyvoditsya_iz_dolga(monkeypatch, repo, capsys):
    """Механизма нет, но событие названо и предмет измерен — это не долг."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
            "holdable": "no",
                               "where": "строить не на чем",
                               "why": "предмета нет",
                               "machine_half": "есть, но нашла бы пустоту",
                               "awaiting": ОТЛОЖЕНО}}},
            export_of("001"))
    assert cb.main() == 0
    out = capsys.readouterr().out
    assert "держится ничем 0" in out
    assert "отложено до появления предмета: 1" in out


def test_otlozhennoe_bez_zamera_eto_nahodka(monkeypatch, repo, capsys):
    """«Построим потом» — обещание, а не замер: число обязательно."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
            "holdable": "no",
                               "where": "строить не на чем",
                               "why": "предмета нет",
                               "machine_half": "есть, но нашла бы пустоту",
                               "awaiting": "построим потом, когда дойдут руки"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "отсутствие предмета не измерено" in capsys.readouterr().err


def test_awaiting_pri_gotovom_mehanizme_eto_nahodka(monkeypatch, repo, capsys):
    """Поле значит «ждём предмета»; рядом с механизмом оно утверждает неправду."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/check_bindings.py",
                               "awaiting": ОТЛОЖЕНО}}},
            export_of("001"))
    assert cb.main() == 1
    assert "механизм краснеет, а поле awaiting осталось" in capsys.readouterr().err


# ── ОТВЕТ «ГЕЙТ» УКАЗЫВАЕТ НА ИСПОЛНЯЕМОЕ (139) ───────────────────────────
# Замер на живом дереве: 113 ответов gate, 12 без скрипта, и все двенадцать
# называют другой законный вид. Находок ноль — поэтому набор здесь не роскошь,
# а единственное место, где проверка вообще ОТВЕРГАЕТ: без него гейт зеленел бы
# и на собственной поломке (140, 146).

@pytest.mark.parametrize("адрес, что", [
    ("scripts/check_bindings.py", "скрипт"),
    (".github/workflows/ci.yml", "прогон"),
    ("tests/test_check_bindings.py", "набор тестов"),
    ("action.yml", "составное действие"),
    (".claude/settings.json", "хук окна"),
])
def test_gate_ukazyvayushchiy_na_ispolnyaemoe_prohodit(monkeypatch, repo, адрес, что):
    """Все пять видов законны. Файл создаётся: соседняя проверка требует, чтобы
    заявленное СУЩЕСТВОВАЛО, и без этого случай проверял бы её, а не 139."""
    # НОМЕР ПРАВИЛА СТОИТ И В НЕ-PYTHON АДРЕСЕ. Случай про 139 — «ответ
    # gate указывает на исполняемое», — но рядом живёт проверка 183:
    # названный механизм обязан о правиле упоминать. Без номера случай
    # спотыкался бы о соседнюю проверку и краснел не по своему предмету.
    содержимое = ('"""Проба.\n\nРеализует правила каталога:\n'
                  '  001 — держит его целиком.\n"""\n'
                  if адрес.endswith(".py") else "# проба: держит правило 001\n")
    write(repo / адрес, содержимое)
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": f"{адрес} — держит правило"}}},
            export_of("001"))
    assert cb.main() == 0, что


# ── 183 ВНЕ scripts/: механизм, не знающий, что он чей-то ──────────────────
#
# ЗАМЕР 8 сентября: активных ответов с механизмом 155, и прежний образец
# `scripts/*.py` сверял 110. Остальные 45 не проверялись ничем — прогон, набор
# или хук могли не иметь к правилу никакого отношения. Ровно этот класс —
# инцидент у соседа: ответ по 085 назвал механизмом tests/test_ai_grounding.py,
# где 12 случаев и ни одного про недоверенный вход.

@pytest.mark.parametrize("адрес", [
    ".github/workflows/ci.yml",
    "tests/test_probe.py",
    ".claude/hooks/probe.py",
])
def test_mehanizm_vne_scripts_bez_upominaniya_otvergaetsya(monkeypatch, repo, адрес):
    """РОВНО ПРЕДМЕТ ПРАВИЛА: файл назван механизмом и о правиле молчит."""
    write(repo / адрес, "# проба без единого номера\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": f"{адрес} — держит правило"}}},
            export_of("001"))

    assert cb.main() == 1, адрес


def test_mehanizm_vne_scripts_s_upominaniem_prohodit(monkeypatch, repo):
    """Граница с другой стороны: гейт обязан УМЕТЬ промолчать. До расширения
    он молчал на любом таком входе — и потому не проверял ничего (140)."""
    write(repo / ".github/workflows/ci.yml", "# держит правило 001\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": ".github/workflows/ci.yml — держит"}}},
            export_of("001"))

    assert cb.main() == 0


def test_nastroyka_bez_prozy_ne_predmet(monkeypatch, repo):
    """.json исключён намеренно: в настройке прозы нет вовсе, и номер туда
    писать некуда — требование было бы отказом на пустом месте (051)."""
    write(repo / ".claude/settings.json", '{"hooks": {}}\n')
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": ".claude/settings.json — объявляет хук"}}},
            export_of("001"))

    assert cb.main() == 0


@pytest.mark.parametrize("where, что", [
    ("держится договорённостью окна", "проза вместо адреса"),
    ("описано в документе, который читают глазами", "документ — не гейт"),
    ("", "пустое поле"),
])
def test_gate_bez_ispolnyaemogo_eto_nahodka(monkeypatch, repo, capsys, where, что):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": where}}},
            export_of("001"))
    assert cb.main() == 1, что
    assert "не назван ни один исполняемый адрес" in capsys.readouterr().err


def test_document_s_prozoy_nahodkoy_ne_yavlyaetsya(monkeypatch, repo):
    """Требование адресовано ответу «гейт», а не всякому ответу (051)."""
    write(repo / "AGENTS.md", "свод\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "document",
                               "where": "AGENTS.md — сказано в своде",
                               "holdable": "no",
                               "why": "предмет не в дереве"}}},
            export_of("001"))
    assert cb.main() == 0


def test_несобранное_производное_декларацией_не_расходится(monkeypatch, repo):
    """Инцидент 8 сентября: свежий клон, сборщик в нём ещё не запускался.

    `export/where.json` в общей ветке не лежит вовсе — его пересобирает прогон
    и держит на своей ветке (`check_derived.OWNED_BY_JOB`). Отказ здесь означал
    бы, что вердикт о ЧУЖОЙ декларации зависит от того, гоняли ли в этой копии
    сборщик (037), — а ступень 0 спрашивается с каталога первой же командой
    нового окна.
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "pipeline",
                               "where": "ответ соседа лежит в export/where.json"}}},
            export_of("001"))
    assert not (repo / "export" / "where.json").exists()
    assert cb.main() == 0


def test_ступень_ноль_печатается_и_без_собранного_производного(
        monkeypatch, repo, capsys):
    """Три числа ступени 0 печатаются ВСЕГДА — так объявляет 177.

    Молчание было дороже самих ложных находок: окно, которому свод велит
    начинать со ступени 0, не получало её вовсе — ни одного из трёх чисел.
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "pipeline",
                               "where": "сводка export/where.json"}}},
            export_of("001"))
    cb.main()
    assert "ступень 0" in capsys.readouterr().out


def test_соседнее_имя_производного_остаётся_находкой(monkeypatch, repo, capsys):
    """Освобождён поимённо названный путь, а не каталог `export/`.

    Список закрытый и разрешительный (068): имя, которого никто не собирает,
    ревизия обязана отвергать по-прежнему — иначе она перестала бы держать то,
    ради чего заведена (146).
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "pipeline",
                               "where": "сводка export/where-nobody-builds.json"}}},
            export_of("001"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "where-nobody-builds.json" in err and "разошлась с фактом" in err


def test_ступень_ноль_печатается_и_вместе_с_настоящей_находкой(
        monkeypatch, repo, capsys):
    """Находка о ЧУЖОЙ декларации не отменяет вопроса о долге по правилам.

    Находка внешнего взгляда на изменении #402: докстрока `tier_zero` обещает
    «ПЕЧАТАЮТСЯ ВСЕГДА, включая нули», а `main()` при непустом `problems`
    возвращал 1 раньше вызова — и обещание было неверно по коду при ЛЮБОЙ
    находке, а не только при снятой в этом же изменении. Числа и находки
    отвечают на разные вопросы (027, 041), и первое не гасит второго.
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/выдумка.py"}}},
            export_of("001"))
    assert cb.main() == 1
    out = capsys.readouterr()
    assert "разошлась с фактом" in out.err
    assert "ступень 0" in out.out


def test_проекция_на_ветку_badges_декларацией_не_расходится(monkeypatch, repo):
    """Инцидент 8 сентября: ответ по 174 назвал `.github/badges/facts.json`.

    Файл там и лежит — на ветке `badges`, куда его уносит `badges.yml`. В общей
    ветке содержимого этого каталога нет вовсе, и отсутствие пути говорит о
    ВЕТКЕ, а не о декларации (160). Обязательная проверка на этом краснела.
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "pipeline",
                               "where": "публикуем .github/badges/facts.json"}}},
            export_of("001"))
    assert not (repo / ".github" / "badges" / "facts.json").exists()
    assert cb.main() == 0


def test_за_пределами_проекции_имя_остаётся_находкой(monkeypatch, repo, capsys):
    """Освобождён названный каталог, а не всё, что похоже на него (068)."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "pipeline",
                               "where": "публикуем .github/badges-нет/facts.json"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "разошлась с фактом" in capsys.readouterr().err


# ── навык: адрес, ревизия дерева и два числа ─────────────────────────────
#
# ПОЧЕМУ ЭТО ПРОВЕРЯЕТСЯ ТЕСТАМИ, А НЕ ЖИВЫМ ОТВЕТОМ. Навыков в дереве
# каталога сегодня нет ни одного, и ни один его ответ поля `skill` не несёт —
# то есть предмет здесь нулевой, и гейт на живых данных зеленел бы, ничего не
# держа (146). Предмет у механизма при этом ЕСТЬ и он чужой: проект механизмов
# держит навыком половину ответов на 047 и 082. Поэтому отказ прогоняется тем,
# что он обязан отвергнуть (140, 145), а не ожиданием первой записи.

def навык_в(repo: Path, имя: str, *, name: str | None = None,
            description: str = "что делает и когда звать") -> None:
    write(repo / ".claude" / "skills" / имя / "SKILL.md",
          f"---\nname: {имя if name is None else name}\n"
          f"description: {description}\n---\n\n# Навык\n")


def test_навык_без_адреса_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": ".claude/skills/probe/SKILL.md — держит"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "каким — не сказано" in capsys.readouterr().err


def test_проза_вместо_адреса_навыка_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": ".claude/skills/probe/SKILL.md — держит",
                               "skill": "навык перечитывания свода"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "это не адрес" in capsys.readouterr().err


def test_навык_при_механизме_ничем_это_противоречие(monkeypatch, repo, capsys):
    навык_в(repo, "probe")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
            "holdable": "no",
                               "where": "CLAUDE.md — раздел про окна",
                               "why": "требует суждения",
                               "machine_half": "ничего не следует из данных",
                               "skill": ".claude/skills/probe"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "оба утверждения" in capsys.readouterr().err


def test_объявленного_навыка_может_не_быть_в_дереве(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": ".claude/skills/probe/SKILL.md — держит",
                               "skill": ".claude/skills/probe"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "SKILL.md нет" in capsys.readouterr().err


def test_навык_без_описания_это_находка(monkeypatch, repo, capsys):
    навык_в(repo, "probe", description="")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": ".claude/skills/probe/SKILL.md — держит",
                               "skill": ".claude/skills/probe"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "`description`" in capsys.readouterr().err


def test_имя_навыка_обязано_совпасть_с_каталогом(monkeypatch, repo, capsys):
    навык_в(repo, "probe", name="совсем-другое")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": ".claude/skills/probe/SKILL.md — держит",
                               "skill": ".claude/skills/probe"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "расходятся молча" in capsys.readouterr().err


def test_целый_навык_проходит(monkeypatch, repo):
    навык_в(repo, "probe")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": ".claude/skills/probe/SKILL.md — держит",
                               "skill": ".claude/skills/probe"}}},
            export_of("001"))
    assert cb.main() == 0


def навык_плагина_в(repo: Path, плагин: str, имя: str) -> None:
    write(repo / "plugins" / плагин / "skills" / имя / "SKILL.md",
          f"---\nname: {имя}\ndescription: что делает и когда звать\n---\n\n# Навык\n")


def test_навык_плагина_каталога_проходит(monkeypatch, repo):
    """Контракт 1.7: навык называется так же, как зовётся, — `<плагин>:<имя>`."""
    навык_плагина_в(repo, "catalogue", "probe")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": "plugins/catalogue/skills/probe/SKILL.md — держит",
                               "skill": "catalogue:probe"}}},
            export_of("001"))
    assert cb.main() == 0


def test_навыка_плагина_нет_в_дереве_каталога(monkeypatch, repo, capsys):
    """Плагинный навык сверяется с деревом каталога: названный и отсутствующий —
    обещание, а не механизм, как и навык окна."""
    навык_плагина_в(repo, "catalogue", "probe")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": "plugins/catalogue/skills/probe/SKILL.md — держит",
                               "skill": "catalogue:missing"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "plugins/catalogue/skills/missing/SKILL.md нет" in capsys.readouterr().err


def test_плагина_нет_вовсе(monkeypatch, repo, capsys):
    навык_плагина_в(repo, "catalogue", "probe")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": "plugins/catalogue/skills/probe/SKILL.md — держит",
                               "skill": "elsewhere:probe"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "plugins/elsewhere/skills/probe/SKILL.md нет" in capsys.readouterr().err


def test_навык_второй_половиной_при_гейте_законен(monkeypatch, repo, capsys):
    # ГЛАВНЫЙ СЛУЧАЙ: гейт берёт машинную половину, навык — остаток. Оба
    # объявлены, и ни один не спрятан. Именно так отвечает проект механизмов.
    write(repo / "scripts/check_probe.py",
          '"""Проба.\n\nРеализует правила каталога:\n  001 — держит половину.\n"""\n')
    навык_в(repo, "probe")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/check_probe.py — машинная половина",
                               "skill": ".claude/skills/probe"}}},
            export_of("001"))
    assert cb.main() == 0
    напечатано = capsys.readouterr().out
    assert "держится навыком: 1" in напечатано
    assert "второй половиной при другом механизме у 1" in напечатано


def test_навык_целиком_и_половиной_считаются_порознь(monkeypatch, repo, capsys):
    # Сложить их значило бы повторить `process-step`: одно число о двух
    # разных состояниях — машинного отказа нет вовсе против «он есть и покрывает часть».
    write(repo / "scripts/check_probe.py",
          '"""Проба.\n\nРеализует правила каталога:\n  002 — держит половину.\n"""\n')
    навык_в(repo, "alpha")
    навык_в(repo, "beta")
    prepare(monkeypatch, repo,
            {"rules": {
                "001": {"status": "active", "mechanism": "skill",
                "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                        "where": ".claude/skills/alpha/SKILL.md — держит целиком",
                        "skill": ".claude/skills/alpha"},
                "002": {"status": "active", "mechanism": "gate",
                        "where": "scripts/check_probe.py — машинная половина",
                        "skill": ".claude/skills/beta"}}},
            export_of("001", "002"))
    assert cb.main() == 0
    напечатано = capsys.readouterr().out
    assert "целиком у 1, второй половиной при другом механизме у 1" in напечатано
    assert "навыком 1" in напечатано


# ── СЛОВАРЬ МЕХАНИЗМОВ ОДИН, ЧИТАТЕЛЕЙ У НЕГО ШЕСТЬ ──────────────────────
#
# ПОЧЕМУ ЭТО ОТКАЗ, А НЕ ВНИМАТЕЛЬНОСТЬ. Заводя `skill`, окно обновило пять
# мест из шести: `MECHANISM_RU` (aggregate_bindings.py:344) и `MECHANISM_HEAD`
# (там же, :353) лежат в одном файле в девяти строках друг от друга, и обновлён
# был только второй. Ни один прогон этого не
# видел — `.get(mech, mech)` не падает, а откатывается на сырое значение, и в
# русской колонке «Чем держат другие» встало бы английское `skill`. Поймал
# внешний взгляд на PR #497, а не прогон.
#
# Канон живёт здесь, в check_bindings; все шестеро обязаны его покрывать. Тест
# держит не форму словарей — они разные по построению: `MECHANISM_HEAD`
# двуязычен, `MECHANISM_RU` даёт русское существительное, палитра даёт цвет, —
# а ПОЛНОТУ. Седьмое значение теперь нельзя добавить наполовину (022, 183).

def test_каждый_механизм_назван_всеми_читателями_словаря():
    import aggregate_bindings as ab
    import consumers_picture as cp

    for мех in cb.MECHANISM_ORDER:
        assert мех in ab.MECHANISM_HEAD, f"{мех}: нет подписи колонки where.md"
        assert мех in cp.LANG["ru"], f"{мех}: нет русского слова витрины"
        assert мех in cp.LANG["en"], f"{мех}: нет английского слова витрины"
        for тёмная in (False, True):
            assert мех in cp.THEME[тёмная], f"{мех}: нет цвета витрины"
    # `none` в «чем держат» не попадает намеренно: это не механизм, а его
    # отсутствие, и сказать в разделе ему нечего. Спрашивается с остальных.
    for мех in cb.MECHANISM_ORDER:
        if мех == "none":
            assert мех not in ab.MECHANISM_RU
            continue
        assert мех in ab.MECHANISM_RU, f"{мех}: нет имени в разделе «чем держат»"


def test_чужой_механизм_навык_назван_по_русски():
    """Поведение, а не словарь: раздел печатает «навык», а не сырое `skill`."""
    import aggregate_bindings as ab

    строки = ab._how_others_enforce(
        [{"repo": "чужой/проект", "holds": {
            "001": {"mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                    "where": ".claude/skills/probe/SKILL.md"}}},
         {"repo": "другой/проект", "holds": {"001": {"mechanism": "none"}}}])
    текст = "\n".join(строки)
    assert "навык" in текст
    assert "— skill:" not in текст


# ── СВЁРНУТОЕ ОПИСАНИЕ: ЗАГОЛОВОК БЛОКА — НЕ ЗНАЧЕНИЕ ───────────────────
#
# ПОЛОМКА, ИЗ КОТОРОЙ ЭТО ВЫРОСЛО (находка ревью на #497). Разбор брал `>-` за
# непустое значение и продолжения не читал: навык с ПУСТЫМ свёрнутым описанием
# гейт проходил, а навык с настоящим — проходил по неверной причине. Граница
# «свёрнутые блоки принимаются по отступу следующей строки» стояла в
# комментарии и не стояла в коде (183).
#
# Случаи взяты формами YAML, а не догадкой: `>` и `|`, с отсечкой и с отступом,
# и В ОБОИХ ПОРЯДКАХ индикаторов — `>-2` и `>2-` равно законны по YAML 1.2.
# Второй порядок регэксп сперва пропускал, и на нём поломка воспроизводилась
# целиком (находка ревью #500). Формы сверены с PyYAML, а не со спецификацией
# по памяти: четырнадцать заголовков и семь не-заголовков.

#: Узкий разбор — ровно по спецификации: одна цифра 1–9. Определён здесь, а не
#: в гейте: он существует только затем, чтобы ЦЕНА сужения была видна числом.
УЗКИЙ = re.compile(r"^[|>](?:[+-][1-9]?|[1-9][+-]?)?$")

#: Формы, названные в границе `check_bindings.БЛОЧНЫЙ_RE`. Списки здесь ПОЛНЫЕ
#: и совпадают с теми, что названы там: неполный список под фразой «обе
#: половины закреплены» — то же самое «объявленное шире исполняемого», которое
#: эта правка и разбирает (находка ревью #502).
ВНЕ_СПЕЦИФИКАЦИИ = (">0", "|0", ">23", ">-10", "|+12", ">99")
ЗАКОННЫЕ = (">", "|", ">-", ">2", ">2-", ">-2", "|1+", ">9")


def скилл(repo: Path, текст: str) -> None:
    write(repo / ".claude" / "skills" / "probe" / "SKILL.md", текст)


def ответ_на_навык(monkeypatch, repo: Path, capsys) -> str:
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "skill",
            "holdable": "no", "why": "навык не краснеет: машинной половины нет",
                               "where": ".claude/skills/probe/SKILL.md — держит",
                               "skill": ".claude/skills/probe"}}},
            export_of("001"))
    код = cb.main()
    return "ПРИНЯТ" if код == 0 else capsys.readouterr().err


@pytest.mark.parametrize("заголовок", ЗАКОННЫЕ, ids=lambda з: з)
def test_свёрнутое_описание_с_текстом_принимается(monkeypatch, repo, capsys,
                                                  заголовок):
    """ВСЕ восемь законных форм — через гейт целиком, а не выборкой.

    Список тот же, что назван в границе `check_bindings.БЛОЧНЫЙ_RE`: раньше
    здесь стояли шесть форм из восьми, и голые `>` и `>9` через гейт не
    проходили ни разу (находка ревью #502).
    """
    скилл(repo, f"---\nname: probe\ndescription: {заголовок}\n  настоящее описание\n---\n")
    assert ответ_на_навык(monkeypatch, repo, capsys) == "ПРИНЯТ"


@pytest.mark.parametrize("форма", [
    "---\nname: probe\ndescription: >-\n---\n",
    "---\nname: probe\ndescription: |\n---\n",
    "---\nname: probe\ndescription: >2-\n---\n",
    "---\nname: probe\ndescription: |1+\n---\n",
], ids=["свёрнутый", "буквальный",
        "отступ-потом-отсечка", "буквальный-наоборот"])
def test_свёрнутое_описание_без_текста_это_находка(monkeypatch, repo, capsys, форма):
    """Заголовок блока без отступленных строк — пустое описание, а не значение."""
    скилл(repo, форма)
    assert "`description`" in ответ_на_навык(monkeypatch, repo, capsys)




# ── ЗАПАС ШИРЕ СПЕЦИФИКАЦИИ ДЕРЖИТСЯ НАРОЧНО ────────────────────────────
#
# ЭТО НЕ НЕДОСМОТР, А ИЗМЕРЕННОЕ РЕШЕНИЕ (находка ревью #501). Индикатор
# отступа в YAML — одна цифра 1–9, а `\d` пропускает `>0`, `>23`, `|+12`.
# Сузить до спецификации значило бы ухудшить: на ВОСЬМИ законных формах узкий
# и широкий разбор ведут себя одинаково, а на этих шести узкий ПРОПУСТИЛ БЫ
# битый файл — `">23"` для него непустая строка, то есть «описание есть».
# Широкому это заголовок: значение ищется ниже, ниже пусто, отказ.
#
# Тест стоит здесь, чтобы следующее окно не «починило» границу сужением, не
# заметив цены: предмет проверки — «описание непусто», а не «YAML безупречен».

@pytest.mark.parametrize("форма", ВНЕ_СПЕЦИФИКАЦИИ, ids=lambda ф: ф)
def test_заголовок_вне_спецификации_уводит_в_отказ(monkeypatch, repo, capsys, форма):
    """Битый YAML без продолжения отвергается, а не читается как описание."""
    скилл(repo, f"---\nname: probe\ndescription: {форма}\n---\n")
    assert "`description`" in ответ_на_навык(monkeypatch, repo, capsys)


@pytest.mark.parametrize("форма", ВНЕ_СПЕЦИФИКАЦИИ, ids=lambda ф: ф)
def test_узкий_разбор_пропустил_бы_эти_формы(форма):
    """Цена сужения: ВСЕ шесть форм широкий видит заголовком, узкий — нет."""
    assert cb.БЛОЧНЫЙ_RE.match(форма), f"{форма}: широкий обязан видеть заголовок"
    assert not УЗКИЙ.match(форма), (
        f"{форма}: узкий заголовка не видит — значит счёл бы строку значением")


@pytest.mark.parametrize("форма", ЗАКОННЫЕ, ids=lambda ф: ф)
def test_на_законных_формах_сужение_не_покупает_ничего(форма):
    """Вторая половина замера, и до сих пор она держалась только прозой.

    Утверждение «на восьми законных формах узкий и широкий ведут себя
    одинаково» стояло в границе и в журнале, а тестом не проверялось ни разу —
    то есть было ровно тем, что эта же правка называет дефектом (166).
    """
    assert bool(cb.БЛОЧНЫЙ_RE.match(форма)) == bool(УЗКИЙ.match(форма)), (
        f"{форма}: ширины разошлись — значит сужение что-то меняет, и довод "
        "«не покупает ничего» неверен")
