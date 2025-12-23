#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/../controller"

export INTERVALO_SEGUNDOS=10
export ARCHIVO_ESTADO="estado.json"

export URL_REPO_ESTADO_DESEADO="/home/hector/Documentos/proyecto portafolio/gitops-compose-controller/repos/estado-deseado"
export RUTA_REPO_LOCAL="../repos/_clonado_estado_deseado"

python3 main.py
