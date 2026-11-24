from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

import api
from state_store import guardar_evento


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    archivo = tmp_path / "estado.json"
    monkeypatch.setattr(api, "ARCHIVO_ESTADO", str(archivo))
    monkeypatch.setattr(api, "INTERVALO_SEGUNDOS", 10)
    return TestClient(api.app), str(archivo)


def test_health(cliente):
    c, _ = cliente
    assert c.get("/health").json() == {"estado": "ok"}


def test_estado_503_antes_del_primer_ciclo(cliente):
    c, _ = cliente
    assert c.get("/estado").status_code == 503


def test_estado_con_controlador_activo(cliente):
    c, archivo = cliente
    guardar_evento(archivo, {"ultimo_commit": "abc", "ultimo_evento": "Aplicado correctamente"}, registrar=True)
    datos = c.get("/estado").json()
    assert datos["controlador_activo"] is True
    assert "historial" not in datos


def test_detecta_controlador_parado(cliente):
    c, archivo = cliente
    guardar_evento(archivo, {"ultimo_evento": "Sin cambios"})
    import json
    datos = json.loads(open(archivo).read())
    datos["actualizado_en"] = (datetime.now() - timedelta(minutes=5)).isoformat(timespec="seconds")
    open(archivo, "w").write(json.dumps(datos))
    assert c.get("/estado").json()["controlador_activo"] is False


def test_historial(cliente):
    c, archivo = cliente
    guardar_evento(archivo, {"ultimo_evento": "Aplicado correctamente"}, registrar=True)
    guardar_evento(archivo, {"ultimo_evento": "Deriva corregida"}, registrar=True)
    eventos = c.get("/historial").json()["eventos"]
    assert [e["evento"] for e in eventos] == ["Deriva corregida", "Aplicado correctamente"]


def test_json_danado_no_rompe_la_api(cliente):
    c, archivo = cliente
    open(archivo, "w").write("{roto")
    assert c.get("/estado").status_code == 503
    assert c.get("/historial").json() == {"eventos": []}
