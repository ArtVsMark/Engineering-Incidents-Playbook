"""Три числа версии сходятся: гейт проверяется тем, что обязан отвергнуть,
и тем, что обязан пропустить.

Пропуск здесь дороже ложного отказа, и это не рассуждение, а разбор: «чисто
локально», снятое НИЖЕ объявленной планки, — утверждение о поверхности, на
которой изменение не поедет. Автор ему верит и толкает.

Источник подделки (правило 170): подделывается свой же манифест и свои же
прогоны — их форма снята с дерева каталога, `pyproject.toml` и
`.github/workflows/*.yml`.
"""

from __future__ import annotations

import check_python_version as cv


ПЛАНКА = (3, 12)


# ── разбор объявлений ──────────────────────────────────────────────────────

def test_planka_chitaetsya():
    assert cv.floor('requires-python = ">=3.12"\n') == (3, 12)


def test_planka_bez_obyavleniya():
    assert cv.floor("[project]\nname = 'x'\n") is None


def test_versiya_progona_chitaetsya(tmp_path):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "a.yml").write_text(
        '        with:\n          python-version: "3.12"\n', encoding="utf-8")
    assert cv.in_workflows(tmp_path) == [("a.yml", (3, 12))]


def test_versiya_bez_kavychek_tozhe_chitaetsya(tmp_path):
    """У площадки кавычки необязательны, и находка должна быть о ВЕРСИИ, а не
    о кавычках (051)."""
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "a.yml").write_text(
        "          python-version: 3.13\n", encoding="utf-8")
    assert cv.in_workflows(tmp_path) == [("a.yml", (3, 13))]


# ── что гейт обязан отвергнуть ─────────────────────────────────────────────

def test_okno_nizhe_planki_nahodka():
    """ГЛАВНЫЙ СЛУЧАЙ, И ОН ЖИВОЙ: 4 сентября окно работало на 3.11.15 при
    планке >=3.12, и «чисто: 39 шагов» печаталось с неё же."""
    найдено = cv.findings(ПЛАНКА, [("ci.yml", (3, 12))], (3, 11))
    assert найдено and "прогон перед толчком" in найдено[0]


def test_progon_nizhe_planki_nahodka():
    найдено = cv.findings(ПЛАНКА, [("ci.yml", (3, 11))], (3, 12))
    assert найдено and "ci.yml" in найдено[0]


def test_progony_razoshlis_mezhdu_soboy_nahodka():
    """Зелёное на одной версии не переносится на другую, и какая из них
    закрывает изменение — не сказано нигде."""
    найдено = cv.findings(ПЛАНКА, [("a.yml", (3, 12)), ("b.yml", (3, 13))],
                          (3, 13))
    assert any("разные версии" in n for n in найдено)


# ── что гейт обязан пропустить ─────────────────────────────────────────────

def test_vsyo_shoditsya_chisto():
    assert cv.findings(ПЛАНКА, [("ci.yml", (3, 12))], (3, 12)) == []


def test_okno_vyshe_planki_ne_nahodka():
    """ГРАНИЦА: планка НИЖНЯЯ. Окно новее объявленного — законно, и красное на
    нём приучало бы читать красное как фон (051). Верхних границ у нас нет
    намеренно: потолок версии запрещает потребителю обновляться."""
    assert cv.findings(ПЛАНКА, [("ci.yml", (3, 12))], (3, 13)) == []


def test_progon_vyshe_planki_ne_nahodka():
    assert cv.findings(ПЛАНКА, [("ci.yml", (3, 13))], (3, 13)) == []


# ── решение гейта, а не повторение его условия (правило 150) ───────────────

def дерево(tmp_path, планка: str, версия: str):
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nrequires-python = "{планка}"\n', encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        f'        with:\n          python-version: "{версия}"\n',
        encoding="utf-8")
    return ["--root", str(tmp_path)]


def test_glavnyy_otvet_gejta_otkaz(tmp_path):
    """Прогон гоняет версию ниже объявленной планки — конвейер проверяет то,
    чего проект не поддерживает."""
    assert cv.main(дерево(tmp_path, ">=3.12", "3.11")) == 1


def test_shoditsya_gejt_molchit(tmp_path):
    """Обратная половина: планка нижняя, и окно новее её законно. Красное на
    верном приучало бы читать красное как фон (051)."""
    высокая = f"3.{__import__('sys').version_info[1]}"
    assert cv.main(дерево(tmp_path, ">=3.8", высокая)) == 0


# ── исход 2 ────────────────────────────────────────────────────────────────

def test_net_manifesta_eto_tretiy_ishod(tmp_path):
    assert cv.main(["--root", str(tmp_path)]) == 2


def test_net_progonov_s_versiey_eto_tretiy_ishod(tmp_path):
    """Гейт, не нашедший предмета, обязан упасть, а не зазеленеть (075)."""
    (tmp_path / "pyproject.toml").write_text('requires-python = ">=3.12"\n',
                                             encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    assert cv.main(["--root", str(tmp_path)]) == 2
