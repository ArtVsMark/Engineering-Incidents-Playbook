"""Производное с чужим владельцем: гейт проверяется тем, что обязан отвергнуть.

Набор двусторонний (правило 140). Из одних «обязан отвергнуть» не виден ложный
отказ, а он здесь дороже пропуска: сводка законно едет вместе с правкой своего
сборщика, и красное на этом заставило бы обходить гейт руками.

Площадка и git не трогаются: `findings` — чистая функция над списком путей.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import check_derived as cd

СБОРЩИК = "scripts/aggregate_bindings.py"


def test_svodka_v_izmenenii_nahodka():
    """Ровно тот случай, что дал три конфликта за смену."""
    assert cd.findings(["rules/ru/001-x.md", "export/where.md"], "agent/тема") == \
        ["export/where.md"]


def test_oba_fayla_svodki_nazyvayutsya():
    got = cd.findings(["export/where.json", "export/where.md"], "agent/тема")
    assert got == ["export/where.json", "export/where.md"]


def test_izmenenie_bez_svodki_chisto():
    assert cd.findings(["rules/ru/001-x.md", "export/rules.json"], "agent/тема") == []


def test_pravka_sborshchika_svodku_bolshe_ne_osvobozhdaet():
    """ИСКЛЮЧЕНИЙ НЕТ, И ЭТО ЗАМЕР. Пока сводка лежала в дереве, правка
    сборщика законно везла её с собой. Файла в дереве больше нет — и правка
    сборщика перестала быть поводом его вернуть."""
    assert cd.findings([СБОРЩИК, "export/where.md"], "agent/тема") == ["export/where.md"]


def test_vetka_peresborki_bolshe_ne_osvobozhdena():
    """Ветки пересборки не стало вместе с изменениями, которые она открывала:
    публикует сводку тот же прогон, что публикует картинку."""
    assert cd.findings(["export/where.md"], "agent/consumers-refresh") == ["export/where.md"]


def test_svodka_v_dereve_nahodka_dazhe_bez_izmeneniya():
    """Второй предмет: `.gitignore` при слиянии не спрашивают, и файл
    возвращается молча — без единого пути в разнице."""
    assert cd.findings([], "agent/тема", {"export/where.json"}) == ["export/where.json"]


def test_chuzhoe_v_export_pod_ohranu_ne_popadaet():
    """Обратная сторона (140): под охраной названные два файла, а не папка."""
    assert cd.findings([], "agent/тема", {"export/rules.json", "export/README.md"}) == []


def test_ukazatel_pod_ohranoy_ne_stoit():
    """Указатель и выгрузка правил принадлежат ИЗМЕНЕНИЮ: гейт свежести
    требует их вместе с правилом, и запрещать их значило бы запереть работу."""
    assert cd.findings(["rules/README.md", "export/rules.json"], "agent/тема") == []


def test_tretiy_ishod_na_nerazobrannom_diapazone(tmp_path):
    """Исход «проверка не отработала» объявлен и прогоняется (145): диапазона
    нет — это код 2, а не чистый прогон (075)."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    done = subprocess.run(
        [sys.executable, str(Path(cd.__file__)), "--root", str(tmp_path),
         "--range", "нет-такого...HEAD"],
        capture_output=True, text=True, encoding="utf-8")
    assert done.returncode == 2
    assert "не отработала" in done.stderr


def test_gejt_otvechaet_otkazom_cherez_main(tmp_path):
    """Случай спрашивает РЕШЕНИЕ гейта, а не повторяет его условие (150).
    Подделка — настоящее дерево с настоящим диапазоном, где сводка едет в
    изменении: `main` обязан ответить единицей."""
    def git(*args):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True,
                       capture_output=True)

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    git("config", "user.email", "проба@пример")
    git("config", "user.name", "проба")
    (tmp_path / "README.md").write_text("основание\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "основание")
    (tmp_path / "export").mkdir()
    (tmp_path / "export" / "where.md").write_text("сводка\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "сводка поехала в изменении")

    общие = ["--root", str(tmp_path), "--range", "HEAD~1...HEAD", "--branch"]
    assert cd.main([*общие, "agent/тема"]) == 1
    # И на прежде освобождённой ветке тоже: исключений не осталось, потому что
    # не осталось законного повода держать файл в дереве.
    assert cd.main([*общие, "agent/consumers-refresh"]) == 1

    # ОБРАТНАЯ СТОРОНА НА ТОМ ЖЕ ДЕРЕВЕ (140): файл убран — гейт молчит.
    git("rm", "-q", "export/where.md")
    git("commit", "-qm", "сводка ушла на ветку badges")
    assert cd.main(["--root", str(tmp_path), "--range", "HEAD~1...HEAD",
                    "--branch", "agent/тема"]) == 0
