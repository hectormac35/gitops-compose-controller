#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/../controller"

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ARCHIVO_ESTADO="${ARCHIVO_ESTADO:-estado.json}"

uvicorn api:app --host 0.0.0.0 --port 8090
