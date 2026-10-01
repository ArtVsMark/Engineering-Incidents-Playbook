#!/bin/bash
# Старт облачной сессии: Python 3.14 на месте, окружение проверки — на планке.
#
# ТОЛЬКО В ОБЛАКЕ. На машине владельца окружение его, и ставить туда
# интерпретатор без спроса хук не вправе: признак облака — CLAUDE_CODE_REMOTE.
#
# ЗАЧЕМ 3.14, ЕСЛИ ПЛАНКА 3.12. Это задел под переезд семьи на 3.14: образ
# облачного окна несёт только 3.10–3.13, а встроенный uv 0.8.17 знает лишь
# 3.14.0rc2. Сайт установщика uv (astral.sh) закрыт сетевой политикой,
# PyPI — открыт, поэтому свежий uv ставится из PyPI. Замер 1 октября: uv
# 0.12.21 ставит 3.14.7 за ~2 с.
#
# ЗАЧЕМ .venv НА ПЛАНКЕ. Системный python3 окна — 3.11, ниже планки, и
# прогон перед толчком с него отказывает (check_python_version.py). Окружение
# собирается на версии из requires-python — той же, на которой гоняет
# конвейер, — поэтому «чисто локально» снимается с его поверхности (037).
# Планку читает check_python_version.floor, а не второй разбор (214): сдвинется
# планка — хук сам соберёт окружение на новой версии.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
cd "$CLAUDE_PROJECT_DIR"

if ! command -v python3.14 >/dev/null 2>&1; then
  python3.12 -m venv /opt/uv
  /opt/uv/bin/pip install -q -U uv
  /opt/uv/bin/uv python install 3.14
  ln -sf "$(/opt/uv/bin/uv python find 3.14)" /usr/local/bin/python3.14
fi

floor=$(python3 -c "import sys, pathlib; sys.path.insert(0, 'scripts'); import check_python_version as c; f = c.floor(pathlib.Path('pyproject.toml').read_text(encoding='utf-8')); print(f'{f[0]}.{f[1]}')")
if [ ! -x .venv/bin/python ] || [ "$(.venv/bin/python -c 'import sys; print("%d.%d" % sys.version_info[:2])')" != "$floor" ]; then
  rm -rf .venv
  "python$floor" -m venv .venv
fi
.venv/bin/pip install -q -r requirements-test.txt

echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
