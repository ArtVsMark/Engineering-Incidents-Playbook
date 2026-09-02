"""Сторож толчка: отвергается ветка, отличная от текущей, и только она.

Случаи спрашивают САМ ХУК через `main()` — событие подаётся на stdin ровно в
том виде, в каком его подаёт площадка (правило 150). Текущая ветка
подменяется: спрашивать настоящую значило бы проверять состояние машины, а не
решение сторожа.

Сторож живёт вне `scripts/`, потому что запускает его не конвейер, а окно, — и
потому подключается путём, а не импортом из общего каталога.
"""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import pytest

ХУК = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "push_guard.py"
_spec = importlib.util.spec_from_file_location("push_guard", ХУК)
pg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pg)


def событие(command: str, tool: str = "Bash") -> str:
    return json.dumps({"tool_name": tool, "tool_input": {"command": command}})


@pytest.fixture
def окно(monkeypatch):
    """Окно стоит на своей ветке; вход подаётся как площадкой."""
    def настроить(command: str, branch: str | None = "agent/своя",
                  tool: str = "Bash"):
        monkeypatch.setattr(pg, "current_branch", lambda: branch)
        monkeypatch.setattr("sys.stdin", io.StringIO(событие(command, tool)))
    return настроить


def test_chuzhaya_vetka_otvergaetsya(окно, capsys):
    """Ровно предмет правила: содержимое уехало бы не туда, куда смотрит окно."""
    окно("git push -u origin agent/чужая")

    assert pg.main() == 2
    err = capsys.readouterr().err
    assert "agent/чужая" in err and "agent/своя" in err


def test_svoya_vetka_prohodit(окно):
    окно("git push -u origin agent/своя")

    assert pg.main() == 0


def test_tolchok_bez_imeni_vetki_prohodit(окно):
    """`git push` без ссылки уезжает по настройке ветки — это не промах."""
    окно("git push")

    assert pg.main() == 0


def test_yavnaya_ssylka_prohodit(окно):
    """`HEAD:main` — цель названа явно и осознанно; запрет на общую ветку
    живёт не здесь, а в правиле 131."""
    окно("git push origin HEAD:main")

    assert pg.main() == 0


def test_perenapravlenie_ne_schitaetsya_vetkoy(окно):
    """Замер на первой же живой пробе: `2>&1` уехало в список веток, и сторож
    назвал предметом отказа то, чего в команде не было (158)."""
    окно("git push -u origin agent/своя 2>&1 | tail -3")

    assert pg.main() == 0


def test_tsepochka_komand_razbiraetsya(окно):
    """Толчок прячется за `&&` чаще, чем стоит первым словом."""
    окно("git add -A && git commit -q -m x && git push origin agent/другая")

    assert pg.main() == 2


def test_ne_bash_ne_trogaetsya(окно):
    """Сторож смотрит на действие, а не на текст: строка в файле — не команда."""
    окно("git push origin agent/чужая", tool="Write")

    assert pg.main() == 0


def test_otdelyonnaya_golova_propuskaetsya(окно):
    """Сравнивать не с чем: у отделённой головы имени ветки нет вовсе, и
    отказ здесь был бы отказом на пустом месте (051)."""
    окно("git push origin agent/чужая", branch=None)

    assert pg.main() == 0


def test_slovo_push_v_chuzhoy_komande_ne_schitaetsya(окно):
    """`npm push`, `echo git push` и прочее сторожа не касаются."""
    окно("echo git push origin agent/чужая")

    assert pg.main() == 0
