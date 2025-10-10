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
        """Verificar que la app está instalada en esta máquina/peluquería"""
        # Generar ID único de la máquina
        maquina_id = hashlib.md5(
            f"{getpass.getuser()}{socket.gethostname()}".encode()
        ).hexdigest()[:12]
        
        # Archivo de instalación
        archivo_instalacion = "instalacion.key"
        
        try:
            # Leer instalación existente
            with open(archivo_instalacion, "r") as f:
                instalacion_guardada = f.read().strip()
            
            # Verificar que coincide
            if instalacion_guardada != maquina_id:
                messagebox.showerror(
                    "Error de Licencia", 
                    "⚠️ ESTA APLICACIÓN ESTÁ VINCULADA A OTRA PELUQUERÍA\n\n"
                    "Solo puede utilizarse en:\n"
                    "💈 New Station 2\n\n"
                    "Contacte al proveedor para más información."
                )
                return False
            return True
            
        except FileNotFoundError:
            # Primera instalación - crear archivo
            with open(archivo_instalacion, "w") as f:
                f.write(maquina_id)
            
            messagebox.showinfo(
                "✅ Instalación Exitosa",
                f"💈 New Station 2\n\n"
                f"🔐 Aplicación vinculada correctamente\n"
                f"🆔 ID de instalación: {maquina_id}\n\n"
                "📌 Esta copia no puede transferirse a otra máquina.\n"
                "📞 Soporte técnico disponible."
            )
            return True

    def inicializar_sistema_config(self):
        """Crear tabla de configuración y control de versiones"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    clave TEXT PRIMARY KEY,
                    valor TEXT,
                    actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar versión actual si no existe
            self.cursor.execute(
                "INSERT OR IGNORE INTO config (clave, valor) VALUES (?, ?)", 
                ("version", "1.0")
            )
            self.cursor.execute(
                "INSERT OR IGNORE INTO config (clave, valor) VALUES (?, ?)", 
                ("ultimo_backup", "")
            )
            
            self.conexion.commit()
        except Exception as e:
            print(f"⚠️ Error inicializando config: {e}")

    def hacer_backup_automatico(self):
        """Backup automático si detecta nueva versión"""
        import datetime
        
        try:
            # Obtener versión actual de la base de datos
            self.cursor.execute("SELECT valor FROM config WHERE clave='version'")
            resultado = self.cursor.fetchone()
            
            version_guardada = resultado[0] if resultado else "1.0"
            version_actual = "1.0"  # CAMBIAR ESTO EN FUTURAS VERSIONES
            
            if version_guardada != version_actual:
                print(f"🔄 Detectada nueva versión: {version_guardada} -> {version_actual}")
                
                # Crear backup
                fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                archivo_backup = f"backup_v{version_guardada}_{fecha}.db"
                
                # Copiar base de datos
                shutil.copy2(self.get_db_path(), archivo_backup)
                
                # Actualizar versión en la base de datos
                self.cursor.execute(
                    "UPDATE config SET valor=?, actualizado=CURRENT_TIMESTAMP WHERE clave='version'", 
                    (version_actual,)
                )
                self.cursor.execute(
                    "UPDATE config SET valor=?, actualizado=CURRENT_TIMESTAMP WHERE clave='ultimo_backup'", 
                    (archivo_backup,)
                )
                self.conexion.commit()
                
                print(f"✅ Backup automático creado: {archivo_backup}")
                
                # Mostrar mensaje informativo al usuario
                messagebox.showinfo(
                    "✅ Actualización Exitosa",
                    f"Se detectó una nueva versión del sistema.\n\n"
                    f"📁 Backup automático creado:\n{archivo_backup}\n\n"
                    f"🔄 Versión anterior: {version_guardada}\n"
                    f"🎯 Versión actual: {version_actual}\n\n"
                    f"Todos sus datos están seguros."
                )
                
        except Exception as e:
            print(f"⚠️ Error en backup automático: {e}")

    def verificar_y_crear_backup(self):
        """Verificar integridad y crear backup si es necesario"""
        try:
            # Verificar que la tabla config existe
            self.inicializar_sistema_config()
            
            # Hacer backup si corresponde
            self.hacer_backup_automatico()
            
        except Exception as e:
            print(f"⚠️ Error en verificación de backup: {e}")
    
    def configurar_interfaz(self):
        self.root.title("New Station 2 - Sistema de Turnos")
        self.root.geometry("1300x800")
        self.root.configure(bg="#f8f9fa")
        
        # Estilos Bootstrap-like
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
    
    def get_db_path(self):
        """Obtener ruta absoluta de la base de datos"""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        db_path = os.path.join(base_path, 'turnos_newstation_pueyrredon.db')
        print(f"📁 Ruta de la base de datos: {db_path}")
        return db_path
    
    def conectar_bd(self):
        """CONEXIÓN CON SQLITE - CON RUTA ABSOLUTA"""
        try:
            db_path = self.get_db_path()
            self.conexion = sqlite3.connect(db_path)
            self.cursor = self.conexion.cursor()
            
            # Crear tabla turnos
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
            
            # Crear tabla estilistas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS estilistas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Crear tabla manicuras
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS manicuras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Insertar profesionales actuales
            estilistas = ["Alejandro Cosentini", "Guillermo Mirabile", "Paola Rodriguez", 
                         "Miguel Riviera", "Fabian Gomez", "Rodrigo Carbonero", "Veronica Parra"]
            for estilista in estilistas:
                self.cursor.execute("INSERT OR IGNORE INTO estilistas (nombre) VALUES (?)", (estilista,))
            
            manicuras = ["Liliana Pavon", "Noelia Leguizamon"]
            for manicura in manicuras:
                self.cursor.execute("INSERT OR IGNORE INTO manicuras (nombre) VALUES (?)", (manicura,))
            
            self.conexion.commit()
            print("✅ Base de datos SQLite conectada y verificada")
            
        except Exception as e:
            print(f"❌ Error BD: {e}")
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")
    
    def cargar_profesionales(self):
        """Cargar listas de estilistas y manicuras"""
        try:
            # Cargar estilistas
            self.cursor.execute("SELECT nombre FROM estilistas WHERE activo = 1 ORDER BY nombre")
            self.estilistas = ["Alejandro Cosentini", "Guillermo Mirabile", "Paola Rodriguez", 
                              "Miguel Riviera", "Fabian Gomez", "Rodrigo Carbonero", "Veronica Parra"]
            self.estilistas.append("No aplica")
            
            # Cargar manicuras
            self.cursor.execute("SELECT nombre FROM manicuras WHERE activo = 1 ORDER BY nombre")
            self.manicuras = ["Liliana Pavon", "Noelia Leguizamon"]
            self.manicuras.append("No aplica")
            
            print(f"👥 Estilistas cargados: {len(self.estilistas)}")
            print(f"👥 Manicuras cargadas: {len(self.manicuras)}")
            
        except Exception as e:
            # Valores por defecto
            self.estilistas = ["Alejandro Cosentini", "Guillermo Mirabile", "Paola Rodriguez", 
                              "Miguel Riviera", "Fabian Gomez", "Rodrigo Carbonero", "Veronica Parra", "No aplica"]
            self.manicuras = ["Liliana Pavon", "Noelia Leguizamon", "No aplica"]
            print(f"⚠️ Usando valores por defecto para profesionales: {e}")
    
    def crear_boton_redondeado(self, parent, text, color, command=None):
        """Crear botón con estilo Bootstrap redondeado"""
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
        """Abrir ventana para seleccionar hora con clicks - DE 09:00 A 20:00"""
        ventana_hora = tk.Toplevel(self.root)
        ventana_hora.title("Seleccionar Hora")
        ventana_hora.geometry("300x400")
        ventana_hora.configure(bg=self.estilos["fondo"])
        ventana_hora.transient(self.root)
        ventana_hora.grab_set()
        
        # Frame principal
        frame_principal = tk.Frame(ventana_hora, bg=self.estilos["fondo"], padx=20, pady=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(frame_principal, text="Seleccione la hora", 
                font=("Arial", 14, "bold"), bg=self.estilos["fondo"], 
                fg=self.estilos["texto_oscuro"]).pack(pady=(0, 20))
        
        # Frame para horas
        frame_horas = tk.Frame(frame_principal, bg=self.estilos["fondo"])
        frame_horas.pack(fill=tk.BOTH, expand=True)
        
        # Generar horas de 09:00 a 20:00 en intervalos de 30 min
        horas = []
        for hora in range(9, 21):
            for minuto in [0, 30]:
                if hora == 20 and minuto == 30:
                    continue
                hora_str = f"{hora:02d}:{minuto:02d}"
                horas.append(hora_str)
        
        # Crear botones de hora
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
        
        # Configurar grid
        for i in range(3):
            frame_horas.grid_columnconfigure(i, weight=1)
    
    def seleccionar_hora(self, hora, ventana):
        """Seleccionar hora y cerrar ventana"""
        self.entry_hora.delete(0, tk.END)
        self.entry_hora.insert(0, hora)
        ventana.destroy()

    def selector_fecha_mejorado(self):
        """Selector de fecha mejorado que permite navegar meses y años"""
        ventana_fecha = tk.Toplevel(self.root)
        ventana_fecha.title("Seleccionar Fecha")
        ventana_fecha.geometry("300x350")
        ventana_fecha.configure(bg=self.estilos["fondo"])
        ventana_fecha.transient(self.root)
        ventana_fecha.grab_set()
        
        # Frame principal
        frame_principal = tk.Frame(ventana_fecha, bg=self.estilos["fondo"], padx=20, pady=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(frame_principal, text="Seleccione la fecha", 
                font=("Arial", 14, "bold"), bg=self.estilos["fondo"], 
                fg=self.estilos["texto_oscuro"]).pack(pady=(0, 15))
        
        # Frame para año y mes
        frame_controles = tk.Frame(frame_principal, bg=self.estilos["fondo"])
        frame_controles.pack(fill=tk.X, pady=(0, 10))
        
        # Selector de año
        tk.Label(frame_controles, text="Año:", bg=self.estilos["fondo"], 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        año_actual = datetime.now().year
        años = [str(año) for año in range(año_actual, 2051)]  # Hasta 2050
        
        combo_año = ttk.Combobox(frame_controles, values=años, width=8,
                               state="readonly", font=("Arial", 10))
        combo_año.set(str(año_actual))
        combo_año.pack(side=tk.LEFT, padx=(0, 15))
        
        # Selector de mes
        tk.Label(frame_controles, text="Mes:", bg=self.estilos["fondo"], 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        combo_mes = ttk.Combobox(frame_controles, values=meses, width=12,
                               state="readonly", font=("Arial", 10))
        combo_mes.set(meses[datetime.now().month - 1])
        combo_mes.pack(side=tk.LEFT)
        
        # Frame para días
        frame_dias = tk.Frame(frame_principal, bg=self.estilos["fondo"])
        frame_dias.pack(fill=tk.BOTH, expand=True)
        
        # Días de la semana
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for i, dia in enumerate(dias_semana):
            tk.Label(frame_dias, text=dia, bg=self.estilos["fondo"], 
                    font=("Arial", 9, "bold"), width=4).grid(row=0, column=i, padx=2, pady=2)
        
        def actualizar_calendario():
            """Actualizar los días del calendario según mes y año seleccionados"""
            # Limpiar días anteriores
            for widget in frame_dias.grid_slaves():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()
            
            # Obtener mes y año seleccionados
            mes_seleccionado = combo_mes.current() + 1
            año_seleccionado = int(combo_año.get())
            
            # Primer día del mes
            primer_dia = datetime(año_seleccionado, mes_seleccionado, 1)
            # Último día del mes
            if mes_seleccionado == 12:
                ultimo_dia = datetime(año_seleccionado + 1, 1, 1)
            else:
                ultimo_dia = datetime(año_seleccionado, mes_seleccionado + 1, 1)
            
            dias_en_mes = (ultimo_dia - primer_dia).days
            
            # Encontrar día de la semana del primer día (0=Lunes, 6=Domingo)
            dia_semana_inicio = primer_dia.weekday()
            
            # Crear botones de días
            fila, columna = 1, dia_semana_inicio
            for dia in range(1, dias_en_mes + 1):
                btn_dia = tk.Button(
                    frame_dias,
                    text=str(dia),
                    font=("Arial", 9),
                    bg=self.estilos["info"],
                    fg="white",
                    relief="flat",
                    bd=0,
                    width=4,
                    command=lambda d=dia: seleccionar_fecha(d, mes_seleccionado, año_seleccionado, ventana_fecha)
                )
                
                # Marcar el día actual
                hoy = datetime.now()
                if (dia == hoy.day and mes_seleccionado == hoy.month and 
                    año_seleccionado == hoy.year):
                    btn_dia.config(bg=self.estilos["exito"], fg="white")
                
                btn_dia.grid(row=fila, column=columna, padx=2, pady=2)
                
                columna += 1
                if columna > 6:
                    columna = 0
                    fila += 1
        
        def seleccionar_fecha(dia, mes, año, ventana):
            """Seleccionar fecha y cerrar ventana"""
            fecha_str = f"{dia:02d}/{mes:02d}/{año}"
            self.entry_fecha.delete(0, tk.END)
            self.entry_fecha.insert(0, fecha_str)
            ventana.destroy()
        
        # Actualizar calendario cuando cambien mes o año
        combo_mes.bind('<<ComboboxSelected>>', lambda e: actualizar_calendario())
        combo_año.bind('<<ComboboxSelected>>', lambda e: actualizar_calendario())
        
        # Inicializar calendario
        actualizar_calendario()

    def buscar_turnos(self):
        """Buscar turnos por nombre, teléfono o servicio"""
        texto_busqueda = self.entry_busqueda.get().strip().lower()
        
        if not texto_busqueda:
            messagebox.showwarning("Búsqueda", "Ingrese un término para buscar")
            return
        
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
            
            # Buscar en nombre, teléfono y servicio (case insensitive)
            self.cursor.execute('''
                SELECT * FROM turnos 
                WHERE LOWER(nombre) LIKE ? 
                   OR LOWER(telefono) LIKE ? 
                   OR LOWER(servicio) LIKE ?
                ORDER BY fecha ASC, hora ASC
            ''', (f'%{texto_busqueda}%', f'%{texto_busqueda}%', f'%{texto_busqueda}%'))
            
            turnos = self.cursor.fetchall()
            
            print(f"🔍 Resultados de búsqueda: {len(turnos)} turnos encontrados")
            
            if turnos:
                for turno in turnos:
                    # Convertir fecha de aaaa-mm-dd a dd/mm/aaaa para mostrar
                    fecha_sql = turno[6]
                    try:
                        fecha_obj = datetime.strptime(fecha_sql, "%Y-%m-%d")
                        fecha_mostrar = fecha_obj.strftime("%d/%m/%Y")
                    except:
                        fecha_mostrar = fecha_sql
                    
                    # Crear tupla con fecha formateada
                    turno_formateado = (
                        turno[0], turno[1], turno[2], turno[3], 
                        turno[4], turno[5], fecha_mostrar, turno[7]
                    )
                    
                    # Aplicar color según si el turno ya pasó
                    item_id = self.tabla.insert("", tk.END, values=turno_formateado)
                    self.aplicar_color_turno(item_id, fecha_sql, turno[7])
                
                # Actualizar indicador de búsqueda
                self.label_estado.config(text=f"🔍 {len(turnos)} turnos encontrados para: '{texto_busqueda}'", 
                                       fg=self.estilos["exito"])
            else:
                self.tabla.insert("", tk.END, values=("", "No se encontraron turnos", "", "", "", "", "", ""))
                self.label_estado.config(text=f"❌ No se encontraron turnos para: '{texto_busqueda}'", 
                                       fg=self.estilos["peligro"])
                
        except Exception as err:
            print(f"❌ Error en búsqueda: {err}")
            messagebox.showerror("Error BD", f"No se pudieron buscar los turnos: {err}")

    def mostrar_todos(self):
        """Mostrar todos los turnos (quitar filtro de búsqueda)"""
        self.entry_busqueda.delete(0, tk.END)
        self.label_estado.config(text="📊 Mostrando todos los turnos", fg=self.estilos["info"])
        self.cargar_turnos()
    
    def crear_componentes(self):
        # HEADER con logo
        frame_header = tk.Frame(self.root, bg="white", relief="solid", bd=1)
        frame_header.pack(fill=tk.X, pady=(0, 20))
        
        # Logo como texto (estilo Bootstrap)
        logo_frame = tk.Frame(frame_header, bg="white")
        logo_frame.pack(side=tk.LEFT, padx=30, pady=15)
        
        tk.Label(logo_frame, text="NEW STATION", 
                font=("Arial", 24, "bold"), 
                bg="white", fg=self.estilos["primario"]).pack()
        
        tk.Label(logo_frame, text="PELUQUERÍAS - Sucursal Pueyrredon", 
                font=("Arial", 14), 
                bg="white", fg=self.estilos["texto_claro"]).pack()
        
        # Título principal
        title_frame = tk.Frame(frame_header, bg="white")
        title_frame.pack(expand=True, pady=20)
        
        tk.Label(title_frame, text="SISTEMA DE GESTIÓN DE TURNOS", 
                font=("Arial", 16, "bold"), 
                bg="white", fg=self.estilos["texto_oscuro"]).pack()
        
        # CONTENIDO PRINCIPAL
        frame_main = tk.Frame(self.root, bg=self.estilos["fondo"])
        frame_main.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # FORMULARIO A LA IZQUIERDA (Card style)
        frame_form_container = tk.Frame(frame_main, bg=self.estilos["fondo"])
        frame_form_container.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 20))
        
        # Card del formulario
        frame_form_card = tk.Frame(frame_form_container, bg="white", relief="solid", bd=1)
        frame_form_card.pack(fill=tk.BOTH, expand=True)
        
        # Header de la card
        frame_card_header = tk.Frame(frame_form_card, bg=self.estilos["primario"])
        frame_card_header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(frame_card_header, text="NUEVO TURNO", 
                font=("Arial", 14, "bold"), 
                bg=self.estilos["primario"], fg="white", 
                padx=20, pady=15).pack()
        
        # Contenido del formulario
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
            
            # Label
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
                
                # Botón selector de hora
                btn_selector = tk.Button(frame_hora, text="🕒", 
                                       font=("Arial", 12),
                                       bg=self.estilos["info"], fg="white",
                                       relief="flat", bd=0,
                                       command=self.selector_hora)
                btn_selector.pack(side=tk.RIGHT, padx=(5, 0))
                
            elif attr == "entry_fecha":
                frame_fecha = tk.Frame(frame_campo, bg="white")
                frame_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Campo de entrada para fecha
                self.entry_fecha = tk.Entry(frame_fecha, font=("Arial", 10), 
                                          relief="solid", bd=1, bg="white")
                self.entry_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
                
                # Botón selector de fecha MEJORADO
                btn_calendario = tk.Button(frame_fecha, text="📅", 
                                         font=("Arial", 12),
                                         bg=self.estilos["primario"], fg="white",
                                         relief="flat", bd=0,
                                         command=self.selector_fecha_mejorado)
                btn_calendario.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Botones del formulario
        frame_botones = tk.Frame(frame_form_content, bg="white")
        frame_botones.pack(fill=tk.X, pady=25)
        
        btn_agregar = self.crear_boton_redondeado(
            frame_botones, "➕ AGREGAR TURNO", self.estilos["exito"], self.agregar_turno
        )
        btn_agregar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_limpiar = self.crear_boton_redondeado(
            frame_botones, "🧹 LIMPIAR", self.estilos["advertencia"], self.limpiar_formulario
        )
        btn_limpiar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_actualizar = self.crear_boton_redondeado(
            frame_botones, "🔄 ACTUALIZAR TABLA", self.estilos["info"], self.cargar_turnos
        )
        btn_actualizar.pack(side=tk.LEFT)
        
        # TABLA A LA DERECHA (Card style)
        frame_tabla_container = tk.Frame(frame_main, bg=self.estilos["fondo"])
        frame_tabla_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Card de la tabla
        frame_tabla_card = tk.Frame(frame_tabla_container, bg="white", relief="solid", bd=1)
        frame_tabla_card.pack(fill=tk.BOTH, expand=True)
        
        # Header de la card de tabla
        frame_tabla_header = tk.Frame(frame_tabla_card, bg=self.estilos["primario"])
        frame_tabla_header.pack(fill=tk.X)
        
        tk.Label(frame_tabla_header, text="TURNOS REGISTRADOS", 
                font=("Arial", 14, "bold"), 
                bg=self.estilos["primario"], fg="white", 
                padx=20, pady=15).pack()
        
        # BARRA DE BÚSQUEDA (NUEVA)
        frame_busqueda = tk.Frame(frame_tabla_card, bg="white", padx=15, pady=5)
        frame_busqueda.pack(fill=tk.X)
        
        tk.Label(frame_busqueda, text="🔍 Buscar:", bg="white", 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry_busqueda = tk.Entry(frame_busqueda, font=("Arial", 10), 
                                     relief="solid", bd=1, bg="white", width=30)
        self.entry_busqueda.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_busqueda.bind('<Return>', lambda e: self.buscar_turnos())
        
        btn_buscar = tk.Button(frame_busqueda, text="BUSCAR", 
                             bg=self.estilos["info"], fg="white",
                             font=("Arial", 9, "bold"),
                             command=self.buscar_turnos)
        btn_buscar.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_todos = tk.Button(frame_busqueda, text="MOSTRAR TODOS", 
                            bg=self.estilos["secundario"], fg="white",
                            font=("Arial", 9, "bold"),
                            command=self.mostrar_todos)
        btn_todos.pack(side=tk.LEFT)
        
        # Indicador de estado de búsqueda
        self.label_estado = tk.Label(frame_busqueda, text="📊 Mostrando todos los turnos", 
                                   bg="white", font=("Arial", 9), fg=self.estilos["info"])
        self.label_estado.pack(side=tk.RIGHT)
        
        # Contenido de la tabla
        frame_tabla_content = tk.Frame(frame_tabla_card, bg="white")
        frame_tabla_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        self.tabla = ttk.Treeview(frame_tabla_content, 
                                columns=("ID", "Nombre", "Teléfono", "Servicio", "Estilista", "Manicura", "Fecha", "Hora"), 
                                show="headings", height=15)
        
        # Configurar columnas (ajustadas para ver mejor la hora)
        columnas = [
            ("ID", 40), ("Nombre", 100), ("Teléfono", 90),
            ("Servicio", 120), ("Estilista", 90), ("Manicura", 90),
            ("Fecha", 80), ("Hora", 60)
        ]
        
        for col, width in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame_tabla_content, orient=tk.VERTICAL, command=self.tabla.yview)
        h_scrollbar = ttk.Scrollbar(frame_tabla_content, orient=tk.HORIZONTAL, command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.tabla.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        frame_tabla_content.grid_rowconfigure(0, weight=1)
        frame_tabla_content.grid_columnconfigure(0, weight=1)
        
        # BOTÓN ELIMINAR (Footer de la card)
        frame_footer = tk.Frame(frame_tabla_card, bg="white", pady=15)
        frame_footer.pack(fill=tk.X)
        
        btn_eliminar = self.crear_boton_redondeado(
            frame_footer, "🗑️ ELIMINAR TURNO", self.estilos["peligro"], self.eliminar_turno
        )
        btn_eliminar.pack()
    
    def validar_hora(self, hora):
        try:
            datetime.strptime(hora, "%H:%M")
            return True
        except ValueError:
            return False
    
    def verificar_turno_existente(self, nombre, fecha, hora):
        """VERIFICACIÓN MEJORADA: Evitar turnos duplicados exactos"""
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM turnos 
                WHERE nombre = ? AND fecha = ? AND hora = ?
            ''', (nombre, fecha, hora))
            return self.cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"❌ Error verificando turno existente: {e}")
            return False
    
    def verificar_disponibilidad_estilista(self, fecha, hora, estilista):
        """VERIFICACIÓN MEJORADA: Evitar que estilista tenga turnos superpuestos"""
        if not estilista or estilista == "No aplica":
            return False
            
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM turnos 
                WHERE fecha = ? AND hora = ? AND estilista = ?
            ''', (fecha, hora, estilista))
            return self.cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"❌ Error verificando disponibilidad: {e}")
            return False
    
    def validar_fecha_hora_futura(self, fecha, hora):
        """NUEVA VALIDACIÓN: Evitar turnos en fechas/horas pasadas"""
        try:
            # Convertir fecha y hora a objeto datetime
            turno_datetime = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            ahora = datetime.now()
            
            # Verificar que el turno sea en el futuro
            return turno_datetime > ahora
        except Exception as e:
            print(f"❌ Error validando fecha/hora: {e}")
            return False
    
    def aplicar_color_turno(self, item_id, fecha, hora):
        """NUEVA FUNCIÓN: Cambiar color según si el turno ya pasó"""
        try:
            turno_datetime = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            ahora = datetime.now()
            
            if turno_datetime < ahora:
                # Turno pasado - color rojo claro
                self.tabla.item(item_id, tags=('pasado',))
                self.tabla.tag_configure('pasado', background='#FFCCCC')  # Rojo claro
            else:
                # Turno futuro - color verde claro
                self.tabla.item(item_id, tags=('futuro',))
                self.tabla.tag_configure('futuro', background='#CCFFCC')  # Verde claro
                
        except Exception as e:
            print(f"❌ Error aplicando color: {e}")
    
    def limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        self.entry_nombre.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)
        self.combo_servicio.set("")
        self.combo_estilista.set("")
        self.combo_manicura.set("")
        print("🧹 Formulario limpiado")
    
    def agregar_turno(self):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        servicio = self.combo_servicio.get().strip()
        estilista = self.combo_estilista.get().strip()
        manicura = self.combo_manicura.get().strip()
        
        # Convertir fecha de dd/mm/aaaa a aaaa-mm-dd para SQLite
        fecha_str = self.entry_fecha.get()
        try:
            fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
            fecha = fecha_obj.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Error", "Formato de fecha inválido. Use DD/MM/AAAA")
            return
        
        hora = self.entry_hora.get().strip()
        
        if not all([nombre, servicio, hora]):
            messagebox.showwarning("Error", "Complete los campos obligatorios: Nombre, Servicio y Hora")
            return
        
        if not self.validar_hora(hora):
            messagebox.showwarning("Error", "Formato de hora inválido.\nUse HH:MM (ej: 09:30, 14:15)")
            return
        
        # NUEVA VALIDACIÓN: Verificar que no sea fecha/hora pasada
        if not self.validar_fecha_hora_futura(fecha, hora):
            messagebox.showwarning(
                "Fecha/Hora Inválida", 
                f"⚠️ No se pueden agendar turnos en fechas u horas pasadas.\n\n"
                f"📅 Fecha: {fecha_str}\n"
                f"🕒 Hora: {hora}\n\n"
                f"Por favor, elija una fecha y hora futuras."
            )
            return
        
        # VERIFICACIÓN 1: Turno duplicado para el mismo cliente
        if self.verificar_turno_existente(nombre, fecha, hora):
            messagebox.showwarning(
                "Turno Duplicado", 
                f"⚠️ Ya existe un turno para:\n"
                f"👤 {nombre}\n"
                f"📅 {fecha_str}\n"
                f"🕒 {hora}\n\n"
                f"Por favor, verifique los datos o elija otra hora."
            )
            return
        
        # VERIFICACIÓN 2: Estilista ya ocupado en ese horario
        if self.verificar_disponibilidad_estilista(fecha, hora, estilista):
            messagebox.showwarning(
                "Estilista No Disponible", 
                f"⚠️ El estilista {estilista} ya tiene un turno:\n"
                f"📅 {fecha_str}\n"
                f"🕒 {hora}\n\n"
                f"Por favor, elija otro horario u otro estilista."
            )
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO turnos (nombre, telefono, servicio, estilista, manicura, fecha, hora)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, telefono, servicio, estilista, manicura, fecha, hora))
            
            self.conexion.commit()
            print(f"✅ Turno guardado: {nombre} - {fecha} {hora}")
            messagebox.showinfo("Éxito", "Turno agregado correctamente")
            self.limpiar_formulario()
            self.cargar_turnos()
        except Exception as err:
            print(f"❌ Error al guardar turno: {err}")
            messagebox.showerror("Error BD", f"No se pudo agregar: {err}")
    
    def cargar_turnos(self):
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
            
            # ORDEN CORREGIDO: Por fecha ASC, hora ASC
            self.cursor.execute("SELECT * FROM turnos ORDER BY fecha ASC, hora ASC")
            turnos = self.cursor.fetchall()
            
            print(f"📊 Turnos encontrados: {len(turnos)}")
            
            if turnos:
                for turno in turnos:
                    fecha_sql = turno[6]
                    try:
                        fecha_obj = datetime.strptime(fecha_sql, "%Y-%m-%d")
                        fecha_mostrar = fecha_obj.strftime("%d/%m/%Y")
                    except:
                        fecha_mostrar = fecha_sql
                    
                    turno_formateado = (
                        turno[0], turno[1], turno[2], turno[3], 
                        turno[4], turno[5], fecha_mostrar, turno[7]
                    )
                    
                    # Insertar y aplicar color
                    item_id = self.tabla.insert("", tk.END, values=turno_formateado)
                    self.aplicar_color_turno(item_id, fecha_sql, turno[7])
            else:
                self.tabla.insert("", tk.END, values=("", "No hay turnos registrados", "", "", "", "", "", ""))
                
        except Exception as err:
            print(f"❌ Error al cargar turnos: {err}")
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
                print(f"🗑️ Turno eliminado: ID {turno_id}")
                messagebox.showinfo("Éxito", "Turno eliminado correctamente")
                self.cargar_turnos()
            except Exception as err:
                print(f"❌ Error al eliminar turno: {err}")
                messagebox.showerror("Error BD", f"No se pudo eliminar: {err}")

def main():
    try:
        root = tk.Tk()
        app = AppTurnosPeluqueria(root)
        root.mainloop()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()