"""Изменения, содержащие коммит, читаются до конца и различают отказ и пустоту.

Держит правила каталога 212 и 039 на `check_task_state.pulls_for`: список
читается постранично через общий шов, разбирается по элементу, а отказ
площадки и неразобранный ответ — третий исход, а не «изменений нет».

Источник формы ответа — адрес площадки
https://docs.github.com/rest/commits/commits#list-pull-requests-associated-with-a-commit
и вызов шва `gh api --paginate <путь> --jq '<элемент> | tojson'`: строка JSON
на элемент со всех страниц.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_task_state as cts  # noqa: E402

ИЗМЕНЕНИЕ = {"number": 7, "body": "Closes #5", "merged_at": "2026-09-25T00:00:00Z",
             "merge_commit_sha": "abc"}


def test_chitaetsya_postranichno_i_po_elementu(monkeypatch: pytest.MonkeyPatch) -> None:
    вызовы: list[tuple] = []

    def поддельный(*args: str) -> tuple[int, str]:
        вызовы.append(args)
        # площадка при обходе отдаёт по строке JSON на элемент, со всех страниц
        return 0, "\n".join(json.dumps(dict(ИЗМЕНЕНИЕ, number=n)) for n in (7, 8)) + "\n"

    monkeypatch.setattr(cts, "gh", поддельный)
    pulls, почему = cts.pulls_for("abc")
    assert почему == ""
    assert [p["number"] for p in pulls] == [7, 8]
    (args,) = вызовы
    assert "--paginate" in args
    assert any(a.endswith("/commits/abc/pulls") for a in args)


def test_pustoy_otvet_eto_pustoy_spisok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cts, "gh", lambda *a: (0, ""))
    assert cts.pulls_for("abc") == ([], "")


@pytest.mark.parametrize("ответ, почему", [
    ((1, "HTTP 403"), "HTTP 403"),
    ((0, "{не json"), "не разобран"),
])
def test_otkaz_i_nerazobrannoe_tretiy_iskhod(monkeypatch: pytest.MonkeyPatch,
                                              ответ: tuple[int, str], почему: str) -> None:
    monkeypatch.setattr(cts, "gh", lambda *a: ответ)
    pulls, причина = cts.pulls_for("abc")
    assert pulls is None
    assert почему in причина
