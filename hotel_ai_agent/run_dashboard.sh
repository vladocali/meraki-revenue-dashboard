#!/bin/bash
# Revenue Management Dashboard Launcher
# Linux/Mac Script

echo ""
echo "========================================"
echo "  REVENUE MANAGEMENT DASHBOARD 🏨"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 detectado"

# Check Streamlit installation
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo ""
    echo "⚠️  Streamlit no está instalado"
    echo "Instalando dependencias..."
    echo ""
    pip3 install streamlit plotly numpy
fi

# Change to dashboard directory
cd "$(dirname "$0")/dashboard"

echo ""
echo "🚀 Iniciando Dashboard..."
echo ""
echo "📱 URL: http://localhost:8501"
echo ""
echo "💡 Tip: Presiona Ctrl+C para detener"
echo ""

# Run Streamlit
python3 -m streamlit run app.py
