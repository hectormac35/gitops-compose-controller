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


def estado_compose(ruta_estado_deseado: str) -> str:
    repo = _repo(ruta_estado_deseado)
    r = subprocess.run(_comando_compose() + ["ps"], cwd=str(repo), check=True, capture_output=True, text=True)
    return r.stdout


def hubo_correccion(salida_compose: str) -> bool:
    """True si Docker Compose ha tenido que crear, recrear o arrancar algún contenedor."""
    claves = ("Created", "Recreated", "Started", "Creating", "Recreating", "Starting")
    return any(c in salida_compose for c in claves)
