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
    _ejecutar(["git", "clone", "--quiet", url_repo, str(destino)])


def actualizar_repo(ruta_destino: str) -> None:
    """Deja la copia local exactamente igual que el remoto.

    En GitOps manda Git: se descarga el remoto y se hace reset a su rama. Así el controlador no se
    bloquea si alguien reescribe el historial (push --force) ni si alguien toca la copia local.
    """
    destino = str(Path(ruta_destino).resolve())
    _ejecutar(["git", "fetch", "--quiet", "--prune", "origin"], cwd=destino)
    _ejecutar(["git", "reset", "--quiet", "--hard", "@{upstream}"], cwd=destino)


def obtener_hash_commit(ruta_destino: str) -> str:
    return _ejecutar(["git", "rev-parse", "HEAD"], cwd=str(Path(ruta_destino).resolve()))


def obtener_mensaje_commit(ruta_destino: str) -> str:
    return _ejecutar(["git", "log", "-1", "--format=%s"], cwd=str(Path(ruta_destino).resolve()))
