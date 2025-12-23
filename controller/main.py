import time
from config import Config
from git_sync import asegurar_repo_clonado, actualizar_repo, obtener_hash_commit
from reconciler import aplicar_compose, estado_compose
from state_store import cargar_estado, guardar_evento
from datetime import datetime

def _ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")

def ejecutar():
    config = Config()
    estado = cargar_estado(config.archivo_estado)

    if not config.url_repo_estado_deseado:
        raise RuntimeError("Falta URL_REPO_ESTADO_DESEADO (ruta o URL del repo Git del estado deseado).")

    print("🚀 Controlador GitOps (Docker Compose + Git real)")
    print(f"- Repo estado deseado: {config.url_repo_estado_deseado}")
    print(f"- Carpeta repo local:  {config.ruta_repo_local}")
    print(f"- Intervalo:          {config.intervalo_segundos}s")

    asegurar_repo_clonado(config.url_repo_estado_deseado, config.ruta_repo_local)

    while True:
        try:
            actualizar_repo(config.ruta_repo_local)
            commit = obtener_hash_commit(config.ruta_repo_local)

            if estado.get("ultimo_commit") != commit:
                print(f"[APLICAR] Nuevo commit detectado: {commit[:12]} ({_ahora()})")

                guardar_evento(config.archivo_estado, {
                    "ultimo_evento": "Aplicando cambios",
                    "ultimo_error": None,
                })

                aplicar_compose(config.ruta_repo_local)

                salida_ps = estado_compose(config.ruta_repo_local)

                estado["ultimo_commit"] = commit
                guardar_evento(config.archivo_estado, {
                    "ultimo_commit": commit,
                    "ultima_aplicacion": _ahora(),
                    "ultimo_evento": "Aplicado correctamente",
                    "ultimo_error": None,
                    "docker_compose_ps": salida_ps,
                })

                print("[OK] Estado aplicado correctamente")
                print(salida_ps)

            else:
                print("[SIN CAMBIOS] Ya estás en el commit aplicado")
                guardar_evento(config.archivo_estado, {
                    "ultimo_evento": "Sin cambios",
                    "ultimo_error": None,
                })

        except Exception as e:
            print(f"[ERROR] {e}")
            guardar_evento(config.archivo_estado, {
                "ultimo_evento": "Error",
                "ultimo_error": str(e),
            })

        time.sleep(config.intervalo_segundos)

if __name__ == "__main__":
    ejecutar()
