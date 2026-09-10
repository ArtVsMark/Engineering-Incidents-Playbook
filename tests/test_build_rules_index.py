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
