"""Выгрузка отдаёт правило, а не только его имя.

Предмет берётся из ЖИВОГО дерева (правило 170): случаи стоят на настоящих
записях каталога, а не на выдуманной форме. Инцидент, ради которого разбор
заведён, — задача #454: по заголовку 114 «Миграция идёт от текущей версии, а не
от нуля» потребитель построил механизм про объявление перехода, тогда как буква
требует идемпотентности ступени.
"""

from __future__ import annotations

import glob
from pathlib import Path

import build_rules_index as b


def запись(номер: str, lang: str = "ru") -> Path:
    """Путь к живой записи каталога по номеру."""
    (путь,) = glob.glob(f"rules/{lang}/{номер}-*.md")
    return Path(путь)


def test_bukva_ne_sovpadaet_s_zagolovkom():
    """Инцидент #454 целиком: заголовок задаёт направление, буква — предмет."""
    запись_114 = запись("114")
    заголовок = b.title_of(запись_114)
    буква = b.claim_of(запись_114, "ru")

    assert "от нуля" in заголовок          # направление миграции
    assert "только" in буква               # идемпотентность ступени
    assert "не проходило" in буква
    # То, ради чего поле заведено: по заголовку предмета не восстановить.
    assert "идемпотент" not in заголовок.lower()
    assert буква != заголовок


def test_bukva_beryotsya_na_oboikh_yazykah():
    assert "only" in b.claim_of(запись("114", "en"), "en")
    assert b.claim_of(запись("114", "ru"), "ru")


def test_granica_neset_obe_storony_i_perenosy():
    """Раздел о границе едет разметкой: два противопоставленных абзаца.

    Склеенный в строку, он читается как один довод — а это ровно то место,
    где потребитель решает «у нас это тоже действует».
    """
    граница = b.applies_of(запись("114"), "ru")
    assert "**Работает**" in граница
    assert "**Не работает**" in граница
    assert "\n" in граница                 # переносы сохранены намеренно
    assert not граница.startswith("##")    # заголовок раздела не едет


def test_bukva_shlopyvaet_perenosy():
    """Обратное решение для буквы: она сравнивается построчно у потребителя."""
    assert "\n" not in b.claim_of(запись("114"), "ru")


def test_zapis_bez_markera_daet_pusto(tmp_path):
    """Третий случай: маркера нет — поле пустое, а не выдуманное."""
    подделка = tmp_path / "999-нет-маркера.md"
    подделка.write_text("# Заголовок\n\n**Область.** код\n\nтекст\n", encoding="utf-8")
    assert b.claim_of(подделка, "ru") == ""
    assert b.applies_of(подделка, "ru") == ""


def test_vygruzka_neset_oba_polya_u_kazhdoy_zapisi():
    """Полнота: поле есть у ВСЕХ записей, иначе потребитель гадает, где повезло."""
    import json

    d = json.loads(Path("export/rules.json").read_text(encoding="utf-8"))
    assert d["schema"] == b.EXPORT_SCHEMA
    без_буквы = [r["id"] for r in d["rules"] if not r.get("claim", {}).get("ru")]
    без_границы = [r["id"] for r in d["rules"] if not r.get("applies", {}).get("ru")]
    assert без_буквы == [], f"без буквы: {без_буквы}"
    assert без_границы == [], f"без границы: {без_границы}"


# --- Взаимосвязь записей: объявленное уточнение и фактическая ссылка --------
#
# Два разных предмета, и разбор держит их порознь. «Уточняет» — суждение
# автора: эта буква сужает ту. Ссылка — факт: здесь стоит адрес той записи.
# Инцидент, ради которого разбор заведён: ревизия #456 нашла, что 057 говорит
# о 002 в обе стороны прозой и ссылкой, а сама 002 об этом не знает ничего —
# потребитель, читающий по номерам сверху вниз, первым встречает НЕуточнённую
# букву и строит по ней.


def подделка(tmp_path: Path, номер: str, тело: str) -> Path:
    """Запись-подделка для случаев, которых в живом дереве нет и быть не должно."""
    путь = tmp_path / f"{номер}-подделка.md"
    путь.write_text(тело, encoding="utf-8")
    return путь


МЕТКА = {"ru": "**Уточняет.**", "en": "**Refines.**"}


def дерево(tmp_path: Path,
           уточнения: dict[str, str | None],
           только_ru: set[str] = frozenset()) -> dict[str, dict[str, Path]]:
    """Оба дерева подделкой: номер → кого уточняет (None — пометки нет).

    Пометка пишется НА ЯЗЫКЕ ДЕРЕВА — иначе разбор проверял бы не цикл и не
    разрешимость, а собственную ошибку перевода: русский маркер в английском
    файле даёт «пометка разошлась» на любом случае. `только_ru` задаёт
    расхождение деревьев намеренно.
    """
    out: dict[str, dict[str, Path]] = {}
    for номер, цель in уточнения.items():
        out[номер] = {}
        for lang in b.LANGS:
            каталог = tmp_path / lang
            каталог.mkdir(exist_ok=True)
            путь = каталог / f"{номер}-подделка.md"
            строка = ("" if цель is None or (lang != "ru" and номер in только_ru)
                      else f"\n{МЕТКА[lang]} {цель}\n")
            путь.write_text(f"# З\n{строка}", encoding="utf-8")
            out[номер][lang] = путь
    return out


def test_utochnenie_chitaetsya_v_oboikh_derevyakh():
    """Живой случай: 057 объявляет себя границей 002 и по-русски, и по-английски."""
    assert b.refines_of(запись("057", "ru"), "ru") == "002"
    assert b.refines_of(запись("057", "en"), "en") == "002"
    assert b.refines_of(запись("149", "ru"), "ru") == "103"


def test_utochnyaemaya_zapis_ne_pravitsya():
    """Обратная сторона строится сборкой (120), а не пишется в 002 руками."""
    assert b.refines_of(запись("002", "ru"), "ru") is None
    assert "Уточняет" not in запись("002", "ru").read_text(encoding="utf-8")


def test_pometka_uzkaya_po_forme(tmp_path):
    """Вторая сторона набора: похожий текст пометкой НЕ становится."""
    похоже = "# З\n\n**Уточняет.** правило 002 в части гейтов\n"
    assert b.refines_of(подделка(tmp_path, "900", похоже), "ru") is None
    прозой = "# З\n\nЭта запись уточняет 002.\n"
    assert b.refines_of(подделка(tmp_path, "901", прозой), "ru") is None


def test_ssylka_vidna_i_v_razdele_sled():
    """Регрессия: две трети связей корпуса стоят в строке «Смежное:».

    Первая редакция обрывала чтение перед разделом «След» — и теряла 683
    ссылки из 1020, включая единственную ссылку 057 на 002.
    """
    известные = {"002", "057", "072", "103", "149"}
    assert "002" in b.mentions_of(запись("057", "ru"), "ru", известные)
    assert b.mentions_of(запись("149", "ru"), "ru", известные) == ["072", "103"]


def test_ssylkoy_schitaetsya_adres_a_ne_chislo(tmp_path):
    """Число в прозе, свой номер и чужое дерево — не связи."""
    тело = (
        "# З\n\n"
        "В каталоге 195 правил, и запись 002 названа здесь прозой.\n"
        "Ссылка на себя: [900](900-подделка.md).\n"
        "Чужое дерево: [002](https://example.invalid/rules/002-чужое.md).\n"
        "Настоящая связь: [103](103-a-side-effect-guard.md).\n"
    )
    известные = {"002", "103", "195", "900"}
    assert b.mentions_of(подделка(tmp_path, "900", тело), "ru", известные) == ["103"]


def test_ssylka_ne_perepryghivaet_cherez_abzats(tmp_path):
    """Адрес, процитированный обратными кавычками, связи не образует.

    Живой случай — 166: там `](адрес` стоит в перечислении, и жадный префикс
    склеивал его с настоящей ссылкой абзацем ниже.
    """
    тело = (
        "# З\n\n"
        "- цель ссылки записывается как `](адрес` либо `]: адрес`;\n\n"
        "Смежное: [103](103-a-side-effect-guard.md).\n"
    )
    assert b.mentions_of(подделка(tmp_path, "900", тело), "ru", {"103"}) == ["103"]


def test_zhivoy_katalog_prohodit_gate():
    """Первая сторона набора (140): на живом дереве гейт молчит."""
    found, _, _ = b.collect()
    assert b.check_refines(found) == []


def test_gate_molchit_na_zakonnoy_pometke(tmp_path):
    """Вторая половина набора рядом с красными: законная пара проходит."""
    found = дерево(tmp_path, {"900": "901", "901": None})
    assert b.check_refines(found) == []


def test_gate_lovit_ssylku_v_pustotu(tmp_path):
    found = дерево(tmp_path, {"900": "899"})
    (беда,) = b.check_refines(found)
    assert "899" in беда and "нет" in беда


def test_gate_lovit_utochnenie_samogo_sebya(tmp_path):
    found = дерево(tmp_path, {"900": "900"})
    (беда,) = b.check_refines(found)
    assert "само себя" in беда


def test_gate_lovit_koltso(tmp_path):
    """Кольцо: общей записи нет, порядок чтения не определён вовсе."""
    found = дерево(tmp_path, {"900": "901", "901": "900"})
    беды = b.check_refines(found)
    assert беды and all("цикл" in беда for беда in беды)


def test_gate_lovit_raskhozhdenie_derevev(tmp_path):
    """Пометка в одном дереве и не в другом — указатель расходится по языкам."""
    found = дерево(tmp_path, {"900": "901", "901": None}, только_ru={"900"})
    (беда,) = b.check_refines(found)
    assert "разошлась" in беда and "901" in беда


def test_vygruzka_neset_obe_storony_svyazi():
    """То, ради чего всё: потребитель видит связь с ЛЮБОЙ стороны."""
    import json

    d = json.loads(Path("export/rules.json").read_text(encoding="utf-8"))
    по = {r["id"]: r for r in d["rules"]}
    assert по["057"]["refines"] == "002"
    assert по["002"]["refined_by"] == ["057"]      # 002 не правилась ни на знак
    assert "refines" not in по["002"]
    assert "002" in по["057"]["mentions"]
    assert "057" in по["002"]["mentioned_by"]
