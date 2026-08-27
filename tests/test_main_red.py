"""Дежурный по общей ветке: свёртка по имени, исключения и три исхода.

Скрипт заводит задачу по **чужому** красному, и ошибка в его свёртке молчалива
в обе стороны. Пропущенное красное не заметит никто — за тем дежурный и заведён.
Ложное красное хуже: задача, заведённая на зелёной ветке, приучает закрывать
дежурного не читая, и следующая настоящая краснота уйдёт туда же
(правило 051, и это тот самый случай, когда ложный отказ дороже пропуска).

Отдельно проверяется свёртка **по имени, а не по записям** (правило 009).
Площадка отдаёт по одному имени столько записей, сколько раз проверка
запускалась: отмена предыдущего прогона при новом пуше, повтор после обновления
ветки, ручной перезапуск. Это история событий, а не текущее состояние — и пара
«отменённый рядом со свежим успехом» / «свежий отказ поверх старого успеха»
стоит здесь нарочно: они отличаются одним полем, и слить их в одну ветку можно
случайно.

Сеть не трогается ни одним случаем: свёртка — чистая функция над ответом
площадки, и подделать ответ дешевле, чем ходить за ним.
"""

from __future__ import annotations

import json

import main_red


def run(name: str, conclusion: str | None, *, at: str = "2026-01-01",
        status: str = "completed") -> dict:
    return {"name": name, "status": status, "conclusion": conclusion, "createdAt": at}


def test_krasnaya_rabota_nazvana():
    assert main_red.red_names([run("ci", "failure")], frozenset()) == ["ci"]


def test_zelyonaya_rabota_ne_schitaetsya():
    assert main_red.red_names([run("ci", "success")], frozenset()) == []


def test_nezavershyonnyy_progon_ne_otkaz():
    """«Ещё идёт» — не отказ: задача на состояние, которое пройдёт само, учит
    листать трекер мимо."""
    assert main_red.red_names([run("ci", None, status="in_progress")], frozenset()) == []


def test_otmenyonnyy_ryadom_so_svezhim_uspehom_ne_krasnyy():
    """Свёртка по ИМЕНИ: считать по записям значит объявить красной работу, у
    которой рядом со свежим успехом висит отменённый прогон (правило 009)."""
    runs = [run("ci", "cancelled", at="2026-01-01"), run("ci", "success", at="2026-01-02")]
    assert main_red.red_names(runs, frozenset()) == []


def test_svezhiy_otkaz_poverh_starogo_uspeha_krasnyy():
    """Обратная сторона того же: свежесть решает, а не наличие успеха вообще."""
    runs = [run("ci", "success", at="2026-01-01"), run("ci", "failure", at="2026-01-02")]
    assert main_red.red_names(runs, frozenset()) == ["ci"]


def test_isklyuchyonnaya_rabota_ne_schitaetsya():
    """Исключения принадлежат потребителю: у каталога это attribution-history,
    чьё красное означало бы долг прошлой истории."""
    runs = [run("attribution-history", "failure")]
    assert main_red.red_names(runs, frozenset({"attribution-history"})) == []


def test_isklyuchenie_ne_glushit_ostalnyh():
    """Ошибка, которую легко внести: выйти из разбора на первом исключении."""
    runs = [run("attribution-history", "failure"), run("ci", "failure")]
    assert main_red.red_names(runs, frozenset({"attribution-history"})) == ["ci"]


def test_progonov_net_vovse():
    assert main_red.red_names([], frozenset()) == []


def test_neskolko_krasnyh_po_alfavitu():
    """Порядок задан, а не как придётся: тело задачи иначе меняется от прогона к
    прогону на одном и том же состоянии, и обновление выглядит событием."""
    runs = [run("release", "failure"), run("ci", "timed_out")]
    assert main_red.red_names(runs, frozenset()) == ["ci", "release"]


def test_telo_neset_marker_shablon_i_spisok():
    """Маркер — единственное, на чём держится идемпотентность: заголовок правят
    руками, и тогда прогон заведёт вторую задачу вместо обновления."""
    body = main_red.body_for("Текст потребителя.", ["ci"], "https://example/run/1")
    assert main_red.MARKER in body
    assert "Текст потребителя." in body
    assert "ci" in body
    assert "https://example/run/1" in body


def test_shablon_ne_prochitan_eto_tretiy_ishod(tmp_path, monkeypatch, capsys):
    """Три исхода, а не два: «дежурный не отработал» отличается кодом 2 от
    «есть красные работы» (правило 039)."""
    monkeypatch.setattr("sys.argv", ["main_red.py", "--body-file", str(tmp_path / "нет")])
    assert main_red.main() == 2
    assert "не отработал" in capsys.readouterr().err


def test_ploshchadka_ne_otvetila_eto_tretiy_ishod(tmp_path, monkeypatch, capsys):
    """Отказ Actions API — не «красных работ нет». Дежурный по красноте,
    молчащий о собственной слепоте, и есть та поломка, ради которой он заведён."""
    template = tmp_path / "body.md"
    template.write_text("Текст.", encoding="utf-8")
    monkeypatch.setattr(main_red, "gh", lambda *a: (1, "HTTP 403: Resource not accessible"))
    monkeypatch.setattr("sys.argv", ["main_red.py", "--body-file", str(template)])
    assert main_red.main() == 2
    err = capsys.readouterr().err
    assert "вкладка прогонов не прочитана" in err
    assert "actions: read" in err


def test_zelyonaya_vetka_eto_nol(tmp_path, monkeypatch, capsys):
    template = tmp_path / "body.md"
    template.write_text("Текст.", encoding="utf-8")
    calls = {"n": 0}

    def fake(*args):
        calls["n"] += 1
        if args[0] == "run":
            return 0, json.dumps([run("ci", "success")])
        return 0, "[]"

    monkeypatch.setattr(main_red, "gh", fake)
    monkeypatch.setattr("sys.argv", ["main_red.py", "--body-file", str(template)])
    assert main_red.main() == 0
    assert "зелёная" in capsys.readouterr().out
