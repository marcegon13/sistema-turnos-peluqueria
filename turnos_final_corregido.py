import socket
import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta

class AppTurnosPeluqueria:
    def __init__(self, root):
        self.root = root
        
        # VERIFICACIÓN DE SEGURIDAD
        maquina = socket.gethostname()
        print("Máquina detectada:", maquina)
        
        if maquina != "NewStation2":
            messagebox.showerror(
                "Error de Licencia",
                "ESTA APLICACIÓN ESTÁ VINCULADA A OTRA PELUQUERÍA\n\n"
                "Solo puede utilizarse en:\n"
                "- NewStation2\n\n"
                "Contacte al proveedor para más información."
            )
            self.root.destroy()
            return
        
        # SI PASA LA VERIFICACIÓN, CONTINUAR
        self.conexion = None
        self.cursor = None
        self.conectar_db()
        self.configurar_interfaz()
        self.actualizar_tabla()
