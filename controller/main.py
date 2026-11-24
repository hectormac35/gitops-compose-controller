import time
from typing import Any, Dict

from config import Config
from git_sync import actualizar_repo, asegurar_repo_clonado, obtener_hash_commit, obtener_mensaje_commit
from reconciler import aplicar_compose, estado_compose, hubo_correccion
from state_store import ahora_iso, cargar_estado, guardar_evento


def reconciliar(config: Config, estado: Dict[str, Any]) -> Dict[str, Any]:
    """Una pasada del bucle: sincroniza Git y hace que el estado real coincida con el deseado."""
    try:
        actualizar_repo(config.ruta_repo_local)
        commit = obtener_hash_commit(config.ruta_repo_local)

        if estado.get("ultimo_commit") != commit:
            mensaje = obtener_mensaje_commit(config.ruta_repo_local)
            print(f"[APLICAR] Nuevo commit {commit[:12]} «{mensaje}» ({ahora_iso()})")
            aplicar_compose(config.ruta_repo_local)
            estado = guardar_evento(config.archivo_estado, {
                "ultimo_commit": commit,
                "ultimo_mensaje": mensaje,
                "ultima_aplicacion": ahora_iso(),
                "ultimo_evento": "Aplicado correctamente",
                "ultimo_error": None,
                "servicios": estado_compose(config.ruta_repo_local),
            }, registrar=True)
            print("[OK] Estado aplicado correctamente")
            return estado

        # Mismo commit: reconciliamos igualmente para corregir la deriva
        # (por ejemplo, si alguien ha parado o borrado un contenedor a mano).
        salida = aplicar_compose(config.ruta_repo_local)
        if hubo_correccion(salida):
            print(f"[DERIVA] El estado real no coincidía con Git. Corregido ({ahora_iso()})")
            return guardar_evento(config.archivo_estado, {
                "ultimo_evento": "Deriva corregida",
                "ultima_correccion_deriva": ahora_iso(),
                "ultimo_error": None,
                "servicios": estado_compose(config.ruta_repo_local),
            }, registrar=True)

        print("[SIN CAMBIOS] El estado real coincide con el commit aplicado")
        # Los servicios se consultan en cada ciclo: tras reiniciar el controlador, /estado los muestra al momento
        return guardar_evento(config.archivo_estado, {
            "ultimo_evento": "Sin cambios",
            "ultimo_error": None,
            "servicios": estado_compose(config.ruta_repo_local),
        })

    except Exception as e:  # el controlador nunca se cae: registra el error y lo reintenta en el siguiente ciclo
        error = str(e).strip() or e.__class__.__name__
        print(f"[ERROR] {error}")
        # Solo se añade al historial si es un error nuevo, para no llenarlo con el mismo fallo cada ciclo
        nuevo = error != estado.get("ultimo_error")
        return guardar_evento(config.archivo_estado, {"ultimo_evento": "Error", "ultimo_error": error}, registrar=nuevo)


def ejecutar() -> None:
    config = Config()
    if not config.url_repo_estado_deseado:
        raise RuntimeError("Falta URL_REPO_ESTADO_DESEADO (ruta o URL del repo Git del estado deseado).")

    print("🚀 Controlador GitOps (Docker Compose + Git)")
    print(f"- Repo estado deseado: {config.url_repo_estado_deseado}")
    print(f"- Carpeta repo local:  {config.ruta_repo_local}")
    print(f"- Intervalo:           {config.intervalo_segundos}s")

    asegurar_repo_clonado(config.url_repo_estado_deseado, config.ruta_repo_local)
    estado = cargar_estado(config.archivo_estado)

    while True:
        estado = reconciliar(config, estado)
        time.sleep(config.intervalo_segundos)


if __name__ == "__main__":
    ejecutar()
