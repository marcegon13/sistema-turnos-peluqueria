#!/bin/bash
cp turnos_app.py turnos_app_prueba.py
python -c "
import re
with open('turnos_app_prueba.py', 'r') as f:
    contenido = f.read()
    
# Cambiar verificación para prueba
nuevo_codigo = '''    def verificar_licencia(self):
        # VERSIÓN PRUEBA - Sin restricciones
        return True'''
    
contenido = re.sub(r'def verificar_licencia\(self\):[\s\S]*?return (True|False)', nuevo_codigo, contenido)
contenido = contenido.replace('NewStation2 - Sistema de Turnos', 'MODO PRUEBA - Sistema de Turnos')

with open('turnos_app_prueba.py', 'w') as f:
    f.write(contenido)
print('✅ Versión prueba creada')
"

pyinstaller --onefile --windowed --name "SistemaTurnos_PRUEBA" turnos_app_prueba.py

echo "=== ARCHIVOS LISTOS ==="
ls -lh dist/SistemaTurnos*.exe
