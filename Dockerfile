FROM python:3.11-slim

# Paquetes necesarios: git + docker CLI + docker-compose
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl docker.io docker-compose \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos el código del controller
COPY controller/ /app/controller/

# Dependencias API
RUN pip install --no-cache-dir -r /app/controller/requirements.txt
