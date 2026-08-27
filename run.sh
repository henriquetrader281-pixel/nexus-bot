#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d "venv" ]]; then
  echo "📦 Criando ambiente virtual Python..."
  python3 -m venv venv
fi

"$ROOT_DIR/venv/bin/python" -m pip install --upgrade pip --quiet
"$ROOT_DIR/venv/bin/pip" install -r requirements.txt --quiet

MODE="${NEXUS_MODE:-ui}"
if [[ "$MODE" == "autonomous" ]]; then
  echo "🤖 Iniciando o modo autônomo..."
  exec "$ROOT_DIR/venv/bin/python" nexus_autonome.py
fi

if [[ -z "${NEXUS_PASSWORD:-}" ]]; then
  echo "⚠️ NEXUS_PASSWORD não está definida. O painel iniciará bloqueado até a configuração da senha."
fi

echo "🚀 Iniciando o painel Nexus..."
exec "$ROOT_DIR/venv/bin/streamlit" run app.py
