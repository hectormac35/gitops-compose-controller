import subprocess
from types import SimpleNamespace

import pytest

import reconciler


@pytest.mark.parametrize("salida, esperado", [
    (" Container gitops_web  Running", False),                      # Compose v2, nada que hacer
    (" Container gitops_web  Started", True),                       # Compose v2, lo ha arrancado
    (" Container gitops_web  Recreated\n Container gitops_web  Started", True),
    ("gitops_web is up-to-date", False),                            # Compose v1
    ("Starting gitops_web ... done", True),
])
def test_hubo_correccion(salida, esperado):
    assert reconciler.hubo_correccion(salida) is esperado


def test_usa_compose_v2_si_esta_disponible(monkeypatch):
    monkeypatch.setattr(reconciler.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    assert reconciler._comando_compose() == ["docker", "compose"]


def test_usa_compose_v1_como_alternativa(monkeypatch):
    monkeypatch.setattr(reconciler.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1))
    monkeypatch.setattr(reconciler.shutil, "which", lambda _: "/usr/bin/docker-compose")
    assert reconciler._comando_compose() == ["docker-compose"]


def test_error_claro_si_no_hay_compose(monkeypatch):
    monkeypatch.setattr(reconciler.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1))
    monkeypatch.setattr(reconciler.shutil, "which", lambda _: None)
    with pytest.raises(RuntimeError, match="Docker Compose"):
        reconciler._comando_compose()


def test_falla_si_el_repo_no_tiene_compose(tmp_path):
    with pytest.raises(FileNotFoundError):
        reconciler.aplicar_compose(str(tmp_path))


LINEA_NDJSON = (
    '{"Command":"\\"/docker-entrypoint.…\\"","Image":"nginx:alpine","Name":"gitops_web","Ports":"0.0.0.0:8099->80/tcp, [::]:8099->80/tcp",'
    '"Publishers":[{"URL":"0.0.0.0","TargetPort":80,"PublishedPort":8099,"Protocol":"tcp"},'
    '{"URL":"::","TargetPort":80,"PublishedPort":8099,"Protocol":"tcp"}],'
    '"Service":"web","State":"running","Status":"Up 2 seconds"}'
)


def test_parsea_ps_json_una_linea_por_servicio():
    """Formato de Docker Compose v2.21+ (una línea JSON por servicio)."""
    assert reconciler.parsear_ps_json(LINEA_NDJSON + "\n") == [{
        "servicio": "web",
        "contenedor": "gitops_web",
        "imagen": "nginx:alpine",
        "estado": "running",
        "detalle": "Up 2 seconds",
        "puertos": ["8099->80/tcp"],  # IPv4 e IPv6 se unifican
    }]


def test_parsea_ps_json_en_array():
    """Formato de versiones anteriores de Compose v2 (un array JSON)."""
    servicios = reconciler.parsear_ps_json(f"[{LINEA_NDJSON}, {LINEA_NDJSON.replace('gitops_web', 'otro')}]")
    assert [s["contenedor"] for s in servicios] == ["gitops_web", "otro"]


def test_ps_sin_servicios_y_salida_no_json():
    assert reconciler.parsear_ps_json("") == []
    assert reconciler.parsear_ps_json("NAME  IMAGE  STATUS") is None
