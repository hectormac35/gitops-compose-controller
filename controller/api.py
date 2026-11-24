import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="GitOps Compose Controller API",
    version="1.1.0",
    description="Estado del controlador GitOps: qué commit está desplegado, eventos recientes y errores.",
)

ARCHIVO_ESTADO = os.environ.get("ARCHIVO_ESTADO", "estado.json")
INTERVALO_SEGUNDOS = int(os.environ.get("INTERVALO_SEGUNDOS", "10"))


def _leer_estado() -> dict | None:
    ruta = Path(ARCHIVO_ESTADO)
    if not ruta.exists():
        return None
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _segundos_desde(fecha_iso: str | None) -> float | None:
    if not fecha_iso:
        return None
    try:
        return round((datetime.now() - datetime.fromisoformat(fecha_iso)).total_seconds(), 1)
    except ValueError:
        return None


@app.get("/health", summary="La API responde")
def health():
    return {"estado": "ok"}


@app.get("/estado", summary="Estado actual del despliegue")
def estado():
    datos = _leer_estado()
    if datos is None:
        return JSONResponse(status_code=503, content={"detail": "El controlador todavía no ha escrito su estado"})

    segundos = _segundos_desde(datos.get("actualizado_en"))
    # Si el controlador lleva más de 3 ciclos sin escribir, probablemente se ha parado
    activo = segundos is not None and segundos <= 3 * INTERVALO_SEGUNDOS + 5

    respuesta = {k: v for k, v in datos.items() if k != "historial"}
    respuesta["controlador_activo"] = activo
    respuesta["segundos_desde_ultima_actualizacion"] = segundos
    return respuesta


@app.get("/historial", summary="Últimos eventos (aplicaciones, deriva corregida y errores)")
def historial():
    datos = _leer_estado()
    return {"eventos": (datos or {}).get("historial", [])}
