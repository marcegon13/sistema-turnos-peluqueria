#!/bin/bash
python -c "
import re

with open('turnos_app.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Buscar y reemplazar verificar_instalacion
nuevo_codigo = '''    def verificar_instalacion(self):
        import socket
        nombre_maquina = socket.gethostname()
        
        # SOLO funciona en NewStation2
        if nombre_maquina != \\\"NewStation2\\\":
            messagebox.showerror(
                \\\"Error de Licencia\\\", 
                \\\"⚠️ ESTE SOFTWARE ES EXCLUSIVO DE NEW STATION 2\\\\n\\\\n\\\"
                \\\"Solo puede utilizarse en la peluquería autorizada.\\\\n\\\"
                \\\"Contacte al proveedor para más información.\\\"
            )
            return False
        return True'''

# Reemplazar la función existente
patron = r'def verificar_instalacion\\(self\\):[\\s\\S]*?return (True|False)'
contenido_modificado = re.sub(patron, nuevo_codigo, contenido)

with open('turnos_app.py', 'w', encoding='utf-8') as f:
    f.write(contenido_modificado)

print('✅ Seguridad aplicada correctamente en verificar_instalacion')
"

# Verificar cambios
echo "=== VERIFICANDO CAMBIOS ==="
grep -n -A 15 "def verificar_instalacion" turnos_app.py
