# 📚 Documentación Técnica Ticket System API

Este documento complementa el README y detalla la arquitectura, endpoints, modelos y mejores prácticas del sistema.

---

## Índice
- [Arquitectura General](#arquitectura-general)
- [Modelos de Datos](#modelos-de-datos)
- [Endpoints Principales](#endpoints-principales)
- [Esquemas de Respuesta](#esquemas-de-respuesta)
- [Flujos de Autenticación y Roles](#flujos-de-autenticación-y-roles)
- [Métricas y Dashboards](#métricas-y-dashboards)
- [Testing y Buenas Prácticas](#testing-y-buenas-prácticas)

---

## Arquitectura General
- **FastAPI** como backend principal
- **PostgreSQL** para datos relacionales
- **InfluxDB** para métricas y eventos
- **Grafana** para visualización
- **Docker Compose** para orquestación

## Modelos de Datos
- **User**: id, email, password_hash, full_name, role (ADMIN/AGENT/USER)
- **Ticket**: id, title, description, priority, status, creator_id, assigned_agent_id, timestamps
- **Comment**: id, ticket_id, user_id, content, created_at

## Endpoints Principales
- `/api/v1/auth/register` - Registro de usuario
- `/api/v1/auth/login` - Login y obtención de JWT
- `/api/v1/tickets/` - CRUD de tickets
- `/api/v1/tickets/{id}/comments` - CRUD de comentarios
- `/api/v1/tickets/{id}/assign` - Asignar agente
- `/api/v1/analytics/dashboard` - Dashboard de métricas
- `/api/v1/analytics/agent/{id}` - Métricas por agente

## Esquemas de Respuesta
- Todos los endpoints devuelven objetos JSON con campos claros y tipados.
- Ejemplo de respuesta de ticket:
```json
{
  "id": 1,
  "title": "Error en login",
  "description": "No puedo acceder al sistema",
  "priority": "high",
  "status": "open",
  "creator_id": 1,
  "assigned_agent_id": 2,
  "created_at": "2025-12-15T18:00:00Z",
  "updated_at": null,
  "resolved_at": null
}
```

## Flujos de Autenticación y Roles
- **JWT**: Login devuelve un token que debe enviarse en `Authorization: Bearer <token>`
- **Roles**:
  - USER: Solo sus tickets y comentarios
  - AGENT: Tickets asignados y sin asignar
  - ADMIN: Acceso total

## Métricas y Dashboards
- **Métricas**: Cada acción relevante (crear, asignar, resolver) genera un evento en InfluxDB
- **Dashboards**: Grafana consume métricas para mostrar KPIs, tiempos, distribución, etc.

## Testing y Buenas Prácticas
- Tests automáticos con Pytest cubren autenticación, tickets, comentarios y analytics
- Cobertura recomendada >80%
- Usa fixtures para datos de prueba
- Sigue PEP8 y type hints

---

**Autor:** Adrián Félix
**Contacto:** guerofelix234@gmail.com
**Última actualización:** Diciembre 2025
