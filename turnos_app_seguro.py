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
