"""Витрина: объявленный набор вопросов и названные пробелы.

Замер по пяти публичным проектам (#105): из восьми вопросов пять отвечает один
проект, остальные четыре — ни одного. Пока набор у каждого свой, проекты не
сравнить, и то, что один перестал отвечать, не заметит никто.

Главное, что здесь держится, — **пробел называется, а не опускается**. Значка
нет и значок застыл с витрины неотличимы: «у нас нет покрытия, потому что нет
кода» и «механизм покрытия сломался и молчит» выглядят одинаково, если значка
просто нет (046, 075). Поэтому случай «ответа нет вовсе» — находка, а не
умолчание.

Набор двусторонний, и здоровые предметы взяты у границы: значок с ОТДЕЛЬНОЙ
ветки в дереве не лежит и лежать не должен — требовать его файл значило бы
краснеть на верном.
"""

from __future__ import annotations

import json
from pathlib import Path

import check_showcase as cs
from conftest import write


def prepare(root: Path, questions: list[dict], readme: str = "", badges=()) -> None:
    write(root / ".rules" / "showcase.json",
          json.dumps({"schema": "1.0", "questions": questions}, ensure_ascii=False))
    write(root / "README.md", readme or "# Проект\n")
    write(root / ".github" / "workflows" / "ci.yml", "run: python scripts/a.py\n")
    (root / "tests").mkdir(parents=True, exist_ok=True)
    for b in badges:
        write(root / b, "{}\n")


def run(root: Path) -> int:
    return cs.main(["--root", str(root)])


# ── здоровые предметы ──────────────────────────────────────────────────────

def test_живой_значок_названный_в_витрине_проходит(repo, capsys):
    prepare(repo, [{"id": "coverage", "ask": "покрытие",
                    "badge": ".github/badges/coverage.json"}],
            readme="# П\n\n![c](.github/badges/coverage.json)\n",
            badges=[".github/badges/coverage.json"])
    assert run(repo) == 0
    assert "живым числом" in capsys.readouterr().out


def test_названный_пробел_проходит(repo, capsys):
    prepare(repo, [{"id": "pypi", "ask": "версия в PyPI",
                    "absent": "предмета нет: каталог не пакет и не публикуется"}])
    assert run(repo) == 0
    assert "названо без предмета" in capsys.readouterr().out


def test_значок_с_отдельной_ветки_файла_в_дереве_не_требует(repo):
    """Предмет у самой границы: ветка значков заводится ровно ради этого."""
    prepare(repo, [{"id": "release", "ask": "выпуск",
                    "badge": ".github/badges/release.json", "branch": "badges"}],
            readme="# П\n\n![r](release.json)\n")
    assert run(repo) == 0


def test_витрина_на_втором_языке_тоже_считается(repo):
    prepare(repo, [{"id": "coverage", "ask": "покрытие",
                    "badge": ".github/badges/coverage.json"}],
            badges=[".github/badges/coverage.json"])
    write(repo / "README.en.md", "# P\n\n![c](coverage.json)\n")
    assert run(repo) == 0


# ── предметы, которые гейт обязан отвергнуть ───────────────────────────────

def test_вопрос_без_ответа_это_находка(repo, capsys):
    prepare(repo, [{"id": "pypi", "ask": "версия в PyPI"}])
    assert run(repo) == 1
    assert "ответа нет вовсе" in capsys.readouterr().err


def test_причина_отсутствия_отпиской_не_считается(repo, capsys):
    prepare(repo, [{"id": "pypi", "ask": "версия в PyPI", "absent": "нет"}])
    assert run(repo) == 1
    assert "слишком коротка" in capsys.readouterr().err


def test_объявленный_значок_без_файла_это_находка(repo, capsys):
    prepare(repo, [{"id": "coverage", "ask": "покрытие",
                    "badge": ".github/badges/coverage.json"}],
            readme="# П\n\n![c](coverage.json)\n")
    assert run(repo) == 1
    assert "файла нет" in capsys.readouterr().err


def test_значок_не_показанный_в_витрине_это_находка(repo, capsys):
    prepare(repo, [{"id": "coverage", "ask": "покрытие",
                    "badge": ".github/badges/coverage.json"}],
            badges=[".github/badges/coverage.json"])
    assert run(repo) == 1
    assert "ответ в пустоту" in capsys.readouterr().err


def test_и_значок_и_причина_это_находка(repo, capsys):
    prepare(repo, [{"id": "coverage", "ask": "покрытие",
                    "badge": ".github/badges/coverage.json",
                    "absent": "и то и другое сразу, чего быть не может"}],
            badges=[".github/badges/coverage.json"])
    assert run(repo) == 1
    assert "ответ один" in capsys.readouterr().err


def test_свежесть_значка_здесь_не_судится(repo):
    """Здоровый предмет у самой границы, и это осознанная граница.

    Значки живут на ветке `badges`, в дереве общей ветки их нет. Гейт
    свежести стоял здесь и краснел на верной работе — число сдвинулось,
    изменение ни при чём. Такую проверку приучаются пропускать (051).
    """
    prepare(repo, [{"id": "tests", "ask": "сколько тестов",
                    "badge": ".github/badges/tests.json", "branch": "badges"}],
            readme="# П\n\n![t](tests.json)\n")
    write(repo / "tests" / "test_a.py", "def test_один():\n    pass\n")
    assert run(repo) == 0


# ── третий исход ───────────────────────────────────────────────────────────

def test_набора_нет_это_третий_исход(repo, capsys):
    assert run(repo) == 2
    assert "не отработала" in capsys.readouterr().err


def test_пустой_набор_это_третий_исход(repo, capsys):
    prepare(repo, [])
    assert run(repo) == 2
    assert "ни одного вопроса" in capsys.readouterr().err


def test_витрины_нет_это_третий_исход(repo, capsys):
    prepare(repo, [{"id": "pypi", "ask": "п", "absent": "предмета нет вовсе, вот так"}])
    (repo / "README.md").unlink()
    assert run(repo) == 2
    assert "витрины нет" in capsys.readouterr().err


# ── чего этот гейт больше не делает ────────────────────────────────────────

def test_сборки_значков_здесь_нет(repo):
    """Гейт вычислял три значка сам; все три сняты с витрины вместе с ними.

    Оставленная сборка производила бы значок, которого не показывает никто, —
    ровно то, что этот гейт и запрещает. Случай стоит здесь, чтобы возврат
    сборки без витрины не прошёл молча.
    """
    assert not hasattr(cs, "build")
    assert not hasattr(cs, "counted")


def test_ключа_build_у_команды_нет(repo, capsys):
    """Прогон значков звал `--build`; ключ снят вместе с механикой."""
    import pytest

    with pytest.raises(SystemExit):
        cs.main(["--root", str(repo), "--build"])
