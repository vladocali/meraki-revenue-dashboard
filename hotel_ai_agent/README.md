# Hotel AI Agent (Modo Sugerencia)

Agente de IA completo para revenue management hotelero con **dashboard web profesional**, construido en Python 3.12+ con arquitectura modular.

## 🎯 Características Principales

### 🤖 Agente de Revenue Management (Backend)
- Análisis automático de ocupación (próximos 7 días)
- Lectura de precios desde `parametros` tabla
- Análisis histórico de reservas desde `datos`
- Scraping de competencia (Airbnb/Booking)
- Detección de fechas especiales
- Generación diaria de recomendaciones (2:00 AM)
- **Modo sugerencia**: Sin cambios reales en BD

### 🏨 Dashboard Web Profesional (Frontend)
- **Home**: KPIs, ocupación, ingresos, alertas IA
- **Ocupación**: Mapa de calor, gráficos, detalles
- **Precios**: Sugerencias, aprobación manual, histórico
- **Competencia**: Análisis comparativo, filtros
- **Reportes**: Descargas en TXT/CSV/JSON, análisis IA
- Gráficos interactivos con Plotly
- Integración con OpenAI para análisis inteligente
- Sistema de caché y logs
- Interfaz moderna y responsiva

## 🚀 Inicio Rápido

### 1. Instalación (2 minutos)
```bash
# Ir a proyecto
cd c:\laragon\www\meraki\hotel_ai_agent

# Instalar dependencias
pip install -r requirements.txt

# Copiar .env y configurar
copy .env.example .env  # Windows
# O editar los valores de BD y OpenAI si lo deseas
```

### 2. Ejecutar Dashboard (Recomendado)
```bash
# Windows - Doble click
run_dashboard.bat

# O terminal
cd dashboard
streamlit run app.py

# Abrirá: http://localhost:8501
```

### 3. Ejecutar Agente de IA
```bash
# Ejecutar análisis ahora
python main.py --run-now

# Capturar solo competencia ahora
python main.py --competitor-now

# Activar scheduler (2:00 AM diario)
python main.py --scheduler

# Activar recolector automático de competencia (cada 3 horas por defecto)
python main.py --competitor-scheduler
```

## 📁 Estructura

```text
hotel_ai_agent/
├── 📋 README.md                   # Este archivo
├── 📋 QUICKSTART.md               # Guía de inicio rápido
├── main.py                        # Entrada del agente
├── config.py                      # Config compartida
├── .env                           # Configuración (crear desde .env.example)
├── requirements.txt               # Dependencias Python
│
├── 🏨 dashboard/                  # NUEVO: Dashboard Streamlit
│   ├── app.py                     # Aplicación principal
│   ├── config.py                  # Config del dashboard
│   ├── README.md                  # Docs completas del dashboard
│   ├── QUICKSTART.md              # Inicio rápido dashboard
│   ├── .streamlit/config.toml     # Config Streamlit
│   │
│   ├── pages/                     # 5 páginas del dashboard
│   │   ├── 01_home.py             # Dashboard principal
│   │   ├── 02_ocupacion.py        # Análisis de ocupación
│   │   ├── 03_precios.py          # Gestión de precios
│   │   ├── 04_competencia.py      # Análisis de competencia
│   │   └── 05_reportes.py         # Generación de reportes
│   │
│   ├── components/                # Componentes reutilizables
│   │   ├── metrics.py             # Tarjetas de métricas
│   │   └── charts.py              # Gráficos interactivos
│   │
│   ├── services/                  # Servicios backend
│   │   ├── dashboard_db.py        # Conexión a BD
│   │   ├── analytics_service.py   # Cálculos de análisis
│   │   └── ai_insights.py         # Integración OpenAI
│   │
│   ├── utils/                     # Utilidades
│   │   ├── formatters.py          # Formateos de datos
│   │   ├── logger.py              # Sistema de logs
│   │   └── cache.py               # Caché de sesión
│   │
│   └── data/                      # Datos de demostración
│       └── mock_data.py           # Generador de datos simulados
│
├── agents/                        # Lógica de agente IA
│   └── revenue_agent.py           # Orchestración principal
│
├── tools/                         # Herramientas especializadas
│   ├── db_tools.py                # Acceso a BD
│   ├── pricing_tools.py           # Lógica de precios
│   ├── competitor_tools.py        # Scraping de competencia
│   └── report_tools.py            # Exportación de reportes
│
├── services/                      # Servicios de negocio
│   ├── occupancy_service.py       # Cálculos de ocupación
│   ├── pricing_service.py         # Gestión de tarifas
│   └── competitor_service.py      # Análisis de competencia
│
├── reports/                       # Reportes generados
│   ├── example_report.json
│   └── example_report.txt
│
├── logs/                          # Archivos de log
│   └── hotel_ai_agent.log
│
├── run_dashboard.bat              # NUEVO: Launcher Windows
└── run_dashboard.sh               # NUEVO: Launcher Linux/Mac
```
│   └── report_tools.py
├── services/
│   ├── occupancy_service.py
│   ├── competitor_service.py
│   └── pricing_service.py
├── reports/
└── logs/
```

## ⚙️ Requisitos

- **Python 3.10+** (mínimo Python 3.10, recomendado 3.12)
- **MySQL/MariaDB** con tablas existentes (`datos`, `habitaciones`, `parametros`, `cotizacion_fechas_especiales`)
- **Navegador moderno** (Chrome, Firefox, Safari, Edge)
- **OpenAI API key** (opcional, para análisis IA avanzado)

## 🔧 Instalación

### Opción 1: Instalación Automática (Recomendado)

**Windows:**
```bash
# Solo doble-click en:
run_dashboard.bat

# Se instalarán dependencias y abrirá el dashboard automáticamente
```

**Linux/Mac:**
```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

### Opción 2: Instalación Manual

```bash
# 1. Ir a carpeta del proyecto
cd c:\laragon\www\meraki\hotel_ai_agent

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar plantilla de configuración
copy .env.example .env  # Windows
cp .env.example .env   # Linux/Mac
```

## 📝 Configuración `.env`

Crear o editar archivo `.env` en raíz del proyecto:

```env
# ===== BASE DE DATOS =====
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=meraki
DB_USER=root
DB_PASSWORD=

# ===== OPENAI (Opcional - para IA avanzada) =====
OPENAI_API_KEY=sk-your-key-here

# ===== LOGGING =====
LOG_LEVEL=INFO

# ===== PRECIOS =====
MIN_PRICE_FACTOR=0.85
MAX_PRICE_FACTOR=1.20
DEFAULT_MIN_PRICE=100000
DEFAULT_MAX_PRICE=500000

# ===== COMPETENCIA =====
COMPETITOR_URLS=https://www.airbnb.com/...

# ===== SCHEDULER =====
DAILY_RUN_TIME=02:00
COMPETITOR_POLL_MINUTES=180
```

## 🚀 Uso

### Opción 1: Dashboard Web (Recomendado para Usuarios)

**Inicio rápido (2 minutos):**

```bash
# Windows - Solo doble click
run_dashboard.bat

# O terminal
cd dashboard
streamlit run app.py

# Se abrirá en http://localhost:8501
```

**Características:**
- 📊 **Home**: KPIs, gráficos, alertas IA
- 📅 **Ocupación**: Mapa de calor, detalles
- 💰 **Precios**: Sugerencias con aprobación
- 🎯 **Competencia**: Análisis comparativo
- 📑 **Reportes**: Exportar datos

📚 [Ver guía completa del dashboard →](dashboard/README.md)

### Opción 2: Agente IA (Para Análisis Automático)

**Ejecutar análisis manual:**

```bash
python main.py --run-now
```

Genera:
- Análisis de ocupación
- Sugerencias de precios
- Análisis de competencia
- Reportes TXT/JSON en `/reports`

**Programar ejecución diaria (2:00 AM):**

```bash
python main.py --scheduler
```

Mantiene ejecutándose en background y ejecuta análisis todos los días a las 2:00 AM.

**Recolector automático de competencia:**

```bash
python main.py --competitor-scheduler
```

Captura precios de competencia cada 3 horas por defecto y los guarda en `competitor_price_snapshots`.

### Archivos Generados

```
reports/
├── revenue_report_20240521_140305.json    # Datos completos
└── revenue_report_20240521_140305.txt     # Formato legible

logs/
└── hotel_ai_agent.log                     # Registro de ejecuciones
```

## 📊 Consultas SQL Base

### Ocupación próximos 7 días

```sql
SELECT 
    CURDATE() + INTERVAL 0 DAY as date,
    COUNT(DISTINCT d.Habitacion) as occupied_rooms
FROM datos d
WHERE DATE(d.CheckIn) <= CURDATE() + INTERVAL 7 DAY
  AND DATE(d.CheckOut) > CURDATE()
  AND d.EstadoOperacion NOT IN ('CANCELADA', 'No show')
GROUP BY CURDATE() + INTERVAL 0 DAY;
```


### Precios actuales por habitación

```sql
SELECT 
    parametro,
    valor as price
FROM parametros
WHERE parametro LIKE 'CotizacionHab%'
ORDER BY parametro;
```

### Histórico de reservas (90 días)

```sql
SELECT 
    DATE(CheckIn) as date,
    COUNT(*) as bookings,
    AVG(Valor) as avg_price,
    COUNT(DISTINCT Huesped) as unique_guests
FROM datos
WHERE CheckIn >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
  AND EstadoOperacion NOT IN ('CANCELADA', 'No show')
GROUP BY DATE(CheckIn)
ORDER BY date DESC;
```

## 📋 Reglas de Decisión

El agente implementa lógica de pricing basada en:

| Factor | Acción |
|--------|--------|
| Ocupación < 40% | ⬇️ Bajar 5-15% |
| Ocupación 40-70% | ➡️ Mantener o ajustar |
| Ocupación 70-85% | ⬆️  Subir 5-10% |
| Ocupación > 85% | ⬆️ Subir 10-20% |
| **Fin de semana** | 🔥 Estrategia agresiva |
| **Evento especial** | 🔥 Estrategia agresiva |
| **Precio competencia** | Posicionarse competitivamente |

Siempre respeta:
- ✅ Precio mínimo: `MIN_PRICE_FACTOR × precio_base`
- ✅ Precio máximo: `MAX_PRICE_FACTOR × precio_base`

## 🌐 Integración con Competencia

Se rastrea automáticamente:
- Airbnb (análisis de precios publicados)
- Booking.com (cuando está disponible)
- Competidores locales (URLs configurables)

Scraping **ligero y respetuoso**:
- User-agent identificable
- Timeouts razonables
- No crawling masivo
- Preparado para APIs oficiales (Airbnb, Booking partner)

Datos guardados en tabla `competitor_price_snapshots`:
```sql
SELECT 
    source,
    AVG(nightly_price) as avg_price,
    COUNT(*) as samples,
    MAX(captured_at) as last_update
FROM competitor_price_snapshots
WHERE captured_at >= DATE_SUB(NOW(), INTERVAL 48 HOUR)
GROUP BY source;
```

### URLs de competencia

Para que el recolector genere datos reales, configura `COMPETITOR_URLS` con páginas públicas que muestren precio visible. Ejemplos:

```env
COMPETITOR_URLS=https://www.booking.com/searchresults.es.html?ss=Cali%2C%20Colombia,https://www.airbnb.com/s/Cali--Valle-del-Cauca--Colombia/homes
```

Lo ideal es usar URLs de anuncios concretos o páginas de búsqueda con precios visibles.

## 🔐 Seguridad e IA

### Modo Sugerencia (Actual)
- ✅ **Sin cambios en BD**: Todo es visualización
- ✅ **Aprobación manual**: Dashboard permite ver antes de aplicar
- ✅ **Auditoría**: Logs de todas las acciones
- ✅ **Fallback**: IA opcional, funciona sin OpenAI

### Análisis IA Integrado
- Local: Análisis predeterminados si OpenAI no disponible
- OpenAI: Explicaciones naturales si API key configurada
- Ambos: Sin riesgo, solo análisis/recomendaciones

## 🚀 Próximos Pasos Recomendados

1. **Workflow de Aprobación** (Fase 2)
   - Interfaz para revisar sugerencias
   - Aprobación selectiva (por habitación/fecha)
   - Lotes de cambios programados
   - Auditoría completa de cambios

2. **Automatización Selectiva**
   - Apruevedores automáticos (ej: cambios < 5%)
   - Notificaciones por Slack/Email
   - Dashboard de cambios ejecutados

3. **Optimizaciones**
   - Cálculo de elasticidad precio-demanda
   - Machine Learning para predicciones
   - APIs directas (Airbnb, Booking)
   - Dashboard analytics históricos

## 📞 Soporte y Documentación

- 📖 [Dashboard README](dashboard/README.md) - Guía completa del frontend
- 🚀 [QUICKSTART Dashboard](dashboard/QUICKSTART.md) - Inicio en 2 minutos
- 📚 [QUICKSTART General](QUICKSTART.md) - Guía de todo el proyecto
- 🐛 Errores: Ver `logs/hotel_ai_agent.log`

## 📜 Licencia

Uso interno. Proyecto de revenue management para hoteles.

---

**Versión:** 1.0.0  
**Última actualización:** Mayo 2024  
**Status:** ✅ Producción  
**Modo:** 🔐 Sugerencia (sin cambios automáticos)
