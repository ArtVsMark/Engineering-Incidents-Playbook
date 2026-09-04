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
    # Адресат по умолчанию — посетитель: почти все случаи набора про него, и
    # выписывать `for` в каждом значило бы прятать предмет случая за обвязкой.
    # Случай «адресата нет» задаёт его явно как None — setdefault не тронет.
    for q in questions:
        q.setdefault("for", "visitor")
    write(root / ".rules" / "showcase.json",
          json.dumps({"schema": "1.1", "questions": questions}, ensure_ascii=False))
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
    assert "нет ни одной витрины" in capsys.readouterr().err


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


# ── артефакт витрины не возвращается в дерево (160) ─────────────────────────

def test_vernuvshiysya_znachok_nahodka(tmp_path):
    """Игнор не спрашивают при слиянии: `git checkout --theirs` вернул сюда
    четыре значка разом, и заметить это было нечем."""
    import subprocess
    badge = tmp_path / ".github" / "badges" / "consumers-light.svg"
    badge.parent.mkdir(parents=True)
    badge.write_text("<svg/>", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-f", "-A"], cwd=tmp_path, check=True)

    assert cs.badges_in_tree(tmp_path) == [".github/badges/consumers-light.svg"]


def test_nrisovannyy_no_neotslezhivaemyy_ne_nahodka(tmp_path):
    """ГРАНИЦА: прогон рисует их локально и обязан — он кладёт их на свою
    ветку. Находка — только то, что попало в дерево."""
    import subprocess
    badge = tmp_path / ".github" / "badges" / "consumers-light.svg"
    badge.parent.mkdir(parents=True)
    badge.write_text("<svg/>", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)

    assert cs.badges_in_tree(tmp_path) == []


def test_ne_repozitoriy_ne_lomaet_proverku(tmp_path):
    """Без git смотреть нечего, и это не отказ витрины: у неё свой предмет."""
    assert cs.badges_in_tree(tmp_path) == []


def test_gate_otvergaet_vernuvshiysya_artefakt(repo):
    """ГЕЙТ, А НЕ ФУНКЦИЯ (150). Первая версия этих случаев спрашивала
    `badges_in_tree` напрямую, и мутация «главный ход её не зовёт» их пережила —
    та же ошибка, что была допущена сегодня же в наборе атрибуции.
    """
    import subprocess
    prepare(repo, [{"id": "q", "absent": "предмета нет: проверять нечего"}])
    write(repo / ".github" / "badges" / "consumers-light.svg", "<svg/>")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-f", "-A"], cwd=repo, check=True)

    assert run(repo) == 1


def test_gate_nazyvaet_vernuvshiysya_fayl(repo, capsys):
    import subprocess
    prepare(repo, [{"id": "q", "absent": "предмета нет: проверять нечего"}])
    write(repo / ".github" / "badges" / "consumers-dark.svg", "<svg/>")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-f", "-A"], cwd=repo, check=True)
    run(repo)

    assert "consumers-dark.svg" in capsys.readouterr().err


def test_chistoe_derevo_gate_propuskaet(repo):
    """Обратная сторона: витрина без значков в дереве — штатное состояние, и
    краснеть на нём значило бы требовать того, чего быть не должно."""
    import subprocess
    prepare(repo, [{"id": "q", "absent": "предмета нет: проверять нечего"}])
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)

    assert run(repo) == 0


# ── адресат вопроса и источник ответа (схема 1.1) ─────────────────────────
#
# До схемы 1.1 у трёх вопросов из десяти стояло «значка нет; получается
# прогоном pytest -q»: причина верная, а источник назван прозой и не
# проверяется ничем. Теперь вопрос называет адресата, и ответ ему разный.

ИСТОЧНИК = ("колонка «Тестов» в HISTORY.md; считает "
            "scripts/history_metrics.py по дереву тега")


def сопровождающему(where: str = ИСТОЧНИК) -> dict:
    return {"id": "tests", "ask": "сколько тестов", "for": "maintainer",
            "where": where}


def test_вопрос_сопровождающего_с_адресом_проходит(repo, capsys):
    prepare(repo, [сопровождающему()])
    write(repo / "HISTORY.md", "# И\n")
    write(repo / "scripts" / "history_metrics.py", "# п\n")

    assert run(repo) == 0
    assert "адресом источника 1" in capsys.readouterr().out


def test_вопрос_сопровождающего_без_адреса_это_находка(repo, capsys):
    """Ровно инцидент: «значка нет, получается прогоном pytest -q»."""
    prepare(repo, [{"id": "tests", "ask": "сколько тестов", "for": "maintainer",
                    "absent": "значка нет: получается прогоном pytest -q"}])

    assert run(repo) == 1
    assert "нет `where`" in capsys.readouterr().err


def test_адрес_без_разрешимого_пути_это_находка(repo, capsys):
    """Рецепт для человека адресом живого источника не является (049)."""
    prepare(repo, [сопровождающему("запустите pytest -q и посмотрите число")])

    assert run(repo) == 1
    assert "рецепт для человека" in capsys.readouterr().err


def test_названный_но_несуществующий_источник_это_находка(repo, capsys):
    """Декларация сверяется с деревом, а не принимается на слово (044)."""
    prepare(repo, [сопровождающему("колонка в HISTORY.md; считает "
                                   "scripts/которого-нет.py")])
    write(repo / "HISTORY.md", "# И\n")

    out = (run(repo), capsys.readouterr().err)
    assert out[0] == 1 and "которого-нет.py" in out[1]


def test_значок_вопросу_сопровождающего_это_находка(repo, capsys):
    """Число, дёргающееся от каждого изменения, шумит там, куда смотрят раз."""
    prepare(repo, [{"id": "tests", "ask": "сколько тестов", "for": "maintainer",
                    "badge": ".github/badges/tests.json"}],
            badges=[".github/badges/tests.json"])

    assert run(repo) == 1
    assert "отвечает значок" in capsys.readouterr().err


def test_адрес_вопросу_посетителя_это_находка(repo, capsys):
    """Посетитель не ходит в исходники: ему значок либо названная причина."""
    prepare(repo, [{"id": "coverage", "ask": "покрытие", "for": "visitor",
                    "where": "scripts/coverage_badge.py"}])

    assert run(repo) == 1
    assert "не ходит в исходники" in capsys.readouterr().err


def test_вопрос_без_адресата_это_находка(repo, capsys):
    """Без адресата «значка нет» и «источник назван» неразличимы."""
    prepare(repo, [{"id": "tests", "ask": "сколько тестов", "for": None,
                    "where": ИСТОЧНИК}])

    assert run(repo) == 1
    assert "не назван адресат" in capsys.readouterr().err


def test_адресат_вне_словаря_это_находка(repo, capsys):
    """Словарь закрытый: «кому это» с открытым списком означает столько
    ответов, сколько авторов (068)."""
    prepare(repo, [{"id": "tests", "ask": "сколько тестов", "for": "все",
                    "where": ИСТОЧНИК}])

    assert run(repo) == 1
    assert "не назван адресат" in capsys.readouterr().err
