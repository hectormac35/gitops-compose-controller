import subprocess
from pathlib import Path

def aplicar_compose(ruta_estado_deseado: str) -> None:
    repo = Path(ruta_estado_deseado).resolve()
    compose_file = repo / "docker-compose.yml"

    if not compose_file.exists():
        raise FileNotFoundError(f"No existe docker-compose.yml en {repo}")

    comando = ["docker-compose", "up", "-d", "--remove-orphans"]
    subprocess.run(comando, cwd=str(repo), check=True)

def estado_compose(ruta_estado_deseado: str) -> str:
    repo = Path(ruta_estado_deseado).resolve()
    comando = ["docker-compose", "ps"]
    resultado = subprocess.run(
        comando, cwd=str(repo), check=True, capture_output=True, text=True
    )
    return resultado.stdout
