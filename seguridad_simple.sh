#!/bin/bash

# Crear copia del código original
cp turnos_app.py turnos_app_original.py

# Crear nuevo archivo con seguridad simple
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

# Agregar el resto del código original (sin la función de verificación vieja)
tail -n +20 turnos_app_original.py >> turnos_app_seguro.py

echo "✅ Código seguro creado"

# Crear ejecutable seguro
pyinstaller --onefile --windowed --name "SistemaTurnos_SEGURO" turnos_app_seguro.py

echo "=== EJECUTABLE SEGURO CREADO ==="
ls -lh dist/SistemaTurnos_SEGURO.exe

echo ""
echo "��� PROBAR:"
echo "SistemaTurnos_SEGURO.exe - NO debe abrir en esta máquina"
echo "SistemaTurnos_PRUEBA.exe - SI debe abrir (versión demo)"
