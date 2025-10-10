import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import sqlite3
import traceback
import sys
import hashlib
import getpass
import socket
import shutil

class AppTurnosPeluqueria:
    def __init__(self, root):
        self.root = root

        # VERIFICAR INSTALACIÓN VÁLIDA
        if not self.verificar_instalacion():
            self.root.destroy()
            return

        # Si pasa la verificación, continuar normal
        self.configurar_interfaz()
        self.conectar_bd()

        # SISTEMA DE BACKUP AUTOMÁTICO
        self.verificar_y_crear_backup()

        self.cargar_profesionales()
        self.crear_componentes()
        self.cargar_turnos()

    def verificar_instalacion(self):
        import socket
        nombre_maquina = socket.gethostname()

        # SOLO funciona en NewStation2
        if nombre_maquina != "NewStation2":
            messagebox.showerror(
                "Error de Licencia",
                "ESTA APLICACIÓN ESTÁ VINCULADA A OTRA PELUQUERÍA\n\n"
                "Solo puede utilizarse en:\n"
                "- NewStation2\n\n"
                "Contacte al proveedor para más información."
            )
            return False
        return True
