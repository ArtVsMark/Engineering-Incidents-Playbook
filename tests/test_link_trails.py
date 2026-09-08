"""Обратная сторона следа: свои задачи против чужих, идемпотентность, три исхода.

Скрипт пишет в ЧУЖОЙ трекер, и цена ошибок здесь несимметрична. Пропущенный
след — задача без обратной ссылки, то есть ровно то состояние, которое было до
механизма. Ложный след — комментарий «из этой задачи выросло правило» в чужом
месте, и читатель его уже не проверит: инцидент лежит в другом репозитории.
Поэтому набор двусторонний, а случай «след ведёт в чужой проект» стоит рядом со
«следом сюда» — они отличаются одним полем.

Источник подделки (правило 170): формы ответов сняты с
`gh issue view N --repo OWNER/REPO --json comments` и с выгрузки правил по
`https://raw.githubusercontent.com/<каталог>/<ref>/export/rules.json`. Сверка
требует сети и остаётся человеку.

Идемпотентность проверяется не чтением кода, а вторым прогоном: комментарий
находится по скрытому маркеру, и второй заход обязан НИЧЕГО не писать. Сравнение
по тексту здесь не годится — текст растёт вместе с числом правил.

Сеть не трогается ни одним случаем: разбор — чистая функция над экспортом, а
`gh` подменяется.
"""

from __future__ import annotations

import link_trails as lt

ME = "ArtVsMark/ArtVsMark"


def rule(rid: str, repo: str = ME, issue: str = "7", slug: str = "slug") -> dict:
    return {"id": rid, "slug": slug, "title": {"ru": f"правило {rid}"},
            "trails": [{"repo": repo, "issue": issue}]}


def ids(found: dict) -> dict:
    return {i: [str(r["id"]) for r in rr] for i, rr in found.items()}


def test_svoy_sled_naiden():
    assert ids(lt.trails_for([rule("005")], ME)) == {"7": ["005"]}


def test_chuzhoy_sled_ne_beryotsya():
    """Отличается от предыдущего одним полем — и цена ошибки здесь выше."""
    assert lt.trails_for([rule("005", repo="ArtVsMark/Other")], ME) == {}


def test_odna_zadacha_neskolko_pravil():
    assert ids(lt.trails_for([rule("009"), rule("005")], ME)) == {"7": ["005", "009"]}


def test_poryadok_pravil_zadan():
    """Порядок задан, иначе комментарий меняется от прогона к прогону на одном
    и том же состоянии, и обновление выглядит событием."""
    got = ids(lt.trails_for([rule("132"), rule("005"), rule("009")], ME))
    assert got["7"] == ["005", "009", "132"]


def test_odno_pravilo_neskolko_zadach():
    r = {"id": "132", "slug": "s", "title": {"ru": "t"},
         "trails": [{"repo": ME, "issue": "20"}, {"repo": ME, "issue": "19"}]}
    assert ids(lt.trails_for([r], ME)) == {"19": ["132"], "20": ["132"]}


def test_sled_bez_nomera_i_ne_chislo():
    assert lt.trails_for([rule("005", issue="")], ME) == {}
    assert lt.trails_for([rule("005", issue="abc")], ME) == {}


def test_sledov_net_vovse():
    assert lt.trails_for([{"id": "001", "slug": "s", "title": {"ru": "t"}}], ME) == {}


def test_kommentariy_neset_marker_i_ssylku():
    body = lt.comment_for([rule("005")], "ArtVsMark/Engineering-Incidents-Playbook")
    assert lt.MARKER in body
    assert "rules/ru/005-slug.md" in body
    assert "правило 005" in body


def test_zagolovok_dvuyazychnyy_beryot_russkiy():
    r = {"id": "1", "slug": "s", "title": {"ru": "по-русски", "en": "in english"}}
    assert lt.title_of(r) == "по-русски"


def test_zapis_odna_i_vtoroy_progon_molchit(monkeypatch, capsys):
    """Идемпотентность — вторым прогоном, а не чтением кода."""
    written: list[str] = []
    state = {"exists": 0}

    # ЧТЕНИЕ ОТ ЗАПИСИ ОТЛИЧАЕТСЯ ПОЛЕМ, А НЕ ПОДКОМАНДОЙ. После перевода на
    # REST (001) оба вызова — `gh api`, и различает их наличие `-f body=`:
    # GET по тому же адресу читает, POST с телом пишет. Подделка, глядящая на
    # первое слово, считала бы чтение записью — и «сухой прогон» зеленел бы,
    # ничего не проверив (146).
    def fake(*args):
        пишет = any(a.startswith("body=") for a in args)
        if not пишет:
            return 0, str(state["exists"])
        written.append(args[-1]); state["exists"] = 1
        return 0, "ok"

    monkeypatch.setattr(lt.ghcli, "run", fake)
    monkeypatch.setattr(lt, "fetch_rules", lambda c, r: ([rule("005")], None))
    monkeypatch.setattr("sys.argv", ["link_trails.py", "--repo", ME, "--apply"])
    # БЫЛО 1, И ИМЕННО ЭТО ОКАЗАЛОСЬ ДЕФЕКТОМ. Случай закреплял поведение
    # «нашёл и дописал — отвечаю как находкой»: `missing` считался до записи и
    # после неё не очищался. Читающий не мог отличить удачную запись от
    # неустранённой находки, и прогон по расписанию у потребителя красил
    # успешную работу (109). Остаток после записи пуст — значит ноль.
    assert lt.main() == 0                      # дописал всё, до чего дошёл
    assert written == [written[0]]             # ровно одна запись
    monkeypatch.setattr("sys.argv", ["link_trails.py", "--repo", ME, "--apply"])
    assert lt.main() == 0                      # второй прогон: ставить нечего
    assert len(written) == 1                   # и он ничего не дописал


def test_suhoy_progon_ne_pishet(monkeypatch, capsys):
    """Умолчание сухое: скрипт пишет в чужой трекер."""
    written: list[str] = []

    def fake(*args):
        if not any(a.startswith("body=") for a in args):
            return 0, "0"                      # чтение — не запись
        written.append(args[1])
        return 0, ""

    monkeypatch.setattr(lt.ghcli, "run", fake)
    monkeypatch.setattr(lt, "fetch_rules", lambda c, r: ([rule("005")], None))
    monkeypatch.setattr("sys.argv", ["link_trails.py", "--repo", ME])
    assert lt.main() == 1
    assert written == []
    assert "--apply не задан" in capsys.readouterr().out


def test_kod_ne_menyaet_smysla_mezhdu_rezhimami(monkeypatch, capsys):
    """ГРАНИЦА МЕЖДУ ДВУМЯ СЛУЧАЯМИ ВЫШЕ, И ОНА ЖЕ ПРЕДМЕТ ПОЧИНКИ. Один вход,
    два режима: сухой отвечает «есть находки», записывающий — «чисто». Пока
    код был общим, читающему приходилось знать режим, чтобы понять ответ, —
    а прогон по расписанию его не знал и красил удачную запись."""
    def fake(*args):
        return (0, "ok") if any(a.startswith("body=") for a in args) else (0, "0")

    monkeypatch.setattr(lt.ghcli, "run", fake)
    monkeypatch.setattr(lt, "fetch_rules", lambda c, r: ([rule("005")], None))

    monkeypatch.setattr("sys.argv", ["link_trails.py", "--repo", ME])
    сухой = lt.main()
    monkeypatch.setattr("sys.argv", ["link_trails.py", "--repo", ME, "--apply"])
    пишущий = lt.main()

    assert (сухой, пишущий) == (1, 0), "один вход, разные ответы — по режиму"


def test_eksport_ne_prochitan_eto_tretiy_ishod(monkeypatch, capsys):
    """Три исхода, а не два: «не отработал» отличается кодом 2 от находки."""
    monkeypatch.setattr(lt, "fetch_rules", lambda c, r: (None, "404"))
    monkeypatch.setattr("sys.argv", ["link_trails.py", "--repo", ME])
    assert lt.main() == 2
    assert "не отработал" in capsys.readouterr().err


def test_trekery_nedostupen_eto_tozhe_tretiy_ishod(monkeypatch, capsys):
    """Отказ трекера — не «обратные ссылки на месте». Молчаливый ноль здесь
    означал бы, что механизм не работает и рапортует успех (075)."""
    monkeypatch.setattr(lt.ghcli, "run", lambda *a: (lt.ghcli.NO_GH, "нет gh"))
    monkeypatch.setattr(lt, "fetch_rules", lambda c, r: ([rule("005")], None))
    monkeypatch.setattr("sys.argv", ["link_trails.py", "--repo", ME])
    assert lt.main() == 2
    assert "не прочитана" in capsys.readouterr().err


def test_repo_ne_zadan(monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setattr("sys.argv", ["link_trails.py"])
    assert lt.main() == 2
    assert "не задан --repo" in capsys.readouterr().err
