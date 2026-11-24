import json
import shutil
import subprocess
from pathlib import Path


def _comando_compose() -> list[str]:
    """Usa Docker Compose v2 (`docker compose`) y, si no está, el antiguo `docker-compose`."""
    r = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
    if r.returncode == 0:
        return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    raise RuntimeError("No se encuentra Docker Compose (ni 'docker compose' ni 'docker-compose').")


def _repo(ruta_estado_deseado: str) -> Path:
    repo = Path(ruta_estado_deseado).resolve()
    if not (repo / "docker-compose.yml").exists():
        raise FileNotFoundError(f"No existe docker-compose.yml en {repo}")
    return repo


def aplicar_compose(ruta_estado_deseado: str) -> str:
    """Aplica el estado deseado. `up -d` es idempotente: si nada ha cambiado, no toca nada.

    Devuelve la salida de Docker Compose para poder detectar si ha corregido algo.
    """
    repo = _repo(ruta_estado_deseado)
    comando = _comando_compose() + ["up", "-d", "--remove-orphans"]
    r = subprocess.run(comando, cwd=str(repo), check=True, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


def estado_compose(ruta_estado_deseado: str) -> list[dict] | str:
    """Servicios desplegados como lista estructurada (nombre, imagen, estado y puertos).

    Usa `docker compose ps --format json`. Si no está disponible (Compose v1), devuelve el texto de `ps`.
    """
    repo = _repo(ruta_estado_deseado)
    comando = _comando_compose()
    r = subprocess.run(comando + ["ps", "--all", "--format", "json"], cwd=str(repo), capture_output=True, text=True)
    if r.returncode == 0:
        servicios = parsear_ps_json(r.stdout)
        if servicios is not None:
            return servicios
    r = subprocess.run(comando + ["ps"], cwd=str(repo), check=True, capture_output=True, text=True)
    return r.stdout


def parsear_ps_json(salida: str) -> list[dict] | None:
    """Admite los dos formatos de `docker compose ps --format json`: un array JSON o una línea JSON por servicio."""
    texto = salida.strip()
    if not texto:
        return []
    try:
        datos = json.loads(texto)
        filas = datos if isinstance(datos, list) else [datos]
    except json.JSONDecodeError:
        try:
            filas = [json.loads(linea) for linea in texto.splitlines() if linea.strip()]
        except json.JSONDecodeError:
            return None
    return [
        {
            "servicio": f.get("Service"),
            "contenedor": f.get("Name"),
            "imagen": f.get("Image"),
            "estado": f.get("State"),
            "detalle": f.get("Status"),
            "puertos": f.get("Publishers") and sorted({
                f"{p['PublishedPort']}->{p['TargetPort']}/{p.get('Protocol', 'tcp')}"
                for p in f["Publishers"] if p.get("PublishedPort")
            }) or f.get("Ports"),
        }
        for f in filas
    ]


def hubo_correccion(salida_compose: str) -> bool:
    """True si Docker Compose ha tenido que crear, recrear o arrancar algún contenedor."""
    claves = ("Created", "Recreated", "Started", "Creating", "Recreating", "Starting")
    return any(c in salida_compose for c in claves)
