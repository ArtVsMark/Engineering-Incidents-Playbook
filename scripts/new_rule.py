#!/usr/bin/env python3
"""Собирает КАРКАС новой записи: всё механическое, и ничего сверх того.

ПОЧЕМУ ЭТО ВООБЩЕ ЗАВЕДЕНО. Порядок добавления правила — семь шагов, и все
семь делались руками: выбрать следующий свободный номер, назвать файл
одинаково в двух деревьях, вписать область из закрытого словаря, спросить
каталог о соседях, ответить за правило в bindings, положить фрагмент журнала,
пересобрать производные. Шаг, который надо помнить, пропускают — и человек, и
окно (правило 002). Измерено на этом же каталоге: за одно окно дважды
поставлены НЕСУЩЕСТВУЮЩИЕ имена файлов в перекрёстных ссылках, и оба раза их
нашёл гейт ссылок, а не автор.

ЧТО СОБИРАЕТ. Номер, оба файла из заготовки, строку области, разрешимый след,
запись в ответе каталога, фрагмент журнала. Всё это вычисляется однозначно, и
человеку в нём делать нечего.

ЧЕГО НЕ СОБИРАЕТ И НЕ БУДЕТ. Утверждение, инцидент, механизм поломки, границу
«не работает» и вердикт о соседях. Это не лень генератора: перечисленное и
есть содержание записи, а содержание — суждение. Сгенерированный инцидент был
бы выдумкой, а выдуманный инцидент хуже отсутствующего: он выглядит как
основание.

ПОЭТОМУ СКРИПТ ЗАКАНЧИВАЕТ СПИСКОМ ТОГО, ЧТО ОСТАЛОСЬ ЧЕЛОВЕКУ, а не словом
«готово». Каркас без содержания — не запись, и гейт полноты её не пропустит.

Запуск:
  python scripts/new_rule.py --slug branch-name-is-a-switch \\
      --area конвейер --trail владелец/репозиторий#12

Коды: 0 каркас собран · 1 собрать нельзя · 2 проверка не отработала
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("ru", "en")
TEMPLATE = ROOT / "templates" / "rule-template.md"
BINDINGS = ROOT / ".rules" / "bindings.json"
CONSUMERS = ROOT / ".rules" / "consumers.json"
NEIGHBOURS = ROOT / ".rules" / "neighbours.json"
CHANGELOG_DIR = ROOT / "changelog.d"

RULE_RE = re.compile(r"^(\d{3})-([a-z0-9-]+)\.md$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")
#: След обязан разрешаться: задача либо потребитель с названным артефактом.
ISSUE_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#\d+$")

#: Каркас английской стороны. Заготовка в репозитории одна и русская; делать
#: вторую значило бы завести два места для одной формы (правило 022), а формы
#: расходятся молча. Английские заголовки берутся из канона audit_catalogue.
EN_SKELETON = """# <One-line rule: a claim, not a topic>

**Area.** {area_en}

**The rule.** <Two or three sentences. What to do and what not to do.>

## The incident

<What broke, with numbers and dates.>

<What was tried first and why it did not work.>

## Why

<The mechanism of the failure, not the moral.>

## Where it applies

**Works** <where exactly>.

**Does not work** <where exactly — this half is mandatory>.

**Sign of a violation:** <an observable fact>.

## Trace

{trail}

See also: <neighbouring rules>.
"""


def existing(root: Path) -> dict[str, str]:
    """Номер → слаг по русскому дереву. Английское сверяет сборка указателя."""
    out: dict[str, str] = {}
    for p in (root / "rules" / "ru").glob("*.md"):
        m = RULE_RE.match(p.name)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def next_number(taken: dict[str, str]) -> str:
    """Следующий свободный. Номера НЕ переиспользуются: только выше максимума,
    даже если в середине есть дыры от удалённых записей."""
    return f"{max(int(n) for n in taken) + 1:03d}"


def areas(root: Path) -> tuple[dict[str, str], str | None]:
    """Словарь областей из сборки указателя: он закрытый и живёт там."""
    sys.path.insert(0, str(root / "scripts"))
    try:
        import build_rules_index as index
    except Exception as e:  # pragma: no cover — сборка не импортируется
        return {}, f"словарь областей не прочитан — {e}"
    return {k: v["en"] for k, v in index.AREAS.items()}, None


def trail_resolves(trail: str, root: Path) -> bool:
    if ISSUE_RE.match(trail):
        return True
    try:
        known = {c["repo"] for c in json.loads(
            (root / ".rules" / "consumers.json").read_text(encoding="utf-8"))["consumers"]}
    except (OSError, ValueError, KeyError, TypeError):
        return False
    return any(trail.startswith(repo) and len(trail) > len(repo) for repo in known)


def proposal(root: Path, key: str) -> tuple[dict, str | None]:
    """Приехавшее предложение по ключу «владелец/репозиторий:слаг».

    Берётся ИЗ ИСТОЧНИКА у потребителя, а не из вердикта каталога: вердикт
    хранит решение, а не текст. Слаг и след приходят оттуда, номер — отсюда.
    """
    repo, _, slug = key.partition(":")
    if not slug:
        return {}, f"ключ {key!r} не по форме «владелец/репозиторий:слаг»"
    try:
        registry = json.loads(
            (root / ".rules" / "consumers.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {}, f"реестр потребителей не прочитан — {e}"
    entry = next((c for c in registry.get("consumers", [])
                  if c.get("repo") == repo), None)
    if entry is None:
        return {}, (f"{repo} не объявлен потребителем. Предложение от "
                    "необъявленного проекта принимать нельзя: за ним нет ни "
                    "ответа о правилах, ни адреса, по которому спросить")
    source = entry.get("proposals")
    if not source:
        return {}, (f"у {repo} не назван адрес предложений — канал в эту "
                    "сторону не подключён")
    try:
        if source.startswith("http"):
            import urllib.request
            with urllib.request.urlopen(source, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        else:
            data = json.loads((root / source).read_text(encoding="utf-8"))
    except Exception as e:
        return {}, f"предложения {repo} не прочитаны — {e}"
    found = next((p for p in data.get("proposals", [])
                  if p.get("slug") == slug), None)
    if found is None:
        return {}, f"у {repo} нет предложения со слагом {slug!r}"
    if not found.get("incident"):
        return {}, (f"предложение {key} без инцидента. Правило без инцидента — "
                    "предпочтение, и через месяц его нечем защитить")
    return {"slug": slug, "trail": f"{repo} — {found.get('trail', '')}".strip(" —"),
            "claim": found.get("claim", ""),
            "incident": found.get("incident", "")}, None


def neighbours(root: Path, path: Path) -> str:
    """Верхушка соседей по ЧЕРНОВИКУ — как подсказка, а не как ответ."""
    done = subprocess.run(
        [sys.executable, str(root / "scripts" / "check_duplicates.py"),
         "--near", str(path)], capture_output=True, text=True)
    return (done.stdout or done.stderr).strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--slug", help="слаг латиницей, без номера; при --from-proposal берётся оттуда")
    ap.add_argument("--area", required=True,
                    help="одна-три области через запятую, из закрытого словаря")
    ap.add_argument("--trail",
                    help="владелец/репозиторий#номер либо потребитель с артефактом")
    ap.add_argument("--from-proposal", metavar="ВЛАДЕЛЕЦ/РЕПО:СЛАГ",
                    help="предложение, приехавшее из проекта: слаг, область и "
                         "след берутся из него, а номер присваивает каталог")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    root: Path = args.root

    # ЗАМЫКАНИЕ КРУГА: предложение из проекта становится каркасом одной
    # командой. Номер при этом присваивает КАТАЛОГ и только он — у предложения
    # номера нет и быть не может: они не переиспользуются, а независимый выбор
    # двух проектов уже нечем починить (правило 080, задача #91).
    if args.from_proposal:
        pending, why = proposal(root, args.from_proposal)
        if why:
            print(f"собрать нельзя: {why}", file=sys.stderr)
            return 1
        args.slug = args.slug or pending["slug"]
        args.trail = args.trail or pending["trail"]
    if not args.slug:
        print("собрать нельзя: слаг не назван и взять его неоткуда",
              file=sys.stderr)
        return 1
    if not args.trail:
        print("собрать нельзя: след не назван. Он обязан разрешаться — задача "
              "или потребитель с артефактом", file=sys.stderr)
        return 1

    # ── исход 2 ────────────────────────────────────────────────────────────
    taken = existing(root)
    if not taken:
        print("проверка не отработала: в rules/ru нет ни одной записи — "
              "нумеровать не от чего", file=sys.stderr)
        return 2
    if not (root / "templates" / "rule-template.md").exists():
        print("проверка не отработала: нет заготовки templates/rule-template.md",
              file=sys.stderr)
        return 2
    known_areas, err = areas(root)
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    # ── исход 1 ────────────────────────────────────────────────────────────
    if not SLUG_RE.match(args.slug):
        print(f"собрать нельзя: слаг {args.slug!r} не по форме — латиница, "
              "цифры и дефисы, начинается с буквы", file=sys.stderr)
        return 1
    if args.slug in taken.values():
        num = next(n for n, s in taken.items() if s == args.slug)
        print(f"собрать нельзя: слаг занят записью {num}. Пересмотр — это "
              "НОВАЯ запись с новым слагом, а не правка задним числом",
              file=sys.stderr)
        return 1
    wanted = [a.strip() for a in args.area.split(",") if a.strip()]
    unknown = [a for a in wanted if a not in known_areas]
    if unknown:
        print(f"собрать нельзя: области вне словаря — {', '.join(unknown)}.\n"
              f"  Словарь закрыт и живёт в scripts/build_rules_index.py; новая "
              "дописывается туда осознанно и сразу с описанием.\n"
              f"  Есть: {', '.join(sorted(known_areas))}", file=sys.stderr)
        return 1
    if not trail_resolves(args.trail, root):
        print(f"собрать нельзя: след {args.trail!r} не разрешается. Нужна "
              "задача «владелец/репозиторий#номер» либо потребитель из реестра "
              "с названным артефактом. Проза следом не считается",
              file=sys.stderr)
        return 1

    # ── исход 0 ────────────────────────────────────────────────────────────
    num = next_number(taken)
    name = f"{num}-{args.slug}.md"
    ru_body = (root / "templates" / "rule-template.md").read_text(encoding="utf-8")
    ru_body = re.sub(r"(?m)^\*\*Область\.\*\*.*?(?=\n\n)", f"**Область.** {args.area}",
                     ru_body, count=1, flags=re.S)
    # След подставляется целиком: он разрешим и проверен выше, человеку в нём
    # делать нечего. Всё остальное в заготовке остаётся местом для суждения.
    ru_body = re.sub(r"(?ms)^## След\n\n`<.*?>`\n",
                     f"## След\n\n{args.trail}\n", ru_body, count=1)
    made = []
    for lang in LANGS:
        path = root / "rules" / lang / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if lang == "ru":
            path.write_text(ru_body, encoding="utf-8")
        else:
            en_areas = ", ".join(known_areas[a] for a in wanted)
            path.write_text(EN_SKELETON.format(area_en=en_areas, trail=args.trail),
                            encoding="utf-8")
        made.append(str(path.relative_to(root)))

    # Пути считаются ОТ КОРНЯ, а не берутся из констант модуля: константы
    # указывают на сам каталог, и с ключом --root скрипт писал бы предмет в
    # одно место, а ответ о нём — в другое. Поймано первым же прогоном на
    # копии дерева (правило 139).
    bindings = root / ".rules" / "bindings.json"
    doc = json.loads(bindings.read_text(encoding="utf-8"))
    doc["rules"][num] = {"status": "unreviewed"}
    bindings.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    frag = root / "changelog.d" / f"rule-{num}-{args.slug}.added.md"
    frag.write_text(f"Правило {num}: <утверждение одной фразой> ({args.trail}).\n",
                    encoding="utf-8")

    for p in made:
        print(f"  {p}")
    print(f"  .rules/bindings.json — {num}: не рассмотрено")
    print(f"  {frag.relative_to(root)}")
    print(f"\nкаркас {num} собран. Номер взят выше максимума: они не "
          "переиспользуются даже после удаления.\n")
    print(neighbours(root, root / "rules" / "ru" / name))
    print("\nОСТАЛОСЬ ЧЕЛОВЕКУ — и генератор этого не сделает:\n"
          "  • утверждение, инцидент с числами, механизм поломки;\n"
          "  • граница «НЕ работает» — без неё гейт полноты не пропустит;\n"
          "  • английская сторона по существу, а не подстрочником;\n"
          f"  • вердикт о соседях в .rules/neighbours.json по ГОТОВОМУ тексту,\n"
          f"    а не по этому черновику — гейт сверяет именно готовый;\n"
          "  • ответ о правиле в .rules/bindings.json вместо «не рассмотрено».\n"
          "Потом: закоммитить, затем python scripts/build_rules_index.py —\n"
          "дата берётся из истории файла, и до коммита её нет.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
