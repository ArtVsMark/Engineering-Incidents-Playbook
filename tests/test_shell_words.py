"""Один разбор слов оболочки на каталог (214, #879)."""

import shell_words as sw


def test_слова_до_неразбираемого_места():
    """Незакрытая кавычка дальше по строке не роняет уже прочитанное."""
    assert sw.слова_оболочки("python scripts/x.py --msg 'oops") == ["python", "scripts/x.py", "--msg"]


def test_разделители_режут_команды():
    assert sw.слова_оболочки("gh api x | jq .", "|&;") == ["gh", "api", "x", "|", "jq", "."]


def test_без_разделителей_знак_остаётся_в_слове():
    assert sw.слова_оболочки("a|b") == ["a|b"]


def test_оба_гейта_зовут_один_разбор():
    """Копии больше нет: оба гейта идут через shell_words."""
    import check_paging
    import check_workflows
    assert "shlex" not in vars(check_paging) and "shlex" not in vars(check_workflows)
