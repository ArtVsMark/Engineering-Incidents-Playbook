"""Значок «Python │ 3.14 │ 3.15»: цвет каждой части — исход своего прогона.

Источник подделки (правило 170): прогоны — форма ответа площадки
`actions/workflows/<файл>/runs` (поля `conclusion`, `created_at`), файлы
прогонов — форма своих же `.github/workflows/*.yml`.
"""

from __future__ import annotations

import python_badge as pb


def прогон(conclusion: str, когда: str, id_: int = 1) -> dict:
    return {"conclusion": conclusion, "created_at": когда, "id": id_}


def работа(conclusion: str, метка: str) -> dict:
    return {"conclusion": conclusion, "labels": [метка]}


def дерево(tmp_path, ci: str = "3.14", next_: str | None = "3.15"):
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        f'        with:\n          python-version: "{ci}"\n', encoding="utf-8")
    if next_:
        (wf / "python-next.yml").write_text(
            f'        with:\n          python-version: "{next_}"\n'
            "          allow-prereleases: true\n", encoding="utf-8")
    return tmp_path


# ── состояние: последний прогон С ВЕРДИКТОМ ────────────────────────────────

def test_последний_прошёл_зелёный():
    assert pb.состояние([прогон("failure", "2026-10-01T10:00Z"),
                         прогон("success", "2026-10-01T11:00Z")]) == "pass"


def test_последний_упал_красный():
    assert pb.состояние([прогон("success", "2026-10-01T10:00Z"),
                         прогон("failure", "2026-10-01T11:00Z")]) == "fail"


def test_отмена_не_вердикт_решает_предыдущий():
    """Отменённый прогон ничего не проверил (039): цвет даёт прошлый вердикт,
    а не серый и не зелёный."""
    assert pb.состояние([прогон("failure", "2026-10-01T10:00Z"),
                         прогон("cancelled", "2026-10-01T11:00Z")]) == "fail"


def test_прогонов_нет_серый():
    assert pb.состояние([]) == "none"
    assert pb.состояние([прогон("skipped", "2026-10-01T11:00Z")]) == "none"


# ── версии берутся у прогонов, а не пишутся рукой (005) ────────────────────

def test_версии_из_прогонов(tmp_path):
    assert pb.версии(дерево(tmp_path)) == [("3.14", "ci.yml"),
                                           ("3.15", "python-next.yml")]


def test_сдвиг_планки_сдвигает_подпись(tmp_path):
    assert pb.версии(дерево(tmp_path, "3.15", "3.16"))[0] == ("3.15", "ci.yml")


# ── картинка ───────────────────────────────────────────────────────────────

def test_три_части_и_python_цветом_основного_ci():
    картинка = pb.svg([("3.14", "pass"), ("3.15", "fail")], "pass")
    assert картинка.count("<rect x=") >= 3
    assert ">Python<" in картинка and ">3.14<" in картинка and ">3.15<" in картинка
    зелёный, красный = pb.СОСТОЯНИЯ["pass"][0], pb.СОСТОЯНИЯ["fail"][0]
    # Порядок цветов частей: Python, 3.14, 3.15.
    цвета = [кусок.split('fill="')[1].split('"')[0]
             for кусок in картинка.split('<rect x="')[1:4]]
    assert цвета == [зелёный, зелёный, красный]
    assert "CI не пройден" in картинка  # слово в подсказке, а не только цвет


def test_main_python_красный_когда_ci_упал(tmp_path):
    out = tmp_path / "python.svg"
    исходы = {"ci.yml": [прогон("failure", "2026-10-01T11:00Z")],
              "python-next.yml": []}
    assert pb.main(["--root", str(дерево(tmp_path)), "--out", str(out)],
                   прогоны=исходы.__getitem__,
                   работы=lambda run_id: [работа("failure", "ubuntu-latest")]) == 0
    картинка = out.read_text(encoding="utf-8")
    первый = картинка.split('<rect x="')[1]
    assert pb.СОСТОЯНИЯ["fail"][0] in первый
    assert "проверка не проводилась" in картинка


# ── исход 2: «не спросили» не рисуется серым (075) ─────────────────────────

def test_площадка_молчит_это_третий_исход_а_не_серый(tmp_path):
    out = tmp_path / "python.svg"

    def молчит(файл: str) -> list[dict]:
        raise pb.НеОтветила("gh: 502")

    assert pb.main(["--root", str(дерево(tmp_path)), "--out", str(out)],
                   прогоны=молчит) == 2
    assert not out.exists()


def test_нет_прогонов_с_версией_это_третий_исход(tmp_path):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    assert pb.main(["--root", str(tmp_path), "--out", str(tmp_path / "p.svg")],
                   прогоны=lambda f: []) == 2


# ── части по ОС: где проект действительно проверяется ──────────────────────

def test_непроверенные_ос_серые_а_не_пропадают():
    """Мультиплатформенность решает проект, а значок показывает её честно:
    при прогоне на одном Linux windows и mac стоят серыми — «не проверено»."""
    assert pb.по_ос([работа("success", "ubuntu-latest")]) == [
        ("linux", "pass"), ("windows", "none"), ("mac", "none")]


def test_упавшая_ос_видна_поимённо():
    """Индикатор поломки: из трёх ОС красная та, на которой упало."""
    assert pb.по_ос([работа("success", "ubuntu-latest"),
                     работа("failure", "windows-latest"),
                     работа("success", "macos-14"),
                     работа("success", "windows-latest")]) == [
        ("linux", "pass"), ("windows", "fail"), ("mac", "pass")]


def test_ос_берутся_у_решающего_прогона(tmp_path):
    out = tmp_path / "python.svg"
    спрошено: list[int] = []

    def работы(run_id: int) -> list[dict]:
        спрошено.append(run_id)
        return [работа("success", "ubuntu-latest")]

    исходы = {"ci.yml": [прогон("success", "2026-10-01T10:00Z", 7),
                         прогон("cancelled", "2026-10-01T11:00Z", 8)],
              "python-next.yml": [прогон("success", "2026-10-01T10:00Z", 9)]}
    assert pb.main(["--root", str(дерево(tmp_path)), "--out", str(out)],
                   прогоны=исходы.__getitem__, работы=работы) == 0
    assert спрошено == [7]  # отменённый 8 ничего не проверил
    картинка = out.read_text(encoding="utf-8")
    assert ">linux<" in картинка and ">windows<" in картинка and ">mac<" in картинка


# ── у потребителя: свой файл CI и версия матрицей ──────────────────────────

def test_версия_матрицей_берётся_у_планки(tmp_path):
    """`python-version: ${{ matrix.python }}` числа не несёт; подпись тогда
    — планка из requires-python, которую гейт версий держит равной прогонам."""
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "tests.yml").write_text(
        "          python-version: ${{ matrix.python }}\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        'requires-python = ">=3.14"\n', encoding="utf-8")
    assert pb.версии(tmp_path, "tests.yml") == [("3.14", "tests.yml")]
