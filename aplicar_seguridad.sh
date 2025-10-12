#!/bin/bash
# Reemplazar la función verificar_licencia con una más estricta
python -c "
import re

with open('turnos_app.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Buscar y reemplazar la función verificar_licencia
nuevo_codigo = '''    def verificar_licencia(self):
        import socket
        nombre_maquina = socket.gethostname()
        
        # SOLO funciona en NewStation2
        if nombre_maquina != \"NewStation2\":
            self.root.destroy()
            messagebox.showerror(
                \"Error de Licencia\", 
                \"⚠️ ESTE SOFTWARE ES EXCLUSIVO DE NEW STATION 2\n\n\"
                \"Solo puede utilizarse en la peluquería autorizada.\n\"
                \"Contacte al proveedor para más información.\"
            )
            return False
        return True'''

# Reemplazar la función existente
patron = r'def verificar_licencia\(self\):[\s\S]*?return (True|False)'
contenido_modificado = re.sub(patron, nuevo_codigo, contenido)

with open('turnos_app.py', 'w', encoding='utf-8') as f:
    f.write(contenido_modificado)

print('✅ Seguridad aplicada correctamente')
"

# Verificar los cambios
echo "=== VERIFICANDO CAMBIOS ==="
grep -n -A 10 "def verificar_licencia" turnos_app.py
