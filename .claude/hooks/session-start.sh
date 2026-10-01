#!/bin/bash
# Старт облачной сессии: Python 3.14 на месте, окружение проверки — на планке.
#
# ТОЛЬКО В ОБЛАКЕ. На машине владельца окружение его, и ставить туда
# интерпретатор без спроса хук не вправе: признак облака — CLAUDE_CODE_REMOTE.
#
# ЗАЧЕМ СТАВИТЬ 3.14. Это планка каталога и всей семьи (решение владельца
# 1 октября), а образ облачного окна несёт только 3.10–3.13, и встроенный uv
# 0.8.17 знает лишь 3.14.0rc2. Сайт установщика uv (astral.sh) закрыт сетевой политикой,
# PyPI — открыт, поэтому свежий uv ставится из PyPI. Замер 1 октября: uv
# 0.12.21 ставит 3.14.7 за ~2 с.
#
# ЗАЧЕМ .venv НА ПЛАНКЕ. Системный python3 окна — 3.11, ниже планки, и
# прогон перед толчком с него отказывает (check_python_version.py). Окружение
# собирается на версии из requires-python — той же, на которой гоняет
# конвейер, — поэтому «чисто локально» снимается с его поверхности (037).
# Планку читает check_python_version.floor, а не второй разбор (214): сдвинется
# планка — хук сам соберёт окружение на новой версии.
#
# СБОЙ СЕТИ НЕ РОНЯЕТ СТАРТ. Хук ходит в PyPI и за интерпретатором, а
# «стартовый хук на сетевом вызове превращает открытие окна в лотерею» — так
# это записано у хука грейдера, который поэтому в сеть не ходит вовсе. Здесь
# сеть нужна, поэтому иначе: всякий отказ — предупреждение с названным шагом и
# выход 0. Окно открывается всегда; не готово только то, что названо.
set -uo pipefail

warn() {
  echo "старт окна: $1 — окно работает без этого; прогон перед толчком запускайте интерпретатором не ниже планки вручную" >&2
}

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
cd "$CLAUDE_PROJECT_DIR" || { warn "нет каталога проекта"; exit 0; }

if ! command -v python3.14 >/dev/null 2>&1; then
  { python3.12 -m venv /opt/uv \
      && /opt/uv/bin/pip install -q -U uv \
      && /opt/uv/bin/uv python install 3.14 \
      && ln -sf "$(/opt/uv/bin/uv python find 3.14)" /usr/local/bin/python3.14; } \
    || warn "Python 3.14 не поставлен"
fi

# Планку читает 3.14, если она уже стоит: код каталога пишется под планку, и
# системный 3.11 окна не обязан его импортировать. Без 3.14 — системный, и
# тогда отказ чтения назван предупреждением, а не упавшим стартом.
reader=$(command -v python3.14 || command -v python3)
if ! floor=$("$reader" -c "import sys, pathlib; sys.path.insert(0, 'scripts'); import check_python_version as c; f = c.floor(pathlib.Path('pyproject.toml').read_text(encoding='utf-8')); print(f'{f[0]}.{f[1]}')"); then
  warn "планка requires-python не прочитана"
  exit 0
fi
if [ ! -x .venv/bin/python ] || [ "$(.venv/bin/python -c 'import sys; print("%d.%d" % sys.version_info[:2])')" != "$floor" ]; then
  rm -rf .venv
  "python$floor" -m venv .venv || { warn "окружение на $floor не собрано"; exit 0; }
fi
.venv/bin/pip install -q -r requirements-test.txt \
  || { warn "тестовые зависимости не поставлены"; exit 0; }

echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
exit 0
