# 🚀 GUÍA DE INICIO RÁPIDO - Dashboard

**Tiempo estimado: 5 minutos**

## 1️⃣ Instalación Rápida

### Paso 1: Abrir Terminal
```bash
# PowerShell (Windows)
cd c:\laragon\www\meraki\hotel_ai_agent\dashboard

# O GitBash
cd /c/laragon/www/meraki/hotel_ai_agent/dashboard
```

### Paso 2: Instalar Dependencias
```bash
# Una sola vez
pip install streamlit plotly numpy

# O instalar todo
pip install -r ../requirements.txt
```

### Paso 3: Ejecutar Dashboard
```bash
streamlit run app.py
```

✅ El dashboard se abrirá automáticamente en `http://localhost:8501`

## 2️⃣ Primeros Pasos

### Ver Datos Simulados
El dashboard incluye **datos de demostración** listos para usar:

1. **Home** → Ver ocupación, precios, sugerencias
2. **Ocupación** → Mapa de calor por habitación
3. **Precios** → Sugerencias de cambios
4. **Competencia** → Comparativa de mercado
5. **Reportes** → Descargar análisis

### Probar Funcionalidades
```
🔘 Botones en sidebar:
   - [🔄 Actualizar] → Refrescar datos
   - [⚙️ Config] → Ir a configuración

🔘 Botones en páginas:
   - [✅ Aprobar] → Aprobar sugerencia (simulado)
   - [❌ Rechazar] → Rechazar cambio
   - [📥 Descargar] → Guardar reporte
```

## 3️⃣ Usar Datos Reales

Edita cualquier página (ej: `pages/01_home.py`) y reemplaza:

```python
# ANTES (Datos simulados)
occupancy_data = get_mock_data('daily_summary')

# DESPUÉS (Datos reales)
from dashboard.services.dashboard_db import get_dashboard_db
db = get_dashboard_db()
occupancy_data = db.get_7day_occupancy()
```

## 4️⃣ Activar OpenAI (Opcional)

1. **Obtener API Key:**
   - Ir a https://platform.openai.com/api-keys
   - Crear nueva key
   - Copiar

2. **Configurar `.env`:**
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Reiniciar dashboard:**
   ```bash
   # Control+C para parar
   # Luego:
   streamlit run app.py
   ```

✅ Los análisis IA ahora serán reales

## 5️⃣ Comandos Útiles

```bash
# Limpiar caché de Streamlit
streamlit cache clear

# Ejecutar en puerto diferente
streamlit run app.py --server.port 8502

# IP específica (acceso desde otros equipos)
streamlit run app.py --server.address 192.168.1.50

# Sin banner de "Made with Streamlit"
streamlit run app.py --client.showErrorDetails false

# Ver logs
tail -f ../logs/dashboard_20240521.log  # Mac/Linux
Get-Content ../logs/dashboard_20240521.log -Tail 50 -Wait  # PowerShell
```

## 6️⃣ Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| *Módulo no encontrado* | `pip install streamlit plotly` |
| *Puerto ocupado* | `streamlit run app.py --server.port 8502` |
| *Datos no cargan* | F5 para refrescar o `streamlit cache clear` |
| *Gráficos vacíos* | Esperar 10 segundos, datos están simulados |
| *Conexión DB lenta* | Aumentar `CACHE_TTL` en `config.py` |

## 7️⃣ Estructura Rápida

```
📁 dashboard/
  ├── app.py          ← Iniciar aquí ✨
  ├── config.py       ← Colores, configuración
  ├── pages/          ← 5 páginas diferentes
  ├── components/     ← Gráficos, tarjetas
  ├── services/       ← Base de datos, IA
  ├── data/           ← Datos simulados
  └── .streamlit/     ← Config de Streamlit
```

## 8️⃣ Personalización en 2 Minutos

### Cambiar Colores
Edita `dashboard/config.py`:
```python
COLORS = {
    "primary": "#00A86B",    # Cambiar verde a otro color
    "secondary": "#3B82F6",  # Cambiar azul
}
```

### Cambiar Tema
En `dashboard/.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#00A86B"
backgroundColor = "#F8F9FA"
```

### Agregar Nueva Métrica
En `pages/01_home.py`:
```python
st.metric("Mi Métrica", valor, delta="cambio")
```

## 9️⃣ Acceso desde Otros Equipos

```bash
# 1. Encontrar tu IP local
ipconfig  # Windows
# Buscar IPv4 Address, ej: 192.168.1.50

# 2. Iniciar en esa IP
streamlit run app.py --server.address 192.168.1.50

# 3. Desde otro equipo:
# Abrir navegador → http://192.168.1.50:8501
```

## 🔟 Ir a Producción

```bash
# Opción 1: Streamlit Cloud (más fácil)
# Git push → GitHub → streamlit.io/cloud

# Opción 2: Docker
docker build -t dashboard .
docker run -p 8501:8501 dashboard

# Opción 3: Task Scheduler (Windows)
# Nueva tarea → Ejecutable: streamlit.exe
# Argumentos: run C:\path\to\app.py
```

## ❓ Preguntas Comunes

**P: ¿Dónde están los logs?**
R: `../logs/dashboard_YYYYMMDD.log`

**P: ¿Cómo cambio el puerto?**
R: `streamlit run app.py --server.port 8502`

**P: ¿Puedo usar datos reales?**
R: Sí, cambia `get_mock_data()` por `dashboard_db.get_*()`

**P: ¿El dashboard modifica la BD?**
R: No, todo es en modo simulación/visualización

**P: ¿Cuánto tarda en cargar?**
R: Datos en caché: 1-2 segundos. Primera carga: 5-10 segundos

---

**¿Necesitas ayuda?** Revisa `README.md` para documentación completa

**¡Lista para usar!** 🎉
