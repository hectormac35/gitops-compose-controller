import subprocess
from pathlib import Path

import pytest

COMPOSE = """services:
  web:
    image: nginx:alpine
    ports:
      - "{puerto}:80"
"""


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def commit(repo: Path, puerto: int, mensaje: str):
    (repo / "docker-compose.yml").write_text(COMPOSE.format(puerto=puerto))
    git("add", "docker-compose.yml", cwd=repo)
    git("-c", "user.name=test", "-c", "user.email=test@test", "commit", "-q", "-m", mensaje, cwd=repo)


@pytest.fixture
def repo_deseado(tmp_path):
    """Repo Git real con el estado deseado (como repos/estado-deseado)."""
    repo = tmp_path / "estado-deseado"
    repo.mkdir()
    git("init", "-q", "-b", "main", cwd=repo)
    commit(repo, 8085, "Estado inicial")
    return repo
