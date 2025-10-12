#!/bin/bash
echo "Ì≤à INSTALADOR - TURNOS PELUQUER√çA"
echo "=================================="
echo "Ì≥¶ Instalando mysql-connector-python..."
python -m pip install mysql-connector-python
echo "Ì≥¶ Instalando tkcalendar..."
python -m pip install tkcalendar
echo "Ì≥¶ Instalando pyinstaller..."
python -m pip install pyinstaller
echo ""
echo "‚úÖ Todas las dependencias instaladas!"
echo ""
echo "ÌæØ Pr√≥ximos pasos:"
echo "1. Crear la base de datos MySQL"
echo "2. Ejecutar: python turnos_app.py"
echo "3. Para crear .exe: pyinstaller --onefile --windowed turnos_app.py"
