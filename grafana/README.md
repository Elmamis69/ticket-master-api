# 📊 Grafana Dashboards Configuration

Este directorio contiene la configuración y dashboards de Grafana para el sistema de tickets.

## 📁 Estructura

```
grafana/
├── provisioning/
│   ├── datasources/
│   │   └── influxdb.yml          # Configuración de InfluxDB como datasource
│   └── dashboards/
│       └── default.yml            # Configuración de auto-provisioning
└── dashboards/
    └── ticket-dashboard.json      # Dashboard principal del sistema
```

## 🚀 Acceso a Grafana

1. **URL**: http://localhost:3000
2. **Usuario**: `admin` (por defecto)
3. **Contraseña**: `admin` (por defecto)

> Puedes cambiar las credenciales en el archivo `.env` con las variables `GRAFANA_USER` y `GRAFANA_PASSWORD`

## 📊 Dashboards Disponibles

### 1. Ticket System Dashboard

Dashboard principal con las siguientes visualizaciones:

#### Métricas Generales
- **Total Tickets Created**: Gauge que muestra el total de tickets creados
- **Tickets Created Over Time**: Gráfico de línea temporal de tickets creados

#### Análisis por Categoría
- **Tickets by Priority**: Gráfico de pastel mostrando distribución por prioridad (low, medium, high, critical)
- **Top 10 Agents by Assignments**: Tabla con los agentes con más tickets asignados

#### Performance
- **Average Resolution Time**: Gauge mostrando tiempo promedio de resolución en segundos
- **Ticket Status Changes Over Time**: Gráfico de barras apiladas mostrando cambios de estado por día

## 🔧 Configuración del Datasource

El datasource de InfluxDB se configura automáticamente con:

- **URL**: `http://influxdb:8086`
- **Organization**: `ticket-system`
- **Bucket**: `ticket-metrics`
- **Query Language**: Flux
- **Token**: Se obtiene de la variable de entorno `INFLUXDB_TOKEN`

## 📝 Queries de Flux Utilizadas

### Total de Tickets
```flux
from(bucket: "ticket-metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "ticket_created")
  |> count()
```

### Tickets por Prioridad
```flux
from(bucket: "ticket-metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "ticket_created")
  |> filter(fn: (r) => r["_field"] == "count")
  |> group(columns: ["priority"])
  |> sum()
```

### Tiempo Promedio de Resolución
```flux
from(bucket: "ticket-metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "ticket_resolved")
  |> filter(fn: (r) => r["_field"] == "resolution_time_seconds")
  |> mean()
```

### Top Agentes
```flux
from(bucket: "ticket-metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "ticket_assigned")
  |> group(columns: ["assigned_agent_id"])
  |> count()
  |> sort(desc: true)
  |> limit(n: 10)
```

## 🎨 Personalización

### Agregar Nuevos Paneles

1. Accede a Grafana en http://localhost:3000
2. Ve al dashboard "Ticket System Dashboard"
3. Haz clic en "Add panel"
4. Selecciona el datasource "InfluxDB"
5. Escribe tu query en Flux
6. Configura visualización y guarda

### Exportar Dashboard

1. Ve al dashboard que quieres exportar
2. Haz clic en el ícono de configuración (⚙️)
3. Selecciona "JSON Model"
4. Copia el JSON y guárdalo en `grafana/dashboards/`

## 🔄 Auto-Provisioning

Los dashboards se cargan automáticamente al iniciar Grafana gracias a la configuración en:
- `provisioning/dashboards/default.yml`
- `provisioning/datasources/influxdb.yml`

Cualquier cambio en los archivos JSON se refleja automáticamente (puede tomar ~10 segundos).

## 🐛 Troubleshooting

### Datasource no conecta a InfluxDB

1. Verifica que InfluxDB esté corriendo:
   ```bash
   docker-compose ps influxdb
   ```

2. Verifica el token en `.env`:
   ```bash
   echo $INFLUXDB_TOKEN
   ```

3. Reinicia Grafana:
   ```bash
   docker-compose restart grafana
   ```

### No aparecen datos en los gráficos

1. Verifica que se estén registrando métricas:
   ```bash
   docker-compose logs api | grep "Metric recorded"
   ```

2. Accede a InfluxDB UI (http://localhost:8086) y verifica que existan datos en el bucket `ticket-metrics`

3. Ajusta el rango de tiempo en Grafana (esquina superior derecha)

### Dashboard no se carga automáticamente

1. Verifica los logs de Grafana:
   ```bash
   docker-compose logs grafana
   ```

2. Importa manualmente desde: Settings → Data Sources → Add data source

## 📈 Mejores Prácticas

- **Rangos de Tiempo**: Usa rangos apropiados (7d, 30d) para análisis significativos
- **Refresh Rate**: Configura auto-refresh en dashboards en vivo
- **Alertas**: Configura alertas para métricas críticas (SLA, tiempos de respuesta)
- **Variables**: Usa variables de template para filtrar por agente, prioridad, etc.

## 🎯 Próximos Dashboards

- [ ] Dashboard de SLA y compliance
- [ ] Dashboard de análisis de agentes individual
- [ ] Dashboard de tendencias semanales/mensuales
- [ ] Dashboard de satisfacción del cliente (cuando se implemente)

---

**Autor**: Adrián Félix  
**Última actualización**: Diciembre 2025
