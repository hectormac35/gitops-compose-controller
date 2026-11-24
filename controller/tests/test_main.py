"""Bucle de reconciliación con Git real y Docker simulado."""
import pytest

import main
from config import Config
from conftest import commit
from git_sync import asegurar_repo_clonado
from state_store import cargar_estado


class DockerFalso:
    def __init__(self):
        self.aplicaciones = 0
        self.deriva = False
        self.fallo = None

    def aplicar(self, ruta):
        if self.fallo:
            raise RuntimeError(self.fallo)
        self.aplicaciones += 1
        if self.deriva:
            self.deriva = False
            return " Container gitops_web  Started"
        return " Container gitops_web  Running"


@pytest.fixture
def entorno(repo_deseado, tmp_path, monkeypatch):
    docker = DockerFalso()
    monkeypatch.setattr(main, "aplicar_compose", docker.aplicar)
    monkeypatch.setattr(main, "estado_compose", lambda ruta: [{"servicio": "web", "estado": "running"}])
    config = Config(
        url_repo_estado_deseado=str(repo_deseado),
        ruta_repo_local=str(tmp_path / "clon"),
        intervalo_segundos=1,
        archivo_estado=str(tmp_path / "estado.json"),
    )
    asegurar_repo_clonado(config.url_repo_estado_deseado, config.ruta_repo_local)
    return config, docker, repo_deseado


def test_aplica_el_primer_commit(entorno):
    config, docker, _ = entorno
    estado = main.reconciliar(config, cargar_estado(config.archivo_estado))
    assert estado["ultimo_evento"] == "Aplicado correctamente"
    assert estado["ultimo_mensaje"] == "Estado inicial"
    assert estado["servicios"] == [{"servicio": "web", "estado": "running"}]


def test_sin_cambios_no_llena_el_historial(entorno):
    config, _, _ = entorno
    estado = main.reconciliar(config, cargar_estado(config.archivo_estado))
    for _ in range(3):
        estado = main.reconciliar(config, estado)
    assert estado["ultimo_evento"] == "Sin cambios"
    assert len(estado["historial"]) == 1


def test_aplica_un_commit_nuevo(entorno):
    config, _, repo = entorno
    estado = main.reconciliar(config, cargar_estado(config.archivo_estado))
    commit(repo, 8099, "Cambiar puerto a 8099")
    estado = main.reconciliar(config, estado)
    assert estado["ultimo_mensaje"] == "Cambiar puerto a 8099"
    assert [e["evento"] for e in estado["historial"]] == ["Aplicado correctamente"] * 2


def test_corrige_la_deriva(entorno):
    config, docker, _ = entorno
    estado = main.reconciliar(config, cargar_estado(config.archivo_estado))
    docker.deriva = True  # alguien ha borrado el contenedor a mano
    estado = main.reconciliar(config, estado)
    assert estado["ultimo_evento"] == "Deriva corregida"
    assert estado["ultima_correccion_deriva"]


def test_un_error_no_para_el_controlador_y_no_se_repite_en_el_historial(entorno):
    config, docker, _ = entorno
    estado = main.reconciliar(config, cargar_estado(config.archivo_estado))
    docker.fallo = "Cannot connect to the Docker daemon"
    for _ in range(3):
        estado = main.reconciliar(config, estado)
    assert estado["ultimo_evento"] == "Error"
    assert [e["evento"] for e in estado["historial"]].count("Error") == 1

    docker.fallo = None  # Docker vuelve
    estado = main.reconciliar(config, estado)
    assert estado["ultimo_error"] is None
