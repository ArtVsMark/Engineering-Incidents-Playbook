"""Карта направлений: роль без своего возражения ролью не является.

Подделка — таблица, а не файл свода: гейт спрашивается через `main()` на
подставленном корне (правило 150), и здоровый предмет взят у самой границы —
две роли с РАЗНЫМИ возражениями к одному адресату законны, а с одинаковыми нет.
"""

from __future__ import annotations

from pathlib import Path

import check_roles as cr
from conftest import write

ШАПКА = ("| Направление | Вопрос | Возражение — и кому | Зона · артефакт | Покрыто |\n"
         "|---|---|---|---|---|\n")
ЦЕЛАЯ = (ШАПКА
         + "| Автор правил | что за инцидент | Инженер гейтов — «нет инцидента» | `rules/**` | да |\n"
         + "| Инженер гейтов | чем держится | Автор правил — «признак недоступен» | `scripts/*` | да |\n")


def карта(root: Path, text: str) -> Path:
    return write(root / "AGENTS.md", "# Свод\n\n" + text)


# ── здоровые предметы ──────────────────────────────────────────────────────

def test_tselaya_karta_prohodit(repo, capsys):
    карта(repo, ЦЕЛАЯ)

    assert cr.main(["--root", str(repo)]) == 0
    assert "ролей 2" in capsys.readouterr().out


def test_odin_adresat_u_dvuh_rolei_zakonen(repo):
    """Предмет у границы: различаться обязаны ДОВОДЫ, а не адресаты."""
    карта(repo, ЦЕЛАЯ
          + "| Ревизор | сходится ли | Инженер гейтов — «адреса на диске нет» | `.rules/**` | да |\n")

    assert cr.main(["--root", str(repo)]) == 0


def test_razmetka_v_imeni_roli_ne_meshaet(repo):
    """«**Диспетчер**» и «Диспетчер» — одна роль, а не две."""
    карта(repo, ШАПКА
          + "| **Диспетчер** | что без метки | Автор правил — «источника нет» | трекер | нет |\n"
          + "| Автор правил | что за инцидент | **Диспетчер** — «задачи нет» | `rules/**` | да |\n")

    assert cr.main(["--root", str(repo)]) == 0


# ── предметы, которые гейт обязан отвергнуть ───────────────────────────────

def test_vozrazheniya_net_eto_nahodka(repo, capsys):
    """Ровно предмет правила: направление без возражения — раздел документации."""
    карта(repo, ЦЕЛАЯ.replace("Инженер гейтов — «нет инцидента»", ""))

    assert cr.main(["--root", str(repo)]) == 1
    assert "пуста" in capsys.readouterr().err


def test_vozrazhenie_bez_adresata_eto_nahodka(repo, capsys):
    карта(repo, ЦЕЛАЯ.replace("Инженер гейтов — «нет инцидента»",
                              "тут что-то не так"))

    assert cr.main(["--root", str(repo)]) == 1
    assert "не называет адресата" in capsys.readouterr().err


def test_adresat_vne_karty_eto_nahodka(repo, capsys):
    карта(repo, ЦЕЛАЯ.replace("Инженер гейтов — «нет инцидента»",
                              "Сторонний наблюдатель — «мне не нравится»"))

    assert cr.main(["--root", str(repo)]) == 1
    assert "такой роли в карте нет" in capsys.readouterr().err


def test_vozrazhenie_sebe_eto_nahodka(repo, capsys):
    """Спор с собой проходит всегда и не останавливает ничего."""
    карта(repo, ЦЕЛАЯ.replace("Инженер гейтов — «нет инцидента»",
                              "Автор правил — «сам себе не верю»"))

    assert cr.main(["--root", str(repo)]) == 1
    assert "сама себе" in capsys.readouterr().err


def test_odinakovye_dovody_eto_nahodka(repo, capsys):
    """Два направления с одним доводом — одно направление, записанное дважды."""
    карта(repo, ЦЕЛАЯ
          + "| Ревизор | сходится ли | Инженер гейтов — «нет инцидента» | `.rules/**` | да |\n")

    assert cr.main(["--root", str(repo)]) == 1
    assert "повторяет" in capsys.readouterr().err


def test_nedostayushchaya_kolonka_eto_nahodka(repo, capsys):
    карта(repo, ШАПКА
          + "| Автор правил | что за инцидент | Инженер гейтов — «нет» | `rules/**` |\n")

    assert cr.main(["--root", str(repo)]) == 1
    assert "вместо пяти" in capsys.readouterr().err


# ── третий исход: проверка не отработала ──────────────────────────────────

def test_svoda_net_eto_tretiy_ishod(repo, capsys):
    assert cr.main(["--root", str(repo)]) == 2
    assert "не отработала" in capsys.readouterr().err


def test_karty_v_svode_net_eto_tretiy_ishod(repo, capsys):
    """«Ролей ноль» и «карты нет» — разные ответы (039, 075)."""
    write(repo / "AGENTS.md", "# Свод\n\nтекст без таблицы\n")

    assert cr.main(["--root", str(repo)]) == 2
    assert "нет таблицы" in capsys.readouterr().err


def test_pustaya_karta_eto_tretiy_ishod(repo, capsys):
    карта(repo, ШАПКА)

    assert cr.main(["--root", str(repo)]) == 2
    assert "пуста" in capsys.readouterr().err
