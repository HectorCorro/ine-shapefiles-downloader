#!/usr/bin/env bash
set -e

echo "🔄 Ejecutando descarga nacional…"
python app/download_nacional.py

echo "🔄 Ejecutando descarga PEEPJF…"
python app/download_peepjf.py

echo "✅ ¡Todo completado!"
