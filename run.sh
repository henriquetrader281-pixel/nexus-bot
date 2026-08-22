#!/bin/bash
echo "=================================================="
echo "      🔱 NEXUS BOT - EXECUTOR AUTÓNOMO 🔱         "
echo "=================================================="

if [ ! -d "venv" ]; then
    echo "📦 A criar ambiente virtual Python..."
    python3 -m venv venv
fi

echo "📦 A instalar dependências no venv..."
./venv/bin/pip install --upgrade pip --quiet
./venv/bin/pip install -r requirements.txt --quiet

echo "🚀 A executar Nexus Bot..."
./venv/bin/python3 nexus_autonome.py

echo "=================================================="
echo "      Processo concluído com sucesso!             "
echo "=================================================="
