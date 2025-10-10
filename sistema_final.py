import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import sqlite3
import traceback
import sys
import socket

class AppTurnosPeluqueria:
    def __init__(self, root):
        self.root = root
        
        # VERIFICAR LICENCIA - PRIMERO
        if not self.verificar_licencia():
            self.root.destroy()
            return
        
        # Si pasa la verificación, continuar
        self.configurar_interfaz()
        self.conectar_bd()
        self.cargar_profesionales()
        self.crear_componentes()
        self.cargar_turnos()
    
    def verificar_licencia(self):
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
    
    def configurar_interfaz(self):
        self.root.title("NewStation2 - Sistema de Turnos")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
    
    def get_db_path(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, 'turnos_newstation_pueyrredon.db')
    
    def conectar_bd(self):
        try:
            db_path = self.get_db_path()
            self.conexion = sqlite3.connect(db_path)
            self.cursor = self.conexion.cursor()
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS turnos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT,
                    servicio TEXT NOT NULL,
                    estilista TEXT,
                    fecha TEXT NOT NULL,
                    hora TEXT NOT NULL
                )
            ''')
            self.conexion.commit()
            print("✅ Base de datos conectada")
            
        except Exception as e:
            print(f"❌ Error BD: {e}")
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")
    
    def cargar_profesionales(self):
        self.estilistas = ["Alejandro Cosentini", "Guillermo Mirabile", "Paola Rodriguez", 
                          "Miguel Riviera", "Fabian Gomez", "Rodrigo Carbonero", "Veronica Parra", "No aplica"]
    
    def crear_componentes(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(main_frame, text="NEW STATION - SISTEMA DE TURNOS", 
                font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
        
        # Frame del formulario
        form_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1, padx=20, pady=20)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Campos del formulario
        tk.Label(form_frame, text="Nombre:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nombre = tk.Entry(form_frame, width=30)
        self.entry_nombre.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Teléfono:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_telefono = tk.Entry(form_frame, width=30)
        self.entry_telefono.grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Servicio:", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_servicio = ttk.Combobox(form_frame, width=27, values=[
            "Corte de Cabello", "Coloración", "Peinado", "Tratamiento Capilar"
        ])
        self.combo_servicio.grid(row=2, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Estilista:", bg="white").grid(row=3, column=0, sticky="w", pady=5)
        self.combo_estilista = ttk.Combobox(form_frame, width=27, values=self.estilistas)
        self.combo_estilista.grid(row=3, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Fecha (DD/MM/AAAA):", bg="white").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_fecha = tk.Entry(form_frame, width=30)
        self.entry_fecha.grid(row=4, column=1, pady=5, padx=10)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        tk.Label(form_frame, text="Hora (HH:MM):", bg="white").grid(row=5, column=0, sticky="w", pady=5)
        self.entry_hora = tk.Entry(form_frame, width=30)
        self.entry_hora.grid(row=5, column=1, pady=5, padx=10)
        
        # Botones
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="AGREGAR TURNO", bg="green", fg="white", 
                 command=self.agregar_turno).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="LIMPIAR", bg="orange", fg="white",
                 command=self.limpiar_formulario).pack(side=tk.LEFT, padx=5)
        
        # Tabla de turnos
        table_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.tabla = ttk.Treeview(table_frame, columns=("ID", "Nombre", "Teléfono", "Servicio", "Estilista", "Fecha", "Hora"), show="headings")
        
        for col in ["ID", "Nombre", "Teléfono", "Servicio", "Estilista", "Fecha", "Hora"]:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón eliminar
        tk.Button(main_frame, text="ELIMINAR TURNO SELECCIONADO", bg="red", fg="white",
                 command=self.eliminar_turno).pack(pady=10)
    
    def limpiar_formulario(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)
        self.combo_servicio.set("")
        self.combo_estilista.set("")
    
    def agregar_turno(self):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        servicio = self.combo_servicio.get().strip()
        estilista = self.combo_estilista.get().strip()
        fecha = self.entry_fecha.get().strip()
        hora = self.entry_hora.get().strip()
        
        if not all([nombre, servicio, fecha, hora]):
            messagebox.showwarning("Error", "Complete todos los campos obligatorios")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO turnos (nombre, telefono, servicio, estilista, fecha, hora)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, telefono, servicio, estilista, fecha, hora))
            
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Turno agregado correctamente")
            self.limpiar_formulario()
            self.cargar_turnos()
            
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo agregar: {err}")
    
    def cargar_turnos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        try:
            self.cursor.execute("SELECT * FROM turnos ORDER BY fecha, hora")
            turnos = self.cursor.fetchall()
            
            for turno in turnos:
                self.tabla.insert("", tk.END, values=turno)
                
        except Exception as err:
            print(f"Error al cargar turnos: {err}")
    
    def eliminar_turno(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione un turno para eliminar")
            return
        
        turno_id = self.tabla.item(seleccion[0])["values"][0]
        
        if messagebox.askyesno("Confirmar", "¿Eliminar este turno?"):
            try:
                self.cursor.execute("DELETE FROM turnos WHERE id = ?", (turno_id,))
                self.conexion.commit()
                self.cargar_turnos()
                messagebox.showinfo("Éxito", "Turno eliminado")
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo eliminar: {err}")

def main():
    try:
        root = tk.Tk()
        app = AppTurnosPeluqueria(root)
        root.mainloop()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
