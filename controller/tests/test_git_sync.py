import subprocess

from conftest import commit, git
from git_sync import actualizar_repo, asegurar_repo_clonado, obtener_hash_commit, obtener_mensaje_commit


def test_clona_y_detecta_commits_nuevos(repo_deseado, tmp_path):
    clon = tmp_path / "clon"
    asegurar_repo_clonado(str(repo_deseado), str(clon))
    primero = obtener_hash_commit(str(clon))

    commit(repo_deseado, 8099, "Cambiar puerto a 8099")
    actualizar_repo(str(clon))

    assert obtener_hash_commit(str(clon)) != primero
    assert obtener_mensaje_commit(str(clon)) == "Cambiar puerto a 8099"
    assert "8099:80" in (clon / "docker-compose.yml").read_text()


def test_clonar_dos_veces_no_falla(repo_deseado, tmp_path):
    clon = tmp_path / "clon"
    asegurar_repo_clonado(str(repo_deseado), str(clon))
    asegurar_repo_clonado(str(repo_deseado), str(clon))
    assert (clon / ".git").exists()


def test_sobrevive_a_un_push_force(repo_deseado, tmp_path):
    """Con 'git pull --ff-only' el controlador se quedaba bloqueado si se reescribía el historial."""
    clon = tmp_path / "clon"
    asegurar_repo_clonado(str(repo_deseado), str(clon))
    commit(repo_deseado, 8099, "Cambio que luego se reescribe")
    actualizar_repo(str(clon))

    # Reescribimos el historial del remoto (equivalente a un push --force)
    git("reset", "-q", "--hard", "HEAD~1", cwd=repo_deseado)
    commit(repo_deseado, 8100, "Historial reescrito")

    actualizar_repo(str(clon))
    assert obtener_mensaje_commit(str(clon)) == "Historial reescrito"


def test_descarta_cambios_hechos_a_mano_en_la_copia_local(repo_deseado, tmp_path):
    clon = tmp_path / "clon"
    asegurar_repo_clonado(str(repo_deseado), str(clon))
    (clon / "docker-compose.yml").write_text("editado a mano\n")
    actualizar_repo(str(clon))
    assert "8085:80" in (clon / "docker-compose.yml").read_text()
