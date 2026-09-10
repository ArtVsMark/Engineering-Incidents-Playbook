"""Строка связи изменения с задачей: сборка, проверка и три исхода.

Скрипт закрывает вторую половину правила 064 — ту, которую до сих пор не
держало ничто. Тесты бьют в то, ради чего он есть: **упоминание задачи связью
не является**. Случай «задача названа только в заголовке» стоит здесь первым,
потому что именно он двенадцать раз подряд выглядел исправным.

Освобождение проверяется с двух сторон нарочно (правило 097): заполненное
проходит, пустое — нет. Смешать их значило бы разрешить пропуск, спрятанный за
формой отказа.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import pr_body as pb
from conftest import write

TRAILERS = "Co-Authored-By: Claude <noreply@anthropic.com>"


def check(monkeypatch, repo, body: str) -> int:
    path = write(repo / "body.md", body)
    return pb.main(["--check", "--body-file", str(path)])


# ── разбор: что считается связью ───────────────────────────────────────────

@pytest.mark.parametrize("line", [
    "Closes #83", "closes #83", "CLOSES #83",
    "Fixes #83", "fixed #83", "Resolves #83", "resolve #83",
    "- Closes #83", "> Closes #83",
    "Closes https://github.com/owner/repo/issues/83",
])
def test_закрывающие_слова_площадки_считаются_связью(line):
    assert pb.linked(f"Текст.\n\n{line}\n") == "83"


@pytest.mark.parametrize("body", [
    "См. задачу #83.\n",
    "Правило 145 (#83)\n",
    "Это closes-подобное, но не строка: закрывает #83\n",
])
def test_упоминание_связью_не_является(body):
    assert pb.linked(body) is None


def test_освобождение_требует_причины():
    assert pb.exempt("Без задачи, потому что метрика назвала работу сама.\n")
    assert not pb.exempt("Без задачи.\n")
    assert not pb.exempt("Без задачи, потому что\n")


# ── сборка ─────────────────────────────────────────────────────────────────

def test_задача_из_хвоста_заголовка_становится_связью():
    out, problem = pb.build("Правило 145: что-то (#83)", f"Тело.\n\n{TRAILERS}\n")
    assert problem is None
    assert "Closes #83" in out


def test_строка_связи_встаёт_перед_блоком_трейлеров():
    out, _ = pb.build("X (#83)", f"Тело.\n\n{TRAILERS}\n")
    assert out.index("Closes #83") < out.index("Co-Authored-By")


def test_готовую_связь_сборка_не_трогает():
    body = f"Тело.\n\nCloses #7\n\n{TRAILERS}\n"
    out, problem = pb.build("Заголовок (#83)", body)
    assert (out, problem) == (body, None)
    assert "#83" not in out


def test_освобождённое_тело_сборка_не_трогает():
    body = "Тело.\n\nБез задачи, потому что работу назвала метрика.\n"
    assert pb.build("Заголовок без номера", body) == (body, None)


def test_без_задачи_и_без_освобождения_сборка_называет_чего_нет():
    out, problem = pb.build("Заголовок без номера", "Тело.\n")
    assert out == "Тело.\n"
    assert problem and "заголовка" in problem


# ── три исхода у --check ───────────────────────────────────────────────────

def test_связь_есть_это_чисто(monkeypatch, repo, capsys):
    assert check(monkeypatch, repo, f"Тело.\n\nCloses #83\n\n{TRAILERS}\n") == 0
    assert "#83" in capsys.readouterr().out


def test_освобождение_заполнено_это_чисто(monkeypatch, repo, capsys):
    assert check(monkeypatch, repo,
                 "Тело.\n\nБез задачи, потому что так решили.\n") == 0


def test_только_упоминание_это_находка(monkeypatch, repo, capsys):
    assert check(monkeypatch, repo, "Правило 145 (#83)\n\nСм. #83.\n") == 1
    assert "упоминание" in capsys.readouterr().err


def test_пустое_тело_это_третий_исход(monkeypatch, repo, capsys):
    assert check(monkeypatch, repo, "   \n\n") == 2
    assert "не отработала" in capsys.readouterr().err


def test_нет_файла_это_третий_исход(repo, capsys):
    assert pb.main(["--check", "--body-file", str(repo / "нет-такого")]) == 2
    assert "не отработала" in capsys.readouterr().err


def test_тело_не_передано_это_третий_исход(capsys):
    assert pb.main(["--check"]) == 2


# ── третий ответ: сделана часть (173) ──────────────────────────────────────

def test_chast_s_ostatkom_prohodit(tmp_path):
    """«Часть» — такой же полноправный ответ, как закрытие: без него автор
    вынужден соврать в одну из сторон."""
    f = tmp_path / "b.md"
    f.write_text("Правка витрины.\n\nPart of #186\n\nОстаётся: два ответа.\n",
                 encoding="utf-8")
    assert pb.main(["--check", "--body-file", str(f)]) == 0


def test_chast_bez_ostatka_otvergaetsya(tmp_path):
    """Гейт проверяется тем, что обязан отвергнуть (140): «часть» без остатка
    неотличима от полного закрытия."""
    f = tmp_path / "b.md"
    f.write_text("Правка витрины.\n\nPart of #186\n", encoding="utf-8")
    assert pb.main(["--check", "--body-file", str(f)]) == 1


def test_pustoy_ostatok_ostatkom_ne_schitaetsya():
    """«Остаётся:» с пустотой — это пустота с двоеточием."""
    assert not pb.names_rest("Part of #1\n\nОстаётся:\n")


def test_sborka_ne_zakryvaet_chastichnoe(tmp_path):
    """ГРАНИЦА: дописать `Closes` поверх «части» значило бы закрыть задачу,
    сделанную наполовину."""
    out, problem = pb.build("Правка (#186)", "Тело.\n\nPart of #186\n")
    assert problem is None
    assert "Closes" not in out



# ── снятие заметки внешнего взгляда: форма проверяется машинно ─────────────

def test_snyatie_slovami_otvergaetsya(tmp_path, capsys):
    """ГЛАВНЫЙ СЛУЧАЙ, и он про подделку, неотличимую при чтении (140).

    Инцидент 10 сентября: в теле #475 стояло `Разобрано: 202-boundary`. Для
    человека тело выглядело разобранным, для механизма находок не совпадало ни
    с чем — и ни один гейт об этом не сказал.
    """
    f = tmp_path / "b.md"
    f.write_text("Починка.\n\nРазобрано: 202-boundary\n\nCloses #1\n",
                 encoding="utf-8")
    assert pb.main(["--check", "--body-file", str(f)]) == 1
    assert "ничего не снимет" in capsys.readouterr().err


def test_otpechatok_prohodit(tmp_path):
    """Зелёная сторона: семь шестнадцатеричных знаков и хвост при них."""
    f = tmp_path / "b.md"
    f.write_text("Починка.\n\nРазобрано: 8f60732 · #479 — заголовок находки\n"
                 "\nCloses #1\n", encoding="utf-8")
    assert pb.main(["--check", "--body-file", str(f)]) == 0


def test_dlina_otpechatka_nesushchaya():
    """Шесть знаков и восемь — не отпечаток: гейт принимает РОВНО то, что
    примет уборщик, иначе он пропустит строку, которая ничего не снимет."""
    assert pb.dead_marks("Разобрано: fdfddd\n")        # шесть
    assert pb.dead_marks("Разобрано: fdfddd6a\n")      # восемь
    assert not pb.dead_marks("Разобрано: fdfddd6\n")   # семь


def test_telo_bez_snyatiy_ne_zadeto():
    """ГРАНИЦА: предмет проверки — только строки снятия. Тело без них
    проходит, и красное на нём было бы ложным отказом (051)."""
    assert pb.dead_marks("Обычное тело.\n\nCloses #1\n") == []


def test_forma_odna_u_geyta_i_u_uborshchika():
    """022 замером: выражение у уборщика — то же самое, а не похожее.

    Разойдясь, они молчали бы в разные стороны: гейт пропустил бы строку,
    которую уборщик не примет, — ровно инцидент 10 сентября.
    """
    import review_findings as rf
    assert rf.РАЗОБРАНО is pb.РАЗОБРАНО


def test_obyavlenie_kodov_nazyvaet_vse_istochniki():
    """039/183 ЧИСЛОМ, а не глазом: объявление обязано назвать все отказы.

    Инцидент #488: правка, чинившая неполноту объявления, назвала ДВА источника
    кода 1 из трёх — пропущенным оказался «часть объявлена, остаток не назван»
    (173). Дефект того же класса, что и чинимый, и глаз его пропустил дважды:
    у автора и на первом ревью. Поэтому счёт теперь сверяется машиной.
    """
    исходник = Path(pb.__file__).read_text(encoding="utf-8")
    отказов = len(re.findall(r"^\s*return 1\s*$", исходник, re.M))
    докстрока = pb.__doc__ or ""
    объявлено = len(re.findall(r"^\s*\d+\.\s+\S", докстрока, re.M))
    assert отказов == объявлено, (
        f"отказов с кодом 1 в коде {отказов}, названо в докстроке {объявлено}")
