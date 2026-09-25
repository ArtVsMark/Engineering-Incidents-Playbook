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
    """ГРАНИЦА ИЗ САМОГО ПРАВИЛА: у `off-prefix` предмет — состояние ветки, а не
    коммит, и сообщение одинаково для любой головы. Разрешение объявлено
    списком с причиной, а не выведено из формы файла."""
    workflow(tmp_path, "off-prefix.yml", BUTTON
             + "concurrency:\n  group: off-prefix-${{ github.ref }}\n"
               "  cancel-in-progress: true\n"
             + РАБОТА)
    assert cw.main(["--root", str(tmp_path)]) == 0


def test_badges_bolshe_ne_v_spiske_razresheniy(tmp_path):
    """Обратная сторона списка (140): `badges` из него УШЁЛ, потому что больше
    не отменяет, а ставит в очередь. Разрешение, пережившее свой предмет,
    читалось бы как действующее — и им объяснили бы возврат отмены."""
    workflow(tmp_path, "badges.yml", BUTTON
             + "concurrency:\n  group: badges\n  cancel-in-progress: true\n"
             + РАБОТА)
    assert cw.main(["--root", str(tmp_path)]) == 1


# ── запись о списке не переживает сам список ───────────────────────────────
#
# ИНЦИДЕНТ, А НЕ ПРЕДОСТОРОЖНОСТЬ. Правка, снявшая `badges.yml` из
# `CANCELS_BY_STATE`, оставила в `.rules/bindings.json` запись правила 179,
# которая этот файл в списке НАЗЫВАЛА. Гейт записей остался зелёным: сверка
# адреса видит, что `.github/workflows/badges.yml` существует на диске, а не
# то, значится ли он строкой в словаре. Поймал внешний взгляд, а не прогон —
# ровно та форма, о которой 183: утверждение о механизме стареет молча и
# читается как исполненное решение.


def прогоны_в_записи(текст: str) -> set[str]:
    """Имена прогонов, названные в тексте записи. Ищется ПУТЬ, а не голое имя:
    голое `badges` стоит в записях и как имя ветки, и как имя группы."""
    import re
    return {p.rsplit("/", 1)[1]
            for p in re.findall(r"\.github/workflows/[\w.-]+\.yml", текст)}


def запись_179() -> str:
    import json
    from pathlib import Path
    реестр = json.loads(
        (Path(cw.ROOT) / ".rules" / "bindings.json").read_text(encoding="utf-8"))
    return реестр["rules"]["179"]["where"]


def test_zapis_o_spiske_sovpadaet_so_spiskom():
    """Живой предмет: что запись 179 называет разрешённым, то и разрешено."""
    assert прогоны_в_записи(запись_179()) == set(cw.CANCELS_BY_STATE)


#: Текст записи 179 ДОСЛОВНО из коммита 3e05f4a — `git show 3e05f4a:.rules/
#: bindings.json`. Пересказ здесь был бы тем же дефектом, что и чинится: первая
#: редакция случая пропустила «с причиной у каждой строки», и внешний взгляд
#: это назвал. Случай о дословности обязан быть дословным сам.
БЫЛО_В_ЗАПИСИ = (
    "Разрешение объявлено списком CANCELS_BY_STATE с причиной у каждой строки: "
    "у .github/workflows/badges.yml и .github/workflows/off-prefix.yml предмет "
    "— состояние, а не коммит")


def test_zapis_o_spiske_lovit_rashozhdenie():
    """Обратная сторона (140): сверка обязана РАЗОЙТИСЬ на том самом тексте,
    что стоял в записи до починки, — иначе она не держит ничего."""
    assert прогоны_в_записи(БЫЛО_В_ЗАПИСИ) == {"badges.yml", "off-prefix.yml"}
    assert прогоны_в_записи(БЫЛО_В_ЗАПИСИ) != set(cw.CANCELS_BY_STATE)


def test_dosloznost_byla_svyorena_s_istoriey():
    """И сама дословность сверена с историей, а не объявлена.

    Без этого случая строка выше — просто ещё один пересказ, только с более
    уверенной подписью. Прогон без истории (мелкий клон) случай не выполняет и
    НЕ зеленеет молча: он говорит, чего ему не хватило.
    """
    import json
    import subprocess
    из_истории = subprocess.run(
        ["git", "show", "3e05f4a:.rules/bindings.json"],
        cwd=cw.ROOT, capture_output=True, text=True, encoding="utf-8")
    if из_истории.returncode != 0:
        import pytest
        pytest.skip("истории нет: мелкий клон — сверять дословность не с чем")

    было = json.loads(из_истории.stdout)["rules"]["179"]["where"]

    assert БЫЛО_В_ЗАПИСИ in было, "цитата разошлась с тем, что стояло в записи"


#: ВТОРОЙ ЖИВОЙ АДРЕС ТОГО ЖЕ УТВЕРЖДЕНИЯ. Запись в реестре — не единственное
#: место, где сказано, кому позволено отменять по состоянию: то же самое стоит
#: прозой в самом правиле, в разделе «Не работает». Первая редакция починки
#: держала только реестр и назвала это границей; внешний взгляд показал, что
#: граница проведена не там — у утверждения два адреса, а не один.
РАЗДЕЛ = {"ru": "**Не работает**", "en": "**Does not work**"}


def пример_в_тексте(текст: str, язык: str) -> set[str]:
    """Кого раздел «Не работает» называет своим примером. Берётся ОДИН абзац:
    соседние говорят о другом, и их имена примером не являются."""
    import re
    абзацы = текст.split("\n\n")
    (нужный,) = [a for a in абзацы if a.lstrip().startswith(РАЗДЕЛ[язык])]
    return set(re.findall(r"`([a-z][\w-]*)`", нужный))


def правило_179(язык: str, ревизия: str | None = None) -> str | None:
    """Текст правила — из дерева либо из истории. `None`, если истории нет."""
    from pathlib import Path
    (файл,) = (Path(cw.ROOT) / "rules" / язык).glob("179-*.md")
    if ревизия is None:
        return файл.read_text(encoding="utf-8")
    import subprocess
    путь = файл.relative_to(cw.ROOT).as_posix()
    из_истории = subprocess.run(["git", "show", f"{ревизия}:{путь}"],
                                cwd=cw.ROOT, capture_output=True, text=True,
                                encoding="utf-8")
    return из_истории.stdout if из_истории.returncode == 0 else None


def позволено_отменять() -> set[str]:
    return {k.removesuffix(".yml") for k in cw.CANCELS_BY_STATE}


#: ВТОРОЙ ПУНКТ ТОГО ЖЕ ПРАВИЛА, И ЭТО ТРЕТИЙ РАЗ ЗА СМЕНУ. Первая починка
#: держала реестр, вторая — абзац «Не работает», а перечень в «Практических
#: границах» состарился отдельно от обоих: он называл двоих, когда `false`
#: стояло у троих, и после #525 — у четверых. Граница «один абзац» и была тем,
#: что позволяло соседнему абзацу стареть молча.
ПУНКТ = "`cancel-in-progress: false`"


def имена_в_пункте(текст: str) -> set[str]:
    """Имена прогонов в ОДНОМ пункте списка — том, что говорит про очередь.

    Пункт, а не весь список: соседние пункты говорят о другом, и их имена
    утверждением о составе не являются.
    """
    import re
    строки = текст.splitlines()
    (начало,) = [n for n, с in enumerate(строки)
                 if с.startswith("- ") and ПУНКТ in с]
    конец = начало + 1
    while конец < len(строки) and not строки[конец].startswith("- "):
        конец += 1
    пункт = "\n".join(строки[начало:конец])
    return set(re.findall(r"`([a-z][\w-]*)`", пункт))


def не_отменяют() -> set[str]:
    """Кто в дереве объявил очередь вместо отмены — по разбору, а не по списку."""
    from pathlib import Path
    из = set()
    for файл in (Path(cw.ROOT) / ".github" / "workflows").glob("*.yml"):
        группы = cw.cancelling_groups(файл.read_text(encoding="utf-8"))
        if группы and not any(отменяет for _, отменяет in группы):
            из.add(файл.stem)
    return из


def test_perechen_ocheredey_sovpadaet_s_derevom():
    """Кого правило называет очередью, тот очередь и есть — в обоих деревьях."""
    for язык in ("ru", "en"):
        assert имена_в_пункте(правило_179(язык)) == не_отменяют(), \
            f"{язык}: перечень очередей разошёлся с деревом"


def test_perechen_ocheredey_lovit_ustarevshiy():
    """Обратная сторона (140): на перечне ИЗ ИСТОРИИ сверка обязана разойтись —
    там их двое, а в дереве четверо."""
    for язык in ("ru", "en"):
        было = правило_179(язык, "3e05f4a")
        if было is None:
            import pytest
            pytest.skip("истории нет: мелкий клон — сверять не с чем")

        assert имена_в_пункте(было) == {"automerge", "thaw"}
        assert имена_в_пункте(было) != не_отменяют()


def test_primer_v_pravile_sovpadaet_so_spiskom():
    """Оба дерева называют примером ровно тех, кому это и разрешено."""
    for язык in ("ru", "en"):
        assert пример_в_тексте(правило_179(язык), язык) == позволено_отменять(), \
            f"{язык}: пример в правиле разошёлся со списком"


def test_primer_v_pravile_lovit_ustarevshiy():
    """Обратная сторона (140): на ТОМ САМОМ абзаце, что стоял до починки,
    сверка обязана разойтись — иначе она не держит ничего.

    Абзац берётся из истории, а не переписывается сюда: пересказ был бы тем же
    дефектом, что и чинится.
    """
    for язык in ("ru", "en"):
        было = правило_179(язык, "3e05f4a")
        if было is None:
            import pytest
            pytest.skip("истории нет: мелкий клон — сверять не с чем")

        assert пример_в_тексте(было, язык) == {"badges"}
        assert пример_в_тексте(было, язык) != позволено_отменять()


def test_zhivoy_badges_stoit_v_ocheredi_a_ne_otmenyaet():
    """ЖИВОЙ ПРЕДМЕТ, а не выдумка: отменявшая группа убивала толчковый прогон
    отправленным, и общая ветка краснела после КАЖДОГО слияния — 8dcaaff (#519),
    366b038 (#521), 3a70d9e (#522), по одному `cancelled` из семи прогонов.
    Значки при этом были свежи: убивали ровно тот проход, что потом повторяли
    целиком. Случай держит саму починку в дереве, а не рассказ о ней."""
    from pathlib import Path
    текст = (Path(cw.ROOT) / ".github" / "workflows" / "badges.yml").read_text(
        encoding="utf-8")

    assert cw.cancelling_groups(текст) == [("badges", False)]


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


# ── ЛОЖНЫЙ ОТКАЗ НА ПРОЗЕ, ЗАМЕР 8 сентября ───────────────────────────────
#
# Строка «ВЕРДИКТ: находок N» в промпте ревьюера — предписанная форма ответа
# для модели — была принята за имя ключа env и отвергнута как «не латиницей».
# Гейт краснел на верном файле, а ложный отказ дороже пропуска (051).

def test_kirillica_v_promte_ne_nahodka():
    """РОВНО ПРЕДМЕТ: двоеточие в прозе — не ключ разметки."""
    прогон = (
        "jobs:\n  review:\n    steps:\n      - uses: some/action@v1\n"
        "        with:\n          prompt: |\n"
        "            Последней строкой поставь ровно это:\n\n"
        "                ВЕРДИКТ: находок N\n\n"
        "            По ней твою работу читает механизм.\n")

    assert cw.non_ascii_names(прогон) == []


def test_kirillica_v_run_ostayotsya_nahodkoy():
    """Граница с другой стороны: в `run:` лежит КОД, и там присваивание
    кириллицей падает кодом 127 — предмет правила 167 никуда не делся."""
    прогон = ("jobs:\n  x:\n    steps:\n      - name: шаг\n        run: |\n"
              "          ИМЯ=значение\n          echo \"$ИМЯ\"\n")

    assert cw.non_ascii_names(прогон) == ["ИМЯ"]


def test_klyuch_env_kirillicey_ostayotsya_nahodkoy():
    """И вторая половина границы: настоящий ключ разметки по-прежнему ловится."""
    прогон = ("jobs:\n  x:\n    steps:\n      - name: шаг\n        env:\n"
              "          КЛЮЧ: значение\n        run: echo ок\n")

    assert "КЛЮЧ" in cw.non_ascii_names(прогон)


def test_posle_bloka_razmetka_chitaetsya_snova():
    """Блок кончается по отступу: ключи ПОСЛЕ него обязаны проверяться."""
    прогон = ("jobs:\n  x:\n    steps:\n      - uses: a/b@v1\n"
              "        with:\n          prompt: |\n            проза: с двоеточием\n"
              "      - name: следующий\n        env:\n          ЗНАЧЕНИЕ: 1\n"
              "        run: echo ок\n")

    assert "ЗНАЧЕНИЕ" in cw.non_ascii_names(прогон)


# ── разрешённый агенту прогон исполним (032) ───────────────────────────────
#
# Замер 25.09: ревьюеру был разрешён `python -m pytest`, а в работе не было ни
# интерпретатора, ни проверок, и `python3` отклонялся. Набор двусторонний
# (140): каждая из трёх форм невозможного разрешения — находка, исполнимое
# разрешение и прогон без агента — нет.

def агент(разрешено: str, *, python: bool = True, проверки: bool = True) -> str:
    """Прогон с агентом: разрешения и, по выбору, шаги, делающие их исполнимыми."""
    шаги = "    steps:\n      - uses: actions/checkout@v4\n"
    if python:
        шаги += "      - uses: actions/setup-python@v5\n        with:\n          python-version: \"3.12\"\n"
    if проверки:
        шаги += "      - name: обвязка\n        run: python -m pip install --quiet -r requirements-test.txt\n"
    шаги += ("      - uses: anthropics/claude-code-action@v1\n        with:\n"
             "          claude_args: >-\n            --allowedTools\n"
             f"            \"{разрешено}\"\n")
    return "jobs:\n  review:\n    timeout-minutes: 20\n" + шаги


ОБА = "Bash(python -m pytest:*),Bash(python3 -m pytest:*),Bash(git diff:*)"


def test_ispolnimoe_razreshenie_ne_nahodka():
    assert cw.impossible_permissions(агент(ОБА)) == []


def test_bez_agenta_nahodok_net():
    """Прогон, где разрешений агенту нет вовсе, — не предмет."""
    assert cw.impossible_permissions("jobs:\n  a:\n    steps:\n      - run: echo\n") == []


def test_razreshenie_bez_pitona_ne_kasaetsya_ustanovok():
    """Агенту разрешён только git — ставить интерпретатор незачем."""
    assert cw.impossible_permissions(
        агент("Bash(git diff:*),Bash(git log:*)", python=False, проверки=False)) == []


def test_net_ustanovki_interpretatora_nahodka():
    находки = cw.impossible_permissions(агент(ОБА, python=False))
    assert any("setup-python" in н for н in находки)


def test_pytest_bez_proverok_nahodka():
    находки = cw.impossible_permissions(агент(ОБА, проверки=False))
    assert any("requirements-test" in н for н in находки)


def test_proverki_v_kommentarii_ne_schitayutsya():
    """Установка, упомянутая комментарием, проверок не ставит."""
    прогон = агент(ОБА, проверки=False).replace(
        "    steps:\n", "    # python -m pip install -r requirements-test.txt\n    steps:\n")
    assert any("requirements-test" in н for н in cw.impossible_permissions(прогон))


@pytest.mark.parametrize("разрешено, нет", [
    ("Bash(python -m pytest:*)", "python3 -m pytest"),
    ("Bash(python3 scripts/preflight.py:*)", "python scripts/preflight.py"),
])
def test_odno_imya_interpretatora_nahodka(разрешено, нет):
    """Живой случай 25.09: разрешено одно имя, агент зовёт другое."""
    находки = cw.impossible_permissions(агент(разрешено))
    assert any(f"«{нет}» — нет" in н for н in находки)


def test_zhivoy_fayl_prohodit_i_otkat_krasneet(tmp_path):
    """Живой review.yml проходит; он же без установки интерпретатора — отказ."""
    живой = (Path(__file__).resolve().parent.parent / ".github" / "workflows"
             / "review.yml").read_text(encoding="utf-8")
    assert cw.impossible_permissions(живой) == []
    откат = живой.replace("uses: actions/setup-python@", "uses: actions/other@")
    workflow(tmp_path, "review.yml", откат)
    assert cw.main(["--root", str(tmp_path)]) == 1


# ── код составного действия — из его пути (095) ────────────────────────────
#
# Замер 25.09: оба действия каталога выкачивали каталог ещё раз по входу с
# умолчанием main и исполняли скрипт оттуда — тег в строке uses: закреплял
# только разметку. Набор двусторонний (140).

ДЕЙСТВИЕ = ("runs:\n  using: composite\n  steps:\n    - name: шаг\n      shell: bash\n"
            "      run: |\n        {строка}\n")


@pytest.mark.parametrize("строка", [
    "python .rules-sync/scripts/sync_inbox.py --ref main",
    'python3 ".attribution-gate/scripts/check_attribution.py" "${args[@]}"',
])
def test_kod_iz_vykachannogo_kataloga_nahodka(строка):
    assert cw.code_not_from_action_path(ДЕЙСТВИЕ.format(строка=строка))


@pytest.mark.parametrize("строка", [
    'python "$GITHUB_ACTION_PATH/scripts/sync_inbox.py" --ref main',
    'python "$GITHUB_ACTION_PATH/../../../scripts/check_attribution.py" "${args[@]}"',
    'python "${{ github.action_path }}/scripts/x.py"',
    "echo без питона",
])
def test_kod_iz_svoego_puti_ne_nahodka(строка):
    assert cw.code_not_from_action_path(ДЕЙСТВИЕ.format(строка=строка)) == []


def test_upominanie_v_opisanii_ne_nahodka():
    """Проза описания входа — не шаг оболочки."""
    действие = ("inputs:\n  ref:\n    description: >-\n"
                "      python legacy/x.py больше не зовётся\n"
                + ДЕЙСТВИЕ.format(строка="echo ok"))
    assert cw.code_not_from_action_path(действие) == []


def test_zhivye_deystviya_prohodyat_i_otkat_krasneet(tmp_path):
    """Оба живых действия проходят; прежняя форма — отказ всего гейта."""
    корень = Path(__file__).resolve().parent.parent
    for путь in ("action.yml", ".github/actions/attribution/action.yml"):
        assert cw.code_not_from_action_path((корень / путь).read_text(encoding="utf-8")) == []
    workflow(tmp_path, "w.yml", "on:\n  workflow_dispatch:\njobs:\n  a:\n    timeout-minutes: 5\n")
    (tmp_path / "action.yml").write_text(
        ДЕЙСТВИЕ.format(строка="python .rules-sync/scripts/sync_inbox.py"), encoding="utf-8")
    assert cw.main(["--root", str(tmp_path)]) == 1
