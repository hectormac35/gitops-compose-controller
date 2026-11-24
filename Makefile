.PHONY: ayuda bootstrap up down reiniciar logs logs-controller logs-api estado historial health limpiar-web cambiar-puerto test demo

# Ruta al repo Git del estado deseado
ESTADO_DESEADO_REPO=./repos/estado-deseado

ayuda:
	@echo "Comandos disponibles:"
	@echo "  make bootstrap             -> Crea el repo Git del estado deseado (solo la primera vez)"
	@echo "  make up                    -> Levanta controller + API (docker compose)"
	@echo "  make down                  -> Para y elimina contenedores"
	@echo "  make reiniciar             -> Reinicia los servicios"
	@echo "  make logs                  -> Logs de todos los servicios"
	@echo "  make logs-controller       -> Logs del controller"
	@echo "  make logs-api              -> Logs de la API"
	@echo "  make estado                -> Consulta el estado (API /estado)"
	@echo "  make historial             -> Últimos eventos (API /historial)"
	@echo "  make test                  -> Tests del controlador y la API"
	@echo "  make demo                  -> Demo: cambio por commit, deriva y rollback"
	@echo "  make health                -> Healthcheck (API /health)"
	@echo "  make limpiar-web           -> Elimina el contenedor gitops_web"
	@echo "  make cambiar-puerto PUERTO=8099 -> Cambia el puerto y hace commit GitOps"

bootstrap:
	@./scripts/bootstrap_env_repo.sh

up: bootstrap
	docker compose up --build -d
	@echo "✅ Levantado. API: http://localhost:8090"

down:
	docker compose down
	@echo "🛑 Parado."

reiniciar:
	docker compose restart
	@echo "🔄 Reiniciado."

logs:
	docker compose logs -f

logs-controller:
	docker compose logs -f controller

logs-api:
	docker compose logs -f api

estado:
	@curl -s http://localhost:8090/estado | python3 -m json.tool || true

historial:
	@curl -s http://localhost:8090/historial | python3 -m json.tool || true

health:
	@curl -s http://localhost:8090/health | python3 -m json.tool || true

limpiar-web:
	@docker rm -f gitops_web >/dev/null 2>&1 || true
	@echo "🧹 Contenedor gitops_web eliminado (si existía)."

cambiar-puerto:
	@if [ -z "$(PUERTO)" ]; then \
		echo "❌ Debes indicar el puerto: make cambiar-puerto PUERTO=8099"; \
		exit 1; \
	fi
	@echo "🔧 Cambiando puerto a $(PUERTO)..."
	@sed -i -E 's/[0-9]+:80/$(PUERTO):80/' $(ESTADO_DESEADO_REPO)/docker-compose.yml
	@cd $(ESTADO_DESEADO_REPO) && git add docker-compose.yml
	@cd $(ESTADO_DESEADO_REPO) && git commit -m "Cambiar puerto a $(PUERTO)"
	@echo "✅ Puerto cambiado y commit realizado. GitOps aplicará el cambio automáticamente."

test:
	cd controller && python3 -m pip install -q -r requirements-dev.txt && python3 -m pytest -q

demo:
	@./scripts/demo.sh
