#!/usr/bin/env python3
"""Форма одной записи ответа проекта каталогу — одна на каталог и семью.

ЗАЧЕМ ОТДЕЛЬНЫЙ МОДУЛЬ. Запись ответа читают три места: гейт ответа каталога о
себе (`check_bindings.py`), сводка ответов семьи (`aggregate_bindings.py`) и —
с контракта 1.9 — проверка, которую каталог ОТДАЁТ потребителю
(`check_answer.py`, действие `.github/actions/answer`). Три разбора одного
поля разошлись бы молча на первой же правке (214), и ответы семьи перестали бы
быть однотипными, ради чего контракт и заведён. Поэтому форма записи живёт
здесь, а все трое её зовут.

ЧТО ДОБАВИЛ КОНТРАКТ 1.9 (8 октября, решение владельца):

  • происхождение механизма ОБЯЗАТЕЛЬНО у `gate` и `pipeline`: `origin_kind`
    с новым словом `own` — механизм разработан здесь; для `called`, `copied`,
    `adapted` — ещё `origin`, адрес источника с версией. Замер перед подъёмом:
    объявили 16 записей из ~810 таких по семье — необязательное поле не
    заполнял почти никто, и вопрос «кто у кого взял гейт» оставался без ответа;
  • `refuted_by` — проба, опровергающая «не применимо»: `{globs, contains}`.
    Три проекта завели её САМИ, каждый в своём диалекте (`refuted_by` строкой,
    `refuted_by` объектом, `absent`) — около 60 записей. Диалекты читаются до
    перечитывания ответа, новая форма одна;
  • `note` — свободная мысль проекта по правилу, то, что не ложится в поля;
    `metric` — замер `{what, value, measured}`. Оба необязательны и едут в
    сводку, чтобы каталог видел идеи и числа семьи;
  • форма записи ЗАКРЫТАЯ: незнакомый ключ — находка. Иначе каждый проект
    растит свой диалект, как это уже случилось с пробой.

ЧТО ПРОВЕРЯЕТСЯ ПО ВЕРСИИ. Требования 1.9 действуют на ответ, объявивший
`schema` 1.9 и выше; ответ 1.8 сверяется по правилам 1.8. Задним числом
контракт не спрашивает — подъём своей схемы и есть перечитывание (157).

Реализует правила каталога:
  214 — одна форма записи на три читателя;
  205 — «не применимо» несёт машинную пробу, которую можно прогнать;
  174 — факт о проекте публикует сам проект: происхождение механизма и замер.
"""


import re
from pathlib import Path

#: Способ, которым механизм оказался у проекта. `own` — с 1.9.
ORIGIN_KINDS = ("own", "called", "copied", "adapted")
#: Адрес источника: `<владелец>/<репозиторий>:<путь>@<версия>`.
ORIGIN_RE = re.compile(r"^[\w.-]+/[\w.-]+:[^\s@:]+@[^\s@]+$")
#: Механизмы, у которых происхождение обязательно с 1.9: то, что отвергает
#: или замечает машинно, кто-то написал — здесь или у соседа.
С_ПРОИСХОЖДЕНИЕМ = ("gate", "pipeline")
#: Ключи записи, которые знает контракт. Закрытый список с 1.9.
ПОЛЯ = frozenset({
    "status", "mechanism", "where", "why", "skill", "holdable",
    "machine_half", "awaiting", "origin", "origin_kind", "analysed",
    "decided", "refuted_by", "note", "metric",
    # Переходный слой со старого словаря (094): поле читается, пока не снят.
    "document_reason",
})
#: Диалект пробы до 1.9 у грейдера: `absent: {substring, globs}`.
ДИАЛЕКТ_ПРОБЫ = "absent"


def версия(schema: object) -> tuple[int, ...]:
    """«1.9» → (1, 9); нечитаемое — (0,), то есть «старше всего»."""
    try:
        return tuple(int(x) for x in str(schema).split("."))  # не проза: номер версии схемы
    except ValueError:
        return (0,)


def с_19(schema: object) -> bool:
    return версия(schema) >= (1, 9)


def происхождение(rec: dict, schema: object = "1.8") -> str | None:
    """Что не так с `origin`/`origin_kind`; None — порядок.

    С 1.9 у `gate`/`pipeline` объявление обязательно, а `own` значит «разработан
    здесь» и адреса не несёт. Существование адреса не проверяется: чужого
    дерева у сверяющего нет."""
    for поле in ("origin", "origin_kind"):
        v = rec.get(поле)
        if v is not None and not isinstance(v, str):
            # Чужой ответ может нести что угодно: падение уронило бы сверку
            # всех вместо находки одному (051).
            return (f"`{поле}` — {type(v).__name__} `{str(v)[:40]}`, а ждётся "
                    "строка")
    origin = (rec.get("origin") or "").strip()
    kind = (rec.get("origin_kind") or "").strip()
    mech = rec.get("mechanism") or "none"
    if not origin and not kind:
        if с_19(schema) and rec.get("status") == "active" and mech in С_ПРОИСХОЖДЕНИЕМ:
            return (f"`{mech}` без `origin_kind` — с контракта 1.9 происхождение "
                    "механизма обязательно: `own`, если разработан здесь, иначе "
                    "`called`/`copied`/`adapted` и `origin` с адресом источника")
        return None
    if kind and kind not in ORIGIN_KINDS:
        return (f"`origin_kind: {kind}` — такого слова нет; ждётся одно из "
                + ", ".join(ORIGIN_KINDS))
    if kind == "own" and not с_19(schema):
        return "`origin_kind: own` появился в контракте 1.9 — у ответа схема ниже"
    if mech == "none":
        return ("происхождение при механизме `none` — у того, чего нет, "
                "утверждать не о чем")
    if kind == "own":
        if origin:
            return ("`origin_kind: own` с `origin` — свой механизм ниоткуда не "
                    "взят, адрес источника здесь противоречит слову")
        return None
    if kind and not origin:
        return (f"`origin_kind: {kind}` без `origin` — способ переноса назван, "
                "а откуда перенесено, нет")
    if not kind:
        return ("`origin` назван без `origin_kind` — вызов по тегу и копию "
                "не различить, а ради этого поле и заведено")
    if not ORIGIN_RE.match(origin):
        return (f"`origin` — «{origin[:60]}», а это не адрес. Ждётся "
                "`<владелец>/<репозиторий>:<путь>@<версия>`")
    return None


def проба(rec: dict) -> dict | None:
    """Проба записи в единой форме `{globs, contains}`; None — пробы нет.

    Диалекты до 1.9 читаются: строка — маска, наличие файла по которой
    опровергает ответ; `absent: {substring, globs}` у грейдера."""
    сырая = rec.get("refuted_by")
    if сырая is None and isinstance(rec.get(ДИАЛЕКТ_ПРОБЫ), dict):
        a = rec[ДИАЛЕКТ_ПРОБЫ]
        сырая = {"globs": a.get("globs") or [],
                 "contains": [a["substring"]] if a.get("substring") else []}
    if сырая is None:
        return None
    if isinstance(сырая, str):
        return {"globs": [сырая], "contains": []}
    if isinstance(сырая, dict):
        return {"globs": сырая.get("globs"), "contains": сырая.get("contains", [])}
    return {"globs": None, "contains": None}


def проба_неверна(rec: dict, schema: object) -> str | None:
    """Что не так с формой пробы; None — порядок или пробы нет."""
    if "refuted_by" not in rec and ДИАЛЕКТ_ПРОБЫ not in rec:
        return None
    if rec.get("status") != "not-applicable":
        return ("проба опровергает «не применимо», а статус записи "
                f"`{rec.get('status')}` — опровергать нечего")
    if с_19(schema):
        if ДИАЛЕКТ_ПРОБЫ in rec:
            return ("`absent` — диалект до 1.9; с 1.9 проба пишется "
                    "`refuted_by: {globs, contains}`")
        if not isinstance(rec.get("refuted_by"), dict):
            return ("`refuted_by` строкой — диалект до 1.9; с 1.9 проба "
                    "пишется объектом `{globs, contains}`")
    п = проба(rec)
    маски, строки = п["globs"], п["contains"]
    if (not isinstance(маски, list) or not маски
            or not all(isinstance(m, str) and m.strip() for m in маски)):
        return "`refuted_by.globs` — непустой список масок путей"
    if not isinstance(строки, list) or not all(isinstance(s, str) and s for s in строки):
        return "`refuted_by.contains` — список строк (пустой — «файл есть»)"
    return None


def прогнать_пробу(rec: dict, root: Path) -> str | None:
    """Опровергнут ли ответ «не применимо» деревом; None — нет или пробы нет.

    АСИММЕТРИЯ НАМЕРЕННАЯ, как у пробы каталога о себе: нашли — опровергнуто;
    не нашли — молчание. «Не нашли» и «нет» — разные ответы (039)."""
    п = проба(rec)
    if not п or проба_неверна(rec, "1.8"):
        return None
    for маска in п["globs"]:
        for путь in sorted(root.glob(маска)):
            if not путь.is_file() or ".git" in путь.parts:
                continue
            if not п["contains"]:
                return f"есть {путь.relative_to(root)}"
            try:
                текст = путь.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for s in п["contains"]:
                if s in текст:
                    return f"в {путь.relative_to(root)} есть «{s}»"
    return None


def заметка_неверна(rec: dict) -> str | None:
    """Форма `note` и `metric`; None — порядок или полей нет."""
    if "note" in rec and not (isinstance(rec["note"], str) and rec["note"].strip()):
        return "`note` — непустая строка: мысль проекта по правилу"
    if "metric" in rec:
        m = rec["metric"]
        if not isinstance(m, dict):
            return "`metric` — объект `{what, value, measured}`"
        if not (isinstance(m.get("what"), str) and m["what"].strip()):
            return "`metric.what` — что измерено, словами"
        if not isinstance(m.get("value"), (int, float, str)) or isinstance(m.get("value"), bool):
            return "`metric.value` — число или строка с числом и единицей"
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(m.get("measured") or "")):
            return "`metric.measured` — дата замера, ГГГГ-ММ-ДД"
    return None


def незнакомые(rec: dict, schema: object) -> list[str]:
    """Ключи записи вне контракта; с 1.9 — находка."""
    if not с_19(schema):
        return []
    # Ключ с подчёркиванием — пояснение, а не данные: так заготовка объясняет
    # поля, и так же проекты пишут пояснения на верхнем уровне ответа.
    return sorted(k for k in rec if k not in ПОЛЯ and not str(k).startswith("_"))


def запись(rid: str, rec: object, schema: object) -> list[str]:
    """Все находки формы одной записи — то, что сверяют все три читателя."""
    if not isinstance(rec, dict):
        return [f"{rid}: запись — {type(rec).__name__}, а ждётся объект"]
    out: list[str] = []
    for что in (происхождение(rec, schema), проба_неверна(rec, schema),
                заметка_неверна(rec)):
        if что:
            out.append(f"{rid}: {что}")
    лишние = незнакомые(rec, schema)
    if лишние:
        out.append(f"{rid}: ключи вне контракта — {', '.join(лишние)}. Форма "
                   "записи закрытая с 1.9: то, что не ложится в поля, пишется в "
                   "`note`, замер — в `metric`")
    return out

