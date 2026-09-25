"""Список площадки читается до конца, а предел — решение, названное поимённо.

Держит правило каталога 212. Здесь проверяется то, чего не видит самопроверка
гейта: сверка с таблицей пределов на подделанном дереве — названное проходит,
неназванное и незнакомое краснеют, запись без предмета тоже, а таблица,
которой нет, — отказ проверки, а не зелень.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_paging as cp  # noqa: E402


@pytest.fixture
def дерево(tmp_path: Path) -> Path:
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / ".rules").mkdir()
    return tmp_path


def скрипт(дерево: Path, текст: str, строк_сверху: int = 0) -> None:
    шапка = "".join(f"# строка {i}\n" for i in range(строк_сверху))
    (дерево / "scripts" / "проба.py").write_text(шапка + текст, encoding="utf-8")


def таблица(дерево: Path, записи: list[dict]) -> None:
    (дерево / ".rules" / "limits.json").write_text(
        json.dumps({"_": "проба", "allowed": записи}, ensure_ascii=False),
        encoding="utf-8")


ОДНА_СТРАНИЦА = 'gh("api", f"repos/{{owner}}/{{repo}}/pulls?per_page={N}")\n'
ПРЕДЕЛ = {"where": "scripts/проба.py", "what": "gh api pulls",
          "why": "свежие N открытых, от новых"}


def test_obkhod_chisto(дерево: Path) -> None:
    скрипт(дерево, 'gh("api", "--paginate", "repos/{owner}/{repo}/pulls")\n'
                   'ghcli.список("repos/{owner}/{repo}/issues")\n')
    таблица(дерево, [])
    assert cp.main(["--root", str(дерево)]) == 0


def test_odna_stranitsa_bez_predela_otkaz(дерево: Path,
                                          capsys: pytest.CaptureFixture[str]) -> None:
    скрипт(дерево, ОДНА_СТРАНИЦА)
    таблица(дерево, [])
    assert cp.main(["--root", str(дерево)]) == 1
    assert "scripts/проба.py:1: gh api pulls" in capsys.readouterr().err


def test_nazvannyy_predel_perezhivaet_perestanovku_strok(дерево: Path) -> None:
    таблица(дерево, [ПРЕДЕЛ])
    for сверху in (0, 7):
        скрипт(дерево, ОДНА_СТРАНИЦА, строк_сверху=сверху)
        assert cp.main(["--root", str(дерево)]) == 0


def test_predel_drugogo_chteniya_ne_propuskaet(дерево: Path) -> None:
    скрипт(дерево, 'gh("api", f"repos/{r}/issues/{n}/comments")\n')
    таблица(дерево, [ПРЕДЕЛ | {"what": "gh api pulls"}])
    # предел назван для pulls, а читаются комментарии — и запись без предмета
    assert cp.main(["--root", str(дерево)]) == 1


def test_zapis_bez_predmeta_otkaz(дерево: Path,
                                  capsys: pytest.CaptureFixture[str]) -> None:
    скрипт(дерево, 'gh("api", "--paginate", "repos/{owner}/{repo}/pulls")\n')
    таблица(дерево, [ПРЕДЕЛ])
    assert cp.main(["--root", str(дерево)]) == 1
    assert "нечего разрешать" in capsys.readouterr().err


def test_neznakomoe_zveno_ne_ugadyvaetsya(дерево: Path,
                                          capsys: pytest.CaptureFixture[str]) -> None:
    скрипт(дерево, 'gh("api", "repos/{owner}/{repo}/widgets")\n')
    таблица(дерево, [])
    assert cp.main(["--root", str(дерево)]) == 1
    assert "не классифицирован" in capsys.readouterr().err


def test_v_progone_nakhoditsya(дерево: Path) -> None:
    (дерево / ".github" / "workflows" / "x.yml").write_text(
        'jobs:\n  x:\n    steps:\n      - run: |\n'
        '          n=$(gh api "repos/$GITHUB_REPOSITORY/issues?state=open" \\\n'
        "                 --jq 'length')\n", encoding="utf-8")
    таблица(дерево, [])
    assert cp.main(["--root", str(дерево)]) == 1


@pytest.mark.parametrize("содержимое, почему", [
    (None, "не найден"),
    ("{не json", "не разобран"),
    ('{"allowed": [{"where": "scripts/проба.py", "what": "gh api pulls"}]}',
     "нет where, what или why"),
])
def test_tablitsa_ne_prochitana_tretiy_iskhod(
        дерево: Path, capsys: pytest.CaptureFixture[str],
        содержимое: str | None, почему: str) -> None:
    скрипт(дерево, ОДНА_СТРАНИЦА)
    if содержимое is not None:
        (дерево / ".rules" / "limits.json").write_text(содержимое, encoding="utf-8")
    assert cp.main(["--root", str(дерево)]) == 2
    assert почему in capsys.readouterr().err


def test_derevo_kataloga_chisto() -> None:
    assert cp.main([]) == 0
