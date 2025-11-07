#!/bin/bash

echo "🔍 Verificando estado de Python..."
echo "=========================================="

# Probar diferentes comandos
echo "1. Probando 'python --version':"
python --version 2>&1 || echo "   ❌ No funciona"

echo ""
echo "2. Probando 'py --version':" 
py --version 2>&1 || echo "   ❌ No funciona"

echo ""
echo "3. Listando Python instalados:"
py --list 2>&1 || echo "   ❌ py no disponible"

echo ""
echo "4. Buscando python.exe en el sistema:"
find /c/ -name "python.exe" 2>/dev/null | head -10