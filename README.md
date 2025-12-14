# 🎫 Ticket System API

Sistema de gestión de tickets similar a **Cherwell** o sistemas de **Service Desk**, construido con FastAPI, PostgreSQL, InfluxDB y Grafana.

---

## 📋 Descripción

Este proyecto es una API REST para gestionar tickets de soporte técnico con las siguientes características:

- ✅ Autenticación JWT con roles (ADMIN, AGENT, USER)
- ✅ CRUD completo de tickets con estados y prioridades
- ✅ Sistema de comentarios en tickets
- ✅ Métricas en tiempo real con InfluxDB
- ✅ Dashboards de visualización con Grafana
- ✅ Activity logging de todas las acciones
- ✅ Dockerizado con Docker Compose

---

## 🛠️ Stack Tecnológico

- **Python** 3.11+
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL 16** - Base de datos relacional
- **InfluxDB 2.x** - Base de datos de series temporales para métricas
- **Grafana** - Visualización de métricas
- **SQLAlchemy** - ORM para PostgreSQL
- **Alembic** - Migraciones de base de datos
- **JWT** - Autenticación con tokens
- **Docker & Docker Compose** - Containerización
- **Pytest** - Testing

---

## 📁 Estructura del Proyecto

```
ticket-system-api/
├── app/
│   ├── api/
│   │   └── v1/              # Endpoints versión 1
│   ├── core/
│   │   ├── config.py        # Configuración
│   │   ├── security.py      # JWT y passwords
│   │   └── logging.py       # Logging
│   ├── db/
│   │   ├── session.py       # PostgreSQL
│   │   ├── influxdb.py      # InfluxDB
│   │   └── deps.py          # Dependencies
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── main.py              # FastAPI app
├── tests/                   # Tests con Pytest
├── migrations/              # Alembic migrations
├── grafana/                 # Dashboards de Grafana
├── docker-compose.yml       # Orquestación de servicios
├── Dockerfile               # Imagen de la API
├── requirements.txt         # Dependencias Python
└── .env.example             # Variables de entorno de ejemplo
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Docker** y **Docker Compose** instalados
- **Python 3.11+** (solo si quieres correr sin Docker)
- **Git**

### 1. Clonar el repositorio

```bash
git clone https://github.com/Elmamis69/ticket-master-api.git
cd ticket-system-api
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` según tus necesidades. Las configuraciones por defecto funcionan para desarrollo local.

**Variables importantes:**
- `SECRET_KEY`: Genera una clave segura con `openssl rand -hex 32`
- `DATABASE_URL`: Conexión a PostgreSQL
- `INFLUXDB_TOKEN`: Token de InfluxDB

### 3. Levantar servicios con Docker Compose

```bash
docker-compose up -d
```

Esto levantará:
- **PostgreSQL** en `localhost:5432`
- **InfluxDB** en `localhost:8086`
- **Grafana** en `localhost:3000`
- **API FastAPI** en `localhost:8000`

### 4. Verificar que todo funciona

```bash
curl http://localhost:8000/health
```

Deberías ver: `{"status":"healthy"}`

### 5. Ver logs

```bash
docker-compose logs -f api
```

---

## 📊 Acceso a los Servicios

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **API** | http://localhost:8000 | Ver archivo `.env` |
| **Docs interactivos** | http://localhost:8000/docs | - |
| **PostgreSQL** | localhost:5432 | Ver archivo `.env` (POSTGRES_USER/POSTGRES_PASSWORD) |
| **InfluxDB** | http://localhost:8086 | Ver archivo `.env` (INFLUXDB_USERNAME/INFLUXDB_PASSWORD) |
| **Grafana** | http://localhost:3000 | Ver archivo `.env` (GRAFANA_USER/GRAFANA_PASSWORD) |

---

## 🔧 Comandos Útiles

### Crear una migración (después de modificar modelos)

```bash
docker-compose exec api alembic revision --autogenerate -m "descripción del cambio"
```

### Aplicar migraciones

```bash
docker-compose exec api alembic upgrade head
```

### Revertir última migración

```bash
docker-compose exec api alembic downgrade -1
```

### Ejecutar tests

```bash
docker-compose exec api pytest
```

### Ver cobertura de tests

```bash
docker-compose exec api pytest --cov=app --cov-report=html
```

### Entrar al contenedor de la API

```bash
docker-compose exec api bash
```

### Reiniciar solo la API

```bash
docker-compose restart api
```

### Detener todos los servicios

```bash
docker-compose down
```

### Limpiar todo (⚠️ borra los datos)

```bash
docker-compose down -v
```

---

## 🧪 Testing

El proyecto incluye tests con Pytest. Para ejecutarlos:

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app

# Solo un archivo
pytest tests/test_auth.py

# Con verbose
pytest -v
```

---

## 📖 Documentación de la API

Una vez levantado el proyecto, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 👥 Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **USER** | Crear tickets, ver sus propios tickets, comentar en sus tickets |
| **AGENT** | Ver todos los tickets, resolver tickets asignados, reasignar tickets |
| **ADMIN** | Acceso total, gestión de usuarios, configuración del sistema |

---

## 📈 Métricas en InfluxDB

El sistema registra automáticamente:

- 📊 Tickets creados por día
- ⏱️ Tiempo de resolución promedio
- 📌 Tickets por estado
- 🔥 Tickets por prioridad
- 👤 Tickets por agente
- 📞 SLA (tiempo de primera respuesta)

---

## 📊 Grafana Dashboards

Los dashboards muestran:

- Total de tickets activos
- Gráfico de tendencias (tickets resueltos vs pendientes)
- Distribución por prioridad (pie chart)
- Tiempo promedio de resolución (gauge)
- Tickets por agente (bar chart)
- Análisis semanal/mensual

---

## 🗂️ Roadmap de Implementación

### ✅ Fase 1: Setup (COMPLETADA)
- [x] Estructura de proyecto
- [x] Docker Compose
- [x] Configuración base
- [x] Conexiones a BD

### ✅ Fase 2: Autenticación (COMPLETADA)
- [x] Modelos User
- [x] JWT auth
- [x] RBAC
- [x] Endpoints: register, login, /me

### ✅ Fase 3: Tickets CRUD (COMPLETADA)
- [x] Modelo Ticket con estados y prioridades
- [x] Schemas Pydantic completos
- [x] Endpoints CRUD con RBAC
- [x] Asignación de agentes
- [x] Migraciones de base de datos

### ✅ Fase 4: Comentarios (COMPLETADA)
- [x] Modelo Comment con CASCADE delete
- [x] Schemas Pydantic completos
- [x] Endpoints CRUD con RBAC
- [x] Rutas anidadas bajo tickets
- [x] Migraciones de base de datos

### ✅ Fase 5: Métricas (COMPLETADA)
- [x] Integración InfluxDB
- [x] Servicio de métricas (metrics_service.py)
- [x] Registro automático de eventos (crear ticket, cambio estado, asignación)
- [x] Endpoints analytics:
  - [x] `/api/v1/analytics/dashboard` - Dashboard completo
  - [x] `/api/v1/analytics/agent/{id}` - Estadísticas por agente
- [x] Schemas para analytics
- [x] Métricas de tickets, prioridades, estados y agentes

### 🚧 Fase 6: Grafana (PENDIENTE)
- [ ] Configurar datasources de InfluxDB
- [ ] Crear dashboards visuales
- [ ] Conectar métricas a gráficos

### 🚧 Fase 7: Testing (PENDIENTE)
- [x] Tests de autenticación (8/8 pasando)
- [ ] Tests de tickets
- [ ] Tests de comentarios
- [ ] Tests de analytics
- [ ] Cobertura >80%

---

## 🤝 Contribución

Este es un proyecto de práctica para aprendizaje. Si quieres contribuir:

1. Haz fork del proyecto
2. Crea una rama con tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📝 Notas de Desarrollo

- El proyecto usa **SQLAlchemy 2.0** con async support
- Las migraciones se manejan con **Alembic**
- El código sigue **PEP 8** y usa **type hints**
- Los endpoints están organizados por versión (`/api/v1/`)
- Logs estructurados para producción
- Soft delete en lugar de borrado físico

---

## 📄 Licencia

Este proyecto es de código abierto para fines educativos.

---

## 🆘 Troubleshooting

### Error: "Cannot connect to PostgreSQL"
```bash
docker-compose down
docker-compose up -d postgres
# Espera 10 segundos
docker-compose up -d api
```

### Error: "InfluxDB connection refused"
```bash
docker-compose restart influxdb
docker-compose logs influxdb
```

### Error: "Port already in use"
Cambia los puertos en `docker-compose.yml` o libera el puerto:
```bash
lsof -ti:8000 | xargs kill -9  # Para el puerto 8000
```

---

## Author
Adrián Félix

Software Engineering

Passionate about Android Developer, Full Stack and iOS development and clean architecture.

GitHub: @Elmamis69
Email: guerofelix234@gmail.com

**License**
This project is licensed under the MIT License.

## Getting Started
1. Clone the repository:
   ```bash
   https://github.com/Elmamis69/ticket-master-api.git
