# GitOps Compose Controller

Herramienta **DevOps / GitOps** para gestionar despliegues locales usando **Git como fuente de verdad** y **Docker Compose**, sin necesidad de Kubernetes.

Este proyecto implementa un **controlador GitOps** que detecta cambios en un repositorio Git (estado deseado) y reconcilia automáticamente el estado real del sistema.

---

## 🚀 ¿Qué problema resuelve?

En muchos entornos DevOps:
- Los cambios se aplican manualmente
- No hay trazabilidad clara
- El estado real puede diferir del esperado

Este proyecto demuestra el enfoque **GitOps**:
- **Git define el estado deseado**
- Un **controller** aplica y mantiene ese estado
- El sistema converge automáticamente

Todo de forma **local, reproducible y sin coste**.

---

## 🧠 Filosofía del proyecto

- ❌ No es una aplicación web tradicional
- ❌ No necesita frontend
- ✅ Git es la interfaz principal
- ✅ La terminal (CLI) es el dashboard
- ✅ La API REST expone el estado del sistema

Este enfoque es habitual en herramientas DevOps reales como Terraform, Ansible, Flux o Helm.

---

## 🧱 Arquitectura

- **Controller GitOps**
  - Clona y sincroniza un repo Git
  - Detecta nuevos commits
  - Ejecuta `docker-compose up`
  - Mantiene auditoría de estado

- **API REST (FastAPI)**
  - `GET /health`
  - `GET /estado`

- **Servicio de ejemplo**
  - NGINX (solo para demostrar despliegue)

- **Docker + Docker Compose**
  - Controller y API dockerizados
  - Volúmenes compartidos
  - Acceso al Docker del host

---

## 📂 Estructura del proyecto

gitops-compose-controller/
├─ controller/ # Lógica GitOps + API
├─ repos/
│ └─ estado-deseado/ # Repo Git con docker-compose.yml
├─ docker-compose.yml # Infraestructura del controller
├─ Dockerfile
├─ Makefile
└─ README.md


---

## ⚙️ Requisitos

- Docker
- Docker Compose
- Git
- Make

No se requiere Kubernetes.

---

## ▶️ Puesta en marcha rápida

```bash
make up
API: http://localhost:8090

Estado: http://localhost:8090/estado

🔄 Uso GitOps (ejemplo)
Cambiar el puerto del servicio
make cambiar-puerto PUERTO=8099
Esto:

Modifica el estado deseado en Git

Crea un commit automáticamente

El controller detecta el cambio

Docker recrea el servicio

Acceso:
http://localhost:8099

⏪ Rollback (volver atrás)
cd repos/estado-deseado
git revert HEAD
El controller aplicará automáticamente el estado anterior.

🖥️ Comandos útiles
make estado            # Ver estado actual (API)
make logs-controller   # Logs del controller
make logs-api          # Logs de la API
make down              # Parar servicios

📡 API
Healthcheck
GET /health

Estado del sistema
GET /estado
Devuelve:

Último commit aplicado

Última aplicación

Evento actual

Errores (si existen)

Estado de Docker Compose
