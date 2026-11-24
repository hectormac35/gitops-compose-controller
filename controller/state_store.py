import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

MAX_HISTORIAL = 20


def ahora_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def estado_inicial() -> Dict[str, Any]:
    return {
        "ultimo_commit": None,
        "ultimo_mensaje": None,
        "ultima_aplicacion": None,
        "ultima_correccion_deriva": None,
        "ultimo_error": None,
        "ultimo_evento": "Inicializado",
        "servicios": [],
        "historial": [],
    }


def cargar_estado(archivo_estado: str) -> Dict[str, Any]:
    ruta = Path(archivo_estado)
    if not ruta.exists():
        return estado_inicial()
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        datos.pop("docker_compose_ps", None)  # campo de versiones anteriores (texto en bruto)
        return {**estado_inicial(), **datos}
    except (json.JSONDecodeError, OSError):
        # Fichero dañado (p. ej. un corte de luz a mitad de escritura): empezamos de cero
        return estado_inicial()


def _escribir_atomico(ruta: Path, contenido: str) -> None:
    """Escribe en un fichero temporal y lo renombra: quien lea nunca ve un JSON a medias."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=ruta.parent, prefix=".estado-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(contenido)
        os.replace(tmp, ruta)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def guardar_evento(archivo_estado: str, cambios: Dict[str, Any], registrar: bool = False) -> Dict[str, Any]:
    """Actualiza el estado. Con registrar=True, además añade el evento al historial."""
    estado = cargar_estado(archivo_estado)
    estado.update(cambios)
    estado["actualizado_en"] = ahora_iso()

    if registrar:
        entrada = {
            "fecha": estado["actualizado_en"],
            "evento": cambios.get("ultimo_evento"),
            "commit": (estado.get("ultimo_commit") or "")[:12] or None,
        }
        if cambios.get("ultimo_error"):
            entrada["error"] = cambios["ultimo_error"]
        estado["historial"] = ([entrada] + estado.get("historial", []))[:MAX_HISTORIAL]

    _escribir_atomico(Path(archivo_estado), json.dumps(estado, indent=2, ensure_ascii=False))
    return estado
