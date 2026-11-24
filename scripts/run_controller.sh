#!/usr/bin/env bash
# Ejecuta el controlador fuera de Docker (modo desarrollo)
set -e

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
"$RAIZ/scripts/bootstrap_env_repo.sh"

cd "$RAIZ/controller"

export INTERVALO_SEGUNDOS="${INTERVALO_SEGUNDOS:-10}"
export ARCHIVO_ESTADO="${ARCHIVO_ESTADO:-estado.json}"
export URL_REPO_ESTADO_DESEADO="${URL_REPO_ESTADO_DESEADO:-$RAIZ/repos/estado-deseado}"
export RUTA_REPO_LOCAL="${RUTA_REPO_LOCAL:-$RAIZ/repos/_clonado_estado_deseado}"

python3 main.py
