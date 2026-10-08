#!/usr/bin/env python3
"""Ответ проекта каталогу — по форме контракта, до того как его прочтёт сводка.

ОТДАЁТСЯ ПОТРЕБИТЕЛЮ, действием `.github/actions/answer`. Запускается в
репозитории ПРОЕКТА, на его изменении: каталог определяет, как ему отвечать,
и потому обязан отдавать проверку этой формы — иначе каждый проект растит свой
диалект, а сводка узнаёт о расхождении через сутки и правит его не там (129,
197). Замер 8 октября: три проекта завели пробу «не применимо» в трёх разных
формах, а ключи вне контракта несли два — и ни один прогон об этом не сказал.

ЧТО ПРОВЕРЯЕТСЯ — тем же модулем формы записи, что у каталога о себе и у
сводки (`answer_form.py`, 214):
  • статус из словаря; у `rejected`/`not-applicable` есть причина; у `active`
    назван механизм из словаря;
  • происхождение механизма: с ответа 1.9 обязательно у `gate`/`pipeline`;
  • проба «не применимо» `refuted_by` — форма, и она ПРОГОНЯЕТСЯ по дереву
    проекта: нашла предмет — ответ «не применимо» опровергнут;
  • `note` и `metric` по форме; с 1.9 — закрытый список ключей записи.

ЧЕГО ЗДЕСЬ НЕТ. Существует ли файл, названный механизмом, и объявляет ли он
правило своим, — это дерево проекта, и сверяет его сам проект своим гейтом;
каталог отдаёт форму, а не чужие соглашения о коде.

Запуск:  python scripts/check_answer.py [--bindings .rules/bindings.json] [--root .]
Коды:    0 чисто · 1 есть находки · 2 ответ не прочитан

Реализует правила каталога:
  129 — контракт потребления двусторонний: каталог отдаёт проверку формы;
  197 — издатель пользуется своим: та же форма сверяет ответ каталога о себе;
  205 — проба «не применимо» прогоняется, а не только описывается;
  039 — три исхода, а не два.
"""


import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import answer_form  # noqa: E402
# Словари — у гейта ответа каталога, а не копией здесь (214). Слово
# `process-step` словарь ещё принимает: оно в переходном слое (094).
from check_bindings import MECHANISMS, STATUSES  # noqa: E402


def находки(answer: dict, root: Path) -> list[str]:
    """Все находки формы ответа проекта и опровергнутые пробы."""
    схема = answer.get("schema") or ""
    out: list[str] = []
    if (что := answer_form.схема_неверна(схема)):
        out.append(что)
    for rid, rec in sorted((answer.get("rules") or {}).items()):
        if not isinstance(rec, dict):
            out += answer_form.запись(rid, rec, схема)
            continue
        статус = rec.get("status")
        if статус not in STATUSES:
            out.append(f"{rid}: статус «{статус}» вне словаря — "
                       + ", ".join(STATUSES))
        if статус in ("rejected", "not-applicable") and not rec.get("why"):
            out.append(f"{rid}: статус «{статус}» без причины — решение без "
                       "причины вернётся следующей ревизией")
        if статус == "active" and (rec.get("mechanism") or "none") not in MECHANISMS:
            out.append(f"{rid}: механизм «{rec.get('mechanism')}» вне словаря — "
                       + ", ".join(MECHANISMS))
        out += answer_form.запись(rid, rec, схема)
        if статус == "not-applicable":
            улика = answer_form.прогнать_пробу(rec, root)
            if улика:
                out.append(f"{rid}: «не применимо» опровергнуто своей же пробой — "
                           f"{улика}. Предмет в дереве появился: перечитайте ответ")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bindings", type=Path, default=Path(".rules/bindings.json"))
    ap.add_argument("--root", type=Path, default=Path("."))
    args = ap.parse_args(argv)
    try:
        answer = json.loads(args.bindings.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"проверка не отработала: {args.bindings} не прочитан — {e}",
              file=sys.stderr)
        return 2
    if not isinstance(answer, dict) or not isinstance(answer.get("rules"), dict):
        print(f"проверка не отработала: в {args.bindings} нет объекта `rules`",
              file=sys.stderr)
        return 2
    найдено = находки(answer, args.root)
    if найдено:
        print(f"ответ каталогу не по форме контракта {answer.get('schema')}:",
              file=sys.stderr)
        for f in найдено:
            print(f"  • {f}", file=sys.stderr)
        return 1
    print(f"ответ по форме контракта {answer.get('schema')}: записей "
          f"{len(answer['rules'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
