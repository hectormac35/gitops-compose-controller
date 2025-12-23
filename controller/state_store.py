import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

def _ahora_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def cargar_estado(archivo_estado: str) -> Dict[str, Any]:
    ruta = Path(archivo_estado)
    if not ruta.exists():
        return {
            "ultimo_commit": None,
            "ultima_aplicacion": None,
            "ultimo_error": None,
            "ultimo_evento": "Inicializado",
        }
    return json.loads(ruta.read_text(encoding="utf-8"))

def guardar_evento(archivo_estado: str, cambios: Dict[str, Any]) -> None:
    estado = cargar_estado(archivo_estado)
    estado.update(cambios)
    estado["actualizado_en"] = _ahora_iso()
    Path(archivo_estado).write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8")
