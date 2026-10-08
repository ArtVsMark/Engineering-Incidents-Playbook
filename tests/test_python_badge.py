"""Значок «Python │ 3.14 │ 3.15»: цвет каждой части — исход своего прогона.

Источник подделки (правило 170): прогоны — форма ответа площадки
`actions/workflows/<файл>/runs` (поля `conclusion`, `created_at`), файлы
прогонов — форма своих же `.github/workflows/*.yml`.
"""


import python_badge as pb
import pytest


@pytest.fixture(autouse=True)
def без_площадки(monkeypatch):
    """Выпуск и PyPI в наборе не спрашиваются у сети: выпусков нет."""
    monkeypatch.setattr(pb, "релиз_площадки", lambda: None)
    monkeypatch.setattr(pb, "версия_pypi", lambda пакет: None)


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
    картинка = pb.рисунок(pb.зоны_проверок([("3.14", "pass"), ("3.15", "fail")], "pass"))
    assert картинка.count("<rect x=") >= 3
    assert ">Python<" in картинка and ">3.14<" in картинка and ">3.15<" in картинка
    зелёный, красный = pb.СОСТОЯНИЯ["pass"][0], pb.СОСТОЯНИЯ["fail"][0]
    # Порядок цветов частей: CI (подпись), Python, 3.14, 3.15.
    цвета = [кусок.split('fill="')[1].split('"')[0]
             for кусок in картинка.split('<rect x="')[1:5]]
    assert цвета == [pb.ПОДПИСЬ, зелёный, зелёный, красный]
    assert "CI не пройден" in картинка  # слово в подсказке, а не только цвет


def test_main_python_красный_когда_ci_упал(tmp_path):
    out = tmp_path / "python.svg"
    исходы = {"ci.yml": [прогон("failure", "2026-10-01T11:00Z")],
              "python-next.yml": []}
    assert pb.main(["--root", str(дерево(tmp_path)), "--out", str(out)],
                   прогоны=исходы.__getitem__,
                   работы=lambda run_id: [работа("failure", "ubuntu-latest")]) == 0
    картинка = out.read_text(encoding="utf-8")
    # Первая часть — префикс «CI» (#719); исход CI несёт часть «Python».
    python = картинка.split('<rect x="')[2]
    assert pb.СОСТОЯНИЯ["fail"][0] in python
    assert "проверка не проводилась" in картинка


# ── исход 2: «не спросили» не рисуется серым (039) ─────────────────────────

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


def test_пропущенная_работа_не_делает_ос_серой():
    """Находка обзора #649: порядок работ не решает цвет — fail > pass > none."""
    assert pb.по_ос([работа("skipped", "ubuntu-latest"),
                     работа("success", "ubuntu-latest")])[0] == ("linux", "pass")
    assert pb.по_ос([работа("success", "ubuntu-latest"),
                     работа("failure", "ubuntu-latest"),
                     работа("skipped", "ubuntu-latest")])[0] == ("linux", "fail")


def test_полная_страница_без_вердикта_это_третий_исход(tmp_path):
    """Находка обзора #649: за краем страницы вердикт может быть, и серый
    «не проводилась» о неспрошенном был бы ложью (039)."""
    out = tmp_path / "python.svg"
    без_вердикта = [прогон("cancelled", f"2026-10-01T{i:02d}:00Z", i)
                    for i in range(pb.ПРЕДЕЛ)]
    исходы = {"ci.yml": [прогон("success", "2026-10-01T10:00Z")],
              "python-next.yml": без_вердикта}
    assert pb.main(["--root", str(дерево(tmp_path)), "--out", str(out)],
                   прогоны=исходы.__getitem__,
                   работы=lambda run_id: []) == 2
    assert not out.exists()


def test_прогон_изменения_из_форка_не_красит_значок():
    """Находка обзора #649: `branch=main` у площадки — это head_branch, и он
    равен main у изменения из форка. Цвет даёт только своя ветка."""
    чужой = {**прогон("failure", "2026-10-01T11:00Z"), "event": "pull_request"}
    свой = {**прогон("success", "2026-10-01T10:00Z"), "event": "push"}
    assert pb.состояние([свой, чужой]) == "pass"
    assert pb.состояние([чужой]) == "none"


def test_без_версии_основного_ci_это_третий_исход(tmp_path):
    """Находка обзора #649: если у основного CI нет версии (нет числа и нет
    pyproject), его не спрашивают — и серый «Python» был бы ложью (039)."""
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "pr-check.yml").write_text("    runs-on: ubuntu-latest\n", encoding="utf-8")
    (wf / "python-next.yml").write_text(
        '          python-version: "3.15"\n          allow-prereleases: true\n',
        encoding="utf-8")
    out = tmp_path / "python.svg"
    assert pb.main(["--root", str(tmp_path), "--ci", "pr-check.yml", "--out", str(out)],
                   прогоны=lambda f: [], работы=lambda r: []) == 2
    assert not out.exists()


# ── зоны выпуска: покрытие, release / PyPI, версия ─────────────────────────

def test_выпуск_совпадает_с_pypi_зелёный_и_коротко():
    часть = pb.зона_выпуска("v1.5.0", "1.5.0", True)[1]
    assert часть[0] == "1.5" and часть[1] == pb.СОСТОЯНИЯ["pass"][0]


def test_выпуск_расходится_с_pypi_красный_и_оба_номера():
    часть = pb.зона_выпуска("v2.8.0", "2.7.0", True)[1]
    assert часть[0] == "2.8 / 2.7" and часть[1] == pb.СОСТОЯНИЯ["fail"][0]


def test_pypi_не_объявлен_серый_с_номером_выпуска():
    часть = pb.зона_выпуска("v1.5.0", None, False)[1]
    assert часть[0] == "1.5" and часть[1] == pb.СОСТОЯНИЯ["none"][0]


def test_объявлен_но_пакета_на_pypi_нет_красный():
    часть = pb.зона_выпуска("v1.5.0", None, True)[1]
    assert часть[0] == "1.5 / —" and часть[1] == pb.СОСТОЯНИЯ["fail"][0]


def test_покрытие_по_порогам_coverage_badge():
    assert pb.зона_покрытия("72%")[1][:2] == ("72%", pb.ЦВЕТ_ПОКРЫТИЯ["yellow"])
    assert pb.зона_покрытия("95%")[1][1] == pb.ЦВЕТ_ПОКРЫТИЯ["brightgreen"]
    assert pb.зона_покрытия(None)[1][1] == pb.СОСТОЯНИЯ["none"][0]


def test_порядок_зон_версия_последней(tmp_path):
    """Решение владельца: проверки, ОС, покрытие, выпуск, версия — последней."""
    out = tmp_path / "python.svg"
    (tmp_path / "v.json").write_text('{"message": "1.5.3"}', encoding="utf-8")
    (tmp_path / "c.json").write_text('{"message": "72%"}', encoding="utf-8")
    исходы = {"ci.yml": [прогон("success", "2026-10-01T10:00Z")],
              "python-next.yml": [прогон("success", "2026-10-01T10:00Z")]}
    assert pb.main(["--root", str(дерево(tmp_path)), "--out", str(out),
                    "--coverage-json", str(tmp_path / "c.json"),
                    "--version-json", str(tmp_path / "v.json")],
                   прогоны=исходы.__getitem__,
                   работы=lambda r: [работа("success", "ubuntu-latest")],
                   релиз=lambda: "v1.5.0") == 0
    картинка = out.read_text(encoding="utf-8")
    порядок = [картинка.index(f">{т}<") for т in
               ("Python", "linux", "coverage", "release / PyPI", "version")]
    assert порядок == sorted(порядок)


def test_молчание_pypi_это_третий_исход(tmp_path):
    def молчит(пакет: str) -> str | None:
        raise pb.НеОтветила("PyPI: timeout")
    исходы = {"ci.yml": [прогон("success", "2026-10-01T10:00Z")], "python-next.yml": []}
    assert pb.main(["--root", str(дерево(tmp_path)), "--out", str(tmp_path / "p.svg"),
                    "--pypi", "stepik-python-grader"],
                   прогоны=исходы.__getitem__, работы=lambda r: [],
                   релиз=lambda: "v2.8.0", pypi=молчит) == 2


def test_второе_покрытие_по_всем_ос_рядом_через_слеш():
    """Решение владельца: у проекта с кодом под свою ОС два покрытия —
    основное и по всем ОС; второе число видно только когда оно есть."""
    подпись, часть = pb.зона_покрытия("72%", "85%")
    assert подпись[0] == "coverage / all (os)"
    assert часть[0] == "72% / 85%" and часть[1] == pb.ЦВЕТ_ПОКРЫТИЯ["yellow"]
    подпись, часть = pb.зона_покрытия("72%", None)
    assert (подпись[0], часть[0]) == ("coverage", "72%")
    assert pb.зона_покрытия("72%", "72%")[1][0] == "72%"


def test_сравнение_по_показанным_двум_числам():
    """Находка обзора #653 и решение владельца: выпуск и PyPI всегда `X.Y.0`,
    третье число — счётчик версии. Сравниваются показанные два числа, и
    красного над `2.8 / 2.8` не бывает."""
    часть = pb.зона_выпуска("v2.8.0", "2.8.0", True)[1]
    assert часть[0] == "2.8" and часть[1] == pb.СОСТОЯНИЯ["pass"][0]
    assert pb.зона_выпуска("v2.8.0", "2.8.3", True)[1][1] == pb.СОСТОЯНИЯ["pass"][0]


def test_каждый_порог_покрытия_имеет_цвет_на_значке():
    """Находка обзора #653: имя порога из coverage_badge.COLORS без цвета
    здесь уронило бы сборку KeyError — расхождение ловится набором."""
    import coverage_badge
    assert {имя for _, имя in coverage_badge.COLORS} <= set(pb.ЦВЕТ_ПОКРЫТИЯ)


def test_заданный_но_отсутствующий_файл_значка_это_третий_исход(tmp_path):
    """Находка обзора #653: упавший шаг покрытия не рисуется серым
    «не измерено» — значок не собирается, прежний остаётся (039)."""
    исходы = {"ci.yml": [прогон("success", "2026-10-01T10:00Z")], "python-next.yml": []}
    out = tmp_path / "p.svg"
    assert pb.main(["--root", str(дерево(tmp_path)), "--out", str(out),
                    "--coverage-json", str(tmp_path / "нет.json")],
                   прогоны=исходы.__getitem__, работы=lambda r: []) == 2
    (tmp_path / "битый.json").write_text("{", encoding="utf-8")
    assert pb.main(["--root", str(tmp_path), "--out", str(out),
                    "--version-json", str(tmp_path / "битый.json")],
                   прогоны=исходы.__getitem__, работы=lambda r: []) == 2
    assert not out.exists()


def test_нет_пакета_на_pypi_узнаётся_по_коду_а_не_подстроке():
    """Находка обзора #653: «404» в порте или адресе не значит «пакета нет».
    Форма строки, которую отдаёт fetch, закреплена здесь же."""
    import urllib.error
    отказ = f"не прочитан: {urllib.error.HTTPError('u', 404, 'Not Found', None, None)}"
    assert pb.НЕТ_ПАКЕТА.search(отказ)
    assert not pb.НЕТ_ПАКЕТА.search("не прочитан: <urlopen error [Errno 111] host:4040>")
    assert not pb.НЕТ_ПАКЕТА.search("не прочитан: HTTP Error 503: Service Unavailable")


def test_файл_значка_без_числа_это_третий_исход(tmp_path):
    """Находка обзора #653: файл есть, а message пуст или не число —
    это не «не измерено», а непрочитанный ответ (039)."""
    исходы = {"ci.yml": [прогон("success", "2026-10-01T10:00Z")], "python-next.yml": []}
    out = tmp_path / "p.svg"
    корень = дерево(tmp_path)
    for имя, тело, ключ in (("c.json", '{"message": "n/a"}', "--coverage-json"),
                            ("v.json", '{"message": ""}', "--version-json")):
        (tmp_path / имя).write_text(тело, encoding="utf-8")
        assert pb.main(["--root", str(корень), "--out", str(out), ключ, str(tmp_path / имя)],
                       прогоны=исходы.__getitem__, работы=lambda r: []) == 2
    assert not out.exists()


# ── префикс «CI»: подпись всей картинки, а не статус (#719) ────────────────

def _картинка(tmp_path, *доп: str) -> str:
    out = tmp_path / "python.svg"
    исходы = {"ci.yml": [прогон("failure", "2026-10-01T11:00Z")],
              "python-next.yml": [прогон("success", "2026-10-01T11:00Z")]}
    assert pb.main(["--root", str(дерево(tmp_path)), "--out", str(out), *доп],
                   прогоны=исходы.__getitem__,
                   работы=lambda r: [работа("failure", "ubuntu-latest")]) == 0
    return out.read_text(encoding="utf-8")


def _цвета(картинка: str) -> list[str]:
    return [к.split('fill="')[1].split('"')[0] for к in картинка.split('<rect x="')[1:]]


def test_префикс_ci_первым_нейтральным_цветом(tmp_path):
    """Цвет исхода остаётся у «Python»: подпись не спорит с цветом."""
    картинка = _картинка(tmp_path)
    assert картинка.index(">CI<") < картинка.index(">Python<")
    цвета = _цвета(картинка)
    assert цвета[0] == pb.ПОДПИСЬ and цвета[1] == pb.СОСТОЯНИЯ["fail"][0]
    assert "CI:" not in картинка.split("<title>")[1].split("</title>")[0]


def test_префикс_частью_первой_зоны():
    """Вариант A4 (выбор владельца 08.10): «CI» — часть первой зоны, а не своя
    зона, и стоит прямо перед «Python». Число зон не зависит от префикса —
    прежний счёт «+ 3» ломался от новой зоны (находка обзора #720)."""
    зоны = pb.зоны_проверок([("3.14", "pass"), ("linux", "pass")], "fail")
    assert [т for т, _, _ in зоны[0][:2]] == ["CI", "Python"]
    assert all("CI" not in [т for т, _, _ in з] for з in зоны[1:])
    assert pb.рисунок(зоны).count("<clipPath") == len(зоны)


def test_префикс_не_настраивается(tmp_path):
    """Решение владельца 08.10: «CI» стоит всегда, входа нет."""
    with pytest.raises(SystemExit):
        _картинка(tmp_path, "--prefix", "")