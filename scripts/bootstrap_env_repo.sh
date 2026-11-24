#!/usr/bin/env bash
# Crea el repo Git local con el "estado deseado" a partir de env-repo-example/.
# Es el repo que vigila el controlador: cada commit que hagas en él se aplica solo.
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DESTINO="$RAIZ/repos/estado-deseado"

if [ -d "$DESTINO/.git" ]; then
  echo "ℹ️  El repo de estado deseado ya existe en $DESTINO"
  exit 0
fi

mkdir -p "$DESTINO"
cp "$RAIZ/env-repo-example/docker-compose.yml" "$DESTINO/"

cd "$DESTINO"
git init -q -b main
git add docker-compose.yml
git -c user.name="gitops-bootstrap" -c user.email="bootstrap@localhost" \
    commit -q -m "Estado inicial"

echo "✅ Repo de estado deseado creado en $DESTINO"
