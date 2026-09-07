#!/usr/bin/env python3
"""Гейт перед пушем: один запуск вместо чек-листа в документации.

Реализует правила каталога:
  002 — правило без механизма не соблюдается: чек-лист переписан в команду;
  039 — у проверки три исхода: чисто · есть находки · инструмент не отработал;
  075 — шаг, не нашедший предмета проверки, падает, а не зеленеет на пустом входе;
  068 — секреты ищутся по списку разрешённого, а не запрещённого;
  100 — у каждого шага свой предел времени.

Правьте под себя: список шагов внизу — единственное место, которое обычно
меняется. Всё остальное — обвязка, отвечающая за исходы и вывод.

Запуск:  python preflight.py            # все шаги
         python preflight.py --only tests
         python preflight.py --list
Коды:    0 всё чисто · 1 есть находки · 2 шаг не отработал
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# --- Правило 068: перечисляем РАЗРЕШЁННОЕ, а не запрещённое -----------------
# Список запрещённого не переживёт появления нового поля — а именно так секрет
# и утекает. Здесь наоборот: перечислены имена файлов, которым можно содержать
# что-то похожее на ключ (примеры, фикстуры, сам этот файл).
SECRET_ALLOWLIST = (
    "preflight.py",
    "*/tests/fixtures/*",
    "*.example",
    "*.md",
)
# Что считаем похожим на секрет. Дополняйте — но каждое добавление есть
# решение, и его видно в истории файла.
SECRET_PATTERNS = (
    (re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{12,}"), "литерал ключа"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "приватный ключ"),
    (re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b"), "ключ облачного провайдера"),
)
SCAN_SUFFIXES = (".py", ".js", ".ts", ".json", ".yml", ".yaml", ".toml", ".sh", ".env")

# Правило 100: предел времени у каждого шага, а не один на весь прогон.
DEFAULT_TIMEOUT_S = 600

OK, FINDINGS, BROKEN = 0, 1, 2


@dataclass
class Step:
    name: str
    argv: list[str]
    #: Файлы, без которых шаг бессмыслен. Пусто — шаг всегда применим.
    requires_files: tuple[str, ...] = ()
    timeout_s: int = DEFAULT_TIMEOUT_S
    #: Шаг, который не блокирует пуш (правило 051: предупреждают о вероятном).
    advisory: bool = False


@dataclass
class Result:
    step: str
    outcome: int
    detail: str = ""
    seconds: float = 0.0
    lines: list[str] = field(default_factory=list)


def _tracked_files() -> list[Path]:
    """Файлы под контролем версий. Пустой ответ — повод упасть (правило 075)."""
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=60
    )
    if out.returncode != 0:
        raise RuntimeError(f"git ls-files не отработал: {out.stderr.strip()}")
    names = [n for n in out.stdout.split("\0") if n]
    if not names:
        raise RuntimeError("git ls-files вернул пустой список — репозиторий пуст или мы не в нём")
    return [ROOT / n for n in names]


def check_secrets() -> Result:
    """Правило 068: allowlist. Правило 075: пустой вход — ошибка входа."""
    t0 = time.monotonic()
    try:
        files = _tracked_files()
    except Exception as exc:  # noqa: BLE001 — исход «не отработал» отдельный
        return Result("secrets", BROKEN, str(exc), time.monotonic() - t0)

    scanned, hits = 0, []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if any(fnmatch.fnmatch(rel, pat) for pat in SECRET_ALLOWLIST):
            continue
        if path.suffix not in SCAN_SUFFIXES or not path.is_file():
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return Result("secrets", BROKEN, f"{rel}: {exc}", time.monotonic() - t0)
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, what in SECRET_PATTERNS:
                if pattern.search(line):
                    hits.append(f"{rel}:{lineno}: {what}")

    if scanned == 0:
        # Правило 075: нечего проверять — это не «чисто», это сломанный вход.
        return Result("secrets", BROKEN, "не найдено ни одного файла для проверки", time.monotonic() - t0)
    if hits:
        return Result("secrets", FINDINGS, f"{len(hits)} совпадений", time.monotonic() - t0, hits)
    return Result("secrets", OK, f"проверено файлов: {scanned}", time.monotonic() - t0)


#: Семейства подкоманд `gh`, которые идут через GraphQL. Одна операция там
#: стоит ~300 points из часовых 5000, REST — один запрос (правило 001).
GH_GRAPHQL = ("issue", "pr", "project", "search")
#: Строка, где команда ВЫЗЫВАЕТСЯ, а не упоминается в прозе.
GH_CALL = re.compile(r"^\s*(?:[\w.]+=\$\()?\s*gh\s+([a-z-]+)\b")
#: Закрытый список операций без REST-эквивалента. Требование списка — из самого
#: правила 001: каждый такой случай называется поимённо.
TRANSPORT_ALLOW = ROOT / ".rules" / "transport.json"


def check_transport() -> Result:
    """Правило 001: к GitHub ходят по REST; GraphQL — только поимённо.

    ПОЧЕМУ ЭТО ЕДЕТ ПОТРЕБИТЕЛЮ. Инцидент был у каталога, но предмет общий:
    квота у площадки одна на учётную запись, и конвейер, который по REST
    укладывается в проценты часового бюджета, по GraphQL в час не помещается
    ФИЗИЧЕСКИ. У каталога 7 сентября исчерпание уронило дежурного и заморозило
    очередь целиком, а ответ «всё переведено на REST» при этом стоял в
    привязках и был ложен: держался он прозой, и разошёлся с деревом молча.

    Здесь тот же гейт, что у каталога, но без его дерева: ищет вызовы в
    `*.py` и в `.github/workflows/*.yml`. Список исключений опционален — если
    файла нет, законных исключений нет, и это верно по построению: правило
    требует называть их поимённо, а не подразумевать.
    """
    t0 = time.monotonic()
    try:
        allow = set()
        if TRANSPORT_ALLOW.exists():
            data = json.loads(TRANSPORT_ALLOW.read_text(encoding="utf-8"))
            allow = {и.get("where", "") for и in data.get("allowed", [])}
    except (OSError, ValueError) as exc:
        return Result("transport", BROKEN, f"{TRANSPORT_ALLOW.name}: {exc}",
                      time.monotonic() - t0)

    hits, scanned = [], 0
    for path in sorted(ROOT.rglob("*.py")) + sorted(
            (ROOT / ".github" / "workflows").glob("*.yml")):
        if ".git" in path.parts or not path.is_file():
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return Result("transport", BROKEN, f"{path}: {exc}", time.monotonic() - t0)
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(text.splitlines(), 1):
            # Комментарий — это упоминание, а не вызов: находка о нём была бы
            # находкой о форме текста, а не о транспорте.
            if line.lstrip().startswith("#"):
                continue
            m = GH_CALL.search(line)
            if m and m.group(1) in GH_GRAPHQL and f"{rel}:{lineno}" not in allow:
                hits.append(f"{rel}:{lineno}: gh {m.group(1)} — через GraphQL")

    if scanned == 0:
        return Result("transport", BROKEN, "не найдено ни одного файла для проверки",
                      time.monotonic() - t0)
    if hits:
        return Result("transport", FINDINGS,
                      f"{len(hits)} вызовов мимо REST", time.monotonic() - t0, hits)
    return Result("transport", OK, f"проверено файлов: {scanned}", time.monotonic() - t0)


#: Откуда берётся выгрузка каталога. Читается ЛОКАЛЬНАЯ копия, если она есть:
#: ходить в сеть из прогона перед толчком значит менять его цену и надёжность
#: на удобство. Нет копии — шаг честно говорит, что не отработал.
CATALOGUE_EXPORT = ROOT / ".rules" / "catalogue-rules.json"


def check_trails() -> Result:
    """Правило 185: следы каталога, ведущие в МОИ документы, разрешаются.

    ПОЧЕМУ ЭТО ПРОВЕРЯЕТ ПОТРЕБИТЕЛЬ, А НЕ КАТАЛОГ. След указывает на документ
    в ЭТОМ дереве — значит только здесь его и можно разрешить: у прогона
    каталога чужого дерева нет. И правит его тоже эта сторона: тот, кто
    переименовал раздел, знает о переименовании в тот же миг, а автор ссылки не
    узнает никогда, пока не пойдёт по следу.

    ЗАМЕР, ИЗ КОТОРОГО ЭТО ВЫРОСЛО (7 сентября 2026, каталог против грейдера):
    71 след-документ, два сгнили молча — раздел переименовали, след остался.
    А в английском дереве каталога разрешались ТРИ из семидесяти одного: там
    название раздела перевели вместе с текстом записи.

    ЧТО СЧИТАЕТСЯ НАХОДКОЙ. Файла нет либо раздел не найден в его тексте.
    Раздел ищется подстрокой, а не разбором заголовков: у документа бывает
    «§ Что прощается / § Что не прощается» — два адреса в одной строке, и
    разбор заголовками отверг бы законную форму (051).
    """
    t0 = time.monotonic()
    if not CATALOGUE_EXPORT.exists():
        return Result("trails", BROKEN,
                      f"нет {CATALOGUE_EXPORT.relative_to(ROOT)} — выгрузку каталога "
                      "кладёт сюда шаг синхронизации; без неё проверять нечего",
                      time.monotonic() - t0)
    try:
        данные = json.loads(CATALOGUE_EXPORT.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return Result("trails", BROKEN, f"{CATALOGUE_EXPORT.name}: {exc}",
                      time.monotonic() - t0)

    # СВОЁ ИМЯ ПОТРЕБИТЕЛЬ ЗНАЕТ САМ, А НЕ УЗНАЁТ ИЗ ВЫГРУЗКИ. Выгрузка одна
    # на всех, и ключа «чей это прогон» в ней нет по построению. Имя лежит в
    # СВОЁМ ответе — .rules/bindings.json, поле project, — и это единственное
    # место, где оно и должно быть: иначе две копии имени разошлись бы молча.
    ответ = ROOT / ".rules" / "bindings.json"
    if not ответ.exists():
        return Result("trails", BROKEN,
                      f"нет {ответ.relative_to(ROOT)} — своё имя проекта берётся "
                      "оттуда, и без него шаг проверял бы чужие следы",
                      time.monotonic() - t0)
    try:
        моё = (json.loads(ответ.read_text(encoding="utf-8")).get("project") or "").strip()
    except (OSError, ValueError) as exc:
        return Result("trails", BROKEN, f"{ответ.name}: {exc}", time.monotonic() - t0)
    if not моё:
        return Result("trails", BROKEN,
                      f"в {ответ.relative_to(ROOT)} пусто поле project — некому "
                      "сказать, какие следы мои",
                      time.monotonic() - t0)

    hits, всего = [], 0
    for правило in данные.get("rules") or []:
        for след in правило.get("trails") or []:
            if след.get("repo") != моё or "doc" not in след:
                continue
            всего += 1
            цель = ROOT / след["doc"]
            if not цель.is_file():
                hits.append(f"{правило.get('id')}: нет {след['doc']}")
                continue
            раздел = (след.get("section") or "").strip()
            if раздел and раздел not in цель.read_text(encoding="utf-8", errors="replace"):
                hits.append(f"{правило.get('id')}: {след['doc']} — нет «{раздел}»")

    if всего == 0:
        return Result("trails", OK, "следов каталога в мои документы нет",
                      time.monotonic() - t0)
    if hits:
        return Result("trails", FINDINGS,
                      f"{len(hits)} из {всего} следов не разрешаются",
                      time.monotonic() - t0, hits)
    return Result("trails", OK, f"следов проверено: {всего}", time.monotonic() - t0)


def check_contracts() -> Result:
    """Правило 157: номера контрактов каталога сверяются со своим ответом.

    ПОЧЕМУ СВЕРЯЕТСЯ ЗДЕСЬ, А НЕ ПРИСЫЛАЕТСЯ ОТТУДА. Каталог ПУБЛИКУЕТ свои
    номера — блок `contracts` в выгрузке. Значит письма не нужно: достаточно
    прочитать то, что уже лежит рядом, и сравнить со своим. Механизм, который
    ждёт уведомления, ломается вместе с каналом уведомления; механизм, который
    сверяет два файла на диске, не ломается никак.

    ЧТО ЗНАЧИТ РАСХОЖДЕНИЕ. Выгрузка сменила формат — значит ответы, собранные
    по прежнему, отвечают на другой вопрос: записи остаются валидными, означая
    уже другое. Правило 157 требует не «поправить номер», а ПЕРЕЧИТАТЬ правила
    и ответить заново; номер проставляется последним, как подпись под работой.

    ЗАМЕР, ИЗ КОТОРОГО ЭТО ВЫРОСЛО (7 сентября 2026): выгрузка каталога
    поднялась 1.4 → 1.5, а в ответе одного из потребителей прозой стояло
    «выгрузка правил каталога — 1.2» — отставание на три подъёма, невидимое
    обеим сторонам. Издатель считал, что объявил; потребитель — что его файл
    валиден.
    """
    t0 = time.monotonic()
    выгрузка, ответ = CATALOGUE_EXPORT, ROOT / ".rules" / "bindings.json"
    for путь in (выгрузка, ответ):
        if not путь.exists():
            return Result("contracts", BROKEN,
                          f"нет {путь.relative_to(ROOT)} — сверять номера не с чем",
                          time.monotonic() - t0)
    try:
        их = (json.loads(выгрузка.read_text(encoding="utf-8")).get("contracts") or {})
        мой = json.loads(ответ.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return Result("contracts", BROKEN, str(exc), time.monotonic() - t0)

    издано = (их.get("export") or "").strip()
    if not издано:
        return Result("contracts", BROKEN,
                      f"{выгрузка.name} не называет contracts.export — "
                      "каталог не объявил версию, с которой сверяться",
                      time.monotonic() - t0)
    моё = (мой.get("answers_to") or "").strip()
    if not моё:
        return Result("contracts", FINDINGS,
                      f"ответ не называет answers_to; у каталога выгрузка {издано}",
                      time.monotonic() - t0,
                      ["Проставьте answers_to — версию выгрузки, по которой "
                       "построены ответы. Без неё отставание не заметит никто."])
    if моё != издано:
        return Result("contracts", FINDINGS,
                      f"ответ построен на выгрузке {моё}, у каталога {издано}",
                      time.monotonic() - t0,
                      [f"Перечитайте правила по выгрузке {издано} и ответьте заново: "
                       "записи остаются валидными, означая уже другое (157).",
                       "Номер answers_to проставляется последним — подписью под "
                       "перечитыванием, а не вместо него."])
    return Result("contracts", OK, f"выгрузка {издано} — ответ построен на ней",
                  time.monotonic() - t0)


def run_step(step: Step) -> Result:
    t0 = time.monotonic()
    if step.requires_files and not any(ROOT.glob(p) for p in step.requires_files):
        return Result(step.name, BROKEN, f"не найдено: {', '.join(step.requires_files)}", 0.0)
    exe = shutil.which(step.argv[0])
    if exe is None:
        # Правило 039: «инструмента нет» — третий исход, а не тихий успех.
        return Result(step.name, BROKEN, f"инструмент не установлен: {step.argv[0]}", 0.0)
    try:
        proc = subprocess.run(
            step.argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=step.timeout_s
        )
    except subprocess.TimeoutExpired:
        return Result(step.name, BROKEN, f"предел времени {step.timeout_s} с", time.monotonic() - t0)
    tail = (proc.stdout + proc.stderr).strip().splitlines()
    outcome = OK if proc.returncode == 0 else FINDINGS
    return Result(step.name, outcome, f"код {proc.returncode}", time.monotonic() - t0, tail[-40:])


# --- Правьте здесь ----------------------------------------------------------
# Порядок — от дешёвого к дорогому: быстрый отказ экономит время.
STEPS: list[Step] = [
    Step("format", ["ruff", "format", "--check", "."]),
    Step("lint", ["ruff", "check", "."]),
    Step("types", ["mypy", "."], advisory=True),
    Step("tests", ["pytest", "-q"], requires_files=("tests",), timeout_s=1800),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", action="append", default=[], help="запустить только названные шаги")
    ap.add_argument("--list", action="store_true", help="показать шаги и выйти")
    args = ap.parse_args()

    names = ["secrets"] + [s.name for s in STEPS]
    if args.list:
        print("\n".join(names))
        return OK

    unknown = [n for n in args.only if n not in names]
    if unknown:
        print(f"неизвестные шаги: {', '.join(unknown)}", file=sys.stderr)
        return BROKEN

    selected = set(args.only) or set(names)
    results: list[Result] = []
    if "secrets" in selected:
        results.append(check_secrets())
        results.append(check_contracts())
        results.append(check_transport())
        results.append(check_trails())
    results.extend(run_step(s) for s in STEPS if s.name in selected)

    print()
    worst = OK
    advisory = {s.name for s in STEPS if s.advisory}
    for r in results:
        mark = {OK: "ok      ", FINDINGS: "НАХОДКИ ", BROKEN: "НЕ РАБОТ"}[r.outcome]
        note = " (не блокирует)" if r.outcome and r.step in advisory else ""
        print(f"{mark} {r.step:<10} {r.seconds:6.1f}s  {r.detail}{note}")
        for line in r.lines:
            print(f"           {line}")
        if r.step not in advisory:
            worst = max(worst, r.outcome)

    print()
    if worst == OK:
        print("чисто — можно пушить")
    elif worst == FINDINGS:
        print("есть находки — чинить")
    else:
        # Правило 039: это не «всё хорошо» и не «всё плохо», это третье.
        print("часть проверок не отработала — о предмете проверки мы не знаем ничего")
    return worst


if __name__ == "__main__":
    sys.exit(main())
