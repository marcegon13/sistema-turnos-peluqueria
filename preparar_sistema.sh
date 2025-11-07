#!/bin/bash

echo "🔧 Preparando Sistema de Turnos..."
echo "=========================================="

# Verificar Python 3.11
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3" 
elif command -v python &> /dev/null; then
    # Verificar que sea Python 3
    if python -c "import sys; print(sys.version_info[0])" | grep -q "3"; then
        PYTHON_CMD="python"
    else
        echo "❌ Se requiere Python 3"
        exit 1
    fi
else
    echo "❌ Python no encontrado"
    echo "📥 Instala Python 3.11 desde: https://python.org"
    exit 1
fi

echo "✅ Python encontrado: $($PYTHON_CMD --version)"

# Verificar tkinter
echo "🔍 Verificando tkinter..."
$PYTHON_CMD -c "import tkinter; print('✅ tkinter funciona')" || {
    echo "❌ tkinter no funciona"
    echo "💡 Reinstala Python marcando 'tcl/tk and IDLE'"
    exit 1
}

# Instalar pyperclip si es necesario
echo "📦 Verificando pyperclip..."
$PYTHON_CMD -c "import pyperclip" 2>/dev/null || {
    echo "📦 Instalando pyperclip..."
    $PYTHON_CMD -m pip install pyperclip
}

echo "🎯 Todo listo! Ejecutando sistema..."
echo "=========================================="

$PYTHON_CMD SistemaTurnos.py