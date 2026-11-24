#!/usr/bin/env bash
# Demo GitOps de principio a fin: cambio por commit, corrección de deriva y rollback.
# Requiere el entorno levantado (make up).
set -euo pipefail

API="${API:-http://localhost:8090}"
REPO="$(cd "$(dirname "$0")/.." && pwd)/repos/estado-deseado"
ESPERA="${ESPERA:-15}"

azul()  { printf '\n\033[1;36m%s\033[0m\n' "$*"; }
gris()  { printf '\033[2m%s\033[0m\n' "$*"; }
estado() {
  local e h
  e=$(curl -s "$API/estado"); h=$(curl -s "$API/historial")
  python3 - "$e" "$h" <<'PY'
import json, sys
e, h = json.loads(sys.argv[1]), json.loads(sys.argv[2])["eventos"]
print(f"  commit desplegado: {(e.get('ultimo_commit') or '')[:12]}  «{e.get('ultimo_mensaje')}»")
if h:
    print(f"  último evento:     {h[0]['evento']} ({h[0]['fecha'][11:]})")
print(f"  controlador activo: {e.get('controlador_activo')}")
PY
}
puerto_web() { grep -oE '"[0-9]+:80"' "$REPO/docker-compose.yml" | tr -d '"' | cut -d: -f1; }
probar_web() { printf '  GET http://localhost:%s -> %s\n' "$1" "$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$1" || true)"; }

azul "[1] Estado inicial"
estado
P0=$(puerto_web); probar_web "$P0"

NUEVO=8099; [ "$P0" = "8099" ] && NUEVO=8098   # si la demo se repite, usa otro puerto
azul "[2] Cambio por commit: el servicio pasa al puerto $NUEVO"
gris "  $ make cambiar-puerto PUERTO=$NUEVO"
( cd "$REPO" && sed -i -E "s/[0-9]+:80/$NUEVO:80/" docker-compose.yml && git add docker-compose.yml && git commit -q -m "Cambiar puerto a $NUEVO" )
gris "  (esperando ${ESPERA}s a que el controlador lo detecte…)"; sleep "$ESPERA"
estado
probar_web "$NUEVO"

azul "[3] Deriva: alguien borra el contenedor a mano"
gris "  $ docker rm -f gitops_web"
docker rm -f gitops_web >/dev/null
probar_web "$NUEVO"
gris "  (esperando ${ESPERA}s…)"; sleep "$ESPERA"
estado
probar_web "$NUEVO"

azul "[4] Rollback con git revert"
gris "  $ git revert HEAD"
( cd "$REPO" && git revert --no-edit HEAD >/dev/null )
gris "  (esperando ${ESPERA}s…)"; sleep "$ESPERA"
estado
probar_web "$P0"

azul "[5] Historial (GET /historial)"
curl -s "$API/historial" | python3 -c "import sys,json; [print(f\"  {e['fecha']}  {e['evento']:<24} {e.get('commit') or ''}\") for e in json.load(sys.stdin)['eventos'][:6]]"
