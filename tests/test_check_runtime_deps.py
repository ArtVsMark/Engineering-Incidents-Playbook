"""Окружение окна против окружения прогона: разрыв — находка, а не отказ.

Предмет берётся из ЖИВОГО дерева (правило 170): случаи строятся на реальных
скриптах каталога и реальном requirements-test.txt, а не на выдуманной форме
прогона. Подделка здесь только одна — временный скрипт с внешним импортом,
и она удаляется в том же тесте.
"""

from __future__ import annotations

import pytest

import check_runtime_deps as m

БЕЗ_УСТАНОВКИ = ("jobs:\n  catalogue:\n    steps:\n"
                 "      - run: python scripts/{s}\n")
С_УСТАНОВКОЙ = ("jobs:\n  catalogue:\n    steps:\n"
                "      - run: python -m pip install -r requirements-test.txt\n"
                "      - run: python scripts/{s}\n")
#: Ровно порядок из ci.yml на 7 сентября: гейт выше, установка ниже.
УСТАНОВКА_НИЖЕ = ("jobs:\n  catalogue:\n    steps:\n"
                  "      - run: python scripts/{s}\n"
                  "      - run: python -m pip install -r requirements-test.txt\n")


@pytest.fixture()
def с_внешним_импортом(tmp_path):
    """Скрипт, зовущий пакет не из стандартной библиотеки."""
    путь = m.ROOT / "scripts" / "_проба_зависимости.py"
    путь.write_text("import yaml\n", encoding="utf-8")
    yield путь.name
    путь.unlink(missing_ok=True)


def test_svoi_modul_i_stdlib_ne_predmet():
    """Гейт отвергает ВНЕШНИЙ пакет, а не всякий импорт (051)."""
    список, разобрано = m.находки(БЕЗ_УСТАНОВКИ.format(s="check_bindings.py"), m.ROOT)
    assert список == []
    assert разобрано == 1


def test_paket_bez_ustanovki_eto_nahodka(с_внешним_импортом):
    список, _ = m.находки(БЕЗ_УСТАНОВКИ.format(s=с_внешним_импортом), m.ROOT)
    assert len(список) == 1 and "yaml" in список[0]


def test_paket_s_ustanovkoy_chisto(с_внешним_импортом):
    assert m.находки(С_УСТАНОВКОЙ.format(s=с_внешним_импортом), m.ROOT)[0] == []


def test_ustanovka_nizhe_shaga_ne_spasaet(с_внешним_импортом):
    """ИНЦИДЕНТ 7 СЕНТЯБРЯ ЦЕЛИКОМ: пакет в работе есть, но ставится ниже.

    Первая редакция гейта считала «ставит ли работа» и на этом случае молчала —
    то есть зеленела ровно там, ради чего написана (146). Случай стоит здесь,
    чтобы правка не вернула прежнее поведение незаметно.
    """
    список, _ = m.находки(УСТАНОВКА_НИЖЕ.format(s=с_внешним_импортом), m.ROOT)
    assert len(список) == 1
    assert "к этому шагу пакет ещё не поставлен" in список[0]


def test_zhivoe_derevo_chisto():
    """На настоящем ci.yml разрывов нет — иначе конвейер уже был бы красным."""
    текст = (m.ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    список, разобрано = m.находки(текст, m.ROOT)
    assert разобрано > 0, "вызовы скриптов не найдены — разбор работ сломан"
    assert список == []


# ── имя модуля берётся из объявления, а не из словаря (022, задача #444) ────

def файл_зависимостей(tmp_path, строки: str) -> str:
    """Свой requirements рядом с деревом. Путь — относительный, как в прогоне."""
    путь = m.ROOT / "_проба_requirements.txt"
    путь.write_text(строки, encoding="utf-8")
    return путь.name


def test_модуль_из_аннотации_читается_этим_гейтом(tmp_path):
    """Случай, ради которого словарь снят: пакет объявлен ТОЛЬКО в файле.

    Такого имени не знал бы никакой зашитый список — и до задачи #444 гейт
    назвал бы модуль непоставленным, хотя пакет ставится и объявлен как велит
    сам файл.
    """
    имя = файл_зависимостей(tmp_path, "чудо-пакет  # модуль: диковина\n")
    подопытный = m.ROOT / "scripts" / "_проба_зависимости.py"
    подопытный.write_text("import диковина\n", encoding="utf-8")
    try:
        прогон = ("jobs:\n  catalogue:\n    steps:\n"
                  f"      - run: python -m pip install -r {имя}\n"
                  f"      - run: python scripts/{подопытный.name}\n")
        assert m.находки(прогон, m.ROOT)[0] == []
    finally:
        подопытный.unlink(missing_ok=True)
        (m.ROOT / имя).unlink(missing_ok=True)


def test_пакет_без_аннотации_читается_своим_именем(tmp_path):
    имя = файл_зависимостей(tmp_path, "диковина\n")
    подопытный = m.ROOT / "scripts" / "_проба_зависимости.py"
    подопытный.write_text("import диковина\n", encoding="utf-8")
    try:
        прогон = ("jobs:\n  catalogue:\n    steps:\n"
                  f"      - run: python -m pip install -r {имя}\n"
                  f"      - run: python scripts/{подопытный.name}\n")
        assert m.находки(прогон, m.ROOT)[0] == []
    finally:
        подопытный.unlink(missing_ok=True)
        (m.ROOT / имя).unlink(missing_ok=True)


def test_аннотация_не_делает_доступным_чужое_имя(tmp_path):
    """Обратный конец набора: объявлено одно, зовётся другое — находка."""
    имя = файл_зависимостей(tmp_path, "чудо-пакет  # модуль: диковина\n")
    подопытный = m.ROOT / "scripts" / "_проба_зависимости.py"
    подопытный.write_text("import небылица\n", encoding="utf-8")
    try:
        прогон = ("jobs:\n  catalogue:\n    steps:\n"
                  f"      - run: python -m pip install -r {имя}\n"
                  f"      - run: python scripts/{подопытный.name}\n")
        список, _ = m.находки(прогон, m.ROOT)
        assert len(список) == 1 and "небылица" in список[0]
    finally:
        подопытный.unlink(missing_ok=True)
        (m.ROOT / имя).unlink(missing_ok=True)


def test_ответ_у_двух_гейтов_один(tmp_path):
    """022 машинно: оба гейта зовут ОДИН разбор, и он даёт то же самое."""
    import check_test_deps as t

    строки = ["чудо-пакет  # модуль: диковина", "простой"]
    карта = t.объявлено(строки)
    assert карта == {"чудо_пакет": {"диковина"}, "простой": set()}
    # `ставится` строит доступное из той же карты: объявленное — модулем,
    # необъявленное — своим именем.
    assert {м for имя, мод in карта.items() for м in (мод or {имя})} == {
        "диковина", "простой"}
