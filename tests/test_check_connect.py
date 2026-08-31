"""Вход в проект: инструмент назван, инструмент существует, вход ведёт сюда.

Случаи спрашивают ГЕЙТ через `main()` на поддельном дереве, а не его функции:
разбор таблицы, проверенный отдельно, ничего не говорит о том, доедет ли
находка до отказа (правило 150).

Подделка нарочно маленькая: один инструмент, один документ входа. Так «отверг»
означает «отверг именно это», а не «упал на первом попавшемся» — та же причина,
по которой атрибуция проверяется по одному коммиту.
"""

from __future__ import annotations

from pathlib import Path

import check_connect as cc
from conftest import write

ТАБЛИЦА = """# Подключение

| Инструмент | Что делает | Где |
|---|---|---|
| `scripts/tool.py` | что-то полезное | у потребителя |
"""

ИНСТРУМЕНТ = '''#!/usr/bin/env python3
"""Полезный инструмент.

ОТДАЁТСЯ ПОТРЕБИТЕЛЮ. Назван в CONNECT.md.
"""
'''

НАШ_ГЕЙТ = '''#!/usr/bin/env python3
"""Наш гейт, который про потребителей только рассказывает."""
'''


def подделка(repo: Path, таблица: str = ТАБЛИЦА, инструмент: str = ИНСТРУМЕНТ,
             вход: tuple[str, ...] = ("README.md", "START.md")) -> Path:
    write(repo / "CONNECT.md", таблица)
    write(repo / "scripts" / "tool.py", инструмент)
    for doc in вход:
        write(repo / doc, "смотри [подключение](CONNECT.md)\n")
    return repo


def test_vsyo_nazvano_i_vsyo_est(repo):
    assert cc.main(["--root", str(подделка(repo))]) == 0


def test_instrument_bez_stroki_v_dokumente_eto_otkaz(repo, capsys):
    """Ровно инцидент: скрипт есть и объявлен, а на входе о нём ни слова."""
    подделка(repo, таблица="# Подключение\n\n| Ин | Что | Где |\n|---|---|---|\n"
                           "| `scripts/other.py` | иное | у потребителя |\n")
    write(repo / "scripts" / "other.py", "#\n")

    assert cc.main(["--root", str(repo)]) == 1
    assert "tool.py" in capsys.readouterr().err


def test_nazvannyy_no_nesushchestvuyushchiy_eto_otkaz(repo, capsys):
    """Обещание адреса, по которому ничего нет, хуже молчания: за ним идут."""
    подделка(repo)
    (repo / "scripts" / "tool.py").unlink()

    assert cc.main(["--root", str(repo)]) == 1
    assert "не существует" in capsys.readouterr().err


def test_deystvie_proveryaetsya_svoim_action_yml(repo, capsys):
    """`uses:` — тоже инструмент, и его тоже можно потерять переименованием."""
    подделка(repo, таблица=ТАБЛИЦА + "| `uses: вл/репо/.github/actions/attr@v1` "
                                     "| атрибуция | у потребителя |\n")

    assert cc.main(["--root", str(repo)]) == 1
    assert "action.yml" in capsys.readouterr().err

    write(repo / ".github" / "actions" / "attr" / "action.yml", "name: attr\n")
    assert cc.main(["--root", str(repo)]) == 0


def test_vhod_ne_vedushchiy_syuda_eto_otkaz(repo, capsys):
    """Список инструментов бесполезен, если на него не приходят (022)."""
    подделка(repo, вход=("README.md",))
    write(repo / "START.md", "порядок первого дня без единой команды\n")

    assert cc.main(["--root", str(repo)]) == 1
    assert "START.md" in capsys.readouterr().err


def test_nash_geyt_pod_marker_ne_popadaet(repo, capsys):
    """Догадка по словам понижена до предупреждения — иначе ложный отказ на
    каждом скрипте, который просто говорит о потребителях (051)."""
    подделка(repo, инструмент=ИНСТРУМЕНТ)
    write(repo / "scripts" / "gate.py",
          '"""Гейт.\n\nЗапускается **в репозитории потребителя** — так сказано '
          'про чужой скрипт.\n"""\n')

    assert cc.main(["--root", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "gate.py" in out and "не отказ" in out


def test_net_dokumenta_vhoda_eto_tretiy_ishod(repo, capsys):
    подделка(repo)
    (repo / "CONNECT.md").unlink()

    assert cc.main(["--root", str(repo)]) == 2
    assert "не отработала" in capsys.readouterr().err


def test_tablitsa_ne_razobralas_eto_tretiy_ishod(repo, capsys):
    """Ноль строк — ошибка разбора, а не пустой список: зеленеть на этом
    значит тихо отключить проверку (075)."""
    подделка(repo, таблица="# Подключение\n\nсписка нет, одна проза\n")

    assert cc.main(["--root", str(repo)]) == 2
    assert "не разобралось" in capsys.readouterr().err
