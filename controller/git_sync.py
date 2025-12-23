import subprocess
from pathlib import Path

def _ejecutar(comando: list[str], cwd: str | None = None) -> str:
    r = subprocess.run(comando, cwd=cwd, check=True, capture_output=True, text=True)
    return r.stdout.strip()

def asegurar_repo_clonado(url_repo: str, ruta_destino: str) -> None:
    destino = Path(ruta_destino).resolve()
    if (destino / ".git").exists():
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    _ejecutar(["git", "clone", url_repo, str(destino)])

def actualizar_repo(ruta_destino: str) -> None:
    destino = Path(ruta_destino).resolve()
    _ejecutar(["git", "pull", "--ff-only"], cwd=str(destino))

def obtener_hash_commit(ruta_destino: str) -> str:
    destino = Path(ruta_destino).resolve()
    return _ejecutar(["git", "rev-parse", "HEAD"], cwd=str(destino))
