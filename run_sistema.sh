#!/bin/bash

echo "🚀 Iniciando Sistema de Turnos NEW STATION..."
echo "=========================================="
echo "Usando: $(py -3.11 --version)"
echo ""

# Verificar dependencias
echo "🔍 Verificando dependencias..."
py -3.11 -c "
try:
    import tkinter; print('✅ tkinter: OK')
    import sqlite3; print('✅ sqlite3: OK') 
    import urllib.parse; print('✅ urllib: OK')
    import webbrowser; print('✅ webbrowser: OK')
    try:
        import pyperclip; print('✅ pyperclip: OK')
    except:
        print('📦 pyperclip: Instalando...')
        import subprocess
        subprocess.check_call(['py', '-3.11', '-m', 'pip', 'install', 'pyperclip'])
        import pyperclip; print('✅ pyperclip: Instalado OK')
    print('')
    print('🎯 Todas las dependencias listas!')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

echo ""
echo "🎯 Iniciando aplicación..."
echo "=========================================="

# Ejecutar el sistema
py -3.11 SistemaTurnos.py