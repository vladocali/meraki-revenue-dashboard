# 🏨 Revenue Management Dashboard

## Descripción General

Dashboard web profesional de Revenue Management para hoteles/hospedajes tipo Airbnb. Interfaz moderna construida con Streamlit y Plotly que permite:

- **Monitoreo en tiempo real** de ocupación, precios e ingresos
- **Análisis inteligente** con IA (integración OpenAI)
- **Comparativa de competencia** automática
- **Sugerencias de precios** basadas en ocupación y mercado
- **Aprobación manual** de cambios (sin ejecución automática)
- **Reportes exportables** en múltiples formatos

## ✨ Características Principales

### 📊 Dashboard Home
- **KPIs en tiempo real**: Ocupación, ADR, RevPAR, Ingresos proyectados
- **Gráficos interactivos**: Ocupación, ingresos, tendencias
- **Alertas IA**: Recomendaciones automáticas del motor inteligente
- **Top sugerencias**: Precios recomendados por habitación
- **Análisis inteligente**: Explicaciones naturales del contexto
- **Acciones rápidas**: Ejecutar análisis, actualizar competencia, etc.

### 📅 Ocupación
- **Mapa de calor**: Ocupación por habitación y día
- **Gráficos de líneas y barras**: Tendencias de ocupación
- **Detalles por día**: Disponibilidad y reservas
- **Detalles por habitación**: Performance individual
- **Estadísticas**: Máximos, mínimos, promedios

### 💰 Precios
- **Precios actuales**: Listado completo por habitación
- **Sugerencias IA**: Cambios recomendados con razones
- **Botones de aprobación**: Aprobar/rechazar (simulado, sin BD)
- **Historico**: Gráficos de precios históricos
- **Análisis**: Volatilidad, máximos, mínimos

### 🎯 Competencia
- **Comparativas**: Tu precio vs competencia
- **Listado de competidores**: Precios en plataformas
- **Filtros**: Por fecha, plataforma, tipo habitación
- **Analytics**: Media, mín, máx por competidor
- **Posicionamiento**: Identificar oportunidades

### 📑 Reportes
- **Reportes listos**: Descargas rápidas en TXT/CSV
- **Análisis IA detallado**: Explicaciones completas
- **Exportar datos**: JSON, CSV con toda la información
- **Análisis por sección**: Ocupación, precios, competencia

## 🚀 Instalación

### 1. Dependencias del Sistema
```bash
# Windows - requiere Python 3.10+
python --version  # Verificar versión

# Instalación de dependencias
cd c:\laragon\www\meraki\hotel_ai_agent
pip install -r requirements.txt
```

### 2. Configuración del `.env`

```env
# Base de datos
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=meraki
DB_USER=root
DB_PASSWORD=

# OpenAI (opcional, para análisis IA)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Dashboard
LOG_LEVEL=INFO
SUGGESTION_MODE=true

# Precios
MIN_PRICE_FACTOR=0.85
MAX_PRICE_FACTOR=1.20
DEFAULT_MIN_PRICE=100000
DEFAULT_MAX_PRICE=500000

# Competencia
COMPETITOR_URLS=https://www.airbnb.com/...

# Scheduler
DAILY_RUN_TIME=02:00
```

### 3. Instalación desde Microsoft Store (Opcional para desarrollo)
```bash
# Instalar Streamlit CLI
pip install streamlit

# Verificar instalación
streamlit --version
```

## 🎯 Uso

### Ejecutar el Dashboard

```bash
# Opción 1: Desde terminal con Streamlit (Recomendado)
cd c:\laragon\www\meraki\hotel_ai_agent\dashboard
streamlit run app.py

# Opción 2: Con IP específica (para acceso desde red)
streamlit run app.py --server.address 192.168.1.100

# Opción 3: Puerto personalizado
streamlit run app.py --server.port 8502
```

El dashboard se abrirá en `http://localhost:8501`

### Acceder desde Otros Equipos

```bash
# Desde otra computadora en la misma red
http://YOUR_IP:8501

# Ejemplo:
http://192.168.1.50:8501
```

## 📁 Estructura del Proyecto

```
dashboard/
├── app.py                      # Aplicación principal
├── config.py                   # Configuración global
│
├── pages/                      # Páginas (Streamlit)
│   ├── 01_home.py             # Dashboard principal
│   ├── 02_ocupacion.py        # Análisis de ocupación
│   ├── 03_precios.py          # Gestión de precios
│   ├── 04_competencia.py      # Análisis de competencia
│   └── 05_reportes.py         # Generación de reportes
│
├── components/                 # Componentes reutilizables
│   ├── metrics.py             # Tarjetas de métrica
│   └── charts.py              # Gráficos Plotly
│
├── services/                   # Lógica de negocio
│   ├── dashboard_db.py        # Conexión base de datos
│   ├── analytics_service.py   # Cálculos analíticos
│   └── ai_insights.py         # Integración OpenAI
│
├── utils/                      # Utilidades
│   ├── formatters.py          # Formatos de datos
│   ├── logger.py              # Logging
│   └── cache.py               # Caché de sesión
│
├── data/                       # Datos
│   └── mock_data.py           # Datos simulados para demo
│
└── logs/                       # Archivos de log
```

## 🔧 Configuración Avanzada

### Cambiar Tema
Edita `dashboard/config.py` - sección `COLORS`

```python
COLORS = {
    "primary": "#00A86B",        # Verde profesional
    "secondary": "#3B82F6",      # Azul
    "success": "#10B981",        # Verde
    "warning": "#F59E0B",        # Ámbar
    "danger": "#EF4444",         # Rojo
}
```

### Ajustar Caché
```python
# dashboard/config.py
CACHE_TTL = 300  # 5 minutos
MOCK_DATA_TTL = 600  # 10 minutos
```

### Alterar Frecuencia de Análisis
```python
# dashboard/services/dashboard_db.py
self.db.execute_query("""SELECT...""")
# Ajustar queries según necesidad
```

## 📊 Datos Simulados

El dashboard viene con generador de datos simulados (`mock_data.py`) para demostración:

```python
from dashboard.data.mock_data import get_mock_data

# Obtener datos simulados
occupancy = get_mock_data('daily_summary')      # Ocupación
prices = get_mock_data('current_prices')        # Precios
suggestions = get_mock_data('suggestions')      # Sugerencias
competitor = get_mock_data('competitor')        # Competencia
```

Para usar **datos reales** de la BD:

```python
# En cualquier página, reemplazar:
# from dashboard.data.mock_data import get_mock_data
# por:
from dashboard.services.dashboard_db import get_dashboard_db

db = get_dashboard_db()
occupancy = db.get_7day_occupancy()
```

## 🤖 Integración con IA (OpenAI)

El sistema genera automáticamente análisis inteligentes:

### Tipos de Análisis
1. **Ocupación**: Evaluación de niveles y tendencias
2. **Precios**: Estrategia de cambios recomendados
3. **Resumen Ejecutivo**: Síntesis de todo el contexto

### Fallback Automático
Si `OPENAI_API_KEY` no está disponible, el sistema genera análisis locales.

### Uso Manual
```python
from dashboard.services.ai_insights import get_ai_service

ai = get_ai_service()

# Generar insights
insight = ai.generate_occupancy_insight(
    occupancy=0.75,
    trend=0.05,
    forecast_days=7
)
print(insight)
```

## 📈 Métricas Disponibles

### KPIs Principales
| Métrica | Descripción | Fórmula |
|---------|------------|---------|
| **ADR** | Tarifa Diaria Promedio | Revenue / Noches Vendidas |
| **RevPAR** | Ingreso por Habitación Disponible | ADR × Ocupación |
| **Ocupación** | % de habitaciones ocupadas | Ocupadas / Total |
| **RevPAR Potencial** | Ingresos máximos posibles | ADR × Rooms × Days |

## 🔐 Seguridad

✅ **Características de Seguridad:**
- Credenciales en `.env` (no en código)
- Modo sugerencia (sin cambios reales en BD)
- Logs de auditoría de acciones
- Botones de aprobación antes de cambios

⚠️ **Recomendaciones:**
- Ejecutar en intranet privada (VPN si es acceso remoto)
- Cambiar contraseña BD regularmente
- Respaldar `.env` en lugar seguro
- Revisar logs regularmente

## 📝 Logging

Los logs se guardan en `../logs/dashboard_YYYYMMDD.log`

Niveles disponibles: `DEBUG`, `INFO`, `WARNING`, `ERROR`

```bash
# Ver logs más recientes
tail -f ../logs/dashboard_20240521.log

# Windows PowerShell
Get-Content ../logs/dashboard_20240521.log -Tail 50 -Wait
```

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
# O reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error: Conexión a base de datos
```python
# Verificar credenciales en .env
DB_HOST=127.0.0.1      # ✓ Correcto
DB_HOST=localhost      # ✗ No funciona siempre
```

### UI lenta
- Aumentar `CACHE_TTL` en config.py
- Reducir rango de fechas en filtros
- Cerrar otras aplicaciones pesadas

### Gráficos no aparecen
```bash
# Limpiar caché de Streamlit
streamlit cache clear

# Recargar página (F5)
```

## 📦 Despliegue en Producción

### Opción 1: Streamlit Cloud (Recomendado)
```bash
# 1. Subir proyecto a GitHub
# 2. Ir a https://streamlit.io/cloud
# 3. Conectar repositorio
# 4. Configurar secretos en UI
```

### Opción 2: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py"]
```

```bash
# Build y run
docker build -t hotel-dashboard .
docker run -p 8501:8501 hotel-dashboard
```

### Opción 3: Windows Service / Task Scheduler
```batch
# Crear tarea en Task Scheduler
# Ejecutar: streamlit run C:\path\to\dashboard\app.py
# Horario: Encendido automático
```

## 🔄 Actualización del Proyecto

```bash
# Descargar últimas actualizaciones
git pull origin main

# Reinstalar dependencias
pip install -r requirements.txt --upgrade

# Reiniciar dashboard
streamlit cache clear
streamlit run app.py
```

## 📚 Documentación Adicional

- **SQL Queries** → Ver `services/dashboard_db.py`
- **Componentes** → Ver `components/` carpeta
- **Formatos** → Ver `utils/formatters.py`
- **Logging** → Ver `utils/logger.py`

## 🤝 Soporte

Para problemas o sugerencias:
- 📧 Email: support@yourdomain.com
- 🐛 Issues: https://github.com/yourrepo/issues
- 💬 Chat: Discord/Slack channel

## 📜 Licencia

Este proyecto es parte del sistema Hotel AI Agent.
Uso interno solamente.

---

**Última actualización:** Mayo 2024
**Versión:** 1.0.0
**Status:** ✅ Producción
