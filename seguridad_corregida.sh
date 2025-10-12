#!/bin/bash

# Crear archivo seguro desde cero
cat > turnos_app_seguro.py << 'PYCODE'
import socket
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import traceback

class AppTurnosPeluqueria:
    def __init__(self, root):
        self.root = root
        
        # VERIFICACIÓN DE SEGURIDAD - PRIMERO QUE TODO
        if not self.verificar_licencia():
            return  # No continúa si la licencia falla
            
        self.conexion = None
        self.cursor = None
        self.conectar_db()
        self.configurar_interfaz()
        self.actualizar_tabla()

    def verificar_licencia(self):
        nombre_maquina = socket.gethostname()
        
        # SOLO funciona en NewStation2
        if nombre_maquina != "NewStation2":
            messagebox.showerror(
                "Error de Licencia", 
                "ESTA APLICACION SOLO FUNCIONA EN NEW STATION 2\n\n"
                "Solo puede utilizarse en la peluqueria autorizada.\n"
                "Contacte al proveedor para mas informacion."
            )
            self.root.destroy()
            return False
        return True
PYCODE

# Agregar el resto del código original (a partir de la línea donde termina __init__)
grep -n "def conectar_db" turnos_app.py | head -1
# Buscar desde después del __init__
tail -n +$(($(grep -n "def conectar_db" turnos_app.py | head -1 | cut -d: -f1) - 1)) turnos_app.py >> turnos_app_seguro.py

echo "✅ Código seguro creado"

# Verificar sintaxis
python -m py_compile turnos_app_seguro.py && echo "✅ Sintaxis correcta" || echo "❌ Error de sintaxis"

# Crear ejecutable seguro
pyinstaller --onefile --windowed --name "SistemaTurnos_SEGURO" turnos_app_seguro.py

echo "=== EJECUTABLES LISTOS ==="
ls -lh dist/SistemaTurnos*.exe 2>/dev/null || echo "No se crearon ejecutables"

echo ""
echo "��� PROBAR AHORA:"
echo "dist/SistemaTurnos_SEGURO.exe - NO debe abrir en DESKTOP-BVL74RK"
echo "dist/SistemaTurnos_PRUEBA.exe - SI debe abrir (versión demo)"
