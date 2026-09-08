"""Находки внешнего взгляда переживают слияние: записаны и снимаются механизмом.

Держит правила каталога:
  142 — у находки назван адресат, и он переживает слияние: комментарий на
        слитом изменении адресатом быть перестаёт;
  002 — снятие едет вместе с починкой строкой «Разобрано: <отпечаток>», а не
        остаётся жестом в трекере, который забудут.

Сеть не трогается: `gh` подменяется, и подделка отвечает ровно тем, чем
отвечает площадка на `--jq` из самого скрипта (170).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import review_findings as rf  # noqa: E402


def подделка(комментарии=(), задачи=(), слитые=(), пишет=None):
    """Подделка `ghcli.run`.

    ИСТОЧНИК ФОРМ — сами вызовы скрипта, и каждый назван адресом (170):
    `gh api repos/{repo}/issues/{pr}/comments --jq "[.[] | {login, body}]"`,
    `gh api repos/{repo}/issues?state=open --jq "[.[] | select(.pull_request ==
    null) | {number, body}]"` и
    `gh api repos/{repo}/pulls?state=closed --jq "[.[] | select(.merged_at !=
    null) | .body]"`. Живой ответ площадки на них снят в этой же смене при
    разборе изменения #392.
    """
    def run(*args):
        адрес = args[1] if len(args) > 1 else ""
        пишущий = "--method" in args or any(
            a.startswith("title=") or a.startswith("body=") for a in args)
        if пишущий:
            if пишет is not None:
                пишет.append(args)
            return 0, '{"number": 500}'
        if "/comments" in адрес:
            return 0, json.dumps(list(комментарии), ensure_ascii=False)
        if "/issues?" in адрес:
            return 0, json.dumps(list(задачи), ensure_ascii=False)
        if "/pulls?" in адрес:
            return 0, json.dumps(list(слитые), ensure_ascii=False)
        return 0, "[]"
    return run


def отзыв(текст: str, кто: str = rf.РЕВЬЮЕР) -> dict:
    return {"login": кто, "body": текст}


ЗАМЕТКА = "числа инцидента противоречат друг другу внутри записи"
ОТП = rf.отпечаток(ЗАМЕТКА)


def тело_записанное(писало: list) -> str:
    return next(a for a in писало[0] if a.startswith("body="))


# ── вердикт: есть, нет, чужой ──────────────────────────────────────────────

def test_verdikta_net_eto_tretiy_ishod(monkeypatch, capsys):
    """«Ревью не отработало» и «находок нет» — разные ответы (027, 039)."""
    monkeypatch.setattr(rf.ghcli, "run", подделка([отзыв("Обычный разбор.")]))

    assert rf.main(["--repo", "o/r", "--pr", "1"]) == 2
    assert "нет вердикта" in capsys.readouterr().err


def test_nol_nahodok_adresata_ne_trebuet(monkeypatch, capsys):
    monkeypatch.setattr(rf.ghcli, "run",
                        подделка([отзыв("Разбор.\n\nВЕРДИКТ: находок 0")]))

    assert rf.main(["--repo", "o/r", "--pr", "1"]) == 0
    assert "находок нет" in capsys.readouterr().out


def test_verdikt_iz_chuzhogo_kommentariya_ne_schitaetsya(monkeypatch):
    """Текст изменения пишет тот, кого проверяют, и вписать «ВЕРДИКТ: находок 0»
    он может свободно. Считается только комментарий ревьюера (085)."""
    monkeypatch.setattr(rf.ghcli, "run", подделка(
        [отзыв("ВЕРДИКТ: находок 0", кто="кто-то-другой")]))

    assert rf.main(["--repo", "o/r", "--pr", "1"]) == 2


def test_chislo_bez_zametok_eto_otkaz(monkeypatch, capsys):
    """Вердикт называет находки, а строк «НАХОДКА: …» нет: записывать нечего,
    и «находок 2» без текста читателю не поможет (075)."""
    monkeypatch.setattr(rf.ghcli, "run", подделка([отзыв("ВЕРДИКТ: находок 2")]))

    assert rf.main(["--repo", "o/r", "--pr", "1"]) == 2
    assert "строк «НАХОДКА" in capsys.readouterr().err


# ── запись: в задачу едет сама заметка, а не счётчик ───────────────────────

def test_zametka_zapisyvaetsya_tekstom_a_ne_chislom(monkeypatch):
    """РОВНО ПРЕДМЕТ, ЗАМЕР 8 сентября: изменение #392 слилось на 2,3 минуты
    раньше вердикта, и две верные находки не увидел никто. «Находок 2» этого не
    чинит — чтобы понять, что делать, нужен текст заметки."""
    писало: list = []
    monkeypatch.setattr(rf.ghcli, "run", подделка(
        [отзыв(f"НАХОДКА: {ЗАМЕТКА}\n\nВЕРДИКТ: находок 1")], пишет=писало))

    assert rf.main(["--repo", "o/r", "--pr", "392", "--apply"]) == 1
    тело = тело_записанное(писало)
    assert ЗАМЕТКА in тело and ОТП in тело and "#392" in тело


def test_bez_apply_zadachu_ne_trogayut(monkeypatch, capsys):
    """Умолчание сухое: скрипт пишет в трекер."""
    писало: list = []
    monkeypatch.setattr(rf.ghcli, "run", подделка(
        [отзыв(f"НАХОДКА: {ЗАМЕТКА}\n\nВЕРДИКТ: находок 1")], пишет=писало))

    assert rf.main(["--repo", "o/r", "--pr", "392"]) == 1
    assert писало == []
    assert "--apply не задан" in capsys.readouterr().out


def test_vtoraya_zametka_dopisyvaetsya_v_tu_zhe_zadachu(monkeypatch):
    """ОДНА ЖИВАЯ ЗАДАЧА, А НЕ ПО ОДНОЙ НА ИЗМЕНЕНИЕ: ежедневная копия завалила
    бы трекер и приучила листать его мимо (051)."""
    писало: list = []
    было = f"{rf.МАРКЕР}\n\n## Не разобрано: 1\n\n- `{ОТП}` · #392 — {ЗАМЕТКА}\n"
    monkeypatch.setattr(rf.ghcli, "run", подделка(
        [отзыв("НАХОДКА: исключительное утверждение не выдерживает грепа\n\n"
               "ВЕРДИКТ: находок 1")],
        задачи=[{"number": 500, "body": было}], пишет=писало))

    assert rf.main(["--repo", "o/r", "--pr", "394", "--apply"]) == 1
    тело = тело_записанное(писало)
    assert ЗАМЕТКА in тело and "исключительное утверждение" in тело
    assert "issues/500" in " ".join(писало[0]), "обновление, а не новая задача"


def test_posledniy_verdikt_perekryvaet_promezhutochnyy(monkeypatch):
    """Действие обновляет свой комментарий по ходу: промежуточное «находок 0»
    до разбора не должно перекрывать итог."""
    monkeypatch.setattr(rf.ghcli, "run", подделка(
        [отзыв("идёт разбор\n\nВЕРДИКТ: находок 0"),
         отзыв(f"НАХОДКА: {ЗАМЕТКА}\n\nВЕРДИКТ: находок 1")]))

    assert rf.main(["--repo", "o/r", "--pr", "1"]) == 1


def test_treker_ne_prinyal_eto_tretiy_ishod(monkeypatch, capsys):
    """Отказ записи — не «находки есть», а «механизм не отработал» (039)."""
    def run(*args):
        адрес = args[1] if len(args) > 1 else ""
        if "/comments" in адрес:
            return 0, json.dumps(
                [отзыв(f"НАХОДКА: {ЗАМЕТКА}\n\nВЕРДИКТ: находок 1")],
                ensure_ascii=False)
        if "/issues?" in адрес:
            return 0, "[]"
        return 1, "403 Forbidden"
    monkeypatch.setattr(rf.ghcli, "run", run)

    assert rf.main(["--repo", "o/r", "--pr", "1", "--apply"]) == 2
    assert "трекер не принял" in capsys.readouterr().err


# ── снятие: механизмом, а не жестом ────────────────────────────────────────

def test_razobrannoe_snimaetsya_slovom_v_tele_izmeneniya(monkeypatch):
    """ВТОРАЯ ПОЛОВИНА МЕХАНИЗМА. Автор починки называет отпечаток в теле
    СВОЕГО изменения — тем же приёмом, каким площадка закрывает задачу по
    `Closes`. Снятие едет вместе с работой, а не остаётся жестом (002)."""
    писало: list = []
    было = (f"{rf.МАРКЕР}\n\n## Не разобрано: 2\n\n"
            f"- `{ОТП}` · #392 — {ЗАМЕТКА}\n- `abc1234` · #390 — другая заметка\n")
    monkeypatch.setattr(rf.ghcli, "run", подделка(
        задачи=[{"number": 500, "body": было}],
        слитые=[f"Починка.\n\nРазобрано: {ОТП}\n"], пишет=писало))

    assert rf.main(["--repo", "o/r", "--sweep", "--apply"]) == 1
    тело = тело_записанное(писало)
    assert ОТП not in тело, "названное разобранным обязано уйти"
    assert "abc1234" in тело, "неназванное обязано остаться"


def test_snyatie_bez_apply_zadachu_ne_trogaet(monkeypatch, capsys):
    писало: list = []
    было = f"{rf.МАРКЕР}\n\n- `{ОТП}` · #392 — {ЗАМЕТКА}\n"
    monkeypatch.setattr(rf.ghcli, "run", подделка(
        задачи=[{"number": 500, "body": было}],
        слитые=[f"Разобрано: {ОТП}"], пишет=писало))

    assert rf.main(["--repo", "o/r", "--sweep"]) == 1
    assert писало == []
    assert "--apply не задан" in capsys.readouterr().out


def test_pustoy_spisok_eto_chisto(monkeypatch):
    """Всё разобрано — исход 0. Задача остаётся: закрывает её человек, потому
    что механизм не знает, кончилась ли работа или просто опустел список."""
    писало: list = []
    было = f"{rf.МАРКЕР}\n\n- `{ОТП}` · #392 — {ЗАМЕТКА}\n"
    monkeypatch.setattr(rf.ghcli, "run", подделка(
        задачи=[{"number": 500, "body": было}],
        слитые=[f"Разобрано: {ОТП}"], пишет=писало))

    assert rf.main(["--repo", "o/r", "--sweep", "--apply"]) == 0
    assert "пусто" in тело_записанное(писало)


def test_snimat_nechego_kogda_zadachi_net(monkeypatch, capsys):
    monkeypatch.setattr(rf.ghcli, "run", подделка(слитые=["Разобрано: abc1234"]))

    assert rf.main(["--repo", "o/r", "--sweep", "--apply"]) == 0
    assert "снимать нечего" in capsys.readouterr().out


def test_bez_pr_i_bez_sweep_eto_otkaz(monkeypatch, capsys):
    """Пустой вход — отказ, а не тихий ноль (075)."""
    monkeypatch.setattr(rf.ghcli, "run", подделка())

    assert rf.main(["--repo", "o/r"]) == 2
    assert "--sweep" in capsys.readouterr().err


def test_otpechatok_perezhivaet_probely():
    """Отпечаток берётся от заголовка, а не от файла со строкой: адрес
    «файл:строка» сдвигается первой же правкой выше — измерено дважды."""
    assert rf.отпечаток("одна   заметка") == rf.отпечаток("одна заметка")
    assert rf.отпечаток("одна заметка") != rf.отпечаток("другая заметка")
