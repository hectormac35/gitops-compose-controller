from fastapi import FastAPI, HTTPException
from pathlib import Path
import json
import os

app = FastAPI(title="GitOps Compose Controller API", version="1.0.0")

ARCHIVO_ESTADO = os.environ.get("ARCHIVO_ESTADO", "estado.json")

@app.get("/health")
def health():
    return {"estado": "ok"}

@app.get("/estado")
def estado():
    ruta = Path(ARCHIVO_ESTADO)
    if not ruta.exists():
        raise HTTPException(status_code=404, detail="No existe estado.json todavía")
    return json.loads(ruta.read_text(encoding="utf-8"))
