"""Ручная кнопка и предел времени: подделка вместо зелени живого корпуса.

Гейт проверяет свойства файлов конвейера, и его ошибка тиха в обе стороны.
Пропущенная работа без предела оставит очередь висеть до умолчания площадки —
молчание вместо отказа. Ложная находка на законном файле приучит читать его
красное как фон (051).

ГЛАВНЫЙ СЛУЧАЙ ЗДЕСЬ — ПОСЛЕДНЯЯ РАБОТА В ФАЙЛЕ. Первая версия разбора
закрывала работу только по началу следующей, а конец файла обозначала строкой
с кириллическим именем, которая ключом не считалась. Гейт был зелёным на живом
корпусе и не держал ничего: у `ci.yml` и `attribution-history.yml` предела не
было, а он молчал (146). Поймано это было тем, что факт знали заранее, — то
есть не механизмом. Здесь стоит случай, который поймал бы это сам.

Площадка не трогается: разбор — чистая функция над текстом файла.
"""

from __future__ import annotations

from pathlib import Path

import check_workflows as cw

BUTTON = "on:\n  push:\n  workflow_dispatch:\n"


def workflow(root: Path, name: str, text: str) -> Path:
    path = root / ".github" / "workflows" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ── ручная кнопка (126) ────────────────────────────────────────────────────

def test_knopka_v_blochnoy_forme_naydena():
    assert cw.has_button(BUTTON)


def test_knopka_spiskom_naydena():
    """`on: [push, workflow_dispatch]` — та же кнопка, другая запись."""
    assert cw.has_button("on: [push, workflow_dispatch]\n")


def test_bez_knopki_nahodka(tmp_path):
    workflow(tmp_path, "w.yml",
             "on:\n  push:\njobs:\n  a:\n    timeout-minutes: 5\n")
    assert cw.main(["--root", str(tmp_path)]) == 1


def test_slovo_v_kommentarii_ne_schitaetsya_knopkoy():
    """Упоминание в прозе кнопкой не является: запускать нечего."""
    assert not cw.has_button("# тут был бы workflow_dispatch\non:\n  push:\n")


# ── предел времени (100) ───────────────────────────────────────────────────

def test_rabota_bez_predela_nahodka(tmp_path):
    workflow(tmp_path, "w.yml", BUTTON + "jobs:\n  a:\n    runs-on: x\n")
    assert cw.main(["--root", str(tmp_path)]) == 1


def test_poslednyaya_rabota_v_fayle_proveryaetsya(tmp_path):
    """Регресс: закрывать работу только началом следующей — значит не
    проверять последнюю ни в одном файле, а она там есть всегда."""
    text = BUTTON + "jobs:\n  a:\n    timeout-minutes: 5\n  b:\n    runs-on: x\n"
    assert cw.jobs_without_timeout(text) == ["b"]


def test_edinstvennaya_rabota_bez_predela_naydena():
    """Частный случай того же: единственная работа — сразу и последняя."""
    assert cw.jobs_without_timeout(BUTTON + "jobs:\n  a:\n    runs-on: x\n") == ["a"]


def test_sobytiya_ne_prinimayutsya_za_raboty():
    """Ключи внутри `on:` выглядят как работы; требовать от `push` предела
    времени значило бы краснеть на верном файле."""
    assert cw.jobs_without_timeout("on:\n  push:\n  pull_request:\n") == []


def test_predel_u_kazhdoy_raboty_chisto():
    text = BUTTON + "jobs:\n  a:\n    timeout-minutes: 5\n  b:\n    timeout-minutes: 7\n"
    assert cw.jobs_without_timeout(text) == []


# ── три исхода ─────────────────────────────────────────────────────────────

def test_chisto_eto_nol(tmp_path):
    workflow(tmp_path, "w.yml", BUTTON + "jobs:\n  a:\n    timeout-minutes: 5\n")
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_net_fayla_progona_eto_dva_a_ne_chisto(tmp_path):
    """Ноль файлов — проверять нечего, и зелёный здесь означал бы «всё в
    порядке» о том, чего не смотрели (075)."""
    assert cw.main(["--root", str(tmp_path)]) == 2


def test_nahodka_nazyvaet_fayl_i_rabotu(tmp_path, capsys):
    workflow(tmp_path, "ci.yml", BUTTON + "jobs:\n  catalogue:\n    runs-on: x\n")
    assert cw.main(["--root", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert "ci.yml" in err and "catalogue" in err
