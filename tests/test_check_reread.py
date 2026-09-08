"""Подпись под перечитыванием не едет одна.

Случаи спрашивают гейт на выдуманной истории: два коммита в временном дереве —
«было» и «стало», — и ответ виден до того, как подпись куда-либо уехала (018).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_reread as cr  # noqa: E402


def git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, encoding="utf-8", check=True)
    return done.stdout.strip()


def ответ(schema: str = "1.1", answers_to: str = "", **rules) -> str:
    d: dict = {"schema": schema}
    if answers_to:
        d["answers_to"] = answers_to
    d["rules"] = {k: {"status": v} for k, v in rules.items()}
    return json.dumps(d, ensure_ascii=False, indent=2)


@pytest.fixture
def дерево(tmp_path: Path) -> Path:
    """Дерево с общей веткой `main`, где уже лежит ответ прежней версии."""
    root = tmp_path / "repo"
    (root / ".rules").mkdir(parents=True)
    git(root.parent, "init", "-q", "-b", "main", str(root))
    git(root, "config", "user.name", "проба")
    git(root, "config", "user.email", "проба@example.com")
    (root / ".rules" / "bindings.json").write_text(
        ответ("1.1", "", **{"001": "active", "002": "not-applicable"}),
        encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "ответ прежней версии")
    return root


def положить(root: Path, текст: str) -> None:
    # Каталог создаётся здесь, а не в фикстуре: `git rm` последнего файла
    # уносит и его — так выглядит дерево потребителя до первого ответа.
    (root / ".rules").mkdir(exist_ok=True)
    (root / ".rules" / "bindings.json").write_text(текст, encoding="utf-8")


def тело(root: Path, текст: str) -> str:
    путь = root / "body.md"
    путь.write_text(текст, encoding="utf-8")
    return str(путь)


def test_podpis_ne_dvigalas_predmeta_net(дерево, capsys):
    """Изменение, не трогающее номера, гейт не касается вовсе."""
    положить(дерево, ответ("1.1", "", **{"001": "rejected", "002": "active"}))

    assert cr.main(["--root", str(дерево), "--base", "main"]) == 0
    assert "не двигалась" in capsys.readouterr().out


def test_podpis_sdvinulas_bez_zamera_eto_nahodka(дерево, capsys):
    """РОВНО ПРЕДМЕТ ПРАВИЛА, ЗАМЕР 8 сентября по коммиту 9bfa9d1: выгрузка
    поднялась 1.4 → 1.5, ответ 1.1 → 1.2, подпись проставлена — а обхода не
    было. Заметил вопрос владельца, а не механизм."""
    положить(дерево, ответ("1.2", "1.5", **{"001": "active",
                                            "002": "not-applicable"}))

    assert cr.main(["--root", str(дерево), "--base", "main", "--body-file",
                    тело(дерево, "Обычное тело без замера.")]) == 1
    err = capsys.readouterr().err
    assert "1.1 → 1.2" in err and "1.5" in err


def test_odna_pravka_zamerom_ne_schitaetsya(дерево, capsys):
    """ГРАНИЦА, НАЙДЕННАЯ ПРОБОЙ НА ИНЦИДЕНТЕ. Первая редакция принимала
    «изменена хотя бы одна запись» за след обхода — и вернула «чисто» по
    9bfa9d1, где правда изменена одна запись, та самая 157. Гейт, не
    отвергающий собственный повод, не проверяет ничего (140)."""
    положить(дерево, ответ("1.2", "1.5", **{"001": "rejected",
                                            "002": "not-applicable"}))

    assert cr.main(["--root", str(дерево), "--base", "main", "--body-file",
                    тело(дерево, "Поправил одну запись.")]) == 1
    assert "это не замер обхода" in capsys.readouterr().err


def test_zamer_v_tele_propuskaet(дерево, capsys):
    """Пустое перечитывание законно: контракт мог двинуться там, где наших
    ответов не касается. Требовать правку значило бы учить менять записи ради
    галочки (051)."""
    положить(дерево, ответ("1.2", "1.5", **{"001": "active",
                                            "002": "not-applicable"}))

    assert cr.main(["--root", str(дерево), "--base", "main", "--body-file",
                    тело(дерево, "Перечитано 78 записей, изменений нет.")]) == 0
    assert "обход назван" in capsys.readouterr().out


def test_slovo_bez_chisla_ne_zamer(дерево):
    """«Перечитано» без числа неотличимо от «я посмотрел» (166)."""
    положить(дерево, ответ("1.2", "1.5", **{"001": "active",
                                            "002": "not-applicable"}))

    # Вызов собран одной строкой намеренно: решение гейта спрашивается прямо,
    # а не через промежуточную переменную (150).
    зов = ["--root", str(дерево), "--base", "main",
           "--body-file", тело(дерево, "Всё перечитал, менять нечего.")]

    assert cr.main(зов) == 1


def test_telo_chitaetsya_so_stdin(дерево, monkeypatch, capsys):
    """Конвейер подаёт тело файлом, окно — потоком: оба входа обязаны работать."""
    положить(дерево, ответ("1.2", "1.5", **{"001": "active",
                                            "002": "not-applicable"}))
    monkeypatch.setattr("sys.stdin",
                        __import__("io").StringIO("перечитано 12 записей"))

    assert cr.main(["--root", str(дерево), "--base", "main",
                    "--body-file", "-"]) == 0


def test_bez_tela_eto_tretiy_ishod(дерево, capsys):
    """Судить не по чему — отдельный ответ, а не «чисто» и не находка (039)."""
    положить(дерево, ответ("1.2", "1.5", **{"001": "active",
                                            "002": "not-applicable"}))

    assert cr.main(["--root", str(дерево), "--base", "main"]) == 2
    assert "--body-file" in capsys.readouterr().err


def test_pervyy_otvet_proekta_ne_predmet(дерево, capsys):
    """Ответа в общей ветке ещё нет — перечитывать нечего, и это не отказ:
    так выглядит первое подключение потребителя (027)."""
    git(дерево, "rm", "-q", ".rules/bindings.json")
    git(дерево, "commit", "-q", "-m", "ответа ещё нет")
    git(дерево, "checkout", "-q", "-b", "работа")
    положить(дерево, ответ("1.2", "1.5", **{"001": "active"}))

    assert cr.main(["--root", str(дерево), "--base", "main"]) == 0
    assert "первый ответ" in capsys.readouterr().out


def test_bazy_ne_sprosit_eto_tretiy_ishod(дерево, capsys):
    """Третий исход называет предмет: команду git, которая не ответила (158)."""
    assert cr.main(["--root", str(дерево), "--base", "такой-ветки-нет"]) == 2
    assert "git show" in capsys.readouterr().err


def test_svoego_otveta_net_eto_tretiy_ishod(tmp_path, capsys):
    """Чужое дерево без ответа — отказ с адресом, а не молчаливое «чисто» (075)."""
    assert cr.main(["--root", str(tmp_path), "--base", "main"]) == 2
    assert ".rules/bindings.json" in capsys.readouterr().err
