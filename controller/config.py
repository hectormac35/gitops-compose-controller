from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    url_repo_estado_deseado: str = os.environ.get("URL_REPO_ESTADO_DESEADO", "")
    ruta_repo_local: str = os.environ.get("RUTA_REPO_LOCAL", "../repos/_clonado_estado_deseado")
    intervalo_segundos: int = int(os.environ.get("INTERVALO_SEGUNDOS", "10"))
    archivo_estado: str = os.environ.get("ARCHIVO_ESTADO", "estado.json")
