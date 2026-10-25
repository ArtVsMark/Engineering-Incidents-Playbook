"""Перепись правил о механизмах сходится с охватом гейтов (220): отказ, чисто, третий исход."""

import json
from pathlib import Path

import check_mechanism_scope as ms
import pytest

МЕСТА = {"scripts": '"scripts"', ".claude/hooks": 'hooks"'}
#: Гейт называет правило блоком объявлений, как его читает check_bindings (обзор #891).
ОБЪЯВЛЕНИЕ = '"""Гейт.\n\nРеализует правила каталога:\n  100 — дедлайн вызова.\n"""\n'
ГЕЙТ = ОБЪЯВЛЕНИЕ + 'ПАПКИ = ("scripts", ".claude/hooks")\n'


def дерево(tmp_path: Path, правила: dict, гейт: str = ГЕЙТ, места: dict = МЕСТА) -> Path:
    (tmp_path / "rules" / "ru").mkdir(parents=True)
    (tmp_path / "rules" / "ru" / "100-x.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "check_x.py").write_text(гейт, encoding="utf-8")
    (tmp_path / ".rules").mkdir()
    (tmp_path / ".rules" / "mechanism-rules.json").write_text(
        json.dumps({"места": места, "rules": правила}), encoding="utf-8"
    )
    return tmp_path


def test_всё_в_охвате_чисто(tmp_path):
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "scripts/check_x.py"}}
    assert ms.main(["--root", str(дерево(tmp_path, правила))]) == 0


@pytest.mark.parametrize(
    "ответ, след",
    [
        ({"scripts": "scripts/check_x.py"}, "не названо"),  # место пропущено
        ({"scripts": "scripts/check_x.py", ".claude/hooks": "исключено:"}, "без причины"),
        (
            {"scripts": "scripts/нет.py", ".claude/hooks": "исключено: x"},
            "гейта scripts/нет.py нет",
        ),
    ],
)
def test_расхождение_отказ(tmp_path, capsys, ответ, след):
    assert ms.main(["--root", str(дерево(tmp_path, {"100": ответ}))]) == 1
    assert след in capsys.readouterr().err


def test_место_не_в_коде_гейта_отказ(tmp_path, capsys):
    """Охват из переписи обязан стоять в коде — так поймано бы 100 до #882."""
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "scripts/check_x.py"}}
    корень = дерево(tmp_path, правила, гейт=ОБЪЯВЛЕНИЕ + 'ПАПКИ = ("scripts",)\n')
    assert ms.main(["--root", str(корень)]) == 1
    assert "перепись разошлась с охватом" in capsys.readouterr().err


def test_гейт_не_называет_правило_отказ(tmp_path, capsys):
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "исключено: x"}}
    корень = дерево(tmp_path, правила, гейт='ПАПКИ = ("scripts",)\n')
    assert ms.main(["--root", str(корень)]) == 1
    assert "не называет правило 100" in capsys.readouterr().err


def test_охват_из_импортированного_модуля(tmp_path):
    """Как check_copies берёт охват у check_orphans."""
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "scripts/check_x.py"}}
    корень = дерево(tmp_path, правила, гейт=ОБЪЯВЛЕНИЕ + "from общее import ПАПКИ\n")
    (корень / "scripts" / "общее.py").write_text(
        'ПАПКИ = ("scripts", ".claude/hooks")\n', encoding="utf-8"
    )
    assert ms.main(["--root", str(корень)]) == 0


def test_долг_печатается_числом(tmp_path, capsys):
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "не построено: хуки"}}
    assert ms.main(["--root", str(дерево(tmp_path, правила))]) == 0
    assert "не построено 1" in capsys.readouterr().out


def test_пустая_перепись_третий_исход(tmp_path):
    assert ms.main(["--root", str(дерево(tmp_path, {}))]) == 2


def test_нет_переписи_третий_исход(tmp_path):
    assert ms.main(["--root", str(tmp_path)]) == 2


def test_живое_дерево_сходится():
    assert ms.main([]) == 0


# Обзор #891: проза охватом и ссылкой на правило не считается.
def test_место_только_в_прозе_отказ(tmp_path, capsys):
    """Место названо в докстринге и комментарии, а в коде его нет — расхождение."""
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "scripts/check_x.py"}}
    гейт = (
        '"""Смотрит .claude/hooks.\n\nРеализует правила каталога:\n'
        '  100 — дедлайн.\n"""\nПАПКИ = ("scripts",)  # и ".claude/hooks"\n'
    )
    assert ms.main(["--root", str(дерево(tmp_path, правила, гейт=гейт))]) == 1
    assert "перепись разошлась с охватом" in capsys.readouterr().err


def test_номер_вне_блока_объявлений_отказ(tmp_path, capsys):
    """Число 100 в коде — порог, а не ссылка на правило."""
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "scripts/check_x.py"}}
    гейт = 'ПАПКИ = ("scripts", ".claude/hooks")\nПРЕДЕЛ = 100\n'
    assert ms.main(["--root", str(дерево(tmp_path, правила, гейт=гейт))]) == 1
    assert "не называет правило 100" in capsys.readouterr().err


def test_охват_через_два_импорта(tmp_path):
    """Гейт берёт охват у модуля, а тот — у третьего: охват виден."""
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "scripts/check_x.py"}}
    корень = дерево(tmp_path, правила, гейт=ОБЪЯВЛЕНИЕ + "from средний import ПАПКИ\n")
    (корень / "scripts" / "средний.py").write_text("from нижний import ПАПКИ\n", encoding="utf-8")
    (корень / "scripts" / "нижний.py").write_text(
        'ПАПКИ = ("scripts", ".claude/hooks")\n', encoding="utf-8"
    )
    assert ms.main(["--root", str(корень)]) == 0


def test_исключения_на_веру_печатаются_числом(tmp_path, capsys):
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "исключено: нет вызовов"}}
    assert ms.main(["--root", str(дерево(tmp_path, правила))]) == 0
    assert "исключений на веру 1" in capsys.readouterr().out


def test_заголовок_объявлений_в_комментарии_не_засчитан(tmp_path, capsys):
    """Блок объявлений — в докстроке модуля; в комментарии он не объявление (обзор #908)."""
    правила = {"100": {"scripts": "scripts/check_x.py", ".claude/hooks": "scripts/check_x.py"}}
    гейт = (
        '# Реализует правила каталога:\n#   100 — дедлайн.\nПАПКИ = ("scripts", ".claude/hooks")\n'
    )
    assert ms.main(["--root", str(дерево(tmp_path, правила, гейт=гейт))]) == 1
    assert "не называет правило 100" in capsys.readouterr().err
