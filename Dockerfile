FROM python:3.11-slim

# Git para clonar/actualizar el repo del estado deseado
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Docker CLI + plugin Docker Compose v2 (desde la imagen oficial)
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:27-cli /usr/local/libexec/docker/cli-plugins/docker-compose /usr/local/libexec/docker/cli-plugins/docker-compose

# El repo montado pertenece al usuario del host: evitamos el error "dubious ownership" de Git
RUN git config --system --add safe.directory '*'

WORKDIR /app

# Dependencias primero para aprovechar la caché de capas
COPY controller/requirements.txt /app/controller/requirements.txt
RUN pip install --no-cache-dir -r /app/controller/requirements.txt

COPY controller/ /app/controller/
