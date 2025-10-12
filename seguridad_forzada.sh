#!/bin/bash

# Crear copia con seguridad extrema
cp turnos_app.py turnos_app_seguro.py

python -c "
import socket

with open('turnos_app_seguro.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Verificación EXTREMA - cierra la aplicación si no es la máquina correcta
nuevo_codigo = '''    def verificar_instalacion(self):
        import socket
        nombre_maquina = socket.gethostname()
        
        # VERIFICACIÓN ESTRICTA - NO abre si no es NewStation2
        if nombre_maquina != \\\"NewStation2\\\":
            print(\\\"��� BLOQUEADO: Esta aplicación solo funciona en NewStation2\\\")
            self.root.destroy()
            import sys
            sys.exit(1)
            return False
        print(\\\"✅ MÁQUINA AUTORIZADA: NewStation2\\\")
        return True'''

import re
patron = r'def verificar_instalacion\\(self\\):[\\s\\S]*?return (True|False)'
contenido = re.sub(patron, nuevo_codigo, contenido)

with open('turnos_app_seguro.py', 'w', encoding='utf-8') as f:
    f.write(contenido)

print('✅ Seguridad extrema aplicada')
"

# Crear nuevo ejecutable SEGURO
pyinstaller --onefile --windowed --name "SistemaTurnos_SEGURO" turnos_app_seguro.py

echo "=== PROBAR SEGURIDAD ==="
echo "�� SistemaTurnos_SEGURO.exe - NO debería abrir en esta máquina"
