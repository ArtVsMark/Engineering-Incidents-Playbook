"""Сводка «где действует»: ответы потребителей, три исхода и согласованность.

Скрипт закрывает правила 049 и 075: таблица вычисляется из ответов, а не
ведётся руками, и объявленный потребитель, чей ответ не читается, роняет
сборку — иначе «не смогли прочитать» неотличимо от «у него всё хорошо».

Здесь же держится граница, которую легко потерять при правке: **отсутствие
связи и нечитаемый ответ — разные вещи**. Первое объявленное состояние и
проходит молча, второе находка. Тест на пару стоит рядом нарочно: они
отличаются одним полем реестра, и слить их в одну ветку можно случайно.

Сеть не трогается ни одним случаем: у всех потребителей ответ локальный. Это
не удобство теста, а то же требование, что и у `--check` в конвейере —
обязательная проверка не зависит от чужого сервера.
"""

from __future__ import annotations

import json
from pathlib import Path

import aggregate_bindings as ab
from conftest import write


def prepare(monkeypatch, repo: Path, consumers, rules=("001", "002")) -> None:
    registry = repo / ".rules" / "consumers.json"
    write(registry, json.dumps({"schema": "1.0", "consumers": consumers},
                               ensure_ascii=False))
    write(repo / "export" / "rules.json",
          json.dumps({"rules": [{"id": i} for i in rules]}))
    monkeypatch.setattr(ab, "ROOT", repo)
    monkeypatch.setattr(ab, "CONSUMERS", registry)
    monkeypatch.setattr(ab, "EXPORT_JSON", repo / "export" / "where.json")
    monkeypatch.setattr(ab, "EXPORT_MD", repo / "export" / "where.md")
    monkeypatch.setattr(ab, "RULES", repo / "export" / "rules.json")


def cli(monkeypatch, *argv: str) -> None:
    monkeypatch.setattr("sys.argv", ["aggregate_bindings.py", *argv])


def answer(repo: Path, where: str, **rules) -> str:
    """Кладёт ответ потребителя и возвращает путь ОТНОСИТЕЛЬНО корня."""
    write(repo / where,
          json.dumps({"rules": {k: {"status": v} for k, v in rules.items()}}))
    return where


# ── третий исход: сверять нечего ───────────────────────────────────────────

def test_нет_реестра_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, [])
    ab.CONSUMERS.unlink()
    cli(monkeypatch)
    assert ab.main() == 2
    assert "не отработала" in capsys.readouterr().err


def test_пустой_реестр_это_третий_исход(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, [])
    cli(monkeypatch)
    assert ab.main() == 2
    assert "не отработала" in capsys.readouterr().err


# ── состояния, которые находкой НЕ являются ────────────────────────────────

def test_потребитель_без_связи_это_состояние(monkeypatch, repo):
    slices, problems = ab.collect([{"repo": "owner/one"}])
    assert problems == []
    assert slices[0]["state"] == ab.NOT_CONNECTED
    assert slices[0]["why"]


def test_приватный_ответ_называется_неизвестным(monkeypatch, repo):
    slices, problems = ab.collect([{"repo": "owner/one", "access": "private"}])
    assert problems == []
    assert slices[0]["state"] == ab.UNKNOWN


# ── находка: объявленный потребитель, чей ответ не читается ────────────────

def test_нечитаемый_ответ_объявленного_потребителя_это_находка(
        monkeypatch, repo, capsys):
    prepare(monkeypatch, repo,
            [{"repo": "owner/one", "bindings": ".rules/нет-такого.json"}])
    cli(monkeypatch)
    assert ab.main() == 1
    assert "не читается" in capsys.readouterr().err


def test_живой_ответ_собирается_в_срез(monkeypatch, repo):
    prepare(monkeypatch, repo, [])
    monkeypatch.setattr(ab, "ROOT", repo)
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    slices, problems = ab.collect([{"repo": "owner/one", "bindings": src}])
    assert problems == []
    assert slices[0]["state"] == "подключён"
    assert slices[0]["rules"] == {"001": "active"}


# ── сверка собранного: --check ─────────────────────────────────────────────

def test_собранная_сводка_согласована(monkeypatch, repo):
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    cli(monkeypatch, "--check")
    assert ab.main() == 0


def test_реестр_ушёл_вперёд_сводки_это_находка(monkeypatch, repo, capsys):
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    # Потребитель приехал в реестр, сводку не пересобрали.
    write(ab.CONSUMERS, json.dumps(
        {"schema": "1.0", "consumers": [{"repo": "owner/one", "bindings": src},
                                        {"repo": "owner/two"}]},
        ensure_ascii=False))
    cli(monkeypatch, "--check")
    assert ab.main() == 1
    assert "owner/two" in capsys.readouterr().err


def test_несобранной_сводки_достаточно_для_находки(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, [{"repo": "owner/one"}])
    cli(monkeypatch, "--check")
    assert ab.main() == 1
    assert "Соберите" in capsys.readouterr().err


def test_ответ_потребителя_уехал_вперёд_сводки_это_находка(monkeypatch, repo, capsys):
    """Расхождение, которое до #122 ловил только НОЧНОЙ прогон с сетью.

    Изменение правит ответ и не пересобирает сводку; обязательная проверка
    убеждалась, что сводка согласована сама с собой, и зеленела. Сети для
    этого не нужно: местный ответ лежит на диске.
    """
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    answer(repo, ".rules/bindings.json", **{"001": "rejected"})
    cli(monkeypatch, "--check")
    assert ab.main() == 1
    err = capsys.readouterr().err
    assert "отстала от ответа" in err and "001 (active → rejected)" in err


def test_сводка_в_ногу_с_ответом_проходит(monkeypatch, repo):
    """Здоровый предмет у самой границы: ответ менялся, сводку пересобрали."""
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    answer(repo, ".rules/bindings.json", **{"001": "rejected"})
    cli(monkeypatch)
    assert ab.main() == 0
    cli(monkeypatch, "--check")
    assert ab.main() == 0


def test_местный_ответ_пропал_после_сборки_это_находка(monkeypatch, repo, capsys):
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [{"repo": "owner/one", "bindings": src}])
    cli(monkeypatch)
    assert ab.main() == 0
    (repo / src).unlink()
    cli(monkeypatch, "--check")
    assert ab.main() == 1
    assert "не читается" in capsys.readouterr().err


# ── производная таблица ────────────────────────────────────────────────────

def test_таблица_перечисляет_правила_поимённо(repo):
    slices = [{"repo": "owner/one", "state": "подключён", "answered": 1,
               "rules": {"001": "active"}}]
    text = ab.as_markdown(slices, ["001", "002"])
    assert "| 001 |" in text and "| 002 |" in text
    assert "не правится руками" in text


def test_без_подключённых_таблица_правил_объявлена_пустой(repo):
    slices = [{"repo": "owner/one", "state": ab.NOT_CONNECTED, "why": "нет"}]
    text = ab.as_markdown(slices, ["001"])
    assert "| 001 |" not in text
    assert "объявленное состояние" in text


def test_отставший_ответ_это_предупреждение_а_не_отказ():
    old = (__import__("datetime").date.today()
           - __import__("datetime").timedelta(days=ab.TTL_DAYS + 1)).isoformat()
    assert ab.stale([{"repo": "owner/one", "read_at": old}])
    assert ab.stale([{"repo": "owner/one", "read_at": "не дата"}]) == []


# ── объявленный и не подключившийся: срок делает адресата ─────────────────
#
# Замер, из которого это выросло: из шести объявленных потребителей пятеро не
# отдают ответа, шестеро не отдают предложений. Канал построен с обеих сторон
# и не пронёс НИ ОДНОГО предложения. «Не подключён» при этом печаталось
# спокойно как законное состояние — и потому не читалось никем, ровно как
# красное по расписанию без адресата (142).
#
# Срок делает адресата. Набор двусторонний: свежий и подключённый обязаны
# проходить, иначе состояние станет находкой на пустом месте.

def days_ago(n: int) -> str:
    import datetime as dt
    return (dt.date.today() - dt.timedelta(days=n)).isoformat()


def test_свежий_неподключённый_это_состояние():
    assert ab.unconnected([{"repo": "o/a", "since": days_ago(1)}]) == []


def test_просроченный_неподключённый_это_находка():
    out = ab.unconnected([{"repo": "o/a", "since": days_ago(ab.UNCONNECTED_DAYS + 1)}])
    assert out and "объявлен потребителем" in out[0]


def test_на_границе_срока_ещё_состояние():
    """Здоровый предмет у самой границы: ровно срок — ещё не находка."""
    assert ab.unconnected([{"repo": "o/a", "since": days_ago(ab.UNCONNECTED_DAYS)}]) == []


def test_подключённый_срока_не_знает():
    assert ab.unconnected([{"repo": "o/a", "since": days_ago(999),
                            "bindings": "x.json"}]) == []


def test_приватный_подключения_не_требует():
    """Его ответ недоступен по объявленной причине — требовать нечего."""
    assert ab.unconnected([{"repo": "o/a", "since": days_ago(999),
                            "access": "private"}]) == []


def test_без_начала_отсчёта_это_находка():
    """Срок без начала не считается, и молчать об этом нельзя (075)."""
    out = ab.unconnected([{"repo": "o/a"}])
    assert out and "since" in out[0]


def test_неразбираемая_дата_это_находка():
    out = ab.unconnected([{"repo": "o/a", "since": "вчера"}])
    assert out and "не разбирается" in out[0]


def test_отказ_живёт_в_сборке_а_не_в_проверке_изменения(monkeypatch, repo, capsys):
    """Разные предметы — разные исходы, и это главное в этой паре.

    Сборку запускает ночной прогон, и его отказ заводит задачу: у находки
    появляется адресат (142). Проверку `--check` запускает изменение, и там
    тот же список только печатается: автор изменения чужой репозиторий
    подключить не может, а красить его работу за это значит приучать к
    красному (051).
    """
    src = answer(repo, ".rules/bindings.json", **{"001": "active"})
    prepare(monkeypatch, repo, [
        {"repo": "owner/one", "bindings": src, "since": days_ago(1)},
        {"repo": "owner/two", "since": days_ago(ab.UNCONNECTED_DAYS + 1)},
    ])
    cli(monkeypatch)
    assert ab.main() == 1
    assert "owner/two" in capsys.readouterr().err
    cli(monkeypatch, "--check")
    assert ab.main() == 0
    assert "owner/two" in capsys.readouterr().out


def test_сводка_всё_равно_записана_при_находке(monkeypatch, repo):
    """Отказ не отменяет работу: сводка собрана, иначе чинить было бы нечем."""
    prepare(monkeypatch, repo, [{"repo": "owner/two",
                                 "since": days_ago(ab.UNCONNECTED_DAYS + 1)}])
    cli(monkeypatch)
    assert ab.main() == 1
    assert ab.EXPORT_MD.exists() and ab.EXPORT_JSON.exists()


# ── чем держится, а не только действует ли ────────────────────────────────
#
# Сводка отвечала «правило у проекта действует» и молчала о том, ЧЕМ. Замер по
# трём подключённым: семьдесят два правила объявлены действующими и не
# обеспечены ничем, а у сорока из них сосед уже построил механизм и назвал его
# адрес. Ответ существовал и был недоступен, пока не откроешь три файла в трёх
# репозиториях.

def held(repo: Path, where: str, **rules) -> str:
    """Ответ потребителя с механизмом: значение — (статус, механизм, адрес)."""
    write(repo / where, json.dumps({"rules": {
        k: {"status": v[0], "mechanism": v[1], "where": v[2]}
        for k, v in rules.items()}}, ensure_ascii=False))
    return where


def test_таблица_потребителей_называет_чем_держится(monkeypatch, repo):
    prepare(monkeypatch, repo, [{
        "repo": "o/a", "bindings": held(repo, ".rules/a.json",
                                        **{"001": ("active", "gate", "s/g.py"),
                                           "002": ("active", "none", "")})}])
    cli(monkeypatch)

    ab.main()
    md = (repo / "export" / "where.md").read_text(encoding="utf-8")
    строка = next(l for l in md.splitlines() if l.startswith("| `a`"))

    assert "| 1 | 0 | 1 |" in строка


def test_отсутствие_механизма_и_none_это_одно_состояние(monkeypatch, repo):
    """`mechanism` не задан и `mechanism: none` — оба «не держится ничем»."""
    write(repo / ".rules/a.json", json.dumps({"rules": {
        "001": {"status": "active"},
        "002": {"status": "active", "mechanism": "none"}}}))
    prepare(monkeypatch, repo, [{"repo": "o/a", "bindings": ".rules/a.json"}])
    cli(monkeypatch)

    ab.main()
    срез = json.loads((repo / "export" / "where.json").read_text(encoding="utf-8"))

    assert срез["consumers"][0]["by_mechanism"] == {"none": 2}


def test_чужой_механизм_виден_там_где_у_соседа_ничем(monkeypatch, repo):
    prepare(monkeypatch, repo, [
        {"repo": "o/a", "bindings": held(repo, ".rules/a.json",
                                         **{"001": ("active", "gate", "s/g.py")})},
        {"repo": "o/b", "bindings": held(repo, ".rules/b.json",
                                         **{"001": ("active", "none", "")})}])
    cli(monkeypatch)

    ab.main()
    md = (repo / "export" / "where.md").read_text(encoding="utf-8")

    assert "## Чем держат другие" in md
    assert "s/g.py" in md
    строка = next(l for l in md.splitlines() if l.startswith("| 001 |"))
    assert "`a` — гейт: s/g.py" in строка and "`b`" in строка


def test_правило_без_механизма_ни_у_кого_в_раздел_не_идёт(monkeypatch, repo):
    """Учиться не у кого — строки быть не должно, иначе раздел станет шумом."""
    prepare(monkeypatch, repo, [
        {"repo": "o/a", "bindings": held(repo, ".rules/a.json",
                                         **{"001": ("active", "none", "")})},
        {"repo": "o/b", "bindings": held(repo, ".rules/b.json",
                                         **{"001": ("active", "none", "")})}])
    cli(monkeypatch)

    ab.main()
    md = (repo / "export" / "where.md").read_text(encoding="utf-8")

    assert "Правил, которые у одного держатся механизмом" in md


def test_сколько_правил_держит_механизм_считается(monkeypatch, repo):
    prepare(monkeypatch, repo, [{
        "repo": "o/a", "bindings": held(repo, ".rules/a.json",
                                        **{"001": ("active", "gate", "s/g.py"),
                                           "002": ("active", "gate", "s/g.py")})},
    ], rules=("001", "002"))
    cli(monkeypatch)

    ab.main()
    md = (repo / "export" / "where.md").read_text(encoding="utf-8")

    assert "## Сколько держит механизм" in md
    assert "| `a` | `s/g.py` | 2 |" in md


def test_держащий_без_названного_адреса_назван_числом(monkeypatch, repo):
    """Доля без остатка выглядела бы как полнота — сколько таких, печатается."""
    prepare(monkeypatch, repo, [{
        "repo": "o/a", "bindings": held(repo, ".rules/a.json",
                                        **{"001": ("active", "gate", "чтением при приёмке")})}])
    cli(monkeypatch)

    ab.main()
    md = (repo / "export" / "where.md").read_text(encoding="utf-8")

    assert "без названного адреса: 1 из 1" in md


def test_смена_механизма_без_пересборки_это_находка(monkeypatch, repo, capsys):
    """Статус тот же, механизм другой — сводка обязана это заметить (146)."""
    путь = held(repo, ".rules/a.json", **{"001": ("active", "gate", "s/g.py")})
    prepare(monkeypatch, repo, [{"repo": "o/a", "bindings": путь}])
    cli(monkeypatch)
    ab.main()

    write(repo / путь, json.dumps({"rules": {
        "001": {"status": "active", "mechanism": "none", "where": ""}}}))
    cli(monkeypatch, "--check")
    код = ab.main()

    assert код == 1
    assert "ЧЕМ держит" in capsys.readouterr().err


# ── отчёт: у кого что и как ───────────────────────────────────────────────
#
# «Ответов N» пряталo сразу три разных числа: сколько правил осталось без
# ответа, сколько ответов относится к удалённым записям и сколько правил
# признано действующими. Замер поймал оба края: у грейдера тринадцать без
# ответа, у витрины один ЛИШНИЙ — ответ за правило, которого в экспорте нет.

def test_следы_считаются_по_экспорту(repo):
    counts = ab.trail_counts([
        {"id": "001", "trails": [{"repo": "o/a"}, {"repo": "o/b"}]},
        {"id": "002", "trails": [{"repo": "o/a"}]},
        {"id": "003"},
    ])

    assert counts == {"o/a": 2, "o/b": 1}


def test_след_есть_а_потребитель_не_подключён(monkeypatch, repo):
    """Следы считаются и у неподключённого: иначе его вклад не виден вовсе."""
    write(repo / "export" / "rules.json", json.dumps(
        {"rules": [{"id": "001", "trails": [{"repo": "o/тихий"}]}]}))
    prepare(monkeypatch, repo, [{"repo": "o/тихий", "bindings": None}],
            rules=("001",))
    write(repo / "export" / "rules.json", json.dumps(
        {"rules": [{"id": "001", "trails": [{"repo": "o/тихий"}]}]}))
    cli(monkeypatch)

    ab.main()
    строка = next(l for l in (repo / "export" / "where.md")
                  .read_text(encoding="utf-8").splitlines()
                  if l.startswith("| `тихий`"))

    assert "| не подключён | 1 |" in строка


def test_без_ответа_и_лишний_ответ_разные_числа(monkeypatch, repo):
    """Оба края видны: правило без ответа и ответ за несуществующее правило."""
    write(repo / ".rules/a.json", json.dumps({"rules": {
        "001": {"status": "active", "mechanism": "gate", "where": "s/g.py"},
        "999": {"status": "active", "mechanism": "gate", "where": "s/g.py"}}}))
    prepare(monkeypatch, repo, [{"repo": "o/a", "bindings": ".rules/a.json"}],
            rules=("001", "002"))
    cli(monkeypatch)

    ab.main()
    строка = next(l for l in (repo / "export" / "where.md")
                  .read_text(encoding="utf-8").splitlines()
                  if l.startswith("| `a`"))
    _, _, _, следы, ответов, без_ответа, лишних, действует, *_ = строка.split("|")

    assert без_ответа.strip() == "1" and лишних.strip() == "1"
    assert ответов.strip() == "2" and действует.strip() == "2"


def test_механизмы_считаются_различными_адресами(monkeypatch, repo):
    """Два правила на одном файле — один механизм, а не два."""
    prepare(monkeypatch, repo, [{
        "repo": "o/a", "bindings": held(repo, ".rules/a.json",
                                        **{"001": ("active", "gate", "s/g.py"),
                                           "002": ("active", "gate", "s/g.py")})}])
    cli(monkeypatch)

    ab.main()
    строка = next(l for l in (repo / "export" / "where.md")
                  .read_text(encoding="utf-8").splitlines()
                  if l.startswith("| `a`"))

    assert строка.split("|")[11].strip() == "1"


# ── сколько правил и сколько разобрано: у находки есть адресат ────────────
#
# У СЕБЯ каталог ответ о несуществующем правиле отвергает — check_bindings,
# «ответ есть, а правила такого в каталоге нет». У потребителей тот же вопрос
# не задавался вовсе. Замер: у витрины лежит ответ о правиле 143, удалённом
# как дубль, и лежал он там с самого удаления, невидимый.

def test_ответ_о_несуществующем_правиле_это_находка():
    срез = [{"repo": "o/a", "rules": {"001": "active", "143": "active"}}]

    находки = ab.stale_answers(срез, ["001", "002"])

    assert len(находки) == 1 and "143" in находки[0]


def test_правило_без_ответа_находкой_не_считается():
    """Очередь — не поломка: нерассмотренное решится, лишний ответ — нет."""
    срез = [{"repo": "o/a", "rules": {"001": "active"}}]

    assert ab.stale_answers(срез, ["001", "002"]) == []


def test_неподключённый_в_находки_не_попадает():
    """У него нет ответа вовсе — упрекать не в чем."""
    assert ab.stale_answers([{"repo": "o/a", "state": "не подключён"}], ["001"]) == []


def test_на_изменении_лишний_ответ_это_предупреждение_а_не_отказ(
        monkeypatch, repo, capsys):
    """Чужой файл отсюда не чинится — красить за него чужую работу нельзя."""
    путь = answer(repo, ".rules/a.json", **{"001": "active", "143": "active"})
    prepare(monkeypatch, repo, [{"repo": "o/a", "bindings": путь}],
            rules=("001", "002"))
    cli(monkeypatch)
    ab.main()

    cli(monkeypatch, "--check")
    код = ab.main()

    assert код == 0
    assert "которых в каталоге нет — 143" in capsys.readouterr().out


def test_перепись_печатается_и_на_зелёном(monkeypatch, repo, capsys):
    """Число, видное только при поломке, не отвечает «куда мы движемся»."""
    путь = answer(repo, ".rules/a.json", **{"001": "active", "002": "unreviewed"})
    prepare(monkeypatch, repo, [{"repo": "o/a", "bindings": путь}],
            rules=("001", "002", "003"))
    cli(monkeypatch)

    код = ab.main()
    вывод = capsys.readouterr().out

    assert код == 0
    assert "правил в каталоге: 3" in вывод
    assert "разобрано 1 из 3 · не рассмотрено 1 · без ответа 1 · лишних 0" in вывод


def test_перепись_называет_неподключённого_состоянием(monkeypatch, repo, capsys):
    prepare(monkeypatch, repo, [{"repo": "o/тихий", "bindings": None}],
            rules=("001",))
    cli(monkeypatch)

    ab.main()

    assert "o/тихий: не подключён" in capsys.readouterr().out


# ── чинит не тот, кто нашёл ───────────────────────────────────────────────
#
# Первый же прогон с проверкой лишнего ответа покрасил общую ветку из-за
# записи 143 в ответе витрины. По 053 красное на общей ветке останавливает
# всю остальную работу — то есть каталог встал из-за строки в ЧУЖОМ файле,
# и снять это красное он не мог ничем, кроме исключения потребителя из
# реестра. Находки делятся по тому, чьей правкой снимаются.

def test_чужая_находка_прогон_не_роняет(monkeypatch, repo, capsys):
    """Лишний ответ правится у потребителя — отсюда недостижимо."""
    путь = answer(repo, ".rules/a.json", **{"001": "active", "143": "active"})
    prepare(monkeypatch, repo, [{"repo": "o/a", "bindings": путь}],
            rules=("001", "002"))
    cli(monkeypatch)

    код = ab.main()

    assert код == 0


def test_чужая_находка_названа_вслух(monkeypatch, repo, capsys):
    """Не краснеть — не значит молчать: иначе это было бы 075."""
    путь = answer(repo, ".rules/a.json", **{"001": "active", "143": "active"})
    prepare(monkeypatch, repo, [{"repo": "o/a", "bindings": путь}],
            rules=("001", "002"))
    cli(monkeypatch)

    ab.main()
    вывод = capsys.readouterr().out

    assert "находки в чужих репозиториях" in вывод
    assert "143" in вывод


def test_своя_находка_прогон_роняет(monkeypatch, repo, capsys):
    """Нечитаемый ответ по объявленному адресу правится ЗДЕСЬ — в реестре."""
    prepare(monkeypatch, repo, [{"repo": "o/a", "bindings": ".rules/нет.json"}],
            rules=("001",))
    cli(monkeypatch)

    код = ab.main()

    assert код == 1
    assert "чей ответ не читается" in capsys.readouterr().err


def test_обе_находки_разом_роняет_только_своя(monkeypatch, repo, capsys):
    """Своя и чужая рядом: код берётся у своей, чужая всё равно названа."""
    путь = answer(repo, ".rules/a.json", **{"001": "active", "143": "active"})
    prepare(monkeypatch, repo, [
        {"repo": "o/a", "bindings": путь},
        {"repo": "o/b", "bindings": ".rules/нет.json"}], rules=("001", "002"))
    cli(monkeypatch)

    код = ab.main()
    поток = capsys.readouterr()

    assert код == 1
    assert "находки в чужих репозиториях" in поток.out
    assert "o/b" in поток.err
