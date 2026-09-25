"""Локальные ссылки и якоря.

Скрипт закрывает правило 002: разовая проверка ссылок руками ничего не
гарантирует. Здесь проверяется, что он действительно ловит битое, и — не менее
важно — что он различает ТРИ исхода (правило 039): чисто, находки и
«проверять было нечего», причём последнее не зеленеет (правило 075).
"""

from __future__ import annotations

from pathlib import Path

import check_links as cl
from conftest import write


def prepare(monkeypatch, repo: Path) -> None:
    monkeypatch.setattr(cl, "ROOT", repo)


def test_якорь_из_заголовка(repo):
    doc = write(repo / "a.md", "# Простой Заголовок\n\n## С Двумя Словами\n")
    assert "простой-заголовок" in cl.anchors(doc)
    assert "с-двумя-словами" in cl.anchors(doc)


def test_якорь_теряет_пунктуацию_но_не_кириллицу(repo):
    doc = write(repo / "a.md", "# Гейты: три исхода, а не два!\n")
    assert "гейты-три-исхода-а-не-два" in cl.anchors(doc)


def test_строки_без_решётки_якорями_не_становятся(repo):
    doc = write(repo / "a.md", "просто текст\n# Заголовок\n")
    assert cl.anchors(doc) == {"заголовок"}


def test_живая_ссылка_проходит(monkeypatch, repo, capsys):
    write(repo / "a.md", "см. [цель](b.md)\n")
    write(repo / "b.md", "# Цель\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 0
    assert "ссылки в порядке" in capsys.readouterr().out


def test_ссылка_в_никуда_это_находка(monkeypatch, repo, capsys):
    write(repo / "a.md", "см. [цель](нет-такого.md)\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 1
    # Отказ обязан назвать, ЧТО именно битое, а не только сколько.
    assert "нет-такого.md" in capsys.readouterr().err


def test_живой_файл_но_мёртвый_якорь_это_находка(monkeypatch, repo, capsys):
    write(repo / "a.md", "см. [цель](b.md#которого-нет)\n")
    write(repo / "b.md", "# Совсем другое\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 1
    assert "якоря нет" in capsys.readouterr().err


def test_внешние_ссылки_не_проверяются(monkeypatch, repo):
    write(repo / "a.md", "[вовне](https://example.com/x.md) и [свой](b.md)\n")
    write(repo / "b.md", "# Свой\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 0


def test_нет_документов_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo)
    assert cl.main() == 2
    assert "проверять нечего" in capsys.readouterr().err


def test_документы_без_локальных_ссылок_это_третий_исход(monkeypatch, repo, capsys):
    write(repo / "a.md", "текст без единой ссылки\n")
    prepare(monkeypatch, repo)
    # Ноль проверенных ссылок — это «вход подозрителен», а не «всё хорошо»:
    # зелёное здесь означало бы, что гейт проспал пустой каталог (правило 075).
    assert cl.main() == 2
    assert "подозрителен" in capsys.readouterr().err


# ── заготовка уходит к потребителю (076) ───────────────────────────────────
#
# Замер 25.09: в 4 заготовках 37 ссылок `](../…)`, и гейт их принимал —
# внутри каталога они разрешаются, а у получателя, в чужом дереве, мертвы.
# Признак 076 дословно: «подсказка выглядит идеально при чтении в репозитории».

def свой(monkeypatch, slug: str = "o/cat") -> None:
    monkeypatch.setattr(cl, "own_slug", lambda root: (slug, ""))


def test_zagotovka_so_ssylkoy_iz_templates_nahodka(monkeypatch, repo, capsys):
    write(repo / "templates" / "CLAUDE.md", "см. [правило](../rules/ru/001-x.md)\n")
    write(repo / "rules" / "ru" / "001-x.md", "# X\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 1
    assert "уходит к потребителю" in capsys.readouterr().err


def test_navyk_plagina_so_ssylkoy_v_derevo_nahodka(monkeypatch, repo, capsys):
    """Плагин ставится папкой: ссылка из неё в наше дерево у потребителя мертва (076)."""
    write(repo / "plugins" / "p" / "skills" / "s" / "SKILL.md",
          "см. [правило](../../../../rules/ru/001-x.md)\n")
    write(repo / "rules" / "ru" / "001-x.md", "# X\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 1
    assert "уходит к потребителю" in capsys.readouterr().err


def test_ssylka_vnutri_plagina_i_oglavlenie_ne_nahodka(monkeypatch, repo):
    """Внутри папки плагина ссылка жива; оглавление плагина читают здесь."""
    write(repo / "plugins" / "p" / "skills" / "s" / "SKILL.md", "см. [соседа](../t/SKILL.md)\n")
    write(repo / "plugins" / "p" / "skills" / "t" / "SKILL.md", "# T\n")
    write(repo / "plugins" / "p" / "README.md", "см. [правило](../../rules/ru/001-x.md)\n")
    write(repo / "rules" / "ru" / "001-x.md", "# X\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 0


def test_ogla_vlenie_zagotovok_chitaetsya_zdes(monkeypatch, repo):
    """templates/README.md читают в каталоге: относительная ссылка у него жива."""
    write(repo / "templates" / "README.md", "см. [правило](../rules/ru/001-x.md)\n")
    write(repo / "rules" / "ru" / "001-x.md", "# X\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 0


def test_ssylka_vnutri_templates_ne_nahodka(monkeypatch, repo):
    """Соседняя заготовка лежит там же — у получателя она рядом."""
    write(repo / "templates" / "a.md", "см. [b](b.md)\n")
    write(repo / "templates" / "b.md", "# B\n")
    prepare(monkeypatch, repo)
    assert cl.main() == 0


def test_svoya_absolyutnaya_ssylka_proveryaetsya_kak_lokalnaya(monkeypatch, repo, capsys):
    write(repo / "templates" / "CLAUDE.md",
          "см. [жива](https://github.com/o/cat/blob/main/rules/ru/001-x.md) "
          "и [мертва](https://github.com/o/cat/blob/main/rules/ru/999-y.md)\n"
          "и [локальная](b.md)\n")
    write(repo / "templates" / "b.md", "# B\n")
    write(repo / "rules" / "ru" / "001-x.md", "# X\n")
    prepare(monkeypatch, repo)
    свой(monkeypatch)
    assert cl.main() == 1
    err = capsys.readouterr().err
    assert "999-y.md" in err and "001-x.md" not in err


def test_chuzhaya_absolyutnaya_ssylka_ne_proveryaetsya(monkeypatch, repo):
    write(repo / "a.md", "[чужое](https://github.com/o/other/blob/main/net.md) и [b](b.md)\n")
    write(repo / "b.md", "# B\n")
    prepare(monkeypatch, repo)
    свой(monkeypatch)
    assert cl.main() == 0


def test_bez_svoego_imeni_svoi_ssylki_ne_provereny_vsluh(monkeypatch, repo, capsys):
    """Нет origin — свои абсолютные не проверены, и это сказано, а не пропущено (045)."""
    write(repo / "a.md", "[b](b.md)\n")
    write(repo / "b.md", "# B\n")
    prepare(monkeypatch, repo)
    monkeypatch.setattr(cl, "own_slug", lambda root: ("", "адреса origin нет"))
    assert cl.main() == 0
    assert "НЕ проверены: адреса origin нет" in capsys.readouterr().out
