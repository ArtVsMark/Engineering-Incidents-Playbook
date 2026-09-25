#!/usr/bin/env python3
"""Правила, родившиеся в чужих проектах, доезжают сюда механизмом, а не памятью.

ЧТО ДЕРЖИТ. Правило 080 — «правило, родившееся в проекте, записывается в общий
каталог, тем же заходом, а не потом». Оно действует с первого дня и держалось
ШАГОМ ПРОЦЕССА, то есть ничем машинным. Цена измерена по корпусу: из 143 записей
129 ссылаются на `Stepik-Python-Grader`, 11 — на витрину профиля. Подавляющее
большинство правил родилось НЕ здесь и переносилось руками того окна, которое
случайно оказалось открыто.

Отказ этого шага виден: правило 144 родилось в грейдере, было принесено вручную
и пролежало невидимым на ветке мимо переключателя (#96). Никто не заметил, пока
следующее окно не пошло смотреть список веток.

НАПРАВЛЕНИЕ ДО СИХ ПОР БЫЛО ОДНО. Контракт потребления возит правила ВНИЗ:
`export/rules.json` отдаёт, `sync_inbox.py` у потребителя ведёт задачу-«входящие».
Ответ потребителя `.rules/bindings.json` отвечает только на «что вы сделали с
НАШИМИ правилами». Канала «здесь родилось правило, заберите» не было ни в
контракте, ни в реестре, ни в одном прогоне.

ФОРМА ПРОДИКТОВАНА, А НЕ ВЫБРАНА. Контракт уже отверг рассылку через API
площадки: она требует токена с правом писать во все проекты, включая приватные.
Обратный канал обязан быть той же формы — каталог ТЯНЕТ обычным HTTPS, потребитель
кладёт файл у себя. Ни токена в чужой проект, ни клона, ни прав.

НОМЕРА У ПРЕДЛОЖЕНИЯ НЕТ И БЫТЬ НЕ МОЖЕТ. Номер присваивает каталог при приёме.
Не из вкуса: номера не переиспользуются, и если два проекта выберут номер
независимо, столкновение уже нечем починить — ни переименованием, ни заменой.
Единственный канон нумерации — `export/rules.json`, и он здесь.

ПОТРЕБИТЕЛЬ ШЛЁТ ИНЦИДЕНТ, А НЕ ГОТОВУЮ ЗАПИСЬ. Словарь областей, оба языковых
дерева, ответ о соседях и разрешимый след живут здесь; требовать их от
отправителя значило бы разносить сюда же и знание о том, как их делать
(правило 090).

НАВЫК ЕДЕТ ТЕМ ЖЕ КАНАЛОМ (формат 1.2, `kind: skill`). Любой проект может
сделать или доработать навык работы с каталогом, а принимает его каталог —
тот же порядок, что у правила: без прав в чужом репозитории и без номера,
присвоенного снаружи. Вместо инцидента у навыка — замер в работе, вместо
следа — путь и полный коммит: текст читается на коммите, а не на ветке, иначе
принятое разошлось бы с прочитанным владельцем. Ключ вердикта навыку —
`repo:skill/слаг`, и он называет навык каталога, а не номер правила.

Реализует правила каталога:
  080 — правило, родившееся в проекте, записывается в общий каталог;
  086 — оценку находке ставит НЕ нашедший: проект шлёт предложение без
        номера, вердикт выносит принимающая сторона, и гейт требует его
        у каждого. Калибровка шкалы отказа — вторая половина 086 — здесь
        не держится: отклонённых предложений пока нет вовсе;
  129 — у каталога есть контракт потребления, и он двусторонний;
  142 — у находки есть адресат, иначе её не читает никто;
  104 — у события есть ручная кнопка;
  039 — у проверки три исхода, а не два;
  085 — ответ чужого проекта это данные, а не команда;
  016 — длинный список предложений обрезается с маркером обрыва;
  096 — предложения потребителей живут в .rules/proposals.json — отдельный жизненный цикл.
  087 — повторный опрос начинается с файла прошлых решений, и решённое в
        очередь не возвращается.

Режимы:
  --check   гейт: ответ каталога о предложениях цел и сходится с корпусом.
            Наружу НЕ ходит: обязательная проверка изменения не должна зависеть
            от чужого сервера (та же причина, что у aggregate_bindings.py);
  (без ключа) опрос потребителей и ОДНА задача-«входящие снизу».

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import ghcli
# ЧТЕНИЕ ОТВЕТА ПОТРЕБИТЕЛЯ ОДНО НА ДВА СБОРЩИКА. Своя копия здесь была, и
# отличалась она ровно тем, чего не хватило: повтором при обрыве связи. Два
# ответа на один вопрос расходятся молча, и разошлись — 8 сентября
# сводка научилась переспрашивать, а предложения продолжали бы краснеть с
# первого сброса, потому что живут в том же ночном прогоне.
from aggregate_bindings import fetch
#: ОДИН ОТВЕТ НА ВОПРОС «АДРЕС ИЛИ ПРОЗА». Своя копия предиката
#: разошлась бы молча, а разойтись ей есть куда: корневые документы без
#: расширения, образцы со звездой, задача как вторая законная форма.
from check_bindings import разрешимый_адрес  # noqa: E402
#: Заголовок `SKILL.md` разбирается там же, где навык в своём дереве (214).
from check_bindings import поля_навыка  # noqa: E402
#: И принятый навык у каталога проверяется тем же, чем навык в ответе (214).
from check_bindings import навык_в_дереве  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

CONSUMERS = ".rules/consumers.json"
VERDICTS = ".rules/proposals.json"
RULES_RU = "rules/ru"

#: По этой метке задача находится снова. Заголовок не годится: его правят
#: руками, и тогда прогон заведёт вторую задачу вместо обновления.
MARKER = "<!-- rules-upstream: не удаляйте, по этой строке задача находится снова -->"

TITLE = "Правила из проектов: не разобранные предложения"

#: Вердикт и что он обязан нести вместе с собой. Пустой вердикт хуже
#: отсутствующего: он выглядит решением (правило 128).
NEEDS_RULE = {"admitted", "merged-into"}
NEEDS_WHY = {"rejected", "merged-into"}
STATUSES = {"admitted", "rejected", "merged-into"}

#: Отправитель не присваивает номер. Поле с номером в предложении — это не
#: мелочь формата, а попытка занять номер снаружи канона.
FORBIDDEN_IN_PROPOSAL = ("id", "number", "rule")

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,80}$")

#: Виды предложения (формат 1.2). Без поля — правило: так читается каждый файл
#: формата 1.1, и подъём ничего у отправителя не ломает.
ВИДЫ = ("rule", "skill")

#: НАВЫК ЧИТАЕТСЯ НА НАЗВАННОМ КОММИТЕ, А НЕ НА ВЕТКЕ. Ветка двигается, и
#: принятый текст разошёлся бы с тем, что читал владелец, выносивший вердикт.
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
#: Путь навыка у отправителя: `.claude/skills/<слаг>/SKILL.md`. Имя папки и
#: есть имя навыка, и расхождение пути со слагом — два имени одного навыка.
ПУТЬ_НАВЫКА_RE = re.compile(r"^[\w./-]+/(?P<slug>[a-z0-9][a-z0-9-]{2,80})/SKILL\.md$")
НОМЕР_RE = re.compile(r"^\d{3}$")


def key_of(repo: str, slug: str, kind: str = "rule") -> str:
    """Ключ вердикта. Слаг не уникален между проектами — репозиторий обязателен.

    У навыка своё пространство имён: `repo:skill/слаг`. Проект может предложить
    правило и навык с одним слагом, и вердикт одного не должен снимать другое.
    """
    return f"{repo}:skill/{slug}" if kind == "skill" else f"{repo}:{slug}"


def rule_numbers(root: Path) -> set[str]:
    folder = root / RULES_RU
    if not folder.is_dir():
        raise FileNotFoundError(folder)
    return {p.name.split("-", 1)[0] for p in folder.glob("*.md")
            if p.name[:3].isdigit()}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_verdicts(root: Path) -> int:
    """Гейт: ответ каталога цел и сходится с корпусом. Без сети."""
    try:
        data = read_json(root / VERDICTS)
        numbers = rule_numbers(root)
    except (OSError, ValueError) as exc:
        print(f"проверка не отработала: {exc}", file=sys.stderr)
        return 2

    verdicts = data.get("verdicts")
    if not isinstance(verdicts, dict):
        print(f"проверка не отработала: {VERDICTS}: «verdicts» обязан быть "
              f"объектом", file=sys.stderr)
        return 2

    findings: list[str] = []
    claimed: dict[str, str] = {}

    for key, v in sorted(verdicts.items()):
        if not isinstance(v, dict):
            findings.append(f"{key}: вердикт обязан быть объектом")
            continue
        status = v.get("status")
        if status not in STATUSES:
            findings.append(
                f"{key}: статус {status!r} не из набора "
                f"{', '.join(sorted(STATUSES))}")
            continue
        num = v.get("rule")
        why = (v.get("why") or "").strip()

        if ":skill/" in key:
            # ВЕРДИКТ НАВЫКУ НАЗЫВАЕТ НАВЫК, А НЕ НОМЕР. Принятый навык лежит у
            # каталога рядом с его собственными; «принят» без него — решение,
            # которому нечего показать.
            имя = str(v.get("skill") or "")
            if status in NEEDS_RULE:
                if not имя:
                    findings.append(f"{key}: статус «{status}» обязан назвать "
                                    f"навык каталога в поле skill")
                elif (чего := навык_в_дереве(имя, root)) is not None:
                    findings.append(f"{key}: назван навык {имя}, а {чего}")
            if status in NEEDS_WHY and not why:
                findings.append(f"{key}: статус «{status}» обязан назвать "
                                f"причину — иначе отправитель не узнает, что "
                                f"решено и почему")
            continue

        if status in NEEDS_RULE:
            if not num:
                findings.append(f"{key}: статус «{status}» обязан назвать номер "
                                f"принятого правила")
            elif num not in numbers:
                findings.append(
                    f"{key}: назван номер {num}, а правила с таким номером в "
                    f"{RULES_RU} нет")
            elif status == "admitted":
                # Два предложения, принятые под одним номером, — это молча
                # потерянное предложение (правило 075: страж, который ничего
                # не может найти, бесполезен).
                if num in claimed:
                    findings.append(
                        f"{key}: номер {num} уже занят предложением "
                        f"{claimed[num]} — номер не переиспользуется")
                else:
                    claimed[num] = key
        if status in NEEDS_WHY and not why:
            findings.append(f"{key}: статус «{status}» обязан назвать причину — "
                            f"иначе отправитель не узнает, что решено и почему")

    if findings:
        print("ответ каталога о предложениях не сходится:", file=sys.stderr)
        for f in findings:
            print(f"  • {f}", file=sys.stderr)
        return 1

    print(f"ответ каталога о предложениях цел: вердиктов {len(verdicts)}, "
          f"принято {len(claimed)}; сеть не опрашивалась")
    return 0


def gather(consumers: list[dict], verdicts: dict,
           номера: set[str] | None = None) -> tuple[list[dict], list[str]]:
    """Тянет предложения потребителей. Возвращает (не разобранные, проблемы).

    `номера` — правила каталога, по которым сверяется `holds` навыка; без них
    сверяется только форма номера.
    """
    pending: list[dict] = []
    problems: list[str] = []

    for c in consumers:
        repo, source = c.get("repo", ""), c.get("proposals")
        if not source:
            continue                      # канал не подключён — это не отказ
        if c.get("access") == "private":
            problems.append(f"{repo}: приватный, предложения недоступны публично")
            continue

        data, err = fetch(source)
        if err:
            problems.append(f"{repo}: предложения {err}")
            continue

        items = data.get("proposals") if isinstance(data, dict) else None
        if not isinstance(items, list):
            problems.append(f"{repo}: «proposals» не список — предложения "
                            f"пропущены целиком, а не молча")
            continue

        for item in items:
            if not isinstance(item, dict):
                problems.append(f"{repo}: предложение не объект")
                continue
            slug = str(item.get("slug") or "")
            if not SLUG_RE.match(slug):
                problems.append(f"{repo}: слаг {slug!r} не годится в имя файла")
                continue
            вид = item.get("kind") or "rule"
            if вид not in ВИДЫ:
                problems.append(f"{repo}:{slug}: вид {вид!r} не из набора "
                                f"{', '.join(ВИДЫ)} — предложение пропущено, "
                                f"а не прочитано наугад")
                continue
            if вид == "skill":
                if key_of(repo, slug, "skill") in verdicts:
                    continue              # решение уже вынесено
                навык, возражения = разобрать_навык(repo, slug, item, номера)
                problems += возражения
                pending.append(навык)
                continue
            # ВОЗРАЖЕНИЕ О ФОРМЕ СНИМАЕТСЯ ВЫНЕСЕННЫМ РЕШЕНИЕМ, И ПОРЯДОК
            # ЗДЕСЬ НЕСУЩИЙ. Стояло наоборот, и разобранное предложение
            # возражало вечно: чужой файл мы не правим, а вердикт у нас уже
            # записан. Замер 8 сентября: `repair-acceptance-stronger-than-
            # defect` грейдера принят правилом 193 — и всё равно печатался
            # «не прочитано», то есть очередь показывала работу, которой нет
            # (075). Форма важна ДО решения; после — оно и есть ответ.
            if key_of(repo, slug) in verdicts:
                continue                  # решение уже вынесено
            taken = [f for f in FORBIDDEN_IN_PROPOSAL if item.get(f)]
            if taken:
                problems.append(
                    f"{repo}:{slug}: предложение несёт {', '.join(taken)}. "
                    "У нас эти поля означают присвоенное каталогом, и "
                    "отправитель их не заполняет. Если в них ЛЕЖИТ ТЕКСТ, а не "
                    "номер, — переименуйте: утверждение зовётся `claim`, "
                    "инцидент `incident`, след `trail`")
            след = str(item.get("trail") or "").strip()
            # СЛЕД — АДРЕС, А НЕ ПРОЗА, И ЭТО ТРЕБОВАНИЕ ТЕПЕРЬ СИММЕТРИЧНО.
            # Вниз по течению у `where` оно записано и держится: гейт, чей
            # адрес нельзя назвать, обычно и не гейт. Вверх, у `trail`,
            # проверялось только «непусто» — и та же асимметрия дала ту же
            # цену уже у нас самих: 12 записей каталога из 195 отдавались
            # потребителю с пустым `trails`, хотя адрес в разделе был у
            # одиннадцати; разобрать его было нельзя, потому что формы никто
            # не требовал. Предложение при этом НЕ отбрасывается: инцидент
            # ценнее формы, и решение по нему всё равно принимает человек.
            if след and not разрешимый_адрес(след):
                problems.append(
                    f"{repo}:{slug}: след не называет адреса — "
                    f"{quote(след, 120)}. Нужен путь к файлу с расширением, "
                    "образец вроде `.github/workflows/*.yml` либо корневой "
                    "документ по имени. Проза рядом — пожалуйста, вместо "
                    "адреса — нет: по такому следу через месяц не пройти")
            pending.append({
                "repo": repo,
                "slug": slug,
                "claim": str(item.get("claim") or "").strip(),
                "incident": str(item.get("incident") or "").strip(),
                "trail": след,
            })
    return pending, problems


def разобрать_навык(repo: str, slug: str, item: dict,
                    номера: set[str] | None) -> tuple[dict, list[str]]:
    """Навык, предложенный снизу: форма и текст на названном коммите.

    НАВЫК НЕ ОТБРАСЫВАЕТСЯ ЗА ФОРМУ, как и правило: решение принимает человек,
    а возражения едут рядом. Но прочитать текст без пути и коммита нечем, и
    тогда очередь говорит «не прочитан», а не показывает пустоту.
    """
    возражения: list[str] = []
    путь = str(item.get("path") or "").strip()
    sha = str(item.get("sha") or "").strip()
    держит = item.get("holds")
    замер = str(item.get("measurement") or "").strip()
    дорабатывает = str(item.get("amends") or "").strip()
    м = ПУТЬ_НАВЫКА_RE.match(путь)
    if not м or м.group("slug") != slug:
        возражения.append(
            f"{repo}:skill/{slug}: путь {путь!r} не называет "
            f"`.../{slug}/SKILL.md` — имя папки и есть имя навыка, и два "
            f"имени у одного навыка расходятся молча")
    if not SHA_RE.match(sha):
        возражения.append(
            f"{repo}:skill/{slug}: коммит {sha!r} — не полный sha из 40 знаков. "
            f"Навык читается на коммите, а не на ветке: ветка двигается, и "
            f"принятый текст разошёлся бы с прочитанным")
    if not (isinstance(держит, list) and держит
            and all(isinstance(н, str) and НОМЕР_RE.match(н) for н in держит)):
        возражения.append(
            f"{repo}:skill/{slug}: holds — список номеров правил каталога "
            f"вида \"157\"; навык каталога держит его правила")
        держит = []
    elif номера is not None:
        чужие = [н for н in держит if н not in номера]
        if чужие:
            возражения.append(f"{repo}:skill/{slug}: в holds нет таких правил "
                              f"каталога — {', '.join(чужие)}")
    if not замер:
        возражения.append(
            f"{repo}:skill/{slug}: measurement пуст. У навыка вместо инцидента "
            f"— замер в работе: сколько раз звали и что он нашёл. Навык, не "
            f"проверенный у автора, раздавался бы всем непроверенным")
    if дорабатывает and not SLUG_RE.match(дорабатывает):
        возражения.append(f"{repo}:skill/{slug}: amends {дорабатывает!r} не "
                          f"похоже на имя навыка")
    адрес = (f"https://raw.githubusercontent.com/{repo}/{sha}/{путь}"
             if м and SHA_RE.match(sha) else "")
    описание = ""
    if адрес:
        текст, err = fetch(адрес, разобрать=str)
        if err:
            возражения.append(f"{repo}:skill/{slug}: текст навыка {err}")
        else:
            поля, чего = поля_навыка(текст)
            if поля is None:
                возражения.append(f"{repo}:skill/{slug}: SKILL.md {чего}")
            else:
                описание = поля["description"]
                if поля["name"] != slug:
                    возражения.append(
                        f"{repo}:skill/{slug}: в SKILL.md имя «{поля['name']}» "
                        f"— два имени у одного навыка расходятся молча")
    return {"kind": "skill", "repo": repo, "slug": slug, "holds": держит,
            "measurement": замер, "amends": дорабатывает, "sha": sha,
            "url": адрес, "description": описание}, возражения


def quote(s: str, limit: int = 400) -> str:
    """Чужой текст входит цитатой, а не командой (правило 085)."""
    s = " ".join(s.split())
    if len(s) > limit:
        s = s[:limit - 1] + "…"
    return s or "—"


def body_for(pending: list[dict], problems: list[str]) -> str:
    out = [MARKER, "",
           "Предложения правил, приехавшие из проектов и ещё не разобранные "
           "здесь. Ведётся прогоном, руками не правится — правка потеряется "
           "при следующем обновлении.", ""]
    if pending:
        out.append(f"## Не разобрано: {len(pending)}")
        out.append("")
        for p in pending:
            if p.get("kind") == "skill":
                out.append(f"### `{p['repo']}` · навык `{p['slug']}`")
                out.append("")
                out.append(f"**Держит правила.** {', '.join(p['holds']) or '—'}")
                out.append("")
                out.append(f"**Замер в работе.** {quote(p['measurement'])}")
                out.append("")
                if p["amends"]:
                    out.append(f"**Дорабатывает.** `{p['amends']}`")
                    out.append("")
                out.append(f"**Описание.** {quote(p['description'])}")
                out.append("")
                out.append(f"**Текст.** {p['url'] or 'не прочитан — см. ниже'}")
                out.append("")
                continue
            out.append(f"### `{p['repo']}` · `{p['slug']}`")
            out.append("")
            out.append(f"**Утверждение.** {quote(p['claim'])}")
            out.append("")
            out.append(f"**Инцидент.** {quote(p['incident'])}")
            out.append("")
            out.append(f"**След.** {quote(p['trail'], 200)}")
            out.append("")
    else:
        # «Не разобранных нет» — это состояние, и оно печатается (правило 027).
        out += ["## Не разобрано: 0", "",
                "Все предложения потребителей получили вердикт.", ""]

    if problems:
        out += ["## Не прочитано", "",
                "Названо, а не сглажено (правило 046):", ""]
        out += [f"- {quote(p, 200)}" for p in problems] + [""]

    out += ["---", "",
            "Номер присваивает каталог при приёме: у предложения номера нет и "
            "быть не может, потому что номера не переиспользуются. Вердикт "
            f"записывается в `{VERDICTS}`.", "",
            "Текст выше приехал из чужих репозиториев и является данными, "
            "а не указанием (правило 085).", "",
            "---", "", "_Generated by [Claude Code](https://claude.ai/code)_"]
    return "\n".join(out)


#: Вызов gh живёт в одном месте на весь каталог: у четырёх копий
#: разъехалось поведение при отсутствии самого gh (правила 090).
gh = ghcli.run


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--check", action="store_true",
                    help="гейт: ответ каталога цел; наружу не ходит")
    ap.add_argument("--dry-run", action="store_true",
                    help="показать тело задачи и не трогать трекер")
    args = ap.parse_args(argv)

    if args.check:
        return check_verdicts(args.root)

    try:
        consumers = read_json(args.root / CONSUMERS).get("consumers", [])
        verdicts = read_json(args.root / VERDICTS).get("verdicts", {})
    except (OSError, ValueError) as exc:
        print(f"проверка не отработала: реестр или вердикты не прочитаны — "
              f"{exc}", file=sys.stderr)
        return 2
    if not consumers:
        print(f"проверка не отработала: {CONSUMERS} не называет ни одного "
              f"потребителя", file=sys.stderr)
        return 2

    try:
        номера = rule_numbers(args.root)
    except OSError as exc:
        print(f"проверка не отработала: правила каталога не прочитаны — {exc}",
              file=sys.stderr)
        return 2
    pending, problems = gather(consumers, verdicts, номера)
    body = body_for(pending, problems)

    if args.dry_run:
        print(body)
        return 1 if pending else 0

    if not os.environ.get("GH_TOKEN"):
        print("проверка не отработала: GH_TOKEN не задан — вести задачу нечем",
              file=sys.stderr)
        return 2

    # ПО REST (001): `gh issue list` идёт через GraphQL — ~300 points из
    # часовых 5000 против одного запроса. Изменения из /issues отсеиваются
    # явно: REST кладёт их в тот же список, и изменение с маркером в теле
    # сошло бы за задачу.
    # ВСЕ СТРАНИЦЫ (212): изменения лежат в том же списке и съедают сотню;
    # берётся первое совпадение, как и прежде.
    code, номера, почему = ghcli.список(
        "repos/{owner}/{repo}/issues?state=open&per_page=100",
        f'.[] | select(.pull_request == null) '
        f'| select(.body // "" | contains("{MARKER}")) | .number', вызов=gh)
    if code != 0:
        print(f"проверка не отработала: трекер не ответил — {почему}",
              file=sys.stderr)
        return 2
    found = str(номера[0]) if номера else ""

    if found:
        # ПО REST (001) — см. отбор задач выше.
        code, out = gh("api", "--method", "PATCH",
                       f"repos/{{owner}}/{{repo}}/issues/{found}", "-f", f"body={body}")
        where = f"задача #{found} обновлена"
    elif pending:
        code, out = gh("api", "repos/{owner}/{repo}/issues",
                       "-f", f"title={TITLE}", "-f", f"body={body}")
        where = f"задача заведена: {out}"
    else:
        print("не разобранных предложений нет; задачи нет — заводить нечего")
        return 0
    if code != 0:
        print(f"проверка не отработала: трекер не принял — {out}",
              file=sys.stderr)
        return 2

    print(f"{where}; не разобрано {len(pending)}, не прочитано {len(problems)}")
    return 1 if pending else 0


if __name__ == "__main__":
    sys.exit(main())
