"""Ответ каталога о самом себе: три исхода и находки по контракту.

Скрипт закрывает правила 128, 129 и 026. Тесты бьют в то, ради чего он есть:
ответ нужен по КАЖДОМУ правилу, «действует» без механизма и без места — не
ответ, а отрицательный статус без причины вернётся следующей ревизией.

Отдельно проверяется разделение отказа и предупреждения (правило 051):
несуществующий путь — факт и находка, число словом — подозрение и только
предупреждение. Смешать их значило бы либо ронять прогон на живой прозе, либо
пропускать разошедшуюся декларацию.
"""

from __future__ import annotations

import json
from pathlib import Path

import check_bindings as cb
from conftest import write


def prepare(monkeypatch, repo: Path, answer, export) -> None:
    b = repo / ".rules" / "bindings.json"
    e = repo / "export" / "rules.json"
    write(b, answer if isinstance(answer, str) else json.dumps(answer))
    write(e, export if isinstance(export, str) else json.dumps(export))
    monkeypatch.setattr(cb, "ROOT", repo)
    monkeypatch.setattr(cb, "BINDINGS", b)
    monkeypatch.setattr(cb, "EXPORT", e)


def export_of(*ids):
    return {"rules": [{"id": i} for i in ids]}


def test_полный_ответ_проходит(monkeypatch, repo):
    write(repo / "CLAUDE.md", "# свод\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "CLAUDE.md — раздел про гейты"}}},
            export_of("001"))
    assert cb.main() == 0


def test_нет_файла_ответа_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, {"rules": {}}, export_of("001"))
    cb.BINDINGS.unlink()
    assert cb.main() == 2
    assert "не отработала" in capsys.readouterr().err


def test_битый_json_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, "{не json", export_of("001"))
    assert cb.main() == 2
    assert "не разобрать JSON" in capsys.readouterr().err


def test_пустой_ответ_это_третий_исход(monkeypatch, repo, capsys):
    # Ноль записей — «сверять нечего», а не «всё сошлось»: зелёное на пустом
    # входе и есть тихо отключённый гейт (правило 075).
    prepare(monkeypatch, repo, {"rules": {}}, export_of("001"))
    assert cb.main() == 2
    assert "сверять нечего" in capsys.readouterr().err


def test_правило_без_ответа_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "нигде"}}},
            export_of("001", "002"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "002" in err and "unreviewed" in err


def test_ответ_на_несуществующее_правило_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "нигде"},
                       "999": {"status": "unreviewed"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "999" in capsys.readouterr().err


def test_статус_вне_набора_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "потом-разберёмся"}}}, export_of("001"))
    assert cb.main() == 1
    assert "вне набора" in capsys.readouterr().err


def test_действует_без_места_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "где именно" in capsys.readouterr().err


def test_отказ_без_причины_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "rejected"}}}, export_of("001"))
    assert cb.main() == 1
    assert "без причины" in capsys.readouterr().err


def test_заявленный_файл_обязан_существовать(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/выдумка.py"}}},
            export_of("001"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "выдумка.py" in err and "разошлась с фактом" in err


def test_живой_заявленный_файл_находкой_не_считается(monkeypatch, repo):
    write(repo / "scripts" / "живой.py", "# он есть\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/живой.py"}}},
            export_of("001"))
    assert cb.main() == 0


def test_число_словом_только_предупреждает(monkeypatch, repo):
    # Правило 051: «три гейта» устареет, но отказ здесь был бы ложным —
    # живая проза даёт достаточно законных сочетаний со словом-числом.
    write(repo / "CLAUDE.md", "# свод\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "CLAUDE.md",
                               "why": "держат три гейта"}}},
            export_of("001"))
    assert cb.main() == 0


# ── адрес механизма: рассказ вместо адреса — находка ──────────────────────
#
# «След» правила гейт требует РАЗРЕШИМЫМ (audit_catalogue), а `where` до сих
# пор проверялся только на непустоту. Набор двусторонний (140): у каждого
# исхода есть предмет, который обязан его дать, — иначе гейт, отвергающий
# всё подряд, выглядел бы так же зелено, как верный.

def test_механизм_без_адреса_это_находка(monkeypatch, repo, capsys):
    """Гейт, чей адрес нельзя назвать, обычно и не гейт."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "все скрипты различают исходы кодом"}}},
            export_of("001"))
    assert cb.main() == 1
    assert "адреса нет" in capsys.readouterr().err


def test_образец_файлов_это_адрес(monkeypatch, repo):
    """Набор файлов — такой же адрес, как один файл.

    Требовать перечислить их поимённо значило бы требовать список, который
    устареет с первым новым прогоном.
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "document",
                               "where": ".github/workflows/*.yml — у всех есть "
                                        "ручная кнопка"}}},
            export_of("001"))
    assert cb.main() == 0


def test_корневой_документ_по_имени_это_адрес(monkeypatch, repo):
    """`CONTRIBUTING` без расширения называют в прозе, и это адрес."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "document",
                               "where": "CONTRIBUTING — раздел про ревью"}}},
            export_of("001"))
    assert cb.main() == 0


def test_у_отсутствия_механизма_адреса_не_требуют(monkeypatch, repo):
    """`none` — это «не держится ничем». Адрес тут нечему называть.

    Требовать его значило бы толкать к выдумыванию: ответ «ничем» честнее
    придуманного пути, и наказывать за честность гейт не должен.
    """
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "намерение, за которым пока ничего",
                               "why": "не дошли руки: предмет счётный"}}},
            export_of("001"))
    assert cb.main() == 0


# ── «ничем» обязано назвать причину (правило 154) ─────────────────────────
#
# `none` без причины означает сразу две вещи — «пробовали, машинно нельзя» и
# «никто не пробовал». Замер при заведении правила: 41 запись не держалась
# ничем, причину называли 5. После заполнения вышло 14 «не дошли руки» —
# очередь на гейты, невидимая до этого. Набор двусторонний (140).

def test_ничем_без_причины_это_находка(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "держится договорённостью"}}},
            export_of("001"))
    assert cb.main() == 1
    err = capsys.readouterr().err
    assert "не держится ничем, и почему" in err


def test_ничем_с_причиной_проходит(monkeypatch, repo):
    """Причина — обычная проза; замкнутый словарь был бы ярлыком вместо ответа."""
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "none",
                               "where": "держится договорённостью",
                               "why": "требует суждения: что считать решением, "
                                      "решает читатель"}}},
            export_of("001"))
    assert cb.main() == 0


def test_у_обеспеченного_правила_причины_не_требуют(monkeypatch, repo):
    """154 спрашивает только у `none`: у механизма причина — его адрес."""
    write(repo / "scripts" / "живой.py", "# он есть\n")
    prepare(monkeypatch, repo,
            {"rules": {"001": {"status": "active", "mechanism": "gate",
                               "where": "scripts/живой.py"}}},
            export_of("001"))
    assert cb.main() == 0
