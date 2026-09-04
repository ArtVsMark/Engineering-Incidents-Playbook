"""Третий исход называет предмет: гейт проверяется тем, что обязан отвергнуть,
и тем, что обязан пропустить.

Ложный отказ здесь дороже пропуска, и это не рассуждение, а замер: первая
редакция гейта дала 39 находок, из которых 20 оказались ложными — она не знала
трёх законных способов назвать предмет. По правилу 180 такая находка не шумит,
а приглашает переписать верное сообщение, поэтому каждый из трёх способов стоит
отдельным случаем.

Разбор — чистая функция над текстом: ни площадка, ни файловая система не
трогаются.
"""

from __future__ import annotations

import check_third_outcome as ct


# ── что гейт обязан отвергнуть ─────────────────────────────────────────────

def test_prichina_bez_predmeta_nahodka():
    """Ровно тот случай, ради которого заведено: сломалось, а искать негде."""
    код = ("import sys\n"
           "def main():\n"
           "    if not файлы:\n"
           "        print('проверка не отработала: смотреть нечего',\n"
           "              file=sys.stderr)\n"
           "        return 2\n")
    assert [n for n, _ in ct.безымянные(код)] == [6]


def test_tretiy_ishod_molcha_nahodka():
    """Хуже безымянного сообщения только его отсутствие (045)."""
    код = "def main():\n    if плохо:\n        return 2\n"
    строки = ct.безымянные(код)
    assert строки and "без единого слова" in строки[0][1]


def test_pechat_v_stdout_ne_schitaetsya():
    """ГРАНИЦА: третий исход печатается в stderr. Сообщение в stdout уедет в
    вывод механизма и потеряется среди обычного."""
    код = ("import sys\n"
           "def main():\n"
           "    if плохо:\n"
           "        print(f'не отработала: {путь}')\n"
           "        return 2\n")
    assert ct.безымянные(код)


# ── что гейт обязан пропустить ─────────────────────────────────────────────

def test_podstanovka_eto_predmet():
    код = ("import sys\n"
           "def main():\n"
           "    if плохо:\n"
           "        print(f'не отработала: {путь} не прочитан', file=sys.stderr)\n"
           "        return 2\n")
    assert ct.безымянные(код) == []


def test_bukvalnyy_adres_eto_predmet():
    код = ("import sys\n"
           "def main():\n"
           "    if плохо:\n"
           "        print('не отработала: в .github/workflows пусто',\n"
           "              file=sys.stderr)\n"
           "        return 2\n")
    assert ct.безымянные(код) == []


def test_dlinnyy_klyuch_eto_adres_zapuska():
    """ГРАНИЦА: предмет бывает не файлом. «--paths-from не передан» отвечает на
    вопрос «где искать» полностью."""
    код = ("import sys\n"
           "def main():\n"
           "    if плохо:\n"
           "        print('не отработала: --paths-from не передан', file=sys.stderr)\n"
           "        return 2\n")
    assert ct.безымянные(код) == []


# ── три класса ложных находок, найденные живьём (180) ──────────────────────

def test_soobschenie_uezzhaet_znacheniem_ne_nahodka():
    """ЛОЖНАЯ НАХОДКА №1: `return 2, "..."` — печатает вызывающий, и предмет
    назван здесь же. Так устроен preflight.py."""
    код = ("def шаг():\n"
           "    if плохо:\n"
           "        return 2, f'шаг не уложился в {предел} с'\n")
    assert ct.безымянные(код) == []


def test_soobschenie_kopitsya_v_spisok_ne_nahodka():
    """ЛОЖНАЯ НАХОДКА №2: сообщение накапливается и уезжает вверх списком.
    Так устроен refresh_derived.py."""
    код = ("def сборка():\n"
           "    if плохо:\n"
           "        problems.append(f'сборщика нет: {script}')\n"
           "        return 2, [], problems\n")
    assert ct.безымянные(код) == []


def test_vlozhennaya_pechat_ne_nahodka():
    """ЛОЖНАЯ НАХОДКА №3: предмет печатается циклом, а не соседним оператором.
    Обычный вид отказа со списком причин; так устроен build_rules_index.py."""
    код = ("import sys\n"
           "def main():\n"
           "    if blockers:\n"
           "        print('проверка не отработала:', file=sys.stderr)\n"
           "        for b in blockers:\n"
           "            print(f'  • {b}', file=sys.stderr)\n"
           "        return 2\n")
    assert ct.безымянные(код) == []


def test_vychislennoe_znachenie_ravnosilno_podstanovke():
    """ЛОЖНАЯ НАХОДКА №2, вторая половина: `', '.join(stray)` называет предмет
    не хуже f-строки, а FormattedValue там нет вовсе."""
    код = ("import sys\n"
           "def main():\n"
           "    if плохо:\n"
           "        print('тронул лишнее: ' + ', '.join(stray), file=sys.stderr)\n"
           "        return 2\n")
    assert ct.безымянные(код) == []


def test_argparse_stavit_adres_sam():
    """ГРАНИЦА: parser.error печатает usage с именем программы — адрес ставит
    библиотека, и требовать его второй раз значило бы краснеть на верном (051)."""
    код = ("def main():\n"
           "    parser.error('нужен --check или --add')\n"
           "    return 2\n")
    assert ct.безымянные(код) == []


# ── исход 2 самого гейта ───────────────────────────────────────────────────

def дерево(tmp_path, имя: str, код: str):
    """Поддельное дерево с одним скриптом. Подделка нарочная, а не из жизни:
    ждать настоящего безымянного отказа значит проверять гейт тогда, когда он
    уже не сработал (170)."""
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / имя).write_text(код, encoding="utf-8")
    return tmp_path


def test_glavnyy_otvet_gejta_otkaz(tmp_path):
    """РЕШЕНИЕ ГЕЙТА, А НЕ ПОВТОРЕНИЕ ЕГО УСЛОВИЯ (150): подделанное дерево с
    одним безымянным отказом обязано дать код 1."""
    дерево(tmp_path, "плохой.py",
           "import sys\n"
           "def main():\n"
           "    if плохо:\n"
           "        print('не отработала: смотреть нечего', file=sys.stderr)\n"
           "        return 2\n")
    assert ct.main(["--root", str(tmp_path)]) == 1


def test_chistoe_derevo_prohodit(tmp_path):
    """Обратная половина: ложный отказ здесь дороже пропуска (051, 180)."""
    дерево(tmp_path, "хороший.py",
           "import sys\n"
           "def main():\n"
           "    if плохо:\n"
           "        print(f'не отработала: {путь} не прочитан', file=sys.stderr)\n"
           "        return 2\n")
    assert ct.main(["--root", str(tmp_path)]) == 0


def test_net_ishodnikov_eto_tretiy_ishod(tmp_path):
    """Гейт, не нашедший предмета, обязан упасть, а не зазеленеть (075)."""
    (tmp_path / "scripts").mkdir()
    assert ct.main(["--root", str(tmp_path)]) == 2
