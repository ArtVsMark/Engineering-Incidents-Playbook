"""Заготовки против своего документа: подделка вместо зелени живого корпуса.

Правило 155 держится тем, что о каждой заготовке сказано, чем она применяется у
самого каталога. Ошибка гейта тиха в обе стороны: пропущенная заготовка уедет
потребителю непроверенной, а ложная находка на законном «нет: причина» приучит
читать красное как фон (051) — и тогда первый настоящий разъезд пройдёт мимо.

Главное, что здесь проверяется, — что ОТВЕТ обязан быть, а не выглядеть.
Пустая ячейка, «нет» без причины и проза без адреса ловятся отдельно: все три
на глаз неотличимы от заполненного ответа, и ровно на этом каталог уже
попадался — поле `where` год принимало рассказ вместо адреса.

Файловая система трогается во временном каталоге; сеть — нет.
"""

from __future__ import annotations

from pathlib import Path

import check_templates as ct

HEAD = ("| Файл · File | Зачем | Правила | У себя · At home |\n"
        "|---|---|---|---|\n")


def make(root: Path, files: dict[str, str], table: str) -> Path:
    folder = root / "templates"
    folder.mkdir(parents=True, exist_ok=True)
    for name, body in files.items():
        (folder / name).write_text(body, encoding="utf-8")
    (folder / "README.md").write_text("## Что здесь\n\n" + HEAD + table,
                                      encoding="utf-8")
    return root


def row(name: str, answer: str) -> str:
    return f"| [`{name}`]({name}) | зачем | [002](x.md) | {answer} |\n"


# ── ответ есть и он адрес ──────────────────────────────────────────────────

def test_adres_svoego_artefakta_chisto(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "preflight.py").write_text("x", encoding="utf-8")
    make(tmp_path, {"preflight.py": "x"}, row("preflight.py", "`scripts/preflight.py`"))
    assert ct.main(["--root", str(tmp_path)]) == 0


def test_net_s_prichinoy_chisto(tmp_path):
    """«У себя иначе» — законный ответ, если сказано почему."""
    make(tmp_path, {"brief.md": "x"},
         row("brief.md", "нет: параллельных исполнителей у каталога не бывает"))
    assert ct.main(["--root", str(tmp_path)]) == 0


# ── ответ отсутствует или только выглядит ответом ──────────────────────────

def test_zagotovka_bez_stroki_nahodka(tmp_path):
    make(tmp_path, {"orphan.md": "x"}, row("other.md", "`scripts/x.py`"))
    assert ct.main(["--root", str(tmp_path)]) == 1


def test_pustaya_yacheyka_nahodka(tmp_path):
    make(tmp_path, {"a.md": "x"}, row("a.md", ""))
    assert ct.main(["--root", str(tmp_path)]) == 1


def test_net_bez_prichiny_nahodka(tmp_path):
    """«нет» без причины неотличимо от «забыли» — это и есть 046."""
    make(tmp_path, {"a.md": "x"}, row("a.md", "нет"))
    assert ct.main(["--root", str(tmp_path)]) == 1


def test_proza_vmesto_adresa_nahodka(tmp_path):
    """Рассказ применением не является: открыть его нечем."""
    make(tmp_path, {"a.md": "x"}, row("a.md", "мы делаем так же руками"))
    assert ct.main(["--root", str(tmp_path)]) == 1


def test_nesushchestvuyushchiy_adres_nahodka(tmp_path):
    make(tmp_path, {"a.md": "x"}, row("a.md", "`scripts/net-takogo.py`"))
    assert ct.main(["--root", str(tmp_path)]) == 1


def test_stroka_perezhila_zagotovku_nahodka(tmp_path, capsys):
    """Обещание файла, которого нет, — та же порча, но в другую сторону."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "a.py").write_text("x", encoding="utf-8")
    make(tmp_path, {"a.md": "x"},
         row("a.md", "`scripts/a.py`") + row("ushedshaya.md", "`scripts/a.py`"))
    assert ct.main(["--root", str(tmp_path)]) == 1
    assert "ushedshaya.md" in capsys.readouterr().err


# ── три исхода ─────────────────────────────────────────────────────────────

def test_bez_dokumenta_eto_dva(tmp_path):
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "a.md").write_text("x", encoding="utf-8")
    assert ct.main(["--root", str(tmp_path)]) == 2


def test_pustye_zagotovki_eto_dva_a_ne_chisto(tmp_path):
    make(tmp_path, {}, "")
    assert ct.main(["--root", str(tmp_path)]) == 2


def test_tablitsa_ne_razobralas_eto_dva(tmp_path):
    """Ноль строк при живых заготовках — ошибка разбора, а не пустой каталог."""
    folder = tmp_path / "templates"
    folder.mkdir(parents=True)
    (folder / "a.md").write_text("x", encoding="utf-8")
    (folder / "README.md").write_text("совсем без таблицы\n", encoding="utf-8")
    assert ct.main(["--root", str(tmp_path)]) == 2


# ── разбор таблицы ─────────────────────────────────────────────────────────

def test_beryotsya_posledniy_stolbets_a_ne_lyuboy():
    """Столбец «Правила» стоит рядом и полон ссылок: спутать их с ответом
    значило бы считать заготовку применённой у себя всегда."""
    table = HEAD + "| [`a.md`](a.md) | зачем | [002](../rules/ru/002-x.md) | `scripts/a.py` |\n"
    assert ct.rows(table)["a.md"] == "`scripts/a.py`"
