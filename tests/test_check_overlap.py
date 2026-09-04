"""Пересечение файлов с чужим открытым изменением: находка, а не отказ.

Площадка подменяется на уровне `ghcli.run` — там же, где её зовёт сам гейт, —
а решение спрашивается через `main()`: подмена разбора JSON проверяла бы
`json.loads`, а не гейт (правило 150).

Источник подделки (правило 170): форма ответа снята с
`gh pr list --state open --limit 50 --json number,title,headRefName,files`.
Расхождение подделки с живой стороной обнаруживается только сверкой, а сверить
нечем, пока не сказано с чем; сама сверка требует сети и остаётся человеку.
"""

from __future__ import annotations

import json

import check_overlap as co

МОЙ = "agent/моя-ветка"


def площадка(monkeypatch, изменения: list[dict], code: int = 0) -> None:
    def подделка(*args: str) -> tuple[int, str]:
        return code, json.dumps(изменения) if code == 0 else "gh сказал нет"
    monkeypatch.setattr(co.ghcli, "run", подделка)


def изменение(number: int, branch: str, *files: str) -> dict:
    return {"number": number, "title": f"работа {number}", "headRefName": branch,
            "files": [{"path": f} for f in files]}


def test_peresecheniy_net_eto_chisto(monkeypatch, capsys):
    площадка(monkeypatch, [изменение(1, МОЙ, "scripts/a.py"),
                           изменение(2, "agent/чужая", "scripts/b.py")])

    assert co.main(["--branch", МОЙ]) == 0
    assert "пересечений нет" in capsys.readouterr().out


def test_obshchiy_fayl_eto_nahodka(monkeypatch, capsys):
    """Ровно инцидент: ночной прогон и окно тронули export/where.* разом."""
    площадка(monkeypatch, [изменение(1, МОЙ, "export/where.json", "scripts/a.py"),
                           изменение(2, "agent/ночной", "export/where.json")])

    assert co.main(["--branch", МОЙ]) == 1
    out = capsys.readouterr().out
    assert "export/where.json" in out and "#2" in out


def test_svoyo_izmenenie_s_soboy_ne_peresekaetsya(monkeypatch):
    """Ветка сравнивается с ЧУЖИМИ: пересечение с собой было бы всегда."""
    площадка(monkeypatch, [изменение(1, МОЙ, "export/where.json")])

    assert co.main(["--branch", МОЙ]) == 0


def test_ploshchadka_ne_otvetila_eto_tretiy_ishod(monkeypatch, capsys):
    """«Никто не правит» и «спросить не вышло» — разные ответы (039)."""
    площадка(monkeypatch, [], code=1)

    assert co.main(["--branch", МОЙ]) == 2
    assert "не отработала" in capsys.readouterr().err


def test_otvet_ne_razobran_eto_tretiy_ishod(monkeypatch, capsys):
    monkeypatch.setattr(co.ghcli, "run", lambda *a: (0, "{не json"))

    assert co.main(["--branch", МОЙ]) == 2
    assert "не разобран" in capsys.readouterr().err
