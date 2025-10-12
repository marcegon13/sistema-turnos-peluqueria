@echo off
echo === CREANDO EJECUTABLE CON SEGURIDAD ===

:: Crear archivo Python con protecciÃ³n
echo import socket > turnos_protegido.py
echo import tkinter as tk >> turnos_protegido.py
echo from tkinter import messagebox >> turnos_protegido.py
echo. >> turnos_protegido.py
echo class AppTurnosPeluqueria: >> turnos_protegido.py
echo     def __init__(self, root): >> turnos_protegido.py
echo         self.root = root >> turnos_protegido.py
echo         maquina = socket.gethostname() >> turnos_protegido.py
echo         if maquina != "NewStation2": >> turnos_protegido.py
echo             messagebox.showerror("Error", "SOLO NewStation2") >> turnos_protegido.py
echo             self.root.destroy() >> turnos_protegido.py
echo             return >> turnos_protegido.py
echo         # Continuar con app >> turnos_protegido.py

:: Agregar el resto del cÃ³digo original
type turnos_app.py >> turnos_protegido.py

:: Compilar
pyinstaller --onefile --windowed --name "SistemaTurnos_EXCLUSIVO" turnos_protegido.py

echo.
echo âœ… EJECUTABLE SEGURO CREADO: dist\SistemaTurnos_EXCLUSIVO.exe
echo.
echo í·ª PRUEBA:
echo - En NewStation2: DEBE abrir
echo - En otras PCs: NO debe abrir
echo.
pause
