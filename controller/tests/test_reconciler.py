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
