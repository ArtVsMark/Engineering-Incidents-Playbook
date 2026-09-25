"""Имя рабочего кода живо, пока до него доходит рабочий путь, а не набор.

Держит правило каталога 211. Самопроверка гейта разбирает достижимость; здесь
— сверка со списком законных соседей на подделанном дереве: названный сосед
проходит, неназванная сирота краснеет, набор её не спасает, запись без
предмета — отказ, а непрочитанный список — третий исход, а не зелень.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_orphans as co  # noqa: E402

ГЛАВНЫЙ = "def main(): f()\nif __name__ == '__main__': main()\n"


@pytest.fixture
def дерево(tmp_path: Path) -> Path:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / ".rules").mkdir()
    return tmp_path


def код(дерево: Path, текст: str) -> None:
    (дерево / "scripts" / "проба.py").write_text(текст, encoding="utf-8")


def соседи(дерево: Path, записи: list[dict]) -> None:
    (дерево / ".rules" / "orphans.json").write_text(
        json.dumps({"_": "проба", "allowed": записи}, ensure_ascii=False),
        encoding="utf-8")


СОСЕД = {"where": "scripts/проба.py", "what": "РОСПИСЬ",
         "why": "закрытая роспись для набора"}


def test_dostizhimoe_chisto(дерево: Path) -> None:
    код(дерево, "def f(): pass\n" + ГЛАВНЫЙ)
    соседи(дерево, [])
    assert co.main(["--root", str(дерево)]) == 0


def test_sirota_s_zelenym_naborom_otkaz(дерево: Path,
                                         capsys: pytest.CaptureFixture[str]) -> None:
    код(дерево, "def f(): pass\ndef g(): pass\n" + ГЛАВНЫЙ)
    (дерево / "tests" / "test_проба.py").write_text(
        "import проба\ndef test_g():\n    проба.g()\n", encoding="utf-8")
    соседи(дерево, [])
    assert co.main(["--root", str(дерево)]) == 1
    assert "scripts/проба.py::g" in capsys.readouterr().err


def test_vyzov_v_znachenii_prisvaivaniya_zhivoy(дерево: Path) -> None:
    # `X = f()` исполняет f при импорте, даже если X не читает никто: f живая,
    # сирота здесь — X (находка обзора на #611)
    код(дерево, "def f(): return 1\nX = f()\n" + ГЛАВНЫЙ.replace("f()", "pass"))
    соседи(дерево, [])
    найдено = {имя for _, имя in co.сироты(co.модули(дерево)[0], дерево)}
    assert найдено == {"X"}


def test_nazvannyy_sosed_prokhodit(дерево: Path) -> None:
    код(дерево, "РОСПИСЬ = ('a', 'b')\ndef f(): pass\n" + ГЛАВНЫЙ)
    соседи(дерево, [СОСЕД])
    assert co.main(["--root", str(дерево)]) == 0


def test_sosed_bez_predmeta_otkaz(дерево: Path,
                                   capsys: pytest.CaptureFixture[str]) -> None:
    # роспись начали читать рабочим путём — послабление больше ничего не разрешает
    код(дерево, "РОСПИСЬ = ('a',)\ndef f(): print(РОСПИСЬ)\n" + ГЛАВНЫЙ)
    соседи(дерево, [СОСЕД])
    assert co.main(["--root", str(дерево)]) == 1
    assert "нечего" in capsys.readouterr().err


@pytest.mark.parametrize("содержимое, почему", [
    (None, "не найден"),
    ("{не json", "не разобран"),
    ('{"allowed": [{"where": "scripts/проба.py", "what": "X"}]}',
     "нет where, what или why"),
])
def test_spisok_ne_prochitan_tretiy_iskhod(
        дерево: Path, capsys: pytest.CaptureFixture[str],
        содержимое: str | None, почему: str) -> None:
    код(дерево, "def g(): pass\n" + ГЛАВНЫЙ)
    if содержимое is not None:
        (дерево / ".rules" / "orphans.json").write_text(содержимое, encoding="utf-8")
    assert co.main(["--root", str(дерево)]) == 2
    assert почему in capsys.readouterr().err


def test_nerazobrannyy_modul_tretiy_iskhod(дерево: Path) -> None:
    код(дерево, "def f(:\n")
    соседи(дерево, [])
    assert co.main(["--root", str(дерево)]) == 2


def test_derevo_kataloga_chisto() -> None:
    assert co.main([]) == 0
