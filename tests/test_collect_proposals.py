"""Приехавшие предложения: что читается, что возражает и когда возражение снято.

Предмет здесь ВХОДЯЩАЯ сторона канала, а не вердикты каталога: их проверяет
подделка в `check_gates.py`. Сеть подменяется — `fetch` спрашивают за настоящий
адрес, и без подмены случай проверял бы доступность чужого репозитория, а не
решение гейта (170: у подделки назван источник — `.rules/consumers.json`
каждого потребителя, поле `proposals`).
"""

from __future__ import annotations

import collect_proposals as cp


ПОТРЕБИТЕЛЬ = [{"repo": "o/r", "proposals": "https://example.invalid/p.json"}]


def подменить(monkeypatch, предложения: list[dict]) -> None:
    monkeypatch.setattr(cp, "fetch",
                        lambda url: ({"proposals": предложения}, None))


ГОДНОЕ = {"slug": "a-good-one", "claim": "утверждение",
          "incident": "инцидент с числами", "trail": "o/r#1"}


def test_годное_предложение_читается(monkeypatch):
    подменить(monkeypatch, [ГОДНОЕ])
    pending, problems = cp.gather(ПОТРЕБИТЕЛЬ, {})
    assert problems == []
    assert [p["slug"] for p in pending] == ["a-good-one"]


def test_поле_номера_у_НЕразобранного_возражает(monkeypatch):
    """Пока решения нет, форма важна: `rule` у нас означает присвоенный номер."""
    подменить(monkeypatch, [{**ГОДНОЕ, "rule": "196"}])
    _, problems = cp.gather(ПОТРЕБИТЕЛЬ, {})
    assert len(problems) == 1
    assert "rule" in problems[0]
    # Сообщение обязано назвать и второй случай: в поле лежит ТЕКСТ, а не номер.
    assert "claim" in problems[0]


def test_вынесенное_решение_снимает_возражение_о_форме(monkeypatch):
    """Инцидент 8 сентября: разобранное предложение возражало вечно.

    `repair-acceptance-stronger-than-defect` грейдера принят правилом 193, а
    гейт всё равно печатал возражение: проверка полей стояла ДО проверки «решение
    вынесено». Чужой файл мы не правим, вердикт у нас записан — и очередь
    показывала работу, которой нет (075).
    """
    подменить(monkeypatch, [{**ГОДНОЕ, "rule": "текст утверждения, а не номер"}])
    pending, problems = cp.gather(
        ПОТРЕБИТЕЛЬ, {cp.key_of("o/r", "a-good-one"): {"status": "admitted"}})
    assert problems == []
    assert pending == []


def test_разобранное_не_попадает_в_очередь_и_без_поля(monkeypatch):
    """Вторая сторона: решение снимает предложение с очереди в любом случае."""
    подменить(monkeypatch, [ГОДНОЕ])
    pending, problems = cp.gather(
        ПОТРЕБИТЕЛЬ, {cp.key_of("o/r", "a-good-one"): {"status": "rejected"}})
    assert (pending, problems) == ([], [])


def test_негодный_слаг_возражает_до_всякого_решения(monkeypatch):
    """Слаг проверяется раньше: без него ключа вердикта не построить вовсе."""
    подменить(monkeypatch, [{**ГОДНОЕ, "slug": "НеЛатиница"}])
    _, problems = cp.gather(ПОТРЕБИТЕЛЬ, {})
    assert len(problems) == 1 and "слаг" in problems[0]
