#!/bin/bash

# Crear copia para pruebas
cp turnos_app.py turnos_app_prueba.py

# Modificar para modo prueba (siempre funciona)
python -c "
with open('turnos_app_prueba.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Cambiar la verificaci√≥n para que siempre sea True
contenido = contenido.replace('if nombre_maquina != \"NewStation2\":', 'if False:  # MODO PRUEBA')

# Cambiar t√≠tulo para identificar versi√≥n prueba
contenido = contenido.replace('NewStation2 - Sistema de Turnos', 'MODO PRUEBA - Sistema de Turnos')

with open('turnos_app_prueba.py', 'w', encoding='utf-8') as f:
    f.write(contenido)

print('‚úÖ Versi√≥n prueba creada')
"

# Crear ejecutable de prueba
pyinstaller --onefile --windowed --name "SistemaTurnos_PRUEBA" turnos_app_prueba.py

echo "=== ARCHIVOS LISTOS ==="
ls -lh dist/SistemaTurnos*.exe

# Crear paquete final
zip -r Entrega_Final_NewStation2.zip \
    dist/SistemaTurnos.exe \
    dist/SistemaTurnos_PRUEBA.exe \
    turnos_newstation_pueyrredon.db

echo "ÌæÅ PAQUETE LISTO: Entrega_Final_NewStation2.zip"
echo ""
echo "‚úÖ ¬°ENTREGA COMPLETADA!"
echo "Ì¥í SistemaTurnos.exe - Solo funciona en NewStation2"
echo "Ì¥ì SistemaTurnos_PRUEBA.exe - Funciona en cualquier PC"
