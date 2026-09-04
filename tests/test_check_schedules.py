"""Темп по расписанию выведен из бюджета: гейт проверяется тем, что обязан
отвергнуть, и тем, что обязан пропустить.

Здесь дорог именно пропуск, а не ложный отказ, и это отличает набор от
большинства соседних. Расписание, не уложившееся в квоту, упирается в стену
посреди работы и теряет её целиком (033); страховка без замера выглядит
работающей ровно до дня, когда она понадобится (169). Ложный отказ виден сразу
и чинится строкой в объявлении.

Площадка не трогается: разбор cron и арифметика — чистые функции.
"""

from __future__ import annotations

import json

import check_schedules as cs


# ── разбор расписания ──────────────────────────────────────────────────────

def test_sutochnoe_raspisanie_odin_zapusk_v_svoy_chas():
    assert cs.запусков_в_час("23 6 * * *", 6) == 1
    assert cs.запусков_в_час("23 6 * * *", 7) == 0


def test_kazhdye_pyatnadtsat_minut_chetyre_v_chas():
    assert cs.запусков_в_час("*/15 * * * *", 3) == 4


def test_spisok_i_diapazon_raskryvayutsya():
    assert cs.запусков_в_час("0,30 8-9 * * *", 8) == 2
    assert cs.запусков_в_час("0,30 8-9 * * *", 10) == 0


def test_nerazbornoe_raspisanie_ne_pritvoryaetsya_nulyom():
    """ГРАНИЦА: «не разобрано» и «не запускается» — разные ответы, и путать их
    значит считать бюджет по нулю (075)."""
    assert cs.часы_и_минуты("каждый час") is None
    assert cs.часы_и_минуты("0 0 * *") is None


def test_interval_schitaetsya_po_hudshemu_sluchayu():
    """Суточное даёт сутки; два запуска в 8:00 и 8:30 дают 30 минут, а не
    среднее по суткам."""
    assert cs.интервал_минут("23 6 * * *") == 24 * 60
    assert cs.интервал_минут("0,30 8 * * *") == 30


# ── что гейт обязан отвергнуть ─────────────────────────────────────────────

ЛИМИТ = {"gh_api_per_hour": 100}


def дерево(tmp_path, прогоны: dict[str, str], ответ: dict):
    (tmp_path / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".rules").mkdir(exist_ok=True)
    for имя, cron in прогоны.items():
        (tmp_path / ".github" / "workflows" / имя).write_text(
            f'name: x\non:\n  schedule:\n    - cron: "{cron}"\n',
            encoding="utf-8")
    (tmp_path / ".rules" / "schedules.json").write_text(
        json.dumps(ответ, ensure_ascii=False), encoding="utf-8")
    return ["--root", str(tmp_path)]


def test_summa_chasa_prevyshaet_dolyu_otkaz(tmp_path):
    """ГЛАВНЫЙ СЛУЧАЙ 033 и половина 058: каждое расписание по отдельности
    укладывается, а вместе — нет. Квота общая."""
    argv = дерево(tmp_path, {"a.yml": "10 6 * * *", "b.yml": "40 6 * * *"},
                  {"limits": ЛИМИТ, "share": 0.5, "runs": {
                      "a.yml": {"cron": "10 6 * * *", "role": "main",
                                "gh_calls_per_run": 30},
                      "b.yml": {"cron": "40 6 * * *", "role": "main",
                                "gh_calls_per_run": 30}}})
    assert cs.main(argv) == 1


def test_raspisanie_bez_obyavleniya_otkaz(tmp_path):
    argv = дерево(tmp_path, {"a.yml": "10 6 * * *"},
                  {"limits": ЛИМИТ, "share": 0.5, "runs": {}})
    assert cs.main(argv) == 1


def test_obyavlenie_bez_raspisaniya_otkaz(tmp_path):
    """Протухшая запись молчит громче дыры: она выглядит ответом (146)."""
    argv = дерево(tmp_path, {"a.yml": "10 6 * * *"},
                  {"limits": ЛИМИТ, "share": 0.5, "runs": {
                      "a.yml": {"cron": "10 6 * * *", "role": "main",
                                "gh_calls_per_run": 1},
                      "b.yml": {"cron": "0 5 * * *", "role": "main",
                                "gh_calls_per_run": 1}}})
    assert cs.main(argv) == 1


def test_cron_razoshelsya_s_faylom_otkaz(tmp_path):
    """Объявление, разошедшееся с фактом, хуже отсутствующего (049)."""
    argv = дерево(tmp_path, {"a.yml": "10 6 * * *"},
                  {"limits": ЛИМИТ, "share": 0.5, "runs": {
                      "a.yml": {"cron": "10 5 * * *", "role": "main",
                                "gh_calls_per_run": 1}}})
    assert cs.main(argv) == 1


def test_strahovka_bez_zamera_otkaz(tmp_path):
    """ГЛАВНЫЙ СЛУЧАЙ 169: пока замера нет, основной путь строят так, будто
    страховки не существует."""
    argv = дерево(tmp_path, {"a.yml": "10 6 * * *"},
                  {"limits": ЛИМИТ, "share": 0.5, "runs": {
                      "a.yml": {"cron": "10 6 * * *", "role": "safety-net",
                                "gh_calls_per_run": 1}}})
    assert cs.main(argv) == 1


def test_strahovka_koroche_promezhutka_otkaz(tmp_path):
    """Вторая половина 169, и она запрет, а не риск: планировщик говорит
    «когда-нибудь», а не «раз в N минут»."""
    argv = дерево(tmp_path, {"a.yml": "10 6 * * *"},
                  {"limits": ЛИМИТ, "share": 0.5, "runs": {
                      "a.yml": {"cron": "10 6 * * *", "role": "safety-net",
                                "measured": 0, "deadline_minutes": 5,
                                "gh_calls_per_run": 1}}})
    assert cs.main(argv) == 1


def test_bez_tseny_otkaz(tmp_path):
    argv = дерево(tmp_path, {"a.yml": "10 6 * * *"},
                  {"limits": ЛИМИТ, "share": 0.5, "runs": {
                      "a.yml": {"cron": "10 6 * * *", "role": "main"}}})
    assert cs.main(argv) == 1


# ── что гейт обязан пропустить ─────────────────────────────────────────────

def test_ulozhilis_chisto(tmp_path):
    argv = дерево(tmp_path, {"a.yml": "10 6 * * *", "b.yml": "40 7 * * *"},
                  {"limits": ЛИМИТ, "share": 0.5, "runs": {
                      "a.yml": {"cron": "10 6 * * *", "role": "main",
                                "gh_calls_per_run": 30},
                      "b.yml": {"cron": "40 7 * * *", "role": "main",
                                "gh_calls_per_run": 30}}})
    assert cs.main(argv) == 0


def test_strahovka_s_zamerom_i_dlinnym_srokom_prohodit(tmp_path):
    """ГРАНИЦА: страховка законна — когда у неё есть замер, а срок длиннее
    промежутка. Красное на ней было бы ложным отказом (051)."""
    argv = дерево(tmp_path, {"a.yml": "10 6 * * *"},
                  {"limits": ЛИМИТ, "share": 0.5, "runs": {
                      "a.yml": {"cron": "10 6 * * *", "role": "safety-net",
                                "measured": 3, "deadline_minutes": 2880,
                                "gh_calls_per_run": 1}}})
    assert cs.main(argv) == 0


# ── исход 2 ────────────────────────────────────────────────────────────────

def test_net_otveta_eto_tretiy_ishod(tmp_path):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    assert cs.main(["--root", str(tmp_path)]) == 2


def test_net_ni_odnogo_raspisaniya_eto_tretiy_ishod(tmp_path):
    """Гейт, не нашедший предмета, обязан упасть, а не зазеленеть (075)."""
    argv = дерево(tmp_path, {}, {"limits": ЛИМИТ, "share": 0.5, "runs": {}})
    (tmp_path / ".github" / "workflows" / "пусто.yml").write_text(
        "name: x\non:\n  push:\n", encoding="utf-8")
    assert cs.main(argv) == 2
