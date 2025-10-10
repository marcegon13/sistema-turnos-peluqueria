import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import sqlite3
import traceback
import time

def main():
    try:
        print("🚀 Iniciando aplicación...")
        print("📋 Cargando módulos...")
        
        root = tk.Tk()
        root.title("NEW STATION - Sistema de Turnos")
        root.geometry("1300x800")
        root.configure(bg="#f8f9fa")
        
        print("✅ Módulos cargados correctamente")
        print("🎨 Configurando interfaz...")

        class AppTurnosPeluqueria:
            def __init__(self, root):
                self.root = root
                self.configurar_interfaz()
                self.conectar_bd()
                self.cargar_profesionales()
                self.crear_componentes()
                self.cargar_turnos()
            
            def configurar_interfaz(self):
                print("🎨 Configurando estilos...")
                self.estilos = {
                    "fondo": "#f8f9fa",
                    "primario": "#007bff",
                    "secundario": "#6c757d", 
                    "exito": "#28a745",
                    "peligro": "#dc3545",
                    "advertencia": "#ffc107",
                    "info": "#17a2b8",
                    "texto_oscuro": "#343a40",
                    "texto_claro": "#6c757d",
                    "borde": "#dee2e6",
                    "card_bg": "#ffffff"
                }
                print("✅ Estilos configurados")

            def conectar_bd(self):
                print("🔌 Conectando a SQLite...")
                try:
                    self.conexion = sqlite3.connect('turnos_peluqueria.db')
                    self.cursor = self.conexion.cursor()
                    
                    # Crear tablas si no existen
                    self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS turnos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            telefono TEXT,
                            servicio TEXT NOT NULL,
                            estilista TEXT,
                            manicura TEXT,
                            fecha TEXT NOT NULL,
                            hora TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS estilistas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            activo BOOLEAN DEFAULT 1
                        )
                    ''')
                    
                    self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS manicuras (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            activo BOOLEAN DEFAULT 1
                        )
                    ''')
                    
                    # Insertar datos de ejemplo
                    estilistas = ["Ana García", "Carlos López", "María Rodríguez", "Pedro Martínez", "Laura Sánchez"]
                    for estilista in estilistas:
                        self.cursor.execute("INSERT OR IGNORE INTO estilistas (nombre) VALUES (?)", (estilista,))
                    
                    manicuras = ["Sofía Hernández", "Elena Castro", "Miguel Torres", "Carmen Díaz"]
                    for manicura in manicuras:
                        self.cursor.execute("INSERT OR IGNORE INTO manicuras (nombre) VALUES (?)", (manicura,))
                    
                    self.conexion.commit()
                    print("✅ Base de datos SQLite conectada y configurada")
                    
                except Exception as err:
                    print(f"❌ Error de conexión SQLite: {err}")
                    messagebox.showerror("Error BD", f"No se pudo conectar a la base de datos:\n{err}")

            def cargar_profesionales(self):
                print("👥 Cargando profesionales...")
                try:
                    self.cursor.execute("SELECT nombre FROM estilistas WHERE activo = 1 ORDER BY nombre")
                    self.estilistas = [row[0] for row in self.cursor.fetchall()]
                    
                    self.cursor.execute("SELECT nombre FROM manicuras WHERE activo = 1 ORDER BY nombre")
                    self.manicuras = [row[0] for row in self.cursor.fetchall()]
                    
                    self.estilistas.append("No aplica")
                    self.manicuras.append("No aplica")
                    print("✅ Profesionales cargados")
                    
                except Exception:
                    self.estilistas = ["Ana García", "Carlos López", "María Rodríguez", "Pedro Martínez", "Laura Sánchez", "No aplica"]
                    self.manicuras = ["Sofía Hernández", "Elena Castro", "Miguel Torres", "Carmen Díaz", "No aplica"]
                    print("⚠️ Usando valores por defecto para profesionales")

            def crear_boton_redondeado(self, parent, text, color, command=None):
                return tk.Button(
                    parent,
                    text=text,
                    bg=color,
                    fg="white",
                    font=("Arial", 10, "bold"),
                    relief="flat",
                    bd=0,
                    padx=20,
                    pady=10,
                    command=command
                )

            def selector_hora(self):
                ventana_hora = tk.Toplevel(self.root)
                ventana_hora.title("Seleccionar Hora")
                ventana_hora.geometry("300x400")
                ventana_hora.configure(bg=self.estilos["fondo"])
                ventana_hora.transient(self.root)
                ventana_hora.grab_set()
                
                frame_principal = tk.Frame(ventana_hora, bg=self.estilos["fondo"], padx=20, pady=20)
                frame_principal.pack(fill=tk.BOTH, expand=True)
                
                tk.Label(frame_principal, text="Seleccione la hora", 
                        font=("Arial", 14, "bold"), bg=self.estilos["fondo"], 
                        fg=self.estilos["texto_oscuro"]).pack(pady=(0, 20))
                
                frame_horas = tk.Frame(frame_principal, bg=self.estilos["fondo"])
                frame_horas.pack(fill=tk.BOTH, expand=True)
                
                horas = []
                for hora in range(8, 21):
                    for minuto in [0, 30]:
                        if hora == 20 and minuto == 30:
                            continue
                        hora_str = f"{hora:02d}:{minuto:02d}"
                        horas.append(hora_str)
                
                fila, columna = 0, 0
                for i, hora in enumerate(horas):
                    btn = tk.Button(
                        frame_horas,
                        text=hora,
                        font=("Arial", 9),
                        bg=self.estilos["info"],
                        fg="white",
                        relief="flat",
                        bd=0,
                        padx=10,
                        pady=8,
                        command=lambda h=hora: self.seleccionar_hora(h, ventana_hora)
                    )
                    btn.grid(row=fila, column=columna, padx=5, pady=5, sticky="ew")
                    
                    columna += 1
                    if columna > 2:
                        columna = 0
                        fila += 1
                
                for i in range(3):
                    frame_horas.grid_columnconfigure(i, weight=1)

            def seleccionar_hora(self, hora, ventana):
                self.entry_hora.delete(0, tk.END)
                self.entry_hora.insert(0, hora)
                ventana.destroy()

            def crear_componentes(self):
                print("🔧 Creando componentes de la interfaz...")
                
                # HEADER
                frame_header = tk.Frame(self.root, bg="white", relief="solid", bd=1)
                frame_header.pack(fill=tk.X, pady=(0, 20))
                
                logo_frame = tk.Frame(frame_header, bg="white")
                logo_frame.pack(side=tk.LEFT, padx=30, pady=15)
                
                tk.Label(logo_frame, text="NEW STATION", 
                        font=("Arial", 24, "bold"), 
                        bg="white", fg=self.estilos["primario"]).pack()
                
                tk.Label(logo_frame, text="PELUQUERÍAS", 
                        font=("Arial", 14), 
                        bg="white", fg=self.estilos["texto_claro"]).pack()
                
                title_frame = tk.Frame(frame_header, bg="white")
                title_frame.pack(expand=True, pady=20)
                
                tk.Label(title_frame, text="SISTEMA DE GESTIÓN DE TURNOS", 
                        font=("Arial", 16, "bold"), 
                        bg="white", fg=self.estilos["texto_oscuro"]).pack()
                
                # CONTENIDO PRINCIPAL
                frame_main = tk.Frame(self.root, bg=self.estilos["fondo"])
                frame_main.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
                
                # FORMULARIO
                frame_form_container = tk.Frame(frame_main, bg=self.estilos["fondo"])
                frame_form_container.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 20))
                
                frame_form_card = tk.Frame(frame_form_container, bg="white", relief="solid", bd=1)
                frame_form_card.pack(fill=tk.BOTH, expand=True)
                
                frame_card_header = tk.Frame(frame_form_card, bg=self.estilos["primario"])
                frame_card_header.pack(fill=tk.X, pady=(0, 20))
                
                tk.Label(frame_card_header, text="NUEVO TURNO", 
                        font=("Arial", 14, "bold"), 
                        bg=self.estilos["primario"], fg="white", 
                        padx=20, pady=15).pack()
                
                frame_form_content = tk.Frame(frame_form_card, bg="white", padx=25, pady=20)
                frame_form_content.pack(fill=tk.BOTH, expand=True)
                
                # Campos del formulario
                campos = [
                    ("Nombre Cliente:", "entry_nombre"),
                    ("Teléfono:", "entry_telefono"), 
                    ("Servicio:", "combo_servicio"),
                    ("Estilista:", "combo_estilista"),
                    ("Manicura:", "combo_manicura"),
                    ("Hora:", "entry_hora"),
                    ("Fecha:", "entry_fecha")
                ]
                
                for i, (label, attr) in enumerate(campos):
                    frame_campo = tk.Frame(frame_form_content, bg="white")
                    frame_campo.pack(fill=tk.X, pady=12)
                    
                    tk.Label(frame_campo, text=label, bg="white", 
                            font=("Arial", 10, "bold"), 
                            fg=self.estilos["texto_oscuro"],
                            width=15, anchor="w").pack(side=tk.LEFT, padx=(0, 15))
                    
                    if attr == "entry_nombre":
                        self.entry_nombre = tk.Entry(frame_campo, font=("Arial", 10), 
                                                   relief="solid", bd=1, bg="white")
                        self.entry_nombre.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    elif attr == "entry_telefono":
                        self.entry_telefono = tk.Entry(frame_campo, font=("Arial", 10), 
                                                     relief="solid", bd=1, bg="white")
                        self.entry_telefono.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    elif attr == "combo_servicio":
                        self.combo_servicio = ttk.Combobox(frame_campo, font=("Arial", 10), 
                                                          values=["Corte de Cabello", "Coloración", "Peinado", 
                                                                 "Tratamiento Capilar", "Lavado", "Alisado",
                                                                 "Manicura Básica", "Manicura Spa", "Esmaltado Semi",
                                                                 "Pedicura", "Uñas Esculpidas"],
                                                          state="readonly")
                        self.combo_servicio.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    elif attr == "combo_estilista":
                        self.combo_estilista = ttk.Combobox(frame_campo, font=("Arial", 10), 
                                                           values=self.estilistas,
                                                           state="readonly")
                        self.combo_estilista.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    elif attr == "combo_manicura":
                        self.combo_manicura = ttk.Combobox(frame_campo, font=("Arial", 10), 
                                                          values=self.manicuras,
                                                          state="readonly")
                        self.combo_manicura.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    elif attr == "entry_hora":
                        frame_hora = tk.Frame(frame_campo, bg="white")
                        frame_hora.pack(side=tk.LEFT, fill=tk.X, expand=True)
                        
                        self.entry_hora = tk.Entry(frame_hora, font=("Arial", 10), 
                                                 relief="solid", bd=1, bg="white")
                        self.entry_hora.pack(side=tk.LEFT, fill=tk.X, expand=True)
                        
                        btn_selector = tk.Button(frame_hora, text="🕒", 
                                               font=("Arial", 12),
                                               bg=self.estilos["info"], fg="white",
                                               relief="flat", bd=0,
                                               command=self.selector_hora)
                        btn_selector.pack(side=tk.RIGHT, padx=(5, 0))
                        
                    elif attr == "entry_fecha":
                        # Para SQLite, usamos un Entry normal para fecha
                        self.entry_fecha = tk.Entry(frame_campo, font=("Arial", 10), 
                                                  relief="solid", bd=1, bg="white")
                        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
                        self.entry_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Botones del formulario
                frame_botones = tk.Frame(frame_form_content, bg="white")
                frame_botones.pack(fill=tk.X, pady=25)
                
                btn_agregar = self.crear_boton_redondeado(
                    frame_botones, "➕ AGREGAR TURNO", self.estilos["exito"], self.agregar_turno
                )
                btn_agregar.pack(side=tk.LEFT, padx=(0, 10))
                
                btn_actualizar = self.crear_boton_redondeado(
                    frame_botones, "🔄 ACTUALIZAR", self.estilos["info"], self.cargar_turnos
                )
                btn_actualizar.pack(side=tk.LEFT)
                
                # TABLA
                frame_tabla_container = tk.Frame(frame_main, bg=self.estilos["fondo"])
                frame_tabla_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
                
                frame_tabla_card = tk.Frame(frame_tabla_container, bg="white", relief="solid", bd=1)
                frame_tabla_card.pack(fill=tk.BOTH, expand=True)
                
                frame_tabla_header = tk.Frame(frame_tabla_card, bg=self.estilos["primario"])
                frame_tabla_header.pack(fill=tk.X)
                
                tk.Label(frame_tabla_header, text="TURNOS REGISTRADOS", 
                        font=("Arial", 14, "bold"), 
                        bg=self.estilos["primario"], fg="white", 
                        padx=20, pady=15).pack()
                
                frame_tabla_content = tk.Frame(frame_tabla_card, bg="white")
                frame_tabla_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                self.tabla = ttk.Treeview(frame_tabla_content, 
                                        columns=("ID", "Nombre", "Teléfono", "Servicio", "Estilista", "Manicura", "Fecha", "Hora"), 
                                        show="headings", height=20)
                
                columnas = [
                    ("ID", 50), ("Nombre", 120), ("Teléfono", 100),
                    ("Servicio", 130), ("Estilista", 100), ("Manicura", 100),
                    ("Fecha", 90), ("Hora", 70)
                ]
                
                for col, width in columnas:
                    self.tabla.heading(col, text=col)
                    self.tabla.column(col, width=width, anchor=tk.CENTER)
                
                v_scrollbar = ttk.Scrollbar(frame_tabla_content, orient=tk.VERTICAL, command=self.tabla.yview)
                h_scrollbar = ttk.Scrollbar(frame_tabla_content, orient=tk.HORIZONTAL, command=self.tabla.xview)
                self.tabla.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
                
                self.tabla.grid(row=0, column=0, sticky="nsew")
                v_scrollbar.grid(row=0, column=1, sticky="ns")
                h_scrollbar.grid(row=1, column=0, sticky="ew")
                
                frame_tabla_content.grid_rowconfigure(0, weight=1)
                frame_tabla_content.grid_columnconfigure(0, weight=1)
                
                frame_footer = tk.Frame(frame_tabla_card, bg="white", pady=15)
                frame_footer.pack(fill=tk.X)
                
                btn_eliminar = self.crear_boton_redondeado(
                    frame_footer, "🗑️ ELIMINAR TURNO", self.estilos["peligro"], self.eliminar_turno
                )
                btn_eliminar.pack()
                
                print("✅ Componentes creados correctamente")

            def validar_hora(self, hora):
                try:
                    datetime.strptime(hora, "%H:%M")
                    return True
                except ValueError:
                    return False

            def agregar_turno(self):
                nombre = self.entry_nombre.get().strip()
                telefono = self.entry_telefono.get().strip()
                servicio = self.combo_servicio.get().strip()
                estilista = self.combo_estilista.get().strip()
                manicura = self.combo_manicura.get().strip()
                fecha = self.entry_fecha.get().strip()
                hora = self.entry_hora.get().strip()
                
                if not all([nombre, servicio, fecha, hora]):
                    messagebox.showwarning("Error", "Complete los campos obligatorios: Nombre, Servicio, Fecha y Hora")
                    return
                
                if not self.validar_hora(hora):
                    messagebox.showwarning("Error", "Formato de hora inválido.\nUse HH:MM (ej: 09:30, 14:15)")
                    return
                
                try:
                    self.cursor.execute('''
                        INSERT INTO turnos (nombre, telefono, servicio, estilista, manicura, fecha, hora)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (nombre, telefono, servicio, estilista, manicura, fecha, hora))
                    
                    self.conexion.commit()
                    messagebox.showinfo("Éxito", "Turno agregado correctamente")
                    self.limpiar_formulario()
                    self.cargar_turnos()
                except Exception as err:
                    messagebox.showerror("Error BD", f"No se pudo agregar: {err}")

            def cargar_turnos(self):
                try:
                    for item in self.tabla.get_children():
                        self.tabla.delete(item)
                    
                    self.cursor.execute("SELECT * FROM turnos ORDER BY fecha ASC, hora ASC")
                    turnos = self.cursor.fetchall()
                    
                    if turnos:
                        for turno in turnos:
                            self.tabla.insert("", tk.END, values=turno)
                    else:
                        self.tabla.insert("", tk.END, values=("", "No hay turnos registrados", "", "", "", "", "", ""))
                        
                except Exception as err:
                    messagebox.showerror("Error BD", f"No se pudieron cargar los turnos: {err}")

            def eliminar_turno(self):
                seleccion = self.tabla.selection()
                if not seleccion:
                    messagebox.showwarning("Error", "Seleccione un turno para eliminar")
                    return
                
                turno_id = self.tabla.item(seleccion[0])["values"][0]
                nombre = self.tabla.item(seleccion[0])["values"][1]
                
                if messagebox.askyesno("Confirmar", f"¿Eliminar turno de {nombre}?"):
                    try:
                        self.cursor.execute("DELETE FROM turnos WHERE id = ?", (turno_id,))
                        self.conexion.commit()
                        messagebox.showinfo("Éxito", "Turno eliminado correctamente")
                        self.cargar_turnos()
                    except Exception as err:
                        messagebox.showerror("Error BD", f"No se pudo eliminar: {err}")

            def limpiar_formulario(self):
                self.entry_nombre.delete(0, tk.END)
                self.entry_telefono.delete(0, tk.END)
                self.entry_hora.delete(0, tk.END)
                self.entry_fecha.delete(0, tk.END)
                self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
                self.combo_servicio.set("")
                self.combo_estilista.set("")
                self.combo_manicura.set("")

        app = AppTurnosPeluqueria(root)
        print("✅ Aplicación iniciada correctamente")
        print("🎯 Interfaz lista para usar")
        root.mainloop()

    except Exception as e:
        print("═" * 70)
        print("❌ ERROR CRÍTICO EN LA APLICACIÓN")
        print("═" * 70)
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        print("\n" + "═" * 70)
        print("📋 TRAZA COMPLETA DEL ERROR:")
        print("═" * 70)
        traceback.print_exc()
        print("═" * 70)
        print("\n⏰ La ventana se cerrará automáticamente en 60 segundos...")
        print("   Presiona CTRL + C para cerrar ahora")
        print("═" * 70)
        
        # Mantener la ventana abierta por 60 segundos
        time.sleep(60)

if __name__ == "__main__":
    main()