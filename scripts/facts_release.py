#!/usr/bin/env python3
"""Готовит выпуск договора фактов семьи: тег ``facts-v<номер>`` и файлы для страницы.

ЧТО ВЫПУСКАЕТСЯ. Не каталог — его выпуски ``vX.Y.0`` ставит ``release.yml``, —
а ДОГОВОР фактов: схема, проза, проверка, номер и образец. С 2.0 договор
держит каталог (#843); выпуски ``facts-v1.x`` остались у витрины как история.
Издатель прибивает проверку к тегу, а не к ветке и не к коммиту: живая
``main`` сменила бы требование под ним молча, а коммит не говорит, какой это
договор.

ЭТОТ ШАГ НИЧЕГО НЕ ПУБЛИКУЕТ. Он собирает пять файлов плоско в один каталог —
ровно так они лягут у издателя, — и проверяет их ТАМ, отдельным
интерпретатором с ``-I``: образец обязан отвечать договору (исход 0), номер —
сходиться с заголовками. Выпуск, чья проверка у издателя не запускается, хуже
отсутствующего: его прибьют и получат трассировку. Тег и страницу ставит
прогон ``facts-release.yml`` — кнопкой и токеном человека (131), а не этим
скриптом.

ТЕГ НЕ ПЕРЕСТАВЛЯЕТСЯ. Стоящий тег — отказ, а не перезапись: выпуск, на
который уже прибились, меняться не вправе. Сверка точная, а не по шаблону —
``git tag --list`` понимает образцы, и ``facts-v1.4.*`` ответил бы «есть» на
тег, которого нет.

Перенесено из витрины вместе с договором (ArtVsMark/ArtVsMark:
scripts/facts_release.py); выпуск у неё прекращается письмом из #845.

Реализует правила каталога:
  035 — номер живёт в одном месте, тег выводится из него, а не вписывается;
  131 — тег несёт личность человека: ставит его кнопка с токеном владельца;
  039 — три исхода: собран · выпускать нельзя · шаг не отработал.

Запуск::

    python scripts/facts_release.py --dist КАТАЛОГ --notes ФАЙЛ
    python scripts/facts_release.py --selftest

Исходы: 0 — выпуск собран и проверен; 1 — выпускать нельзя: номер разошёлся с
заголовками, тег уже стоит или собранная проверка у издателя не отработала бы
— причина названа; 2 — шаг не отработал: файл договора или история тегов не
прочитаны.
"""

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

import check_facts
import proc

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Что лежит на странице выпуска — плоско, под своими именами. Порядок — порядок
#: чтения издателем: проза, схема, номер, проверка, образец.
ASSETS = (
    check_facts.CONTRACT_PATH,
    check_facts.SCHEMA_PATH,
    check_facts.VERSION_PATH,
    pathlib.Path(check_facts.__file__).resolve(),
    check_facts.EXAMPLE_PATH,
)


def tag_for(number: str) -> str:
    """Тег выпуска договора: ``facts-v`` и номер из ``export/facts/facts.version``."""
    return f"facts-v{check_facts.contract_version(number)}"


def listed(out: str, tag: str) -> bool:
    """Есть ли ``tag`` среди строк вывода ``git tag --list`` — целиком, а не образцом."""
    return tag in out.split()


def tag_exists(tag: str) -> bool:
    """Стоит ли такой тег — точной сверкой, а не по образцу."""
    out = proc.run(
        ["git", "tag", "--list", tag],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    ).stdout
    return listed(out, tag)


def assemble(dist: pathlib.Path) -> list[pathlib.Path]:
    """Файлы выпуска плоско в ``dist``. Отдаёт пути копий."""
    dist.mkdir(parents=True, exist_ok=True)
    return [pathlib.Path(shutil.copy(source, dist / source.name)) for source in ASSETS]


def verify(dist: pathlib.Path, repo: str) -> list[str]:
    """Собранный выпуск у издателя: образец — 0, номер против заголовков — 0.

    Запуск отдельным интерпретатором с ``-I`` в каталоге выпуска: дерево
    каталога не подхватится — ровно положение издателя.
    """
    found: list[str] = []
    runs = (
        ("образец отвечает договору", ["--file", check_facts.EXAMPLE_PATH.name, "--repo", repo]),
        ("номер сходится с заголовками", ["--contract"]),
    )
    for name, args in runs:
        run = proc.run(
            [sys.executable, "-I", pathlib.Path(check_facts.__file__).name, *args],
            cwd=dist,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=600,
        )
        if run.returncode != 0:
            last = (
                run.stderr.strip().splitlines() or run.stdout.strip().splitlines() or ["вывода нет"]
            )[-1]
            found.append(
                f"у издателя не отработало бы: {name} — исход {run.returncode}, "
                f"последняя строка: {last}"
            )
    return found


def step_files(step: str) -> list[str]:
    """Имена файлов, которые шаг для CI скачивает со страницы выпуска (строка ``for f in``)."""
    for line in step.splitlines():
        words = line.split()
        if words[:2] == ["for", "f"] and "in" in words:
            return [
                word.rstrip(";")
                for word in words[words.index("in") + 1 :]
                if word not in (";", "do")
            ]
    return []


def notes(number: str, repo: str) -> str:
    """Текст страницы выпуска: что приложено, как запустить, шаг для CI, где источник."""
    tag = tag_for(number)
    step = check_facts.ci_step(check_facts.CONTRACT_PATH.read_text(encoding="utf-8")) or ""
    tree = f"https://github.com/{repo}/blob/{tag}"
    # не проза: номер версии «мажор.минор.патч».
    series = ".".join(number.split(".")[:2])
    return "\n".join(
        [
            f"Договор фактов семьи, номер **{number}**: издатель пишет в "
            f'`facts.json` поле `"schema": "{series}"`.',
            "",
            "Приложено — пять файлов, класть в один каталог:",
            "",
            *(f"- `{source.name}`" for source in ASSETS),
            "",
            "Проверить свой файл — тем же кодом, что судит его читатель:",
            "",
            "```",
            "python check_facts.py --file .github/badges/facts.json --repo владелец/имя",
            "```",
            "",
            "Исход `0` — договору отвечает, `1` — расхождения названы, `2` — проверка не "
            "отработала; предупреждения `⚠` кода не меняют.",
            "",
            "Шаг для CI — вставить в прогон, публикующий `facts.json`, перед публикацией:",
            "",
            step,
            "",
            f"Источник по тегу — [`export/facts/facts-contract.md`]({tree}/export/facts/facts-contract.md); "
            f"как договор меняется — там же, раздел «Как контракт меняется».",
        ]
    )


def selftest() -> int:
    """Обе стороны (140): собранный выпуск проверяется, порча и стоящий тег — отказ."""
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415
    import tempfile  # noqa: PLC0415

    broken: list[str] = []
    repo = json.loads(check_facts.EXAMPLE_PATH.read_text(encoding="utf-8"))["repo"]

    if tag_for("1.4.0") != "facts-v1.4.0":
        broken.append(f"тег: {tag_for('1.4.0')!r} вместо facts-v1.4.0")
    for bad in ("1.4", "v1.4.0"):
        try:
            tag_for(bad)
            broken.append(f"тег: номер «{bad}» принят")
        except ValueError:
            pass
    print("  да  — тег: facts-v и три числа, иная форма номера — отказ")

    # Шаг для CI издателя: скачивает только то, что лежит в выпуске (иначе у
    # издателя curl упадёт на 404), прибит к тегу текущего номера и попадает
    # на страницу выпуска — из прозы, а не копией.
    number = check_facts.contract_version(check_facts.VERSION_PATH.read_text(encoding="utf-8"))
    step = check_facts.ci_step(check_facts.CONTRACT_PATH.read_text(encoding="utf-8")) or ""
    wanted = step_files(step)
    shipped = {source.name for source in ASSETS}
    if not wanted or set(wanted) - shipped:
        broken.append(f"шаг для CI скачивает {wanted}, а в выпуске {sorted(shipped)}")
    if f"FACTS_CONTRACT: {tag_for(number)}" not in step or step not in notes(number, repo):
        broken.append("шаг для CI не прибит к текущему тегу или не попал на страницу")
    if step_files("    for f in a.py b.json; do") != ["a.py", "b.json"] or step_files("x") != []:
        broken.append("разбор строки for f in в шаге для CI неверен")
    print(
        f"  {'да ' if wanted and not set(wanted) - shipped else 'НЕТ'} — шаг для CI: "
        f"скачивает {len(wanted)} файла из выпуска, прибит к {tag_for(number)}"
    )

    with tempfile.TemporaryDirectory(dir=os.environ.get("RUNNER_TEMP")) as tmp:
        dist = pathlib.Path(tmp) / "dist"
        copied = assemble(dist)
        if sorted(p.name for p in copied) != sorted(p.name for p in ASSETS) or len(copied) != 5:
            broken.append(f"сборка: в каталоге {sorted(p.name for p in copied)}")
        said = verify(dist, repo)
        if said:
            broken.append(f"сборка из дерева не проверилась у «издателя»: {said}")
        print(
            f"  {'да ' if not said else 'НЕТ'} — сборка из дерева: пять файлов, у издателя исход 0"
        )

        # Порча — обе проверки обязаны её заметить: образец не отвечает
        # договору, проза разошлась с номером.
        (dist / check_facts.EXAMPLE_PATH.name).write_text(
            json.dumps({"schema": "1.4"}), encoding="utf-8"
        )
        prose = dist / check_facts.CONTRACT_PATH.name
        prose.write_text(
            prose.read_text(encoding="utf-8").replace(
                "## Единые требования · договор", "## Требования · договор"
            ),
            encoding="utf-8",
        )
        said = verify(dist, repo)
        if len(said) != 2:
            broken.append(f"порча выпуска: ждали два отказа, вышло {said}")
        print(f"  {'да ' if len(said) == 2 else 'НЕТ'} — порча выпуска: оба отказа названы")

    for shown, asked, expected in (
        ("facts-v1.4.0\n", "facts-v1.4.0", True),
        ("facts-v1.4.0\n", "facts-v1.4.*", False),
        ("facts-v1.4.10\n", "facts-v1.4.1", False),
    ):
        got = listed(shown, asked)
        if got is not expected:
            broken.append(f"сверка тега «{asked}» среди «{shown.strip()}»: {got}")
    print("  да  — сверка тега точная, а не по образцу")

    # Живой путь main — обе стороны отказа: стоящий тег — 1, нечитаемый
    # договор — 2. Сравнение прямо с main(): так его считает храповик
    # непрогнанных исходов (check_mechanisms).
    saved_exists, saved_assets, saved_argv = tag_exists, ASSETS, sys.argv
    before = len(broken)
    with tempfile.TemporaryDirectory(dir=os.environ.get("RUNNER_TEMP")) as tmp:
        sys.argv = ["facts_release.py", "--dist", f"{tmp}/dist", "--notes", f"{tmp}/notes.md"]
        try:
            with (
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                globals()["tag_exists"] = lambda _tag: True
                if main() != 1:
                    broken.append("стоящий тег не отвергнут — выпуск переставил бы его")
                globals()["tag_exists"] = lambda _tag: False
                globals()["ASSETS"] = (*saved_assets, pathlib.Path(tmp) / "нет-такого.md")
                if main() != 2:
                    broken.append("нечитаемый файл договора не назван «не отработал»")
                globals()["ASSETS"] = saved_assets
                if main() != 0:
                    broken.append("исправный выпуск не собран")
                if "check_facts.py --file" not in pathlib.Path(f"{tmp}/notes.md").read_text(
                    encoding="utf-8"
                ):
                    broken.append("текст страницы не говорит, как запустить проверку")
        finally:
            globals()["tag_exists"], globals()["ASSETS"] = saved_exists, saved_assets
            sys.argv = saved_argv
    print(
        f"  {'да ' if len(broken) == before else 'НЕТ'} — main: стоящий тег — 1, "
        f"нечитаемый договор — 2, исправный — 0"
    )

    if broken:
        print(check_facts.annotate("error", "самопроверка провалена"), file=sys.stderr)
        for line in broken:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("самопроверка пройдена: выпуск договора собирается и проверяется у издателя")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--dist", type=pathlib.Path, help="каталог файлов выпуска")
    parser.add_argument("--notes", type=pathlib.Path, help="куда записать текст страницы")
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", "ArtVsMark/Engineering-Incidents-Playbook"),
    )
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if not args.dist or not args.notes:
        print("шаг не отработал: нужны --dist и --notes", file=sys.stderr)
        return 2

    try:
        number = check_facts.contract_version(check_facts.VERSION_PATH.read_text(encoding="utf-8"))
        schema = json.loads(check_facts.SCHEMA_PATH.read_text(encoding="utf-8"))
        drift = check_facts.contract_drift(
            number, schema, check_facts.CONTRACT_PATH.read_text(encoding="utf-8")
        )
        tag = tag_for(number)
        standing = tag_exists(tag)
        missing = [str(source) for source in ASSETS if not source.is_file()]
        if missing:
            raise OSError(f"нет файлов договора: {', '.join(missing)}")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(check_facts.annotate("error", f"шаг не отработал: {error}"), file=sys.stderr)
        return 2

    refusals = list(drift)
    # Шаг для CI раздаётся пятерым издателям разом: скачивай он файл, которого
    # на странице нет, — у всех пятерых curl упал бы на 404 после выпуска.
    step = check_facts.ci_step(check_facts.CONTRACT_PATH.read_text(encoding="utf-8")) or ""
    missing = sorted(set(step_files(step)) - {source.name for source in ASSETS})
    if not step_files(step) or missing:
        refusals.append(f"шаг для CI скачивает того, чего в выпуске нет: {missing or 'ничего'}")
    if standing:
        refusals.append(
            f"тег {tag} уже стоит: выпуск, на который прибились, не "
            f"переставляется — поднимите номер в export/facts/facts.version"
        )
    if not refusals:
        assemble(args.dist)
        refusals += verify(
            args.dist, json.loads(check_facts.EXAMPLE_PATH.read_text(encoding="utf-8"))["repo"]
        )
    if refusals:
        for line in refusals:
            print(check_facts.annotate("error", line), file=sys.stderr)
        return 1

    args.notes.write_text(notes(number, args.repo) + "\n", encoding="utf-8")
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"tag={tag}\nnumber={number}\n")
    print(f"выпуск {tag} собран: файлов {len(ASSETS)} в {args.dist}, проверка у издателя — 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
