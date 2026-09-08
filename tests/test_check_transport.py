"""Исключение транспорта адресуется тем, ЧТО разрешено, а не тем, где лежало.

Держит правило каталога 001: вызов через GraphQL законен, только если назван
поимённо в закрытом списке. Здесь проверяется форма адреса — она пережила три
живых отказа подряд и была из-за них переписана.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_transport as ct  # noqa: E402


@pytest.fixture
def дерево(tmp_path: Path) -> Path:
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / ".rules").mkdir()
    return tmp_path


def прогон(дерево: Path, строк_сверху: int = 0) -> None:
    шапка = "".join(f"# строка {i}\n" for i in range(строк_сверху))
    (дерево / ".github" / "workflows" / "automerge.yml").write_text(
        шапка + 'jobs:\n  x:\n    steps:\n      - run: |\n'
        '          out=$(gh pr merge "$PR" --auto)\n', encoding="utf-8")


def список(дерево: Path, запись: dict) -> None:
    (дерево / ".rules" / "transport.json").write_text(
        json.dumps({"_": "проба", "allowed": [запись]}, ensure_ascii=False),
        encoding="utf-8")


def прогнать(monkeypatch, дерево: Path) -> int:
    monkeypatch.setattr(ct, "СПИСОК", дерево / ".rules" / "transport.json")
    return ct.main(["--root", str(дерево)])


def test_adres_bez_nomera_perezhivaet_sdvig(monkeypatch, дерево):
    """РОВНО ПРЕДМЕТ ПОЧИНКИ, ЗАМЕР 8 сентября: за час гейт упал дважды на одном
    и том же законном вызове — сначала шесть строк комментария в шапке сдвинули
    его с 380 на 386, потом новые шаги на 421. Адрес называл ГДЕ, а не ЧТО."""
    список(дерево, {"where": ".github/workflows/automerge.yml",
                    "what": "gh pr", "why": "у мутации нет REST-адреса"})

    прогон(дерево, строк_сверху=0)
    assert прогнать(monkeypatch, дерево) == 0
    прогон(дерево, строк_сверху=40)
    assert прогнать(monkeypatch, дерево) == 0, "сдвиг строк не должен ронять гейт"


def test_staraya_forma_s_nomerom_ostayotsya_zakonnoy(monkeypatch, дерево):
    """Точный адрес годен там, где вызовов несколько и они разные."""
    прогон(дерево)
    список(дерево, {"where": ".github/workflows/automerge.yml:5",
                    "why": "у мутации нет REST-адреса"})

    assert прогнать(monkeypatch, дерево) == 0


def test_drugoy_vyzov_v_tom_zhe_fayle_otvergaetsya(monkeypatch, дерево):
    """ГРАНИЦА С ДРУГОЙ СТОРОНЫ, И ОНА ГЛАВНАЯ. Разрешение по файлу не должно
    прощать ВСЁ в этом файле: `what` называет одну команду, и вторая, другая,
    обязана остаться находкой (051)."""
    (дерево / ".github" / "workflows" / "automerge.yml").write_text(
        'jobs:\n  x:\n    steps:\n      - run: |\n'
        '          out=$(gh pr merge "$PR" --auto)\n'
        '          gh issue list\n', encoding="utf-8")
    список(дерево, {"where": ".github/workflows/automerge.yml",
                    "what": "gh pr", "why": "у мутации нет REST-адреса"})

    assert прогнать(monkeypatch, дерево) == 1


def test_neназванный_vyzov_otvergaetsya(monkeypatch, дерево):
    """Списка нет — вызов не разрешён ничем."""
    прогон(дерево)
    список(дерево, {"where": ".github/workflows/other.yml",
                    "what": "gh pr", "why": "не про этот файл"})

    assert прогнать(monkeypatch, дерево) == 1


def test_bez_what_fayl_razreshaet_lyuboy_vyzov_v_nyom(monkeypatch, дерево):
    """Форма «файл» без `what` осознанно широка: она говорит «в этом файле
    GraphQL законен», и это законный, хотя и тупой, ответ. Проверяется, чтобы
    поведение было названо, а не случилось."""
    прогон(дерево)
    список(дерево, {"where": ".github/workflows/automerge.yml",
                    "why": "весь файл про мутации"})

    assert прогнать(monkeypatch, дерево) == 0
