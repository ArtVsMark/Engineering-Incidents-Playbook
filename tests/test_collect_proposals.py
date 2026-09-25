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


# ── след предложения: адрес, а не проза ───────────────────────────────────
#
# Требование то же, что у `where` вниз по течению, и предикат у них один
# (022). Инцидент, ради которого разбор заведён: у `trail` проверялось только
# «непусто», и та же асимметрия дала ту же цену уже у каталога — 12 записей из
# 195 отдавались потребителю с пустым `trails` при названном адресе у
# одиннадцати, потому что формы никто не требовал.


def test_след_прозой_это_находка(monkeypatch):
    подменить(monkeypatch, [{**ГОДНОЕ, "trail": "видно в разборе сессии"}])
    pending, problems = cp.gather(ПОТРЕБИТЕЛЬ, {})
    (беда,) = problems
    assert "не называет адреса" in беда
    # ПРЕДЛОЖЕНИЕ ПРИ ЭТОМ ОСТАЁТСЯ: инцидент ценнее формы, решает человек.
    assert [p["slug"] for p in pending] == ["a-good-one"]


def test_след_адресом_возражения_не_вызывает(monkeypatch):
    """Вторая сторона набора (140): законные формы проходят все три."""
    for след in ("scripts/build_metrics.py",
                 ".github/workflows/*.yml — все прогоны разом",
                 "CONTRIBUTING § вход новичка"):
        подменить(monkeypatch, [{**ГОДНОЕ, "trail": след}])
        _, problems = cp.gather(ПОТРЕБИТЕЛЬ, {})
        assert problems == [], (след, problems)


def test_след_без_расширения_не_считается_адресом(monkeypatch):
    """Живая форма, на которой каталог обжёгся: имя решения без пути."""
    подменить(monkeypatch, [{**ГОДНОЕ, "trail": "ADR-0010 § Контекст"}])
    _, problems = cp.gather(ПОТРЕБИТЕЛЬ, {})
    assert problems and "не называет адреса" in problems[0]


# ── задача-«входящие снизу» ищется по всем страницам (212) ─────────────────

def test_zadacha_ishchetsya_po_vsem_stranitsam(monkeypatch, capsys):
    """Поиск идёт с --paginate, и найденная — где бы она ни лежала — правится,
    а не заводится вторая."""
    вызовы: list[tuple[str, ...]] = []

    def gh(*args: str) -> tuple[int, str]:
        вызовы.append(args)
        if any("issues?state=open" in a for a in args):
            assert "--paginate" in args
            return 0, "7\n"                   # совпадение — строкой на элемент
        return 0, "ok"

    monkeypatch.setattr(cp, "read_json", lambda p: {"consumers": ["o/r"], "verdicts": {}})
    monkeypatch.setattr(cp, "gather", lambda c, v, н=None: (["o/r:slug"], []))
    monkeypatch.setattr(cp, "body_for", lambda p, q: "тело")
    monkeypatch.setattr(cp, "gh", gh)
    monkeypatch.setenv("GH_TOKEN", "x")

    assert cp.main([]) == 1
    assert "задача #7 обновлена" in capsys.readouterr().out
    assert not any(any(a.startswith("title=") for a in c) for c in вызовы)


# ── навык снизу (формат 1.2) ─────────────────────────────────────────────
# Источник подделки текста навыка: `https://raw.githubusercontent.com/<repo>/<sha>/<path>`
# — адрес, который строит сам сборщик, и заголовок SKILL.md вида
# `.claude/skills/incident-triage/SKILL.md` этого каталога.

SHA = "0123456789abcdef0123456789abcdef01234567"
НАВЫК = {"kind": "skill", "slug": "answer-a-rule",
         "path": ".claude/skills/answer-a-rule/SKILL.md", "sha": SHA,
         "holds": ["157"], "measurement": "звали 12 раз, нашёл 3 неверных ответа"}
ТЕКСТ = "---\nname: answer-a-rule\ndescription: Звать, когда отвечаете на правило.\n---\n\n# Ответ\n"


def подменить_с_навыком(monkeypatch, предложения: list[dict], текст: str = ТЕКСТ,
                         отказ: str | None = None) -> list[str]:
    адреса: list[str] = []

    def поддельный(url, **kw):
        адреса.append(url)
        if url.endswith("SKILL.md"):
            return (None, отказ) if отказ else (kw.get("разобрать", str)(текст), None)
        return {"proposals": предложения}, None
    monkeypatch.setattr(cp, "fetch", поддельный)
    return адреса


def test_годный_навык_читается_на_коммите(monkeypatch):
    адреса = подменить_с_навыком(monkeypatch, [НАВЫК])
    pending, problems = cp.gather(ПОТРЕБИТЕЛЬ, {}, {"157"})
    assert problems == []
    (навык,) = pending
    assert навык["kind"] == "skill" and навык["description"].startswith("Звать")
    assert f"/o/r/{SHA}/.claude/skills/answer-a-rule/SKILL.md" in адреса[-1]


def test_навык_без_коммита_возражает_и_не_читается(monkeypatch):
    адреса = подменить_с_навыком(monkeypatch, [{**НАВЫК, "sha": "main"}])
    pending, problems = cp.gather(ПОТРЕБИТЕЛЬ, {}, {"157"})
    assert len(pending) == 1 and pending[0]["url"] == ""
    assert any("40 знаков" in p for p in problems)
    assert not any(a.endswith("SKILL.md") for a in адреса)


def test_навык_держит_правило_которого_нет(monkeypatch):
    подменить_с_навыком(monkeypatch, [{**НАВЫК, "holds": ["999"]}])
    _, problems = cp.gather(ПОТРЕБИТЕЛЬ, {}, {"157"})
    assert any("999" in p for p in problems)


def test_путь_навыка_расходится_со_слагом(monkeypatch):
    подменить_с_навыком(monkeypatch, [{**НАВЫК, "path": ".claude/skills/other-name/SKILL.md"}])
    _, problems = cp.gather(ПОТРЕБИТЕЛЬ, {}, {"157"})
    assert any("имя папки" in p for p in problems)


def test_имя_в_тексте_расходится_со_слагом(monkeypatch):
    подменить_с_навыком(monkeypatch, [НАВЫК], текст=ТЕКСТ.replace("name: answer-a-rule", "name: other"))
    _, problems = cp.gather(ПОТРЕБИТЕЛЬ, {}, {"157"})
    assert any("два имени" in p for p in problems)


def test_текст_навыка_не_прочитан_это_возражение(monkeypatch):
    подменить_с_навыком(monkeypatch, [НАВЫК], отказ="не прочитан: HTTP 404")
    pending, problems = cp.gather(ПОТРЕБИТЕЛЬ, {}, {"157"})
    assert len(pending) == 1 and any("404" in p for p in problems)


def test_неизвестный_вид_пропускается_с_возражением(monkeypatch):
    подменить(monkeypatch, [{**ГОДНОЕ, "kind": "hook"}])
    pending, problems = cp.gather(ПОТРЕБИТЕЛЬ, {})
    assert pending == [] and any("hook" in p for p in problems)


def test_вердикт_навыку_снимает_его_и_не_задевает_правило_того_же_слага(monkeypatch):
    подменить_с_навыком(monkeypatch, [НАВЫК, {**ГОДНОЕ, "slug": "answer-a-rule"}])
    pending, _ = cp.gather(
        ПОТРЕБИТЕЛЬ, {cp.key_of("o/r", "answer-a-rule", "skill"): {"status": "rejected", "why": "x"}},
        {"157"})
    assert [p.get("kind", "rule") for p in pending] == ["rule"]


def test_вердикт_принят_называет_навык_каталога(tmp_path):
    (tmp_path / "rules" / "ru").mkdir(parents=True)
    (tmp_path / ".rules").mkdir()
    import json
    (tmp_path / ".rules" / "proposals.json").write_text(json.dumps({"verdicts": {
        "o/r:skill/answer-a-rule": {"status": "admitted", "skill": "answer-a-rule"}}}),
        encoding="utf-8")
    assert cp.check_verdicts(tmp_path) == 1          # навыка в дереве нет
    файл = tmp_path / ".claude" / "skills" / "answer-a-rule" / "SKILL.md"
    файл.parent.mkdir(parents=True)
    файл.write_text(ТЕКСТ, encoding="utf-8")
    assert cp.check_verdicts(tmp_path) == 0
