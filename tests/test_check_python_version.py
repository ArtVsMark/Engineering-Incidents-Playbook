"""Три числа версии сходятся: гейт проверяется тем, что обязан отвергнуть,
и тем, что обязан пропустить.

Пропуск здесь дороже ложного отказа, и это не рассуждение, а разбор: «чисто
локально», снятое НИЖЕ объявленной планки, — утверждение о поверхности, на
которой изменение не поедет. Автор ему верит и толкает.

Источник подделки (правило 170): подделывается свой же манифест и свои же
прогоны — их форма снята с дерева каталога, `pyproject.toml` и
`.github/workflows/*.yml`.
"""


import pytest
import check_python_version as cv


ПЛАНКА = (3, 12)


# ── разбор объявлений ──────────────────────────────────────────────────────

def test_planka_chitaetsya():
    assert cv.floor('requires-python = ">=3.12"\n') == (3, 12)


def test_planka_bez_obyavleniya():
    assert cv.floor("[project]\nname = 'x'\n") is None


def test_versiya_progona_chitaetsya(tmp_path):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "a.yml").write_text(
        '        with:\n          python-version: "3.12"\n', encoding="utf-8")
    assert cv.in_workflows(tmp_path) == [("a.yml", (3, 12))]


def test_versiya_bez_kavychek_tozhe_chitaetsya(tmp_path):
    """У площадки кавычки необязательны, и находка должна быть о ВЕРСИИ, а не
    о кавычках (051)."""
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "a.yml").write_text(
        "          python-version: 3.13\n", encoding="utf-8")
    assert cv.in_workflows(tmp_path) == [("a.yml", (3, 13))]


# ── что гейт обязан отвергнуть ─────────────────────────────────────────────

def test_okno_nizhe_planki_nahodka():
    """ГЛАВНЫЙ СЛУЧАЙ, И ОН ЖИВОЙ: 4 сентября окно работало на 3.11.15 при
    планке >=3.12, и «чисто: 39 шагов» печаталось с неё же."""
    найдено = cv.findings(ПЛАНКА, [("ci.yml", (3, 12))], (3, 11))
    assert найдено and "прогон перед толчком" in найдено[0]


def test_progon_nizhe_planki_nahodka():
    найдено = cv.findings(ПЛАНКА, [("ci.yml", (3, 11))], (3, 12))
    assert найдено and "ci.yml" in найдено[0]


def test_progony_razoshlis_bez_planki_nahodka():
    """Разные версии без планки среди них: обещание потребителю не проверяет
    ни один прогон."""
    найдено = cv.findings(ПЛАНКА, [("a.yml", (3, 13)), ("b.yml", (3, 14))],
                          (3, 13))
    assert any("разные версии" in n for n in найдено)


def test_planka_i_obyazatelnaya_vyshe_ne_nahodka():
    """Планка и обязательная версия выше неё — законно (решение владельца
    14 октября: планка 3.14, обязательная 3.15)."""
    найдено = cv.findings(ПЛАНКА, [("ci.yml", (3, 12)), ("ci.yml", (3, 13))],
                          (3, 12))
    assert not найдено


def test_predvaritelnyy_ne_vyshe_progonov_nahodka():
    """Предварительный прогон на версии прочих ничего не спрашивает о
    следующей, а выглядит так, будто спрашивает (051)."""
    найдено = cv.findings(ПЛАНКА, [("ci.yml", (3, 12))], (3, 12),
                          [("next.yml", (3, 12))])
    assert найдено and "предварительный" in найдено[0]


# ── что гейт обязан пропустить ─────────────────────────────────────────────
def test_predvaritelnyy_vyshe_ne_schitaetsya_raznoy_versiey():
    """Предварительный прогон — вопрос о следующей версии, а не прогон,
    закрывающий изменение: «все на одной версии» его не касается."""
    assert cv.findings(ПЛАНКА, [("ci.yml", (3, 12))], (3, 12),
                       [("next.yml", (3, 13))]) == []


def test_pometka_chitaetsya_tolko_v_svoyom_with(tmp_path):
    """Пометка относится к своему `with:`: соседняя работа без неё остаётся
    обычным прогоном, а помеченная уходит в предварительные."""
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "a.yml").write_text(
        "      - uses: actions/setup-python@v6\n"
        "        with:\n"
        '          python-version: "3.15"\n'
        "          allow-prereleases: true\n"
        "      - uses: actions/setup-python@v6\n"
        "        with:\n"
        '          python-version: "3.14"\n', encoding="utf-8")
    assert cv.in_workflows(tmp_path) == [("a.yml", (3, 14))]
    assert cv.in_workflows(tmp_path, preview=True) == [("a.yml", (3, 15))]


def test_pometka_vyshe_versii_tozhe_chitaetsya(tmp_path):
    """Порядок ключей в `with:` значения не имеет: пометка над версией
    обязана читаться так же, как под ней."""
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "a.yml").write_text(
        "      - uses: actions/setup-python@v6\n"
        "        with:\n"
        "          allow-prereleases: true\n"
        '          python-version: "3.15"\n'
        "      - uses: actions/setup-python@v6\n"
        "        with:\n"
        '          python-version: "3.14"\n', encoding="utf-8")
    assert cv.in_workflows(tmp_path) == [("a.yml", (3, 14))]
    assert cv.in_workflows(tmp_path, preview=True) == [("a.yml", (3, 15))]



def test_vsyo_shoditsya_chisto():
    assert cv.findings(ПЛАНКА, [("ci.yml", (3, 12))], (3, 12)) == []


def test_okno_vyshe_planki_ne_nahodka():
    """ГРАНИЦА: планка НИЖНЯЯ. Окно новее объявленного — законно, и красное на
    нём приучало бы читать красное как фон (051). Верхних границ у нас нет
    намеренно: потолок версии запрещает потребителю обновляться."""
    assert cv.findings(ПЛАНКА, [("ci.yml", (3, 12))], (3, 13)) == []


def test_progon_vyshe_planki_ne_nahodka():
    assert cv.findings(ПЛАНКА, [("ci.yml", (3, 13))], (3, 13)) == []


# ── решение гейта, а не повторение его условия (правило 150) ───────────────

def дерево(tmp_path, планка: str, версия: str):
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nrequires-python = "{планка}"\n', encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        f'        with:\n          python-version: "{версия}"\n',
        encoding="utf-8")
    return ["--root", str(tmp_path)]


def test_glavnyy_otvet_gejta_otkaz(tmp_path):
    """Прогон гоняет версию ниже объявленной планки — конвейер проверяет то,
    чего проект не поддерживает."""
    assert cv.main(дерево(tmp_path, ">=3.12", "3.11")) == 1


def test_shoditsya_gejt_molchit(tmp_path):
    """Обратная половина: планка нижняя, и окно новее её законно. Красное на
    верном приучало бы читать красное как фон (051)."""
    высокая = f"3.{__import__('sys').version_info[1]}"
    assert cv.main(дерево(tmp_path, ">=3.8", высокая)) == 0


# ── исход 2 ────────────────────────────────────────────────────────────────

def test_net_manifesta_eto_tretiy_ishod(tmp_path):
    assert cv.main(["--root", str(tmp_path)]) == 2


def test_net_progonov_s_versiey_eto_tretiy_ishod(tmp_path):
    """Гейт, не нашедший предмета, обязан упасть, а не зазеленеть (075)."""
    (tmp_path / "pyproject.toml").write_text('requires-python = ">=3.12"\n',
                                             encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    assert cv.main(["--root", str(tmp_path)]) == 2


# ── работа без setup-python гоняет код системным python раннера ───────────

def _работа(tmp_path, шаги: str):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "w.yml").write_text(
        "on: push\njobs:\n  open:\n    runs-on: ubuntu-latest\n    steps:\n" + шаги,
        encoding="utf-8")
    return tmp_path


def test_python_без_setup_python_находка(tmp_path):
    """Замер 02.10: открытие изменения, автомерж и сверка задач гоняли код
    каталога системным python раннера — числа версии в них нет, и
    in_workflows их не видел."""
    корень = _работа(tmp_path, "      - uses: actions/checkout@v5\n"
                              "      - run: python3 scripts/pr_body.py --check\n")
    assert any("работа open" in н for н in cv.мимо_планки(корень))


def test_python_раньше_setup_python_находка(tmp_path):
    корень = _работа(tmp_path, "      - run: python3 scripts/a.py\n"
                              "      - uses: actions/setup-python@v6\n"
                              "        with:\n          python-version: \"3.14\"\n")
    assert len(cv.мимо_планки(корень)) == 1


def test_python_после_setup_python_чисто(tmp_path):
    корень = _работа(tmp_path, "      - uses: actions/setup-python@v6\n"
                              "        with:\n          python-version: \"3.14\"\n"
                              "      - run: python3 scripts/a.py\n")
    assert cv.мимо_планки(корень) == []


def test_слово_python_в_комментарии_и_имени_не_вызов(tmp_path):
    корень = _работа(tmp_path, "      # python scripts/a.py здесь не зовётся\n"
                              "      - name: python scripts/b.py в имени\n"
                              "        run: echo ok\n")
    assert cv.мимо_планки(корень) == []


def test_настоящие_прогоны_на_планке():
    from conftest import SCRIPTS
    assert cv.мимо_планки(SCRIPTS.parent) == []


# ── составное действие — тоже прогон (217) ────────────────────────────────

def _действие(tmp_path, путь: str, шаги: str):
    файл = tmp_path / путь
    файл.parent.mkdir(parents=True, exist_ok=True)
    файл.write_text("runs:\n  using: composite\n  steps:\n" + шаги, encoding="utf-8")
    return tmp_path


НА_ПЛАНКЕ = ("    - uses: actions/setup-python@v6\n"
             "      with:\n        python-version: \"3.14\"\n"
             "    - run: python \"$GITHUB_ACTION_PATH/scripts/a.py\"\n"
             "      shell: bash\n")


def test_корневое_действие_ниже_планки_находка(tmp_path):
    """Замер 02.10: #647 перевёл .github/actions/ на 3.14, а корневое
    action.yml — действие ПОТРЕБИТЕЛЕЙ — оставил на 3.12, и гейт его не читал."""
    корень = _действие(tmp_path, "action.yml", НА_ПЛАНКЕ.replace("3.14", "3.12"))
    найдено = cv.действия_мимо_планки(корень, (3, 14))
    assert найдено and найдено[0].startswith("action.yml: ставит 3.12")


def test_вложенное_действие_ниже_планки_находка(tmp_path):
    корень = _действие(tmp_path, ".github/actions/x/action.yml",
                       НА_ПЛАНКЕ.replace("3.14", "3.13"))
    assert cv.действия_мимо_планки(корень, (3, 14)) == [
        ".github/actions/x/action.yml: ставит 3.13, а pyproject.toml объявляет "
        ">=3.14 — код каталога исполняется версией, на которой он не написан"]


def test_действие_без_setup_python_находка(tmp_path):
    корень = _действие(tmp_path, "action.yml",
                       "    - run: python3 scripts/a.py\n      shell: bash\n")
    assert any("раньше setup-python" in н
               for н in cv.действия_мимо_планки(корень, (3, 14)))


def test_действие_на_планке_чисто(tmp_path):
    корень = _действие(tmp_path, "action.yml", НА_ПЛАНКЕ)
    assert cv.действия_мимо_планки(корень, (3, 14)) == []


def test_настоящие_действия_на_планке():
    from conftest import SCRIPTS
    корень = SCRIPTS.parent
    assert len(cv.действия(корень)) >= 2
    assert cv.действия_мимо_планки(корень, cv.floor(
        (корень / "pyproject.toml").read_text(encoding="utf-8"))) == []


# ── шаг установки — строка uses:, и число у него обязательно (#678) ───────

ВЫЗОВ = "    - run: python scripts/a.py\n      shell: bash\n"
УСТАНОВКА = ("    - uses: actions/setup-python@v6\n"
             "      with:\n        python-version: \"3.14\"\n")


def test_слово_setup_python_в_комментарии_не_прячет_ранний_вызов(tmp_path):
    """Находка обзора #678: позиция установки искалась подстрокой по тексту с
    комментариями — упоминание выше вызова делало установку «ранней»."""
    корень = _действие(tmp_path, "action.yml",
                       "    # setup-python ставится ниже\n" + ВЫЗОВ + УСТАНОВКА)
    assert any("раньше setup-python" in н
               for н in cv.действия_мимо_планки(корень, (3, 14)))


def test_установка_после_вызова_находка(tmp_path):
    корень = _действие(tmp_path, "action.yml", ВЫЗОВ + УСТАНОВКА)
    assert any("раньше setup-python" in н
               for н in cv.действия_мимо_планки(корень, (3, 14)))


@pytest.mark.parametrize("with_", [
    "      with:\n        python-version: ${{ inputs.python }}\n",
    "      with:\n        cache: pip\n",
    "",
])
def test_установка_без_числа_находка(tmp_path, with_):
    """Находка обзора #678: версия выражением, файлом или раннером — гейту не
    с чем сверять, и ниже планки она проходила молча."""
    корень = _действие(tmp_path, "action.yml",
                       "    - uses: actions/setup-python@v6\n" + with_ + ВЫЗОВ)
    assert any("без числа" in н for н in cv.действия_мимо_планки(корень, (3, 14)))


def test_with_до_uses_читается_тем_же_шагом(tmp_path):
    корень = _действие(tmp_path, "action.yml",
                       "    - name: python\n      with:\n        python-version: \"3.14\"\n"
                       "      uses: actions/setup-python@v6\n" + ВЫЗОВ)
    assert cv.действия_мимо_планки(корень, (3, 14)) == []


def test_работа_с_установкой_без_числа_находка(tmp_path):
    """Сосед по признаку (195): работа в .github/workflows/ с версией из матрицы
    не попадала в in_workflows вовсе — числа нет."""
    корень = _работа(tmp_path, "      - uses: actions/setup-python@v6\n"
                              "        with:\n          python-version: ${{ matrix.py }}\n"
                              "      - run: python3 scripts/a.py\n")
    assert any("без числа" in н for н in cv.мимо_планки(корень))


def test_работа_слово_в_комментарии_не_прячет_ранний_вызов(tmp_path):
    корень = _работа(tmp_path, "      # setup-python ниже\n"
                              "      - run: python3 scripts/a.py\n"
                              "      - uses: actions/setup-python@v6\n"
                              "        with:\n          python-version: \"3.14\"\n")
    assert len(cv.мимо_планки(корень)) == 1


@pytest.mark.parametrize("версия", ['"3.14"', "'3.14'", "3.14"])
def test_число_в_любых_кавычках_читается(tmp_path, версия):
    """Находка обзора #680: одинарные кавычки выпадали из CI_RE, и шаг с верным
    числом считался шагом «без числа» — гейт отвергал то, что обязан пропустить."""
    корень = _действие(tmp_path, "action.yml",
                       "    - uses: actions/setup-python@v6\n"
                       f"      with:\n        python-version: {версия}\n" + ВЫЗОВ)
    assert cv.действия_мимо_планки(корень, (3, 14)) == []


def test_одинарные_кавычки_видит_и_сверка_прогонов(tmp_path):
    """Сосед по признаку (195): in_workflows читает тот же образец."""
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "a.yml").write_text(
        "jobs:\n  t:\n    steps:\n      - uses: actions/setup-python@v6\n"
        "        with:\n          python-version: '3.13'\n", encoding="utf-8")
    assert cv.in_workflows(tmp_path) == [("a.yml", (3, 13))]


# ── версия из матрицы работы (#926) ─────────────────────────────────────────
# Формы — из справки площадки «Using a matrix for your jobs» (210): список в
# строку с любыми кавычками, список столбцом, одно значение, ячейки include;
# отказ — выражение вместо списка, ячейка не формы X.Y, оси нет, матрицы нет.

def _матрица(tmp_path, матрица: str, установка: str = "") -> object:
    (tmp_path / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        "on: push\njobs:\n  test-matrix:\n    runs-on: ubuntu-latest\n"
        "    strategy:\n      fail-fast: false\n" + матрица +
        "    steps:\n      - uses: actions/setup-python@v6\n        with:\n"
        "          python-version: ${{ matrix.python }}\n" + установка,
        encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("матрица, версии", [
    ('      matrix:\n        python: ["3.14", "3.15"]\n', [(3, 14), (3, 15)]),
    ("      matrix:\n        python: ['3.14', '3.15']\n", [(3, 14), (3, 15)]),
    ("      matrix:\n        python: [3.14, 3.15]\n", [(3, 14), (3, 15)]),
    ('      matrix:\n        python:\n          - "3.14"\n          - "3.15"\n', [(3, 14), (3, 15)]),
    ('      matrix:\n        python: [\n          "3.14",\n          "3.15"]\n', [(3, 14), (3, 15)]),
    ('      matrix:\n        python: "3.14"\n', [(3, 14)]),
    ('      matrix:\n        os: [ubuntu-latest]\n        python: ["3.14"]\n'
     '        include:\n          - python: "3.15"\n            os: ubuntu-latest\n',
     [(3, 14), (3, 15)]),
    ('      matrix:\n        include:\n          - os: ubuntu-latest\n            python: "3.14"\n',
     [(3, 14)]),
    ('      matrix:\n        python:\n          - "3.14"  # планка\n          - 3.15 # обязательная\n',
     [(3, 14), (3, 15)]),                                         # комментарии у ячеек (обзор #928)
    ('      matrix:\n        python: [\n          "3.14",  # планка\n          "3.15"]\n', [(3, 14), (3, 15)]),
    ('      matrix:\n        python: ["3.14"]  # основные\n', [(3, 14)]),
])
def test_ось_матрицы_разбирается_во_всех_формах(tmp_path, матрица, версии):
    корень = _матрица(tmp_path, матрица)
    assert sorted(в for _, в in cv.in_workflows(корень)) == версии
    assert cv.отказы_матриц(корень) == []
    assert not cv.мимо_планки(корень)   # шаг с разобранной осью — с числом


@pytest.mark.parametrize("матрица, причина", [
    ("      matrix:\n        python: ${{ fromJSON(needs.a.outputs.v) }}\n", "выражение"),
    ('      matrix:\n        python: ["3.14", "3.x"]\n', "не формы X.Y"),
    ('      matrix:\n        py: ["3.14"]\n', "оси python в матрице нет"),
    ("      runs-on2: x\n", "матрицы у работы нет"),
    ('      matrix:\n        python: ["3.14"]\n        include:\n'
     '          - python: ${{ fromJSON(needs.a.outputs.v) }}\n', "ячейка include"),   # обзор #928
])
def test_ось_матрицы_не_разобралась_отказ_с_адресом(tmp_path, матрица, причина):
    """Ячейка иной формы — отказ с адресом, а не молчаливый пропуск (#926)."""
    корень = _матрица(tmp_path, матрица)
    отказы = cv.отказы_матриц(корень)
    assert len(отказы) == 1 and причина in отказы[0]
    assert отказы[0].startswith(".github/workflows/ci.yml: работа test-matrix:")
    assert cv.in_workflows(корень) == []
    assert any("без числа" in н for н in cv.мимо_планки(корень))


def test_предрелизная_матрица_читается_предварительной(tmp_path):
    """allow-prereleases в том же with: — предварительная, число буквой не нужно (#926)."""
    корень = _матрица(tmp_path, '      matrix:\n        python: ["3.16"]\n',
                      "          allow-prereleases: true\n")
    assert cv.in_workflows(корень) == []
    assert cv.in_workflows(корень, preview=True) == [("ci.yml", (3, 16))]


def test_гейт_называет_отказ_матрицы(tmp_path, capsys):
    корень = _матрица(tmp_path, '      matrix:\n        python: ["3.14", "3.x"]\n'
                      )
    (корень / "pyproject.toml").write_text('requires-python = ">=3.14"\n', encoding="utf-8")
    with open(корень / ".github" / "workflows" / "ci.yml", "a", encoding="utf-8") as f:
        f.write('  lint:\n    runs-on: ubuntu-latest\n    steps:\n'
                '      - uses: actions/setup-python@v6\n        with:\n          python-version: "3.14"\n')
    assert cv.main(["--root", str(корень)]) == 1
    assert "не формы X.Y" in capsys.readouterr().err
