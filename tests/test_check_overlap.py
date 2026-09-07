"""Пересечение файлов с чужим открытым изменением: находка, а не отказ.

Площадка подменяется на уровне `ghcli.run` — там же, где её зовёт сам гейт, —
а решение спрашивается через `main()`: подмена разбора JSON проверяла бы
`json.loads`, а не гейт (правило 150).

Источник подделки (правило 170): форма ответов снята с двух вызовов REST —
`gh api "repos/{owner}/{repo}/pulls?state=open&per_page=50"` (список) и
`gh api "repos/{owner}/{repo}/pulls/<N>/files"` (файлы одного изменения).
Раньше здесь стоял один ответ `gh pr list --json …,files`; вызов разделён
надвое ради квоты — GraphQL у `pr list` дорог, а поле `files` тянет содержимое
каждого открытого изменения.

Расхождение подделки с живой стороной обнаруживается только сверкой, а сверить
нечем, пока не сказано с чем; сама сверка требует сети и остаётся человеку.
"""

from __future__ import annotations

import json

import check_overlap as co

МОЙ = "agent/моя-ветка"


def площадка(monkeypatch, изменения: list[dict], code: int = 0) -> None:
    """Два вызова, и подделка их РАЗЛИЧАЕТ: иначе набор проверял бы один.

    Список изменений и файлы одного изменения — разные запросы с разной
    формой ответа. Подделка, отвечающая на оба одинаково, зеленела бы там,
    где живой вызов уже разошёлся (146).
    """
    файлы = {c["number"]: c.pop("_files") for c in изменения}

    def подделка(*args: str) -> tuple[int, str]:
        if code != 0:
            return code, "gh сказал нет"
        путь = args[1] if len(args) > 1 else ""
        if "/files" in путь:
            номер = int(путь.split("/pulls/")[1].split("/")[0])
            return 0, json.dumps(файлы.get(номер, []))
        return 0, json.dumps(изменения)
    monkeypatch.setattr(co.ghcli, "run", подделка)


def изменение(number: int, branch: str, *files: str) -> dict:
    return {"number": number, "title": f"работа {number}",
            "headRefName": branch, "_files": list(files)}


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
