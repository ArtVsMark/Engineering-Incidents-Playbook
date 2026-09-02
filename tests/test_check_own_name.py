"""Каталог знает своё имя: переименование не проходит молча.

Подделка — дерево с реестром и текстом; своё имя подставляется ключом
`--slug`, а не подменой git: спрашивать настоящий `origin` значило бы
проверять состояние машины, а не решение гейта (правило 150).

Здоровый предмет взят у границы: репозиторий ЧУЖОГО владельца с похожим
именем законен и находкой быть не должен.

НАСТОЯЩЕЕ СТАРОЕ ИМЯ КАТАЛОГА ЗДЕСЬ НЕ НАПИСАНО, и это не осторожность, а
предмет: набор лежит в том же дереве, которое гейт просматривает, и подделка
с живым старым именем сделала бы находку из самого набора. Первая редакция
именно так и краснела. Подставное имя проверяет то же самое — что слуга
владельца, не объявленный нигде, становится находкой.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import check_own_name as co
from conftest import write

МОЁ = "ArtVsMark/Engineering-Incidents-Playbook"
РЕЕСТР = {"schema": "1.0", "consumers": [
    {"repo": МОЁ}, {"repo": "ArtVsMark/Stepik-Python-Grader"}]}


def дерево(root: Path, text: str, реестр: dict | None = None) -> Path:
    write(root / ".rules" / "consumers.json",
          json.dumps(реестр if реестр is not None else РЕЕСТР, ensure_ascii=False))
    write(root / "README.md", text)
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True,
                   capture_output=True)
    return root


def run(root: Path, slug: str = МОЁ) -> int:
    return co.main(["--root", str(root), "--slug", slug])


# ── здоровые предметы ──────────────────────────────────────────────────────

def test_svoyo_imya_i_potrebiteli_prohodyat(repo, capsys):
    дерево(repo, f"# К\n\nсм. {МОЁ} и ArtVsMark/Stepik-Python-Grader\n")

    assert run(repo) == 0
    assert "знает своё имя" in capsys.readouterr().out


def test_chuzhoy_vladelets_s_pohozhim_imenem_zakonen(repo):
    """Предмет у границы: `chokmah-me/some-playbook` — другой проект."""
    дерево(repo, f"# К\n\n{МОЁ}, а ещё chokmah-me/some-playbook\n")

    assert run(repo) == 0


def test_tochka_v_konce_frazy_ne_delaet_novogo_repozitoriya(repo):
    """Замер на живом дереве: `ArtVsMark/ArtVsMark.` в конце предложения
    становился отдельным репозиторием, и гейт краснел на верном тексте."""
    дерево(repo, f"# К\n\nответ лежит в {МОЁ}.\n")

    assert run(repo) == 0


def test_ssylka_s_hvostom_eto_tot_zhe_repozitoriy(repo):
    дерево(repo, f"# К\n\nhttps://github.com/{МОЁ}.git и /{МОЁ}/blob/main/a.md\n")

    assert run(repo) == 0


# ── предметы, которые гейт обязан отвергнуть ───────────────────────────────

def test_staroe_imya_v_dereve_eto_nahodka(repo, capsys):
    """Ровно инцидент 2 сентября: переименование, 245 старых упоминаний."""
    дерево(repo, f"# К\n\n{МОЁ}, а вот тут ArtVsMark/name-it-no-longer-has\n")

    assert run(repo) == 1
    assert "name-it-no-longer-has" in capsys.readouterr().err


def test_reestr_otstal_ot_ploshchadki_eto_nahodka(repo, capsys):
    """Главный случай: площадка переименовала, реестр знает старое имя.

    Если бы своё имя бралось из реестра, оно совпало бы с собой и гейт
    промолчал бы ровно там, ради чего построен (146)."""
    дерево(repo, "# К\n\nтекст\n",
           реестр={"schema": "1.0",
                   "consumers": [{"repo": "ArtVsMark/name-it-no-longer-has"}]})

    assert run(repo) == 1
    assert "своего имени нет в реестре" in capsys.readouterr().err


# ── третий исход: проверка не отработала ──────────────────────────────────

def test_reestra_net_eto_tretiy_ishod(repo, capsys):
    write(repo / "README.md", "# К\n")
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                   capture_output=True)

    assert run(repo) == 2
    assert "не прочитан" in capsys.readouterr().err


def test_ne_klon_eto_tretiy_ishod(repo, capsys):
    """Без git список файлов пуст, а ноль просмотренных — отказ (075)."""
    write(repo / ".rules" / "consumers.json", json.dumps(РЕЕСТР))
    write(repo / "README.md", "# К\n")

    assert run(repo) == 2
    assert "ноль файлов" in capsys.readouterr().err


def test_bez_origin_imya_ne_vydumyvaetsya(repo, capsys):
    """Своё имя приходит СНАРУЖИ или не приходит вовсе: константой оно быть
    не должно (005), и молчаливого запасного пути здесь нет."""
    write(repo / ".rules" / "consumers.json", json.dumps(РЕЕСТР))
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"],
                   check=True, capture_output=True)

    assert co.main(["--root", str(repo)]) == 2
    assert "origin" in capsys.readouterr().err
