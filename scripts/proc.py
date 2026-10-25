#!/usr/bin/env python3
"""Вызов процесса в механизме каталога: дедлайн обязателен, его истечение — код, а не трасса.

ДВЕ ПОЛОВИНЫ ПРАВИЛА 100 В ОДНОМ МЕСТЕ. Дедлайн без поимки менял зависание на
трассу с кодом 1 — то же нарушение третьего исхода (039), только быстрее. До
22.10 у 44 вызовов в 27 скриптах `timeout=` стоял, а `TimeoutExpired` не
ловил никто; держал это гейт каталога `check_subprocess.py`, судивший только
первую половину. Замер — шаг `pipeline` механизмов на этапе 1 #930
(`check_deadline.py`, v1.9.0).

ИСТЕЧЕНИЕ ВОЗВРАЩАЕТСЯ ОБЫЧНЫМ НЕНУЛЕВЫМ КОДОМ. Вызывающие уже разбирают
`returncode != 0` в свой названный отказ («не спросить коммиты ветки: …»), и
истечение попадает туда же — с причиной в `stderr`, без второй развилки в
каждом месте. Код — `TIMED_OUT`, как у `timeout(1)`: его не даёт ни `git`,
ни `gh`, и спутать истечение с их собственным отказом нельзя. С `check=True`
истечение — `CalledProcessError` с тем же кодом: так вызов обещал отказ, и
вызывающие его уже ловят.

ОДНА РЕАЛИЗАЦИЯ (214). До неё у десяти скриптов были свои `git()`/`run()`
поверх `subprocess.run`, и поимку пришлось бы писать десять раз.

ГРАНИЦА. `OSError` (нет `git`, нет интерпретатора) обёртка не трогает: что
делать без программы, решает вызывающий, и многие уже решают. Хук окна
`push_guard.py` живёт отдельно — он закрывает толчок кодом 2 по истечению в
`main()`, и у него своя обёртка с тем же предметом.

Реализует правила каталога:
  100 — у вызова процесса названный дедлайн и пойманное истечение;
  214 — один предмет держит одна реализация;
  039 — истечение — названный исход, а не трасса.
"""

import subprocess
from collections.abc import Sequence
from typing import Any, Final

__all__ = ["TIMED_OUT", "run"]

#: Код истёкшего дедлайна — как у `timeout(1)`.
TIMED_OUT: Final = 124


def _как_вызов(data: bytes | str | None, текстом: bool) -> bytes | str:
    """Вывод того же рода, что ждёт вызывающий: у `TimeoutExpired` он бывает байтами и при `text=True`."""
    if data is None:
        data = b""
    if текстом:
        return data.decode("utf-8", "replace") if isinstance(data, bytes) else data
    return data.encode("utf-8") if isinstance(data, str) else data


def run(args: Sequence[Any], *, timeout: float, **kwargs: Any) -> subprocess.CompletedProcess:
    """`subprocess.run` с обязательным дедлайном; истёкший — код `TIMED_OUT` и причина в stderr."""
    try:
        return subprocess.run(args, timeout=timeout, **kwargs)  # noqa: S603 — аргументы вызывающего
    except subprocess.TimeoutExpired as exc:
        текстом = bool(
            kwargs.get("text")
            or kwargs.get("encoding")
            or kwargs.get("universal_newlines")
            or kwargs.get("errors")
        )
        вызов = " ".join(map(str, args))[:120]
        причина = f"не ответил за {timeout:g} с: {вызов} (100)"
        вывод, ошибка = _как_вызов(exc.stdout, текстом), _как_вызов(причина, текстом)
        # `check=True` обещает исключение на любом ненулевом исходе, и вызывающие
        # его ловят; вернуть код молча значило бы отдать пустой вывод за успех.
        if kwargs.get("check"):
            raise subprocess.CalledProcessError(TIMED_OUT, args, вывод, ошибка) from exc
        return subprocess.CompletedProcess(args, TIMED_OUT, вывод, ошибка)
