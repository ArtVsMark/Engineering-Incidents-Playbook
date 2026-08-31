"""Фрагменты журнала: разбор, находки и порядок сборки.

Проверяется то, ради чего скрипт написан (правило 030): фрагмент с неверным
именем, пустой фрагмент и фрагмент с ведущим «-» — находки, а не мелочи. Пустой
особенно: файл, в котором ничего не написано, выглядит сделанной работой.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import collect_changelog as cc
from conftest import write


def prepare(monkeypatch, repo: Path, files: dict[str, str]) -> None:
    fragments = repo / "changelog.d"
    fragments.mkdir()
    for name, text in files.items():
        write(fragments / name, text)
    monkeypatch.setattr(cc, "FRAGMENTS", fragments)


def test_читает_годный_фрагмент(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.added.md": "Гейт покрытия (#1).\n"})
    found, problems = cc.validate()
    assert problems == []
    assert found["added"] == ["Гейт покрытия (#1)."]


def test_readme_фрагментом_не_считается(monkeypatch, repo):
    prepare(monkeypatch, repo, {"README.md": "как класть фрагменты"})
    found, problems = cc.validate()
    assert problems == []
    assert all(not lines for lines in found.values())


def test_имя_не_по_форме_это_находка(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.wontfix.md": "текст"})
    _, problems = cc.validate()
    assert len(problems) == 1
    # Отказ обязан называть предмет, а не только факт (правило 083).
    assert "gate.wontfix.md" in problems[0]
    assert "added" in problems[0]


def test_пустой_фрагмент_это_находка(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.added.md": "   \n"})
    found, problems = cc.validate()
    assert len(problems) == 1
    assert "gate.added.md" in problems[0]
    assert found["added"] == []


def test_ведущий_дефис_это_находка(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.added.md": "- уже со списком"})
    _, problems = cc.validate()
    assert len(problems) == 1
    assert "gate.added.md" in problems[0]


def test_перенос_строк_схлопывается(monkeypatch, repo):
    prepare(monkeypatch, repo, {"gate.fixed.md": "длинная\nстрока   в   две"})
    found, _ = cc.validate()
    assert found["fixed"] == ["длинная строка в две"]


def test_секции_идут_объявленным_порядком(monkeypatch, repo):
    prepare(monkeypatch, repo, {
        "z.internal.md": "внутреннее",
        "a.fixed.md": "починка",
        "m.added.md": "новое",
    })
    found, problems = cc.validate()
    assert problems == []
    out = cc.render(found)
    assert out.index("Добавлено") < out.index("Починено") < out.index("Внутреннее")
    assert "- новое" in out


def test_записи_внутри_секции_отсортированы(monkeypatch, repo):
    prepare(monkeypatch, repo, {"b.added.md": "яблоко", "a.added.md": "апельсин"})
    found, _ = cc.validate()
    lines = [s for s in cc.render(found).splitlines() if s.startswith("- ")]
    assert lines == ["- апельсин", "- яблоко"]


def test_пустая_сборка_это_пустая_строка(monkeypatch, repo):
    prepare(monkeypatch, repo, {})
    found, _ = cc.validate()
    assert cc.render(found) == ""


# ─── командные режимы ───────────────────────────────────────────────────────
# Разбор фрагментов проверен выше; здесь — что скрипт делает с разобранным:
# три исхода (039), сборка в [Unreleased] и удаление собранных фрагментов (030).

def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True)


def выпуск(repo: Path, *теги: str) -> None:
    """Подделка — НАСТОЯЩИЙ репозиторий с настоящими тегами.

    Проверка «у каждого выпуска свой раздел» ходит в git, и подмена её входа
    проверяла бы разбор заголовков, а не гейт (правило 150).
    """
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "Владелец")
    git(repo, "config", "user.email", "owner@example.com")
    write(repo / "f.txt", "подделка")
    git(repo, "add", "-A")
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "подделка")
    for тег in теги:
        git(repo, "tag", тег)


def cli(monkeypatch, repo: Path, files: dict[str, str], changelog: str | None,
        *argv: str, теги: tuple[str, ...] = ("0.1.0",)) -> None:
    prepare(monkeypatch, repo, files)
    monkeypatch.setattr(cc, "ROOT", repo)
    path = repo / "CHANGELOG.md"
    if changelog is not None:
        write(path, changelog)
    monkeypatch.setattr(cc, "CHANGELOG", path)
    monkeypatch.setattr("sys.argv", ["collect_changelog.py", *argv])
    выпуск(repo, *теги)


HEADER = "# Журнал\n\n## [Unreleased]\n\n## [0.1.0]\n\n- старое\n"


def test_проверка_чистых_фрагментов(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое"}, HEADER, "--check")
    assert cc.main() == 0
    assert "в порядке" in capsys.readouterr().out


def test_находка_красит_проверку(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": ""}, HEADER, "--check")
    assert cc.main() == 1
    assert "не в порядке" in capsys.readouterr().err


def test_нет_каталога_фрагментов_это_третий_исход(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {}, HEADER, "--check")
    monkeypatch.setattr(cc, "FRAGMENTS", repo / "нет-такого")
    assert cc.main() == 2
    assert "не отработала" in capsys.readouterr().err


def test_нет_журнала_это_третий_исход(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое"}, None, "--check")
    assert cc.main() == 2
    assert "собирать некуда" in capsys.readouterr().err


def test_показ_сборки_ничего_не_меняет(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое"}, HEADER, "--preview")
    assert cc.main() == 0
    assert "- новое" in capsys.readouterr().out
    assert (repo / "changelog.d" / "a.added.md").exists()


def test_сборка_кладёт_записи_и_убирает_фрагменты(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое", "b.fixed.md": "починка"},
        HEADER, "--collect")
    assert cc.main() == 0
    text = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "- новое" in text and "- починка" in text
    # Старый раздел не затёрт: сборка вставляет, а не переписывает.
    assert "- старое" in text
    assert not list((repo / "changelog.d").glob("*.md"))
    assert "собрано записей: 2" in capsys.readouterr().out


def test_сборка_без_раздела_это_третий_исход(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {"a.added.md": "новое"}, "# Журнал без раздела\n",
        "--collect")
    assert cc.main() == 2
    assert "нет раздела" in capsys.readouterr().err
    # Фрагмент уцелел: не собрали — значит не удалили.
    assert (repo / "changelog.d" / "a.added.md").exists()


def test_сборка_пустого_не_трогает_журнал(monkeypatch, repo, capsys):
    cli(monkeypatch, repo, {}, HEADER, "--collect")
    assert cc.main() == 0
    assert (repo / "CHANGELOG.md").read_text(encoding="utf-8") == HEADER


# ── вердикт починки: момент, которого не было ──────────────────────────────
#
# Фильтр «тянет ли это на правило» есть и работает машинно, но срабатывает для
# того, кто УЖЕ решил писать. Здесь стоит момент, в который решают: фрагмент
# пишут ровно тогда, когда починка сделана и инцидент ещё цел (правило 138).
#
# Набор двусторонний, и здоровые предметы взяты у границы: секции, кроме
# `fixed`, вердикта не требуют — иначе вопрос задавался бы там, где починки
# не было.

def frag(repo: Path, name: str, text: str) -> Path:
    return write(repo / "changelog.d" / name, text)


def test_починка_без_вердикта_это_находка(repo):
    out = cc.verdict_problems([frag(repo, "a.fixed.md", "Починили.\n")])
    assert out and "не ответила" in out[0]


def test_отказ_с_причиной_проходит(repo):
    assert cc.verdict_problems([frag(
        repo, "a.fixed.md",
        "Починили.\n\n> правилом не становится, потому что это местная настройка.\n")]) == []


def test_отказ_без_причины_это_находка(repo):
    out = cc.verdict_problems([frag(repo, "a.fixed.md", "Починили.\n\n> не правило.\n")])
    assert out and "не разбирается" in out[0]


def test_ссылка_на_правило_проходит(repo):
    assert cc.verdict_problems([frag(
        repo, "a.fixed.md", "Починили.\n\n> правило 145 — тот же класс.\n")]) == []


def test_ссылка_путём_в_дерево_тоже_проходит(repo):
    assert cc.verdict_problems([frag(
        repo, "a.fixed.md",
        "Починили.\n\n> см. rules/ru/145-every-declared-outcome-is-run.md\n")]) == []


def test_у_остальных_секций_вердикта_не_спрашивают(repo):
    """Здоровый предмет у границы: вопрос адресован починке, а не всякой работе."""
    assert cc.verdict_problems([
        frag(repo, "a.added.md", "Завели.\n"),
        frag(repo, "b.changed.md", "Поменяли.\n"),
        frag(repo, "c.internal.md", "Внутреннее.\n"),
    ]) == []


def test_имя_не_по_форме_вердиктом_не_проверяется(repo):
    """Форму имени судит validate(); дважды об одном не сообщают."""
    assert cc.verdict_problems([frag(repo, "a.md", "Что-то.\n")]) == []


def test_вердикт_в_журнал_не_едет(repo):
    body, verdict = cc.split_verdict(
        "Починили гонку.\n\n> правило 148 — тот же класс.\n")
    assert body == "Починили гонку."
    assert "148" in verdict


def test_фрагмент_из_одного_вердикта_считается_пустым(monkeypatch, repo):
    """Вердикт — не запись журнала: строка «>» одна оставляет тело пустым."""
    prepare(monkeypatch, repo, {"a.fixed.md": "> правило 148 — связано.\n"})
    _, problems = cc.validate()
    assert problems and "пуст" in problems[0]


# ── сборка в уже собранный раздел ──────────────────────────────────────────
#
# Сборка вставляла свежий блок сразу после заголовка `[Unreleased]`, а прежнее
# содержимое оставляла ниже. Пока раздел собирали ровно один раз перед
# выпуском, это работало. Замер на подготовке 1.1.0: собрали, слили ещё три
# изменения, собрали снова — и в теле выпуска встали ДВА «Добавлено» и ДВА
# «Изменено». Разделить их обратно нечем: порядок внутри уже перемешан.

СОБРАННЫЙ = ("# Журнал\n\n## [Unreleased]\n\n### Добавлено · Added\n\n"
             "- первое\n\n## [0.1.0]\n\n- старое\n")


def test_повторная_сборка_не_задваивает_заголовки(monkeypatch, repo):
    cli(monkeypatch, repo, {"second.added.md": "второе\n"}, СОБРАННЫЙ, "--collect")

    assert cc.main() == 0
    свежий = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    unreleased = свежий.split("## [0.1.0]")[0]
    assert unreleased.count("### Добавлено · Added") == 1


def test_повторная_сборка_сохраняет_прежние_записи(monkeypatch, repo):
    cli(monkeypatch, repo, {"second.added.md": "второе\n"}, СОБРАННЫЙ, "--collect")

    assert cc.main() == 0
    свежий = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "- первое" in свежий and "- второе" in свежий


def test_повторная_сборка_не_трогает_прежние_выпуски(monkeypatch, repo):
    cli(monkeypatch, repo, {"second.added.md": "второе\n"}, СОБРАННЫЙ, "--collect")

    assert cc.main() == 0
    свежий = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [0.1.0]" in свежий and "- старое" in свежий


def test_новая_секция_встаёт_рядом_а_не_вместо(monkeypatch, repo):
    cli(monkeypatch, repo,
        {"mended.fixed.md": "починка\n\n> правило 030 — сюда и относится\n"},
        СОБРАННЫЙ, "--collect")

    assert cc.main() == 0
    unreleased = (repo / "CHANGELOG.md").read_text(
        encoding="utf-8").split("## [0.1.0]")[0]
    assert "### Добавлено · Added" in unreleased
    assert "### Починено · Fixed" in unreleased
    assert "- первое" in unreleased and "- починка" in unreleased


def test_разбор_читает_только_свой_раздел():
    """Записи следующего выпуска не должны втянуться в [Unreleased]."""
    было = cc.existing(СОБРАННЫЙ)

    assert было["added"] == ["первое"]
    assert "старое" not in sum(было.values(), [])


# ── у каждого выпуска свой раздел ──────────────────────────────────────────
#
# v1.1.0 вышел 28 августа, а раздела [1.1.0] в журнале не появилось: 42 записи
# выпуска остались в [Unreleased], где их читают как ещё не вышедшие. Нашлось
# это через два выпуска и не проверкой, а взглядом человека.

ВЫШЕДШИЙ = ("# Журнал\n\n## [Unreleased]\n\n### Добавлено · Added\n\n"
            "- свежее\n\n## [0.1.0] — 2026-08-21\n\n- старое\n")


def test_teg_bez_razdela_eto_nahodka(monkeypatch, repo, capsys):
    """Ровно инцидент: тег есть, раздела нет, записи лежат в [Unreleased]."""
    cli(monkeypatch, repo, {}, ВЫШЕДШИЙ, "--check", теги=("0.1.0", "v1.1.0"))

    assert cc.main() == 1
    assert "1.1.0" in capsys.readouterr().err


def test_u_kazhdogo_tega_est_razdel_eto_chisto(monkeypatch, repo):
    cli(monkeypatch, repo, {}, ВЫШЕДШИЙ, "--check")

    assert cc.main() == 0


def test_zakrytie_zavodit_razdel_i_pustoy_unreleased(monkeypatch, repo):
    cli(monkeypatch, repo, {}, ВЫШЕДШИЙ, "--close", "v1.1.0", "--date",
        "2026-08-28", теги=("0.1.0", "v1.1.0"))

    assert cc.main() == 0
    свежий = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    # Записи переехали под номер выпуска ДОСЛОВНО, а [Unreleased] заведён снова.
    assert "## [1.1.0] — 2026-08-28" in свежий and "- свежее" in свежий
    assert свежий.index("## [Unreleased]") < свежий.index("## [1.1.0]")
    новый = свежий.split("## [Unreleased]")[1].split("## [")[0]
    assert "- " not in новый and новый.strip()


def test_posle_zakrytiya_proverka_chista(monkeypatch, repo):
    """Пара «закрыть» и «сверить» обязана сходиться: иначе выпуск оставлял бы
    после себя красное на общей ветке."""
    cli(monkeypatch, repo, {}, ВЫШЕДШИЙ, "--close", "v1.1.0",
        теги=("0.1.0", "v1.1.0"))
    assert cc.main() == 0

    monkeypatch.setattr("sys.argv", ["collect_changelog.py", "--check"])
    assert cc.main() == 0


def test_zakrytie_pustogo_razdela_eto_otkaz(monkeypatch, repo, capsys):
    """Выпуск без записей читается как «ничего не изменилось» — хуже, чем
    отсутствие выпуска (075)."""
    cli(monkeypatch, repo, {}, HEADER, "--close", "v1.1.0",
        теги=("0.1.0", "v1.1.0"))

    assert cc.main() == 1
    assert "пуст" in capsys.readouterr().err


def test_vtoroy_raz_odin_vypusk_ne_zakryvaetsya(monkeypatch, repo, capsys):
    """Номера не переиспользуются: второй раздел с тем же номером — не выпуск,
    а потерянная половина записей."""
    cli(monkeypatch, repo, {}, ВЫШЕДШИЙ, "--close", "0.1.0")

    assert cc.main() == 1
    assert "уже есть" in capsys.readouterr().err


def test_bez_tegov_eto_tretiy_ishod(monkeypatch, repo, capsys):
    """Мелкий клон тегов не приносит: зелёное здесь означало бы «выпусков не
    было», а это ровно то молчание, из-за которого 1.1.0 и потерялся (039)."""
    cli(monkeypatch, repo, {}, ВЫШЕДШИЙ, "--check")
    subprocess.run(["git", "-C", str(repo), "tag", "-d", "0.1.0"],
                   check=True, capture_output=True)

    assert cc.main() == 2
    assert "не отработала" in capsys.readouterr().err
