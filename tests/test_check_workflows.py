"""Ручная кнопка и предел времени: подделка вместо зелени живого корпуса.

Гейт проверяет свойства файлов конвейера, и его ошибка тиха в обе стороны.
Пропущенная работа без предела оставит очередь висеть до умолчания площадки —
молчание вместо отказа. Ложная находка на законном файле приучит читать его
красное как фон (051).

ГЛАВНЫЙ СЛУЧАЙ ЗДЕСЬ — ПОСЛЕДНЯЯ РАБОТА В ФАЙЛЕ. Первая версия разбора
закрывала работу только по началу следующей, а конец файла обозначала строкой
с кириллическим именем, которая ключом не считалась. Гейт был зелёным на живом
корпусе и не держал ничего: у `ci.yml` и `attribution-history.yml` предела не
было, а он молчал (146). Поймано это было тем, что факт знали заранее, — то
есть не механизмом. Здесь стоит случай, который поймал бы это сам.

Площадка не трогается: разбор — чистая функция над текстом файла.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import check_workflows as cw

BUTTON = "on:\n  push:\n  workflow_dispatch:\n"


def workflow(root: Path, name: str, text: str) -> Path:
    path = root / ".github" / "workflows" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ── ручная кнопка (126) ────────────────────────────────────────────────────

def test_knopka_v_blochnoy_forme_naydena():
    assert cw.has_button(BUTTON)


def test_knopka_spiskom_naydena():
    """`on: [push, workflow_dispatch]` — та же кнопка, другая запись."""
    assert cw.has_button("on: [push, workflow_dispatch]\n")


def test_bez_knopki_nahodka(tmp_path):
    workflow(tmp_path, "w.yml",
             "on:\n  push:\njobs:\n  a:\n    timeout-minutes: 5\n")
    assert cw.main(["--root", str(tmp_path)]) == 1


def test_slovo_v_kommentarii_ne_schitaetsya_knopkoy():
    """Упоминание в прозе кнопкой не является: запускать нечего."""
    assert not cw.has_button("# тут был бы workflow_dispatch\non:\n  push:\n")


# ── предел времени (100) ───────────────────────────────────────────────────

def test_rabota_bez_predela_nahodka(tmp_path):
    workflow(tmp_path, "w.yml", BUTTON + "jobs:\n  a:\n    runs-on: x\n")
    assert cw.main(["--root", str(tmp_path)]) == 1


def test_poslednyaya_rabota_v_fayle_proveryaetsya(tmp_path):
    """Регресс: закрывать работу только началом следующей — значит не
    проверять последнюю ни в одном файле, а она там есть всегда."""
    text = BUTTON + "jobs:\n  a:\n    timeout-minutes: 5\n  b:\n    runs-on: x\n"
    assert cw.jobs_without_timeout(text) == ["b"]


def test_edinstvennaya_rabota_bez_predela_naydena():
    """Частный случай того же: единственная работа — сразу и последняя."""
    assert cw.jobs_without_timeout(BUTTON + "jobs:\n  a:\n    runs-on: x\n") == ["a"]


def test_sobytiya_ne_prinimayutsya_za_raboty():
    """Ключи внутри `on:` выглядят как работы; требовать от `push` предела
    времени значило бы краснеть на верном файле."""
    assert cw.jobs_without_timeout("on:\n  push:\n  pull_request:\n") == []


def test_predel_u_kazhdoy_raboty_chisto():
    text = BUTTON + "jobs:\n  a:\n    timeout-minutes: 5\n  b:\n    timeout-minutes: 7\n"
    assert cw.jobs_without_timeout(text) == []


# ── три исхода ─────────────────────────────────────────────────────────────

def test_chisto_eto_nol(tmp_path):
    workflow(tmp_path, "w.yml", BUTTON + "jobs:\n  a:\n    timeout-minutes: 5\n")
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_net_fayla_progona_eto_dva_a_ne_chisto(tmp_path):
    """Ноль файлов — проверять нечего, и зелёный здесь означал бы «всё в
    порядке» о том, чего не смотрели (075)."""
    assert cw.main(["--root", str(tmp_path)]) == 2


def test_nahodka_nazyvaet_fayl_i_rabotu(tmp_path, capsys):
    workflow(tmp_path, "ci.yml", BUTTON + "jobs:\n  catalogue:\n    runs-on: x\n")
    assert cw.main(["--root", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert "ci.yml" in err and "catalogue" in err


# ── необязательный канал не держит слияние (084) ───────────────────────────

def test_neobyazatelnyy_progon_na_izmenenii_nahodka(tmp_path):
    """Значок, отказавший на изменении, задерживает слияние — при том что его
    отсутствие штатный исход, а не ошибка."""
    workflow(tmp_path, "badges.yml",
             "on:\n  pull_request:\n  workflow_dispatch:\njobs:\n  a:\n    timeout-minutes: 5\n")
    assert cw.main(["--root", str(tmp_path)]) == 1


def test_obyazatelnye_proverki_na_izmenenii_zakonny(tmp_path):
    """`ci.yml` за тем и заведён: он и есть основная работа."""
    workflow(tmp_path, "ci.yml",
             "on:\n  pull_request:\n  workflow_dispatch:\njobs:\n  a:\n    timeout-minutes: 5\n")
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_neobyazatelnyy_na_raspisanii_zakonen(tmp_path):
    """Ночной прогон слияние не трогает — предмета правила здесь нет."""
    workflow(tmp_path, "badges.yml",
             "on:\n  schedule:\n  workflow_dispatch:\njobs:\n  a:\n    timeout-minutes: 5\n")
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_sobytiya_chitayutsya_i_spiskom():
    assert cw.events("on: [push, pull_request]\n") == {"push", "pull_request"}


# ── закрепление вызываемого (152) ──────────────────────────────────────────

def test_opasnoe_sobytie_bez_zakrepleniya_nahodka(tmp_path):
    """На `pull_request_target` файл прогона берётся с общей ветки, и код
    исполняется при её правах: здесь закреплять обязательно."""
    workflow(tmp_path, "risky.yml",
             "on:\n  pull_request_target:\n  workflow_dispatch:\n"
             "jobs:\n  a:\n    timeout-minutes: 5\n    steps:\n"
             "      - uses: actions/checkout@v4\n")
    assert cw.main(["--root", str(tmp_path)]) == 1


def test_bez_chuzhogo_koda_zakreplyat_nechego(tmp_path):
    """ВТОРАЯ ГРАНИЦА, И ОНА ИЗ ЖИВОГО ОТКАЗА. Прогон на `workflow_run`, у
    которого нет ни выкачки, ни чужого действия, исполняет только собственные
    `run:` — а сам файл на этом событии берётся с общей ветки. Закреплять
    нечего, и требование заставило бы ДОБАВИТЬ выкачку ради проверки, которая
    её же и сторожит. Замер: так гейт отверг `thaw.yml` (051)."""
    workflow(tmp_path, "thaw.yml",
             "on:\n  workflow_run:\n  workflow_dispatch:\n"
             "jobs:\n  a:\n    timeout-minutes: 5\n    steps:\n"
             "      - run: gh workflow run automerge.yml\n")
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_opasnoe_sobytie_s_zakrepleniem_chisto(tmp_path):
    workflow(tmp_path, "risky.yml",
             "on:\n  pull_request_target:\n  workflow_dispatch:\n"
             "jobs:\n  a:\n    timeout-minutes: 5\n    steps:\n"
             "      - uses: actions/checkout@v4\n        with:\n          ref: main\n")
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_na_pull_request_zakreplenie_ne_trebuetsya(tmp_path):
    """ГРАНИЦА, И ОНА ЕСТЬ ИНЦИДЕНТ ПРАВИЛА: на `pull_request` сам файл прогона
    берётся ИЗ ИЗМЕНЕНИЯ. Правящий изменение переписывает шаг и зовёт что
    угодно — закреплённый скрипт просто перестаёт вызываться. Требовать
    закрепление здесь значит требовать защиту с нулевой ценностью."""
    workflow(tmp_path, "ci.yml",
             "on:\n  pull_request:\n  workflow_dispatch:\n"
             "jobs:\n  a:\n    timeout-minutes: 5\n")
    assert cw.main(["--root", str(tmp_path)]) == 0


# ── имена оболочки латиницей (167) ─────────────────────────────────────────

def test_env_klyuch_kirillicey_nahodka(tmp_path):
    """Тихая половина ошибки: переменная создаётся, а `$ТИП` не раскрывается —
    условие всегда даёт одну ветку, и шаг зеленеет, не проверив ничего."""
    workflow(tmp_path, "w.yml", BUTTON + "jobs:\n  a:\n    timeout-minutes: 5\n"
             "    env:\n      ТИП: bug\n")
    assert cw.main(["--root", str(tmp_path)]) == 1


def test_prisvaivanie_kirillicey_nahodka():
    """Громкая половина: bash разбирает строку как ИМЯ КОМАНДЫ, код 127."""
    assert cw.non_ascii_names("        файлы=$(git diff)\n") == ["файлы"]


def test_latinskie_imena_chisto():
    текст = "    env:\n      TYPE: bug\n      BASE: main\n"
    assert cw.non_ascii_names(текст) == []


def test_proza_i_imena_shagov_ne_trogayutsya(tmp_path):
    """ГРАНИЦА: имя шага и сообщение — на языке проекта, и требовать от них
    латиницу значило бы краснеть на верном файле (051)."""
    workflow(tmp_path, "w.yml", BUTTON + "jobs:\n  a:\n    timeout-minutes: 5\n"
             "    steps:\n      - name: зоны выводятся из путей верно\n"
             "        run: echo 'проверка прошла'\n")
    assert cw.main(["--root", str(tmp_path)]) == 0


# ── правило 179: группа отмены называет голову ──────────────────────────────

ГРУППА_БЕЗ_ГОЛОВЫ = (
    "concurrency:\n"
    "  group: ci-${{ github.ref }}\n"
    "  cancel-in-progress: true\n")
ГРУППА_С_ГОЛОВОЙ = (
    "concurrency:\n"
    "  group: ci-${{ github.ref }}-"
    "${{ github.event.pull_request.head.sha || github.sha }}\n"
    "  cancel-in-progress: true\n")
РАБОТА = "jobs:\n  a:\n    timeout-minutes: 5\n"


def test_otmena_bez_golovy_nahodka(tmp_path):
    """Тот самый предмет: github.ref на pull_request — refs/pull/N/merge, один
    для всех событий изменения, и прогон на устаревшем коммите вытесняет
    прогон на актуальном."""
    workflow(tmp_path, "w.yml", BUTTON + ГРУППА_БЕЗ_ГОЛОВЫ + РАБОТА)
    assert cw.main(["--root", str(tmp_path)]) == 1


def test_golova_v_gruppe_chisto(tmp_path):
    workflow(tmp_path, "w.yml", BUTTON + ГРУППА_С_ГОЛОВОЙ + РАБОТА)
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_gruppa_bez_otmeny_pod_pravilo_ne_podpadaet(tmp_path):
    """ГРАНИЦА: очередь ничего не вытесняет, и голова в ней раздробила бы ровно
    то, что собирают, — так устроены automerge и thaw."""
    текст = (BUTTON + "concurrency:\n  group: automerge-${{ inputs.pr }}\n"
             "  cancel-in-progress: false\n" + РАБОТА)
    workflow(tmp_path, "w.yml", текст)
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_predmet_sostoyanie_nazvan_spiskom(tmp_path):
    """ГРАНИЦА ИЗ САМОГО ПРАВИЛА: у badges предмет — состояние ветки, а не
    коммит, и голова вернула бы гонку двух писателей одного файла. Разрешение
    объявлено списком с причиной, а не выведено из формы файла."""
    workflow(tmp_path, "badges.yml", BUTTON
             + "concurrency:\n  group: badges\n  cancel-in-progress: true\n"
             + РАБОТА)
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_gruppa_vnutri_raboty_tozhe_razbiraetsya():
    """`concurrency` объявляют и на уровне работы; дефект там тот же, а
    sections() знает только ключи первой колонки."""
    текст = ("jobs:\n  a:\n    concurrency:\n      group: x-${{ github.ref }}\n"
             "      cancel-in-progress: true\n    timeout-minutes: 5\n")
    assert cw.cancelling_groups(текст) == [("x-${{ github.ref }}", True)]


# ── `id:` и вывод шага — идентификаторы, а не проза (правило 167) ───────────

def test_id_kirillicey_nahodka():
    """ЖИВОЙ ОТКАЗ, а не выдумка: `id: ключ` в review.yml сделал файл
    НЕРАЗБИРАЕМЫМ — прогон падал за ноль секунд, работ ноль, шагов ноль, и
    выглядело это обычным красным. Красный прогон на общей ветке заморозил
    очередь, и два изменения простояли молча."""
    текст = "jobs:\n  a:\n    steps:\n      - id: ключ\n        run: echo\n"
    assert cw.non_ascii_names(текст) == ["id: ключ"]


def test_obrashchenie_k_vyvodu_kirillicey_nahodka():
    текст = "        if: steps.ключ.outputs.есть == 'да'\n"
    assert cw.non_ascii_names(текст) == ["steps.ключ.outputs.есть"]


def test_name_shaga_ostayotsya_na_yazyke_proekta():
    """ГРАНИЦА, И ОНА ТОНКАЯ: `name:` — проза для человека и пишется
    по-русски; `id:` — имя для площадки. Прежняя редакция гейта не различала
    их и разрешала оба, потому что смотрела на КЛЮЧ, а не на значение."""
    текст = ("jobs:\n  a:\n    steps:\n"
             "      - name: ключа ревью нет — внешний взгляд не состоится\n"
             "        id: token\n        run: echo\n")
    assert cw.non_ascii_names(текст) == []


def test_latinskiy_vyvod_chisto():
    assert cw.non_ascii_names("        if: steps.token.outputs.present == 'yes'\n") == []



# ── код возврата доживает до разбора (145) ─────────────────────────────────


def test_prisvaivanie_koda_otdelnoy_strokoy_nahodka():
    """ЖИВОЙ ОТКАЗ, 4 сентября. `task-state` разбирал три исхода и объявлял
    себя предупреждением, а покраснел на первом же коммите, назвавшем задачу:
    площадка зовёт шаг как `bash -e {0}`, оболочка умерла на присвоении, и
    ни `printf`, ни обе ветки разбора не выполнились. Причина отказа при этом
    пропала вместе с выводом — красное было, диагностики не было."""
    текст = "        run: |\n          out=$(cmd 2>&1); rc=$?\n          echo x\n"
    assert cw.dead_exit_codes(текст) == ["строка 2: rc=$?"]


def test_prisvaivanie_na_svoey_stroke_nahodka():
    """Форма из самого правила 145: команда, следом `rc=$?` отдельной строкой."""
    текст = "        run: |\n          python x.py\n          rc=$?\n"
    assert cw.dead_exit_codes(текст) == ["строка 3: rc=$?"]


def test_forma_cherez_ili_zakonna():
    """`||` снимает `-e` со всей конструкции — присвоение выполняется."""
    текст = "        run: |\n          python x.py || rc=$?\n"
    assert cw.dead_exit_codes(текст) == []


def test_yavnaya_udacha_s_ili_zakonna():
    """`&& rc=0 || rc=$?` — та же живая форма с явным нулём."""
    текст = "        run: |\n          out=$(gh pr view 2>&1) && rc=0 || rc=$?\n"
    assert cw.dead_exit_codes(текст) == []


def test_probros_koda_naruzhu_ne_predmet():
    """`exit $?` разбором НЕ является: он отдаёт код наружу, и под `-e` итог
    тот же. Находка здесь была бы о форме, а не о поломке (051)."""
    assert cw.dead_exit_codes("        run: |\n          f\n          exit $?\n") == []


def test_usloviye_na_kode_ne_prinimaetsya_za_prisvaivanie():
    """Слева от `=` обязано стоять ИМЯ. `[ $? -eq 0 ]` присвоением не является."""
    assert cw.dead_exit_codes("        run: |\n          [ $? -eq 0 ] && echo x\n") == []


def test_upominanie_v_kommentarii_ne_nahodka():
    """Комментарий — проза о форме, а не сама форма. Ровно эта строка стоит в
    трёх прогонах каталога как предупреждение следующему."""
    текст = "        run: |\n          # без `rc=$?` тут ничего не разберётся\n"
    assert cw.dead_exit_codes(текст) == []


def test_hvostovoy_kommentariy_nahodku_ne_pryachet():
    """`#` ПОСЛЕ кода строку не оправдывает: форма от этого не оживает."""
    текст = "        run: |\n          cmd; rc=$?  # разберём ниже\n"
    assert cw.dead_exit_codes(текст) == ["строка 2: rc=$?"]


def прогон(код: str, оболочка: str | None = None) -> str:
    """Файл прогона с одним шагом `run:` — минимальный носитель предмета."""
    shell = f"        shell: {оболочка}\n" if оболочка else ""
    тело = "\n".join("          " + s for s in код.splitlines())
    return ("name: t\non: [push]\njobs:\n  j:\n    steps:\n"
            f"      - name: проба\n{shell}        run: |\n{тело}\n")


@pytest.mark.parametrize("код, что", [
    ("if [ 1 -eq 1 ]; then echo да; fi", "закрытое условие"),
    # bash кириллицу в ИМЕНИ ФУНКЦИИ принимает — в отличие от имени переменной,
    # и это разные предметы: 167 про второе, здесь про разбираемость вообще.
    ("квота_кончилась() { echo x; }", "имя функции не латиницей"),
    # Подстановку площадки оболочка не видит: её подставляют раньше. Находка
    # здесь была бы о синтаксисе шаблона, а не оболочки (051).
    ('echo "${{ github.sha }}"', "подстановка площадки"),
    ('out=$(gh api "repos/${{ github.repository }}/pulls" --jq ".[]")', "подстановка внутри вызова"),
])
def test_razbiraemaya_obolochka_nahodkoy_ne_yavlyaetsya(код, что):
    assert cw.unparsable_shell(прогон(код)) == [], что


@pytest.mark.parametrize("код, что", [
    ("if [ 1 -eq 1 ]; then echo да", "незакрытый if"),
    ("case $x in a) echo a;;", "незакрытый case"),
])
def test_nerazbiraemaya_obolochka_eto_nahodka(код, что):
    """Такой шаг падает МГНОВЕННО и выглядит обычным красным (167)."""
    assert len(cw.unparsable_shell(прогон(код))) == 1, что


def test_shag_ne_na_obolochke_ne_predmet():
    """`shell: python` — другой язык; отвергать его было бы находкой о форме."""
    assert cw.unparsable_shell(прогон("if True", оболочка="python")) == []


def действие(код: str, оболочка: str = "bash") -> str:
    """Составное действие: шаги лежат в `runs:`, а не в `jobs:`."""
    тело = "\n".join("          " + s for s in код.splitlines())
    return ("name: a\ndescription: d\nruns:\n  using: composite\n  steps:\n"
            f"    - name: проба\n      shell: {оболочка}\n      run: |\n{тело}\n")


def test_sostavnoe_deystvie_proveryaetsya_toy_zhe_merkoy():
    """Находка внешнего взгляда на #361: у `action.yml` нет `jobs:` вовсе.

    Цена здесь ВЫШЕ, чем у прогона: неразбираемый шаг составного действия
    красит прогоны чужих проектов, подключивших его, — без единой их строки
    в стеке. Ровно та граница, которую файл уже проводил для разбора кода
    возврата (145), и не провёл для разбираемости.
    """
    assert len(cw.unparsable_shell(действие("if [ 1 -eq 1 ]; then echo да"))) == 1
    assert cw.unparsable_shell(действие("echo ок")) == []


def test_defaults_urovnya_fayla_uvazhaetsya():
    """`defaults.run.shell` бывает и в шапке файла, не только у работы.

    Без этого прогон, объявивший себя pwsh в шапке, мерился бы `bash -n` —
    ложный красный о чужом языке, находка о форме вместо предмета (051).
    """
    текст = ("name: t\non: [push]\ndefaults:\n  run:\n    shell: pwsh\n"
             "jobs:\n  j:\n    steps:\n      - name: проба\n        run: |\n"
             "          if ($true) { Write-Host x }\n")
    assert cw.unparsable_shell(текст) == []
