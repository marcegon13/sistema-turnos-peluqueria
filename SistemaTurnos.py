import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date, timedelta
import os
import sqlite3
import traceback
import sys
import urllib.parse
import webbrowser
import pyperclip
import shutil

class AppTurnosPeluqueria:
    def __init__(self, root):
        self.root = root
        self.configurar_interfaz()
        self.inicializar_base_datos()
        self.cargar_profesionales()
        self.crear_componentes()
        self.cargar_turnos()
        self.agregar_menu_contextual()
        self.agregar_doble_click()
    
    def configurar_interfaz(self):
        self.root.title('NEW STATION - Sistema de Turnos')
        self.root.geometry('1400x800')
        self.root.configure(bg='#f8f9fa')
        self.estilos = {
            'fondo': '#f8f9fa', 'primario': '#007bff', 'secundario': '#6c757d', 
            'exito': '#28a745', 'peligro': '#dc3545', 'advertencia': '#ffc107',
            'info': '#17a2b8', 'texto_oscuro': '#343a40', 'texto_claro': '#6c757d',
            'borde': '#dee2e6', 'card_bg': '#ffffff', 'whatsapp': '#25D366',
            'turno_pasado': '#ffebee', 'turno_presente': '#e3f2fd', 'turno_futuro': '#e8f5e8',
            'ausencia': '#ffcccc'  # 🆕 Color para días de ausencia
        }

    def get_db_path(self):
        """Obtiene la ruta donde debe estar la base de datos"""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        db_path = os.path.join(base_path, 'turnos_peluqueria.db')
        print(f"📁 Ruta de BD: {db_path}")
        return db_path

    def inicializar_base_datos(self):
        """Inicializa la base de datos de manera robusta"""
        try:
            db_path = self.get_db_path()
            
            if not os.path.exists(db_path):
                print("🔍 Base de datos no encontrada en el directorio actual...")
                
                trabajo_path = os.path.join(os.getcwd(), 'turnos_peluqueria.db')
                if os.path.exists(trabajo_path):
                    print(f"📋 Copiando BD desde: {trabajo_path}")
                    shutil.copy2(trabajo_path, db_path)
                    print("✅ Base de datos copiada exitosamente")
                else:
                    print("🆕 Creando nueva base de datos...")
            
            self.conectar_bd()
            self.reparar_base_datos()
            
        except Exception as e:
            print(f'❌ Error inicializando BD: {e}')
            messagebox.showerror('Error', f'No se pudo inicializar la base de datos: {e}')

    def conectar_bd(self):
        try:
            db_path = self.get_db_path()
            print(f"🔗 Conectando a: {db_path}")
            
            self.conexion = sqlite3.connect(db_path)
            self.cursor = self.conexion.cursor()
            
            # Tabla de turnos (existente)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS turnos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT NOT NULL,
                    servicio TEXT,
                    estilista TEXT NOT NULL,
                    manicura TEXT NOT NULL,
                    servicios_manicura TEXT,
                    fecha TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    whatsapp_enviado BOOLEAN DEFAULT 0
                )
            ''')
            
            # 🆕 NUEVA TABLA PARA AUSENCIAS
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ausencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profesional TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    motivo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conexion.commit()
            print('✅ Base de datos lista')
            
        except Exception as e:
            print(f'❌ Error BD: {e}')
            messagebox.showerror('Error', f'No se pudo conectar: {e}')

    def reparar_base_datos(self):
        """Repara la estructura de la base de datos"""
        try:
            print("🔧 Verificando estructura de la base de datos...")
            
            self.cursor.execute("PRAGMA table_info(turnos)")
            columnas = [col[1] for col in self.cursor.fetchall()]
            print(f"📊 Columnas actuales: {columnas}")
            
            # ✅ CORRECCIÓN: Eliminar columna duplicada servmanicura si existe
            if 'servmanicura' in columnas and 'servicios_manicura' in columnas:
                print("🔄 Eliminando columna duplicada 'servmanicura'...")
                self.cursor.execute('''
                    CREATE TABLE temp_turnos AS 
                    SELECT id, nombre, telefono, servicio, estilista, manicura, 
                           servicios_manicura, fecha, hora, created_at, whatsapp_enviado
                    FROM turnos
                ''')
                self.cursor.execute('DROP TABLE turnos')
                self.cursor.execute('ALTER TABLE temp_turnos RENAME TO turnos')
                self.conexion.commit()
                print("✅ Columna duplicada eliminada")
            
            columnas_necesarias = [
                'servicios_manicura',
                'servicio',
                'manicura',
                'estilista',
                'fecha',
                'hora'
            ]
            
            columnas_agregadas = []
            for columna in columnas_necesarias:
                if columna not in columnas:
                    print(f"🔄 Agregando columna '{columna}'...")
                    self.cursor.execute(f'ALTER TABLE turnos ADD COLUMN {columna} TEXT')
                    self.conexion.commit()
                    columnas_agregadas.append(columna)
                    print(f"✅ Columna '{columna}' agregada")
            
            if columnas_agregadas:
                print(f"🎯 Columnas agregadas: {columnas_agregadas}")
            else:
                print("✅ Estructura de BD correcta")
            
        except Exception as e:
            print(f"❌ Error al reparar BD: {e}")
            messagebox.showerror('Error BD', f'Error en estructura: {e}')

    def cargar_profesionales(self):
        self.estilistas = [
            'Alejandro Cosentini', 'Guillermo Mirabile', 'Paola Rodriguez', 
            'Miguel Riviera', 'Fabian Gomez', 'Rodrigo Carbonero', 
            'Veronica Parra', 'Walter Tejada', 'Jorgelina Silvero', 'No aplica'
        ]
        self.manicuras = ['Liliana Pavon', 'Noelia Leguizamon', 'No aplica']

    # 🆕 NUEVO MÓDULO DE GESTIÓN DE AUSENCIAS
    def gestionar_ausencias(self):
        """Abre la ventana de gestión de ausencias"""
        ventana = tk.Toplevel(self.root)
        ventana.title('📅 Gestión de Ausencias - NEW STATION')
        ventana.geometry('1000x700')
        ventana.configure(bg=self.estilos['fondo'])
        ventana.transient(self.root)
        ventana.grab_set()

        # Header
        frame_header = tk.Frame(ventana, bg=self.estilos['primario'])
        frame_header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(frame_header, text='📅 GESTIÓN DE AUSENCIAS', 
                font=('Arial', 16, 'bold'), bg=self.estilos['primario'], 
                fg='white', padx=20, pady=15).pack()

        # Contenido principal
        frame_main = tk.Frame(ventana, bg=self.estilos['fondo'], padx=20, pady=20)
        frame_main.pack(fill=tk.BOTH, expand=True)

        # Selección de profesional
        frame_seleccion = tk.Frame(frame_main, bg=self.estilos['fondo'])
        frame_seleccion.pack(fill=tk.X, pady=(0, 20))

        tk.Label(frame_seleccion, text='Seleccionar Profesional:', 
                font=('Arial', 12, 'bold'), bg=self.estilos['fondo']).pack(side=tk.LEFT, padx=(0, 15))

        # Combobox para seleccionar profesional
        todos_profesionales = self.estilistas + self.manicuras
        combo_profesional = ttk.Combobox(frame_seleccion, values=todos_profesionales, 
                                       state='readonly', font=('Arial', 11), width=25)
        combo_profesional.pack(side=tk.LEFT, padx=(0, 20))
        
        # Botón para abrir calendario
        btn_abrir_calendario = tk.Button(frame_seleccion, text='📅 ABRIR CALENDARIO', 
                                       bg=self.estilos['info'], fg='white',
                                       font=('Arial', 10, 'bold'), padx=15, pady=8,
                                       command=lambda: self.abrir_calendario_profesional(combo_profesional.get(), ventana))
        btn_abrir_calendario.pack(side=tk.LEFT)

        # Lista de ausencias existentes
        frame_ausencias = tk.Frame(frame_main, bg=self.estilos['fondo'])
        frame_ausencias.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame_ausencias, text='Ausencias Programadas:', 
                font=('Arial', 12, 'bold'), bg=self.estilos['fondo']).pack(anchor='w', pady=(0, 10))

        # Treeview para mostrar ausencias
        tree_ausencias = ttk.Treeview(frame_ausencias, 
                                    columns=('ID', 'Profesional', 'Fecha', 'Motivo'), 
                                    show='headings', height=8)
        
        tree_ausencias.heading('ID', text='ID')
        tree_ausencias.heading('Profesional', text='Profesional')
        tree_ausencias.heading('Fecha', text='Fecha')
        tree_ausencias.heading('Motivo', text='Motivo')

        tree_ausencias.column('ID', width=50)
        tree_ausencias.column('Profesional', width=150)
        tree_ausencias.column('Fecha', width=100)
        tree_ausencias.column('Motivo', width=200)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_ausencias, orient=tk.VERTICAL, command=tree_ausencias.yview)
        tree_ausencias.configure(yscrollcommand=scrollbar.set)

        tree_ausencias.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Cargar ausencias existentes
        def cargar_ausencias():
            for item in tree_ausencias.get_children():
                tree_ausencias.delete(item)
            
            try:
                self.cursor.execute('SELECT * FROM ausencias ORDER BY fecha DESC')
                ausencias = self.cursor.fetchall()
                
                for ausencia in ausencias:
                    tree_ausencias.insert('', tk.END, values=ausencia)
                    
            except Exception as e:
                print(f"❌ Error al cargar ausencias: {e}")

        cargar_ausencias()

        # Botón para eliminar ausencia
        def eliminar_ausencia():
            seleccion = tree_ausencias.selection()
            if not seleccion:
                messagebox.showwarning('Eliminar', 'Seleccione una ausencia para eliminar')
                return
            
            ausencia_id = tree_ausencias.item(seleccion[0])['values'][0]
            profesional = tree_ausencias.item(seleccion[0])['values'][1]
            fecha = tree_ausencias.item(seleccion[0])['values'][2]
            
            if messagebox.askyesno('Confirmar', f'¿Eliminar ausencia de {profesional} para el {fecha}?'):
                try:
                    self.cursor.execute('DELETE FROM ausencias WHERE id = ?', (ausencia_id,))
                    self.conexion.commit()
                    messagebox.showinfo('Éxito', 'Ausencia eliminada correctamente')
                    cargar_ausencias()
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo eliminar: {e}')

        frame_botones = tk.Frame(frame_ausencias, bg=self.estilos['fondo'])
        frame_botones.pack(fill=tk.X, pady=(10, 0))

        btn_eliminar = tk.Button(frame_botones, text='🗑️ ELIMINAR AUSENCIA', 
                               bg=self.estilos['peligro'], fg='white',
                               font=('Arial', 10, 'bold'), padx=15, pady=8,
                               command=eliminar_ausencia)
        btn_eliminar.pack(side=tk.LEFT, padx=(0, 10))

        btn_actualizar = tk.Button(frame_botones, text='🔄 ACTUALIZAR', 
                                 bg=self.estilos['info'], fg='white',
                                 font=('Arial', 10, 'bold'), padx=15, pady=8,
                                 command=cargar_ausencias)
        btn_actualizar.pack(side=tk.LEFT)

    def abrir_calendario_profesional(self, profesional, ventana_parent):
        """Abre el calendario individual para un profesional"""
        if not profesional:
            messagebox.showwarning('Seleccionar', 'Seleccione un profesional primero')
            return
        
        ventana = tk.Toplevel(ventana_parent)
        ventana.title(f'📅 Calendario - {profesional}')
        ventana.geometry('800x600')
        ventana.configure(bg=self.estilos['fondo'])
        ventana.transient(ventana_parent)
        ventana.grab_set()

        # Header
        frame_header = tk.Frame(ventana, bg=self.estilos['primario'])
        frame_header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame_header, text=f'📅 CALENDARIO DE {profesional.upper()}', 
                font=('Arial', 14, 'bold'), bg=self.estilos['primario'], 
                fg='white', padx=20, pady=12).pack()

        # Controles de mes/año
        frame_controles = tk.Frame(ventana, bg=self.estilos['fondo'], padx=20, pady=10)
        frame_controles.pack(fill=tk.X)

        tk.Label(frame_controles, text='Año:', bg=self.estilos['fondo'], 
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        
        año_actual = datetime.now().year
        años = [str(año) for año in range(año_actual, año_actual + 3)]
        
        combo_año = ttk.Combobox(frame_controles, values=años, width=8,
                               state="readonly", font=("Arial", 10))
        combo_año.set(str(año_actual))
        combo_año.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(frame_controles, text="Mes:", bg=self.estilos["fondo"], 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        combo_mes = ttk.Combobox(frame_controles, values=meses, width=12,
                               state="readonly", font=("Arial", 10))
        combo_mes.set(meses[datetime.now().month - 1])
        combo_mes.pack(side=tk.LEFT)

        # Frame para el calendario
        frame_calendario = tk.Frame(ventana, bg=self.estilos['fondo'], padx=20, pady=10)
        frame_calendario.pack(fill=tk.BOTH, expand=True)

        # Días de la semana
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for i, dia in enumerate(dias_semana):
            tk.Label(frame_calendario, text=dia, bg=self.estilos['fondo'], 
                    font=('Arial', 10, 'bold'), width=10, height=2).grid(row=0, column=i, padx=2, pady=2)

        # Función para cargar días de ausencia del profesional
        def cargar_ausencias_profesional():
            try:
                self.cursor.execute('SELECT fecha FROM ausencias WHERE profesional = ?', (profesional,))
                ausencias = [ausencia[0] for ausencia in self.cursor.fetchall()]
                return ausencias
            except Exception as e:
                print(f"❌ Error al cargar ausencias: {e}")
                return []

        # Función para actualizar calendario
        def actualizar_calendario():
            # Limpiar calendario
            for widget in frame_calendario.grid_slaves():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()
            
            mes_seleccionado = combo_mes.current() + 1
            año_seleccionado = int(combo_año.get())
            
            primer_dia = datetime(año_seleccionado, mes_seleccionado, 1)
            if mes_seleccionado == 12:
                ultimo_dia = datetime(año_seleccionado + 1, 1, 1)
            else:
                ultimo_dia = datetime(año_seleccionado, mes_seleccionado + 1, 1)
            
            dias_en_mes = (ultimo_dia - primer_dia).days
            dia_semana_inicio = primer_dia.weekday()
            
            # Cargar ausencias actuales
            ausencias_actuales = cargar_ausencias_profesional()
            
            fila, columna = 1, dia_semana_inicio
            for dia in range(1, dias_en_mes + 1):
                fecha_actual = f"{año_seleccionado}-{mes_seleccionado:02d}-{dia:02d}"
                fecha_mostrar = f"{dia:02d}/{mes_seleccionado:02d}/{año_seleccionado}"
                
                # Verificar si es día de ausencia
                es_ausencia = fecha_actual in ausencias_actuales
                
                if es_ausencia:
                    bg_color = self.estilos['ausencia']  # Rojo para ausencia
                    texto = "🚫"
                    tooltip = f"{fecha_mostrar}\n{profesional} NO ATIENDE"
                else:
                    bg_color = self.estilos['info']  # Azul para día normal
                    texto = str(dia)
                    tooltip = f"{fecha_mostrar}\nClick para marcar/desmarcar"
                
                btn_dia = tk.Button(
                    frame_calendario,
                    text=texto,
                    font=("Arial", 9, "bold"),
                    bg=bg_color,
                    fg="white" if es_ausencia else "white",
                    relief="solid",
                    bd=1,
                    width=8,
                    height=2,
                    command=lambda f=fecha_actual, d=dia, m=mes_seleccionado, a=año_seleccionado: 
                    toggle_ausencia(f, f"{d:02d}/{m:02d}/{a}")
                )
                
                # Tooltip
                def make_tooltip(widget, text):
                    def enter(event):
                        tooltip = tk.Toplevel(widget)
                        tooltip.wm_overrideredirect(True)
                        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                        label = tk.Label(tooltip, text=text, bg="yellow", relief="solid", bd=1)
                        label.pack()
                        widget.tooltip = tooltip
                    def leave(event):
                        if hasattr(widget, 'tooltip'):
                            widget.tooltip.destroy()
                    widget.bind("<Enter>", enter)
                    widget.bind("<Leave>", leave)
                
                make_tooltip(btn_dia, tooltip)
                
                # Marcar día actual
                hoy = datetime.now()
                if (dia == hoy.day and mes_seleccionado == hoy.month and 
                    año_seleccionado == hoy.year):
                    btn_dia.config(bg=self.estilos['exito'])
                
                btn_dia.grid(row=fila, column=columna, padx=2, pady=2)
                
                columna += 1
                if columna > 6:
                    columna = 0
                    fila += 1

        # ✅ CORRECCIÓN: Función toggle_ausencia mejorada
        def toggle_ausencia(fecha_sql, fecha_mostrar):
            try:
                # Verificar si ya existe
                self.cursor.execute('SELECT id FROM ausencias WHERE profesional = ? AND fecha = ?', 
                                  (profesional, fecha_sql))
                existe = self.cursor.fetchone()
                
                if existe:
                    # Eliminar ausencia
                    self.cursor.execute('DELETE FROM ausencias WHERE profesional = ? AND fecha = ?', 
                                      (profesional, fecha_sql))
                    mensaje = f'✅ {profesional} ahora SÍ atiende el {fecha_mostrar}'
                else:
                    # Agregar ausencia
                    self.cursor.execute('INSERT INTO ausencias (profesional, tipo, fecha, motivo) VALUES (?, ?, ?, ?)',
                                      (profesional, 'Día específico', fecha_sql, 'Ausencia programada'))
                    mensaje = f'🚫 {profesional} NO atiende el {fecha_mostrar}'
                
                self.conexion.commit()
                
                # ✅ CORRECCIÓN: Usar after() para dar tiempo a la UI
                ventana.after(100, actualizar_calendario)
                
                # ✅ CORRECCIÓN: Mensaje después de la actualización
                ventana.after(150, lambda: messagebox.showinfo('Ausencia', mensaje))
                
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo actualizar: {e}')

        # Configurar eventos
        combo_mes.bind('<<ComboboxSelected>>', lambda e: actualizar_calendario())
        combo_año.bind('<<ComboboxSelected>>', lambda e: actualizar_calendario())
        
        # Cargar calendario inicial
        actualizar_calendario()

    # 🆕 FUNCIÓN PARA VERIFICAR DISPONIBILIDAD
    def verificar_disponibilidad(self, profesional, fecha_str):
        """Verifica si un profesional está disponible en una fecha específica"""
        try:
            # Convertir fecha a formato SQL
            fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
            fecha_sql = fecha_obj.strftime('%Y-%m-%d')
            
            # Verificar en tabla de ausencias
            self.cursor.execute('SELECT id FROM ausencias WHERE profesional = ? AND fecha = ?', 
                              (profesional, fecha_sql))
            
            if self.cursor.fetchone():
                return False  # No está disponible
            return True  # Está disponible
            
        except Exception as e:
            print(f"❌ Error al verificar disponibilidad: {e}")
            return True  # Por defecto, asumir disponible

    # 🆕 MODIFICAR LA FUNCIÓN agregar_turno PARA INCLUIR VALIDACIÓN DE AUSENCIAS
    def agregar_turno(self):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        servicios = self.entry_servicios.get().strip()
        estilista = self.combo_estilista.get().strip()
        manicura = self.combo_manicura.get().strip()
        servicios_manicura = self.entry_servicios_manicura.get().strip()

        fecha_str = self.entry_fecha.get()
        try:
            fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
            fecha = fecha_obj.strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning('Error', 'Formato de fecha inválido. Use DD/MM/AAAA')
            return

        hora = self.entry_hora.get().strip()

        if not all([nombre, telefono, estilista, manicura, hora]):
            messagebox.showwarning('Error', 'Complete los campos obligatorios: Nombre, Teléfono, Estilista, Manicura y Hora')
            return

        # 🆕 VALIDACIÓN 1: Verificar ausencias de estilista
        if estilista != "No aplica" and not self.verificar_disponibilidad(estilista, fecha_str):
            messagebox.showerror(
                'Estilista No Disponible', 
                f'❌ {estilista} NO atiende el {fecha_str}\n\n'
                f'Por favor, seleccione otra fecha o otro estilista.'
            )
            return

        # 🆕 VALIDACIÓN 2: Verificar ausencias de manicura
        if manicura != "No aplica" and not self.verificar_disponibilidad(manicura, fecha_str):
            messagebox.showerror(
                'Manicura No Disponible', 
                f'❌ {manicura} NO atiende el {fecha_str}\n\n'
                f'Por favor, seleccione otra fecha u otra manicura.'
            )
            return

        # Resto de validaciones existentes...
        # Validación de turnos duplicados
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM turnos 
                WHERE nombre = ? AND fecha = ? AND hora = ?
            ''', (nombre, fecha, hora))
            
            turno_duplicado = self.cursor.fetchone()[0] > 0
            
            if turno_duplicado:
                messagebox.showwarning(
                    'Turno Duplicado', 
                    f'❌ Ya existe un turno para {nombre} el {fecha_str} a las {hora}\n\n'
                    f'Por favor, verifique los datos o elija otra fecha/hora.'
                )
                return

            # Validación extra: Verificar superposición de estilista
            self.cursor.execute('''
                SELECT COUNT(*) FROM turnos 
                WHERE estilista = ? AND fecha = ? AND hora = ? AND estilista != "No aplica"
            ''', (estilista, fecha, hora))
            
            estilista_ocupado = self.cursor.fetchone()[0] > 0
            
            if estilista_ocupado:
                respuesta = messagebox.askyesno(
                    'Estilista Ocupado', 
                    f'⚠️ {estilista} ya tiene un turno el {fecha_str} a las {hora}\n\n'
                    f'¿Desea agregar el turno de todas formas?'
                )
                if not respuesta:
                    return

            # Validación extra: Verificar superposición de manicura
            self.cursor.execute('''
                SELECT COUNT(*) FROM turnos 
                WHERE manicura = ? AND fecha = ? AND hora = ? AND manicura != "No aplica"
            ''', (manicura, fecha, hora))
            
            manicura_ocupada = self.cursor.fetchone()[0] > 0
            
            if manicura_ocupada:
                respuesta = messagebox.askyesno(
                    'Manicura Ocupada', 
                    f'⚠️ {manicura} ya tiene un turno el {fecha_str} a las {hora}\n\n'
                    f'¿Desea agregar el turno de todas formas?'
                )
                if not respuesta:
                    return

        except Exception as err:
            print(f"❌ Error en validación: {err}")

        # Si pasó todas las validaciones, insertar el turno
        try:
            self.cursor.execute('''
                INSERT INTO turnos 
                (nombre, telefono, servicio, estilista, manicura, servicios_manicura, fecha, hora)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, telefono, servicios, estilista, manicura, servicios_manicura, fecha, hora))

            self.conexion.commit()
            messagebox.showinfo('Éxito', '✅ Turno agregado correctamente')
            self.limpiar_formulario()
            self.cargar_turnos()
        except Exception as err:
            print(f"❌ Error al agregar: {err}")
            messagebox.showerror('Error BD', f'No se pudo agregar: {err}')

    # ... (el resto de tus funciones existentes se mantienen igual)
    # Solo agregué las funciones nuevas arriba y modifiqué agregar_turno

    def determinar_color_turno(self, fecha_str, hora_str):
        """Determina el color según si el turno es pasado, presente o futuro"""
        try:
            # ✅ CORRECCIÓN: Manejar diferentes formatos de fecha
            fecha_turno = None
            
            # Intentar formato YYYY-MM-DD HH:MM:SS (de la base de datos)
            try:
                fecha_turno = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S').date()
            except:
                # Intentar formato YYYY-MM-DD
                try:
                    fecha_turno = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                except:
                    # Intentar formato DD/MM/YYYY
                    try:
                        fecha_turno = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                    except:
                        print(f"❌ No se pudo parsear fecha: {fecha_str}")
                        return 'white'
            
            fecha_actual = date.today()
            
            if fecha_turno < fecha_actual:
                return self.estilos['turno_pasado']  # 🎀 ROSADO - Turno pasado
            elif fecha_turno > fecha_actual:
                return self.estilos['turno_futuro']  # 🟢 VERDE CLARO - Turno futuro
            else:
                # Misma fecha, verificar hora
                hora_actual = datetime.now().strftime('%H:%M')
                if hora_str < hora_actual:
                    return self.estilos['turno_pasado']  # 🎀 ROSADO - Turno de hoy que ya pasó
                else:
                    return self.estilos['turno_presente']  # 🔵 CELESTE - Turno de hoy que viene
                    
        except Exception as e:
            print(f"❌ Error en determinar_color_turno: {e}")
            return 'white'  # Color por defecto en caso de error

    def agregar_doble_click(self):
        self.tabla.bind("<Double-1>", self.mostrar_detalles_completos)

    def mostrar_detalles_completos(self, event):
        item = self.tabla.identify_row(event.y)
        if item:
            self.tabla.selection_set(item)
            valores = self.tabla.item(item, 'values')
            self.mostrar_detalles_turno(valores)

    def mostrar_detalles_turno(self, valores):
        ventana = tk.Toplevel(self.root)
        ventana.title(f'Detalles Turno - {valores[1]}')
        ventana.geometry('400x500')
        ventana.configure(bg=self.estilos['fondo'])
        
        frame_header = tk.Frame(ventana, bg=self.estilos['primario'])
        frame_header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame_header, text='DETALLES DEL TURNO', 
                font=('Arial', 14, 'bold'), bg=self.estilos['primario'], 
                fg='white', padx=20, pady=12).pack()
        
        frame_content = tk.Frame(ventana, bg=self.estilos['fondo'], padx=20, pady=20)
        frame_content.pack(fill=tk.BOTH, expand=True)
        
        datos = [
            ('ID:', valores[0]),
            ('👤 CLIENTE:', valores[1]),
            ('📞 TELÉFONO:', valores[2]),
            ('💇 ESTILISTA:', valores[3]),
            ('✂️ SERVICIOS:', valores[4]),
            ('💅 MANICURA:', valores[5]),
            ('🎨 SERV. MANICURA:', valores[6]),
            ('📅 FECHA:', valores[7]),
            ('🕒 HORA:', valores[8])
        ]
        
        for etiqueta, valor in datos:
            frame_fila = tk.Frame(frame_content, bg=self.estilos['fondo'])
            frame_fila.pack(fill=tk.X, pady=8)
            tk.Label(frame_fila, text=etiqueta, bg=self.estilos['fondo'],
                    font=('Arial', 10, 'bold'), fg=self.estilos['texto_oscuro'],
                    width=16, anchor='w').pack(side=tk.LEFT)
            tk.Label(frame_fila, text=valor or 'No especificado', bg='white',
                    font=('Arial', 10), fg=self.estilos['texto_oscuro'],
                    relief='solid', bd=1, padx=8, pady=4, width=25, anchor='w').pack(side=tk.LEFT)
        
        tk.Button(frame_content, text='✅ CERRAR', bg=self.estilos['exito'], fg='white',
                 font=('Arial', 11, 'bold'), command=ventana.destroy,
                 padx=20, pady=10).pack(pady=20)

    def agregar_menu_contextual(self):
        self.menu_contextual = tk.Menu(self.tabla, tearoff=0)
        self.menu_contextual.add_command(label="📝 Editar Turno", command=self.editar_turno)
        self.menu_contextual.add_command(label="✅ Enviar WhatsApp", command=self.enviar_whatsapp)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🗑️ Eliminar Turno", command=self.eliminar_turno)
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)

    def mostrar_menu_contextual(self, event):
        item = self.tabla.identify_row(event.y)
        if item:
            self.tabla.selection_set(item)
            self.menu_contextual.post(event.x_root, event.y_root)

    def editar_turno(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning('Editar', 'Seleccione un turno para editar')
            return
        
        item = seleccion[0]
        valores = self.tabla.item(item, 'values')
        self.mostrar_edicion_turno(valores)

    def mostrar_edicion_turno(self, valores):
        ventana = tk.Toplevel(self.root)
        ventana.title(f'Editar Turno - {valores[1]}')
        ventana.geometry('400x600')
        ventana.configure(bg=self.estilos['fondo'])
        
        turno_id = valores[0]
        
        frame_header = tk.Frame(ventana, bg=self.estilos['primario'])
        frame_header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame_header, text='EDITAR TURNO', font=('Arial', 14, 'bold'), 
                bg=self.estilos['primario'], fg='white', padx=20, pady=12).pack()
        
        frame_content = tk.Frame(ventana, bg=self.estilos['fondo'], padx=20, pady=20)
        frame_content.pack(fill=tk.BOTH, expand=True)
        
        # Campos de edición
        tk.Label(frame_content, text='Nombre*:', bg=self.estilos['fondo'], 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        entry_nombre = tk.Entry(frame_content, font=('Arial', 10), width=30)
        entry_nombre.pack(fill=tk.X, pady=(0, 10))
        entry_nombre.insert(0, valores[1])
        
        tk.Label(frame_content, text='Teléfono*:', bg=self.estilos['fondo'], 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        entry_telefono = tk.Entry(frame_content, font=('Arial', 10), width=30)
        entry_telefono.pack(fill=tk.X, pady=(0, 10))
        entry_telefono.insert(0, valores[2])
        
        tk.Label(frame_content, text='Estilista*:', bg=self.estilos['fondo'], 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        combo_estilista = ttk.Combobox(frame_content, values=self.estilistas, state='readonly')
        combo_estilista.pack(fill=tk.X, pady=(0, 10))
        combo_estilista.set(valores[3])
        
        tk.Label(frame_content, text='Servicios:', bg=self.estilos['fondo'], 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        entry_servicios = tk.Entry(frame_content, font=('Arial', 10), width=30)
        entry_servicios.pack(fill=tk.X, pady=(0, 10))
        entry_servicios.insert(0, valores[4])
        
        tk.Label(frame_content, text='Manicura*:', bg=self.estilos['fondo'], 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        combo_manicura = ttk.Combobox(frame_content, values=self.manicuras, state='readonly')
        combo_manicura.pack(fill=tk.X, pady=(0, 10))
        combo_manicura.set(valores[5])
        
        tk.Label(frame_content, text='Servicios Manicura:', bg=self.estilos['fondo'], 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        entry_serv_manicura = tk.Entry(frame_content, font=('Arial', 10), width=30)
        entry_serv_manicura.pack(fill=tk.X, pady=(0, 10))
        entry_serv_manicura.insert(0, valores[6])
        
        tk.Label(frame_content, text='Fecha* (DD/MM/AAAA):', bg=self.estilos['fondo'], 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        entry_fecha = tk.Entry(frame_content, font=('Arial', 10), width=30)
        entry_fecha.pack(fill=tk.X, pady=(0, 10))
        entry_fecha.insert(0, valores[7])
        
        tk.Label(frame_content, text='Hora* (HH:MM):', bg=self.estilos['fondo'], 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        entry_hora = tk.Entry(frame_content, font=('Arial', 10), width=30)
        entry_hora.pack(fill=tk.X, pady=(0, 20))
        entry_hora.insert(0, valores[8])
        
        def guardar_cambios():
            try:
                # Validar campos obligatorios
                if not all([entry_nombre.get(), entry_telefono.get(), 
                           combo_estilista.get(), combo_manicura.get(),
                           entry_fecha.get(), entry_hora.get()]):
                    messagebox.showwarning('Error', 'Complete todos los campos obligatorios')
                    return
                
                # Validar fecha
                try:
                    fecha_obj = datetime.strptime(entry_fecha.get(), '%d/%m/%Y')
                    fecha_sql = fecha_obj.strftime('%Y-%m-%d')
                except:
                    messagebox.showwarning('Error', 'Formato de fecha inválido. Use DD/MM/AAAA')
                    return
                
                # ✅ CORRECCIÓN: Actualizar con índices correctos
                self.cursor.execute('''
                    UPDATE turnos SET nombre=?, telefono=?, servicio=?, estilista=?, 
                    manicura=?, servicios_manicura=?, fecha=?, hora=? WHERE id=?
                ''', (entry_nombre.get(), entry_telefono.get(), entry_servicios.get(),
                      combo_estilista.get(), combo_manicura.get(), entry_serv_manicura.get(),
                      fecha_sql, entry_hora.get(), turno_id))
                
                self.conexion.commit()
                messagebox.showinfo('Éxito', 'Turno actualizado correctamente')
                self.cargar_turnos()
                ventana.destroy()
                
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo actualizar: {e}')
        
        tk.Button(frame_content, text='💾 GUARDAR', bg=self.estilos['exito'], fg='white',
                 font=('Arial', 12, 'bold'), command=guardar_cambios,
                 padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(frame_content, text='❌ CANCELAR', bg=self.estilos['peligro'], fg='white',
                 font=('Arial', 12, 'bold'), command=ventana.destroy,
                 padx=20, pady=10).pack(side=tk.LEFT)

    def enviar_whatsapp(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning('WhatsApp', 'Seleccione un turno para enviar WhatsApp')
            return
        
        item = seleccion[0]
        valores = self.tabla.item(item, 'values')
        
        nombre = valores[1]
        telefono = valores[2]
        estilista = valores[3]
        servicios = valores[4] or "No especificado"
        manicura = valores[5]
        servicios_manicura = valores[6] or "No especificado"
        fecha = valores[7]
        hora = valores[8]
        
        if not telefono or len(telefono) < 8:
            messagebox.showerror('Error', 'El turno no tiene un número de teléfono válido')
            return
        
        # ✅ FORMATO SIMPLIFICADO Y CORRECTO
        telefono_limpio = ''.join(filter(str.isdigit, telefono))
        
        # Quitar prefijos
        if telefono_limpio.startswith('549'):
            telefono_limpio = telefono_limpio[3:]
        elif telefono_limpio.startswith('54'):
            telefono_limpio = telefono_limpio[2:]
        elif telefono_limpio.startswith('15'):
            telefono_limpio = telefono_limpio[2:]
        
        print(f"📱 Teléfono original: {telefono}")
        print(f"📱 Teléfono limpio: {telefono_limpio}")
        
        # Mensaje completo
        mensaje = f"""¡Hola {nombre}! ✨

Confirmamos tu turno en *NEW STATION - Pueyrredon*:

📅 *Fecha:* {fecha}
🕒 *Hora:* {hora}
💇 *Estilista:* {estilista}
💅 *Manicura:* {manicura}

*Servicios:* {servicios}
*Servicios de manicura:* {servicios_manicura}

¡Te esperamos! 🎉"""
        
        # ✅ MEJORA DEFINITIVA: COPIAR AL PORTAPAPELES + OPCIONES FLEXIBLES
        try:
            # 1. COPIAR MENSAJE AL PORTAPAPELES
            pyperclip.copy(mensaje)
            
            # 2. OPCIONAL: Abrir WhatsApp Web (solo si no está abierto)
            try:
                # Intentar abrir en misma pestaña si ya está abierto
                mensaje_codificado = urllib.parse.quote(mensaje)
                url_whatsapp = f"https://web.whatsapp.com/send?phone=54{telefono_limpio}&text={mensaje_codificado}"
                webbrowser.open(url_whatsapp, new=0)  # new=0 reusa misma ventana
            except:
                # Si falla, solo copiar al portapapeles
                pass
            
            # 3. MENSAJE MEJORADO CON MÚLTIPLES OPCIONES
            messagebox.showinfo(
                'WhatsApp Listo 🚀', 
                f'✅ *TODO COPIADO* para {nombre}\n\n'
                f'📱 *NÚMERO:* {telefono_limpio}\n'
                f'💬 *MENSAJE:* (copiado al portapapeles)\n\n'
                f'*OPCIONES RÁPIDAS:*\n'
                f'1. 📋 Pegar mensaje en WhatsApp Web/Desktop (Ctrl+V)\n'
                f'2. 📞 Buscar número: {telefono_limpio}\n' 
                f'3. 🖱️ Click en ENVIAR\n\n'
                f'*¡Listo en segundos!* ⚡\n'
                f'(Se abrió WhatsApp Web si no estaba abierto)'
            )
            
        except Exception as e:
            # Fallback por si pyperclip falla
            messagebox.showerror('Error', f'No se pudo copiar al portapapeles: {e}')

    def crear_boton_redondeado(self, parent, text, color, command=None, width=12):
        return tk.Button(parent, text=text, bg=color, fg='white', font=('Arial', 9, 'bold'),
                        relief='flat', bd=0, padx=8, pady=6, width=width, command=command)

    def selector_hora(self):
        ventana_hora = tk.Toplevel(self.root)
        ventana_hora.title('Seleccionar Hora')
        ventana_hora.geometry('300x400')
        ventana_hora.configure(bg=self.estilos['fondo'])
        ventana_hora.transient(self.root)
        ventana_hora.grab_set()

        frame_principal = tk.Frame(ventana_hora, bg=self.estilos['fondo'], padx=20, pady=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame_principal, text='Seleccionar Hora', font=('Arial', 14, 'bold'), 
                bg=self.estilos['fondo'], fg=self.estilos['texto_oscuro']).pack(pady=(0, 20))

        frame_horas = tk.Frame(frame_principal, bg=self.estilos['fondo'])
        frame_horas.pack(fill=tk.BOTH, expand=True)

        horas = []
        for hora in range(9, 21):
            for minuto in [0, 30]:
                if hora == 20 and minuto == 30: continue
                horas.append(f'{hora:02d}:{minuto:02d}')

        fila, columna = 0, 0
        for hora in horas:
            btn = tk.Button(frame_horas, text=hora, font=('Arial', 9), bg=self.estilos['info'],
                           fg='white', relief='flat', bd=0, padx=10, pady=8,
                           command=lambda h=hora: self.seleccionar_hora(h, ventana_hora))
            btn.grid(row=fila, column=columna, padx=5, pady=5, sticky='ew')
            columna += 1
            if columna > 2: columna, fila = 0, fila + 1
        
        for i in range(3): frame_horas.grid_columnconfigure(i, weight=1)

    def seleccionar_hora(self, hora, ventana):
        self.entry_hora.delete(0, tk.END)
        self.entry_hora.insert(0, hora)
        ventana.destroy()

    def selector_fecha(self):
        ventana_fecha = tk.Toplevel(self.root)
        ventana_fecha.title("Seleccionar Fecha")
        ventana_fecha.geometry("300x350")
        ventana_fecha.configure(bg=self.estilos["fondo"])
        ventana_fecha.transient(self.root)
        ventana_fecha.grab_set()
        
        frame_principal = tk.Frame(ventana_fecha, bg=self.estilos["fondo"], padx=20, pady=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame_principal, text="Seleccionar Fecha", 
                font=("Arial", 14, "bold"), bg=self.estilos["fondo"], 
                fg=self.estilos["texto_oscuro"]).pack(pady=(0, 15))
        
        frame_controles = tk.Frame(frame_principal, bg=self.estilos["fondo"])
        frame_controles.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame_controles, text="Año:", bg=self.estilos["fondo"], 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        año_actual = datetime.now().year
        años = [str(año) for año in range(año_actual, 2051)]
        
        combo_año = ttk.Combobox(frame_controles, values=años, width=8,
                               state="readonly", font=("Arial", 10))
        combo_año.set(str(año_actual))
        combo_año.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(frame_controles, text="Mes:", bg=self.estilos["fondo"], 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        combo_mes = ttk.Combobox(frame_controles, values=meses, width=12,
                               state="readonly", font=("Arial", 10))
        combo_mes.set(meses[datetime.now().month - 1])
        combo_mes.pack(side=tk.LEFT)
        
        frame_dias = tk.Frame(frame_principal, bg=self.estilos["fondo"])
        frame_dias.pack(fill=tk.BOTH, expand=True)
        
        dias_semana = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
        for i, dia in enumerate(dias_semana):
            tk.Label(frame_dias, text=dia, bg=self.estilos["fondo"], 
                    font=("Arial", 9, "bold"), width=4).grid(row=0, column=i, padx=2, pady=2)
        
        def actualizar_calendario():
            for widget in frame_dias.grid_slaves():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()
            
            mes_seleccionado = combo_mes.current() + 1
            año_seleccionado = int(combo_año.get())
            
            primer_dia = datetime(año_seleccionado, mes_seleccionado, 1)
            if mes_seleccionado == 12:
                ultimo_dia = datetime(año_seleccionado + 1, 1, 1)
            else:
                ultimo_dia = datetime(año_seleccionado, mes_seleccionado + 1, 1)
            
            dias_en_mes = (ultimo_dia - primer_dia).days
            dia_semana_inicio = primer_dia.weekday()
            
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
            fecha_str = f"{dia:02d}/{mes:02d}/{año}"
            self.entry_fecha.delete(0, tk.END)
            self.entry_fecha.insert(0, fecha_str)
            ventana.destroy()
        
        combo_mes.bind('<<ComboboxSelected>>', lambda e: actualizar_calendario())
        combo_año.bind('<<ComboboxSelected>>', lambda e: actualizar_calendario())
        actualizar_calendario()

    # ============================================================
    # 🆕 NUEVO SISTEMA DE BÚSQUEDAS SEPARADAS - CORREGIDO
    # ============================================================

    def buscar_por_estilista(self):
        """Búsqueda especializada por estilista"""
        texto = self.entry_busqueda.get().strip()
        if not texto:
            messagebox.showwarning('Búsqueda', 'Ingrese el nombre del estilista')
            return
        
        self.ejecutar_busqueda_especializada('estilista', texto, 'estilista')

    def buscar_por_cliente(self):
        """Búsqueda especializada por nombre de cliente"""
        texto = self.entry_busqueda.get().strip()
        if not texto:
            messagebox.showwarning('Búsqueda', 'Ingrese el nombre del cliente')
            return
        
        self.ejecutar_busqueda_especializada('cliente', texto, 'nombre')

    def buscar_por_telefono(self):
        """Búsqueda especializada por teléfono"""
        texto = self.entry_busqueda.get().strip()
        if not texto:
            messagebox.showwarning('Búsqueda', 'Ingrese el número de teléfono')
            return
        
        self.ejecutar_busqueda_especializada('teléfono', texto, 'telefono')

    def buscar_por_fecha(self):
        """Búsqueda especializada por fecha"""
        texto = self.entry_busqueda.get().strip()
        if not texto:
            messagebox.showwarning('Búsqueda', 'Ingrese la fecha (DD/MM/AAAA)')
            return
        
        # Validar formato de fecha
        try:
            datetime.strptime(texto, '%d/%m/%Y')
        except ValueError:
            messagebox.showwarning('Error', 'Formato de fecha inválido. Use DD/MM/AAAA')
            return
        
        self.ejecutar_busqueda_especializada('fecha', texto, 'fecha')

    def ejecutar_busqueda_especializada(self, tipo, texto, campo_bd):
        """Ejecuta la búsqueda especializada en la base de datos - CORREGIDO"""
        try:
            for item in self.tabla.get_children(): 
                self.tabla.delete(item)
            
            # Convertir formato de fecha si es búsqueda por fecha
            if campo_bd == 'fecha':
                try:
                    fecha_obj = datetime.strptime(texto, '%d/%m/%Y')
                    texto_bd = fecha_obj.strftime('%Y-%m-%d')
                except:
                    texto_bd = texto
            else:
                texto_bd = texto

            # Consulta específica según el tipo de búsqueda
            if campo_bd in ['nombre', 'telefono', 'estilista']:
                query = f'SELECT * FROM turnos WHERE {campo_bd} LIKE ? ORDER BY fecha ASC, hora ASC'
                parametros = (f'%{texto_bd}%',)
            else:  # Para fecha
                query = 'SELECT * FROM turnos WHERE fecha LIKE ? ORDER BY hora ASC'
                parametros = (f'{texto_bd}%',)  # Usar LIKE para coincidir con fechas que tengan hora

            self.cursor.execute(query, parametros)
            turnos = self.cursor.fetchall()
            
            if turnos:
                for turno in turnos:
                    # ✅ CORRECCIÓN DEFINITIVA: Índices correctos según estructura de BD
                    turno_formateado = self.formatear_turno_para_tabla(turno)
                    
                    color_fondo = self.determinar_color_turno(turno[7], turno[8])  # fecha, hora
                    item = self.tabla.insert('', tk.END, values=turno_formateado)
                    self.tabla.item(item, tags=(color_fondo,))
                    self.tabla.tag_configure(color_fondo, background=color_fondo)

                self.label_estado.config(
                    text=f'✅ {len(turnos)} turnos encontrados por {tipo} "{texto}"', 
                    fg=self.estilos['exito']
                )
            else:
                self.tabla.insert('', tk.END, values=('', f'No se encontraron turnos para {tipo} "{texto}"', '', '', '', '', '', '', ''))
                self.label_estado.config(
                    text=f'❌ No se encontraron turnos para {tipo} "{texto}"', 
                    fg=self.estilos['peligro']
                )

        except Exception as err:
            messagebox.showerror('Error BD', f'No se pudieron buscar los turnos: {err}')

    def buscar_turnos_general(self):
        """Búsqueda general (comportamiento original) - CORREGIDO"""
        texto_busqueda = self.entry_busqueda.get().strip().lower()
        
        if not texto_busqueda:
            messagebox.showwarning('Busqueda', 'Ingrese un término para buscar')
            return
        
        try:
            for item in self.tabla.get_children(): 
                self.tabla.delete(item)
            
            self.cursor.execute('''
                SELECT * FROM turnos 
                WHERE LOWER(nombre) LIKE ? 
                   OR LOWER(telefono) LIKE ? 
                   OR LOWER(estilista) LIKE ?
                   OR LOWER(servicio) LIKE ?
                   OR LOWER(manicura) LIKE ?
                   OR LOWER(servicios_manicura) LIKE ?
                ORDER BY 
                    CASE WHEN LOWER(nombre) LIKE ? THEN 1 ELSE 2 END,
                    fecha ASC, hora ASC
            ''', (
                f'%{texto_busqueda}%', f'%{texto_busqueda}%', f'%{texto_busqueda}%',
                f'%{texto_busqueda}%', f'%{texto_busqueda}%', f'%{texto_busqueda}%',
                f'%{texto_busqueda}%'
            ))

            turnos = self.cursor.fetchall()
            
            if turnos:
                for turno in turnos:
                    turno_formateado = self.formatear_turno_para_tabla(turno)
                    
                    color_fondo = self.determinar_color_turno(turno[7], turno[8])  # fecha, hora
                    item = self.tabla.insert('', tk.END, values=turno_formateado)
                    self.tabla.item(item, tags=(color_fondo,))
                    self.tabla.tag_configure(color_fondo, background=color_fondo)

                self.label_estado.config(text=f'✅ {len(turnos)} turnos encontrados para "{texto_busqueda}"', fg=self.estilos['exito'])
            else:
                self.tabla.insert('', tk.END, values=('', 'No se encontraron turnos', '', '', '', '', '', '', ''))
                self.label_estado.config(text=f'❌ No se encontraron turnos para "{texto_busqueda}"', fg=self.estilos['peligro'])

        except Exception as err:
            messagebox.showerror('Error BD', f'No se pudieron buscar los turnos: {err}')

    def formatear_turno_para_tabla(self, turno):
        """✅ CORRECCIÓN DEFINITIVA: Formatea un turno para mostrar en la tabla"""
        # ÍNDICES CORRECTOS según estructura de BD:
        # 0: id, 1: nombre, 2: telefono, 3: servicio, 4: estilista, 
        # 5: manicura, 6: servicios_manicura, 7: fecha, 8: hora
        
        fecha_sql = turno[7]  # Fecha en posición 7
        hora_turno = turno[8]  # Hora en posición 8
        servicios_manicura = turno[6] if turno[6] else ''  # ✅ SERVICIOS DE MANICURA en posición 6
        
        # Extraer solo la parte de la fecha (sin hora) para mostrar
        try:
            if ' ' in str(fecha_sql):
                fecha_obj = datetime.strptime(fecha_sql.split(' ')[0], '%Y-%m-%d')
            else:
                fecha_obj = datetime.strptime(fecha_sql, '%Y-%m-%d')
            
            fecha_mostrar = fecha_obj.strftime('%d/%m/%Y')  # ✅ "08/10/2025"
        except Exception as e:
            print(f"❌ Error al formatear fecha {fecha_sql}: {e}")
            fecha_mostrar = fecha_sql

        return (
            turno[0],  # ID
            turno[1],  # Nombre
            turno[2],  # Teléfono
            turno[4],  # Estilista
            turno[3],  # Servicio
            turno[5],  # Manicura
            servicios_manicura,  # ✅ SERVICIOS DE MANICURA (texto correcto)
            fecha_mostrar,  # Fecha formateada
            hora_turno  # Hora
        )

    def mostrar_todos(self):
        self.entry_busqueda.delete(0, tk.END)
        self.label_estado.config(text='Mostrando todos los turnos', fg=self.estilos['info'])
        self.cargar_turnos()

    def crear_componentes(self):
        # HEADER
        frame_header = tk.Frame(self.root, bg='white', relief='solid', bd=1)
        frame_header.pack(fill=tk.X, pady=(0, 20))

        logo_frame = tk.Frame(frame_header, bg='white')
        logo_frame.pack(side=tk.LEFT, padx=30, pady=15)
        tk.Label(logo_frame, text='NEW STATION', font=('Arial', 24, 'bold'), bg='white', fg=self.estilos['primario']).pack()
        tk.Label(logo_frame, text='PELUQUERIAS - Sucursal Pueyrredon', font=('Arial', 14), bg='white', fg=self.estilos['texto_claro']).pack()

        title_frame = tk.Frame(frame_header, bg='white')
        title_frame.pack(expand=True, pady=20)
        tk.Label(title_frame, text='SISTEMA DE GESTION DE TURNOS', font=('Arial', 16, 'bold'), bg='white', fg=self.estilos['texto_oscuro']).pack()

        # 🆕 BOTÓN DE GESTIÓN DE AUSENCIAS EN EL HEADER
        btn_ausencias = tk.Button(frame_header, text='📅 GESTIONAR AUSENCIAS', 
                                bg='#6f42c1', fg='white', font=('Arial', 11, 'bold'),
                                padx=15, pady=8, command=self.gestionar_ausencias)
        btn_ausencias.pack(side=tk.RIGHT, padx=30)

        # CONTENIDO PRINCIPAL
        frame_main = tk.Frame(self.root, bg=self.estilos['fondo'])
        frame_main.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # FORMULARIO IZQUIERDA
        frame_form_container = tk.Frame(frame_main, bg=self.estilos['fondo'], width=350)
        frame_form_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        frame_form_container.pack_propagate(False)

        frame_form_card = tk.Frame(frame_form_container, bg='white', relief='solid', bd=1)
        frame_form_card.pack(fill=tk.BOTH, expand=True)

        frame_card_header = tk.Frame(frame_form_card, bg=self.estilos['primario'])
        frame_card_header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame_card_header, text='NUEVO TURNO', font=('Arial', 14, 'bold'), bg=self.estilos['primario'], fg='white', padx=20, pady=12).pack()

        frame_form_content = tk.Frame(frame_form_card, bg='white', padx=20, pady=15)
        frame_form_content.pack(fill=tk.BOTH, expand=True)

        # Campos del formulario
        campos = [
            ('Nombre Cliente*:', 'entry_nombre'),
            ('Teléfono*:', 'entry_telefono'), 
            ('Estilista*:', 'combo_estilista'),
            ('Servicios:', 'entry_servicios'),
            ('Manicura*:', 'combo_manicura'),
            ('Servicios Manicura:', 'entry_servicios_manicura'),
            ('Hora*:', 'entry_hora'),
            ('Fecha*:', 'entry_fecha')
        ]

        for i, (label, attr) in enumerate(campos):
            frame_campo = tk.Frame(frame_form_content, bg='white')
            frame_campo.pack(fill=tk.X, pady=6)

            tk.Label(frame_campo, text=label, bg='white', font=('Arial', 10, 'bold'), 
                    fg=self.estilos['texto_oscuro'], width=16, anchor='w').pack(side=tk.LEFT, padx=(0, 10))

            if attr == 'entry_nombre':
                self.entry_nombre = tk.Entry(frame_campo, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_nombre.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_telefono':
                self.entry_telefono = tk.Entry(frame_campo, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_telefono.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'combo_estilista':
                self.combo_estilista = ttk.Combobox(frame_campo, font=('Arial', 10), values=self.estilistas, state='readonly')
                self.combo_estilista.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_servicios':
                self.entry_servicios = tk.Entry(frame_campo, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_servicios.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'combo_manicura':
                self.combo_manicura = ttk.Combobox(frame_campo, font=('Arial', 10), values=self.manicuras, state='readonly')
                self.combo_manicura.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_servicios_manicura':
                self.entry_servicios_manicura = tk.Entry(frame_campo, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_servicios_manicura.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_hora':
                frame_hora = tk.Frame(frame_campo, bg='white')
                frame_hora.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entry_hora = tk.Entry(frame_hora, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_hora.pack(side=tk.LEFT, fill=tk.X, expand=True)
                btn_selector = tk.Button(frame_hora, text='H', font=('Arial', 9), bg=self.estilos['info'], fg='white',
                                       relief='flat', bd=0, width=3, command=self.selector_hora)
                btn_selector.pack(side=tk.RIGHT, padx=(5, 0))
            elif attr == 'entry_fecha':
                frame_fecha = tk.Frame(frame_campo, bg='white')
                frame_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entry_fecha = tk.Entry(frame_fecha, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entry_fecha.insert(0, datetime.now().strftime('%d/%m/%Y'))
                btn_calendario = tk.Button(frame_fecha, text='C', font=('Arial', 9), bg=self.estilos['primario'], fg='white',
                                         relief='flat', bd=0, width=3, command=self.selector_fecha)
                btn_calendario.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Botones del formulario
        frame_botones = tk.Frame(frame_form_content, bg='white')
        frame_botones.pack(fill=tk.X, pady=15)

        btn_agregar = self.crear_boton_redondeado(frame_botones, 'AGREGAR', self.estilos['exito'], self.agregar_turno, width=12)
        btn_agregar.pack(side=tk.LEFT, padx=(0, 8))

        btn_limpiar = self.crear_boton_redondeado(frame_botones, 'LIMPIAR', self.estilos['advertencia'], self.limpiar_formulario, width=12)
        btn_limpiar.pack(side=tk.LEFT, padx=(0, 8))

        btn_actualizar = self.crear_boton_redondeado(frame_botones, 'ACTUALIZAR', self.estilos['info'], self.cargar_turnos, width=12)
        btn_actualizar.pack(side=tk.LEFT)

        # TABLA DERECHA CON NUEVO SISTEMA DE BÚSQUEDAS
        frame_tabla_container = tk.Frame(frame_main, bg=self.estilos['fondo'])
        frame_tabla_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        frame_tabla_card = tk.Frame(frame_tabla_container, bg='white', relief='solid', bd=1)
        frame_tabla_card.pack(fill=tk.BOTH, expand=True)
        
        frame_tabla_header = tk.Frame(frame_tabla_card, bg=self.estilos['primario'])
        frame_tabla_header.pack(fill=tk.X)
        tk.Label(frame_tabla_header, text='TURNOS REGISTRADOS', font=('Arial', 14, 'bold'), 
                bg=self.estilos['primario'], fg='white', padx=20, pady=15).pack()

        # 🆕 NUEVA BARRA DE BÚSQUEDAS ESPECIALIZADAS
        frame_busqueda = tk.Frame(frame_tabla_card, bg='white', padx=15, pady=10)
        frame_busqueda.pack(fill=tk.X)

        # Fila 1: Búsqueda general
        frame_busqueda_general = tk.Frame(frame_busqueda, bg='white')
        frame_busqueda_general.pack(fill=tk.X, pady=(0, 8))

        tk.Label(frame_busqueda_general, text='Buscar:', bg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        self.entry_busqueda = tk.Entry(frame_busqueda_general, font=('Arial', 10), relief='solid', bd=1, bg='white', width=25)
        self.entry_busqueda.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_busqueda.bind('<Return>', lambda e: self.buscar_turnos_general())

        # ✅ BOTONES CON TAMAÑO ORIGINAL
        btn_buscar_general = tk.Button(frame_busqueda_general, text='🔍 BUSCAR GENERAL', bg='#007bff', fg='white',
                                     font=('Arial', 9, 'bold'), command=self.buscar_turnos_general,
                                     padx=8, pady=6, width=15)  # ✅ Tamaño original
        btn_buscar_general.pack(side=tk.LEFT, padx=(0, 5))

        btn_todos = tk.Button(frame_busqueda_general, text='📋 MOSTRAR TODOS', bg='#6c757d', fg='white',
                            font=('Arial', 9, 'bold'), command=self.mostrar_todos,
                            padx=8, pady=6, width=15)  # ✅ Tamaño original
        btn_todos.pack(side=tk.LEFT)

        # Fila 2: Búsquedas especializadas
        frame_busqueda_especializada = tk.Frame(frame_busqueda, bg='white')
        frame_busqueda_especializada.pack(fill=tk.X)

        tk.Label(frame_busqueda_especializada, text='Búsquedas rápidas:', bg='white', 
                 font=('Arial', 10, 'bold'), fg='#343a40').pack(side=tk.LEFT, padx=(0, 10))

        # Botones coloridos
        btn_estilista = tk.Button(frame_busqueda_especializada, text='✂️ POR ESTILISTA', bg='#e83e8c', fg='white',
                                font=('Arial', 9, 'bold'), command=self.buscar_por_estilista,
                                padx=10, pady=5)
        btn_estilista.pack(side=tk.LEFT, padx=(0, 5))

        btn_cliente = tk.Button(frame_busqueda_especializada, text='👤 POR CLIENTE', bg='#20c997', fg='white',
                              font=('Arial', 9, 'bold'), command=self.buscar_por_cliente,
                              padx=10, pady=5)
        btn_cliente.pack(side=tk.LEFT, padx=(0, 5))

        btn_telefono = tk.Button(frame_busqueda_especializada, text='📞 POR TELÉFONO', bg='#fd7e14', fg='white',
                               font=('Arial', 9, 'bold'), command=self.buscar_por_telefono,
                               padx=10, pady=5)
        btn_telefono.pack(side=tk.LEFT, padx=(0, 5))

        btn_fecha = tk.Button(frame_busqueda_especializada, text='📅 POR FECHA', bg='#6f42c1', fg='white',
                            font=('Arial', 9, 'bold'), command=self.buscar_por_fecha,
                            padx=10, pady=5)
        btn_fecha.pack(side=tk.LEFT)

        # ✅ BOTONES DE ACCIÓN EN POSICIÓN MÁS VISIBLE (ARRIBA DE LA TABLA)
        frame_acciones_superiores = tk.Frame(frame_busqueda, bg='white', pady=8)
        frame_acciones_superiores.pack(fill=tk.X, pady=(8, 0))
        
        btn_whatsapp_superior = self.crear_boton_redondeado(frame_acciones_superiores, '📱 ENVIAR WHATSAPP', self.estilos['whatsapp'], self.enviar_whatsapp, width=18)
        btn_whatsapp_superior.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_eliminar_superior = self.crear_boton_redondeado(frame_acciones_superiores, '🗑️ ELIMINAR', self.estilos['peligro'], self.eliminar_turno, width=12)
        btn_eliminar_superior.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_editar_superior = self.crear_boton_redondeado(frame_acciones_superiores, '📝 EDITAR', self.estilos['info'], self.editar_turno, width=12)
        btn_editar_superior.pack(side=tk.LEFT)

        # ✅ LABEL DE ESTADO AL MISMO NIVEL QUE BOTONES (CORREGIDO)
        self.label_estado = tk.Label(frame_acciones_superiores, text='Mostrando todos los turnos', 
                           bg='white', font=('Arial', 9), fg=self.estilos['info'])
        self.label_estado.pack(side=tk.RIGHT, padx=(0, 10))

        # TABLA
        frame_tabla_content = tk.Frame(frame_tabla_card, bg='white')
        frame_tabla_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tabla = ttk.Treeview(frame_tabla_content, 
                                columns=('ID', 'Nombre', 'Tel', 'Estilista', 'Servicios', 'Manicura', 'ServManicura', 'Fecha', 'Hora'), 
                                show='headings', height=15)

        columnas = [
            ('ID', 40),
            ('Nombre', 150),
            ('Tel', 100),
            ('Estilista', 130),
            ('Servicios', 120),
            ('Manicura', 100),
            ('ServManicura', 120),
            ('Fecha', 80),
            ('Hora', 60)
        ]

        for col, width in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=width, anchor=tk.CENTER)

        v_scrollbar = ttk.Scrollbar(frame_tabla_content, orient=tk.VERTICAL, command=self.tabla.yview)
        h_scrollbar = ttk.Scrollbar(frame_tabla_content, orient=tk.HORIZONTAL, command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tabla.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        frame_tabla_content.grid_rowconfigure(0, weight=1)
        frame_tabla_content.grid_columnconfigure(0, weight=1)

        # ✅ MANTENER BOTONES INFERIORES TAMBIÉN (PARA MÚLTIPLES OPCIONES)
        frame_botones_accion = tk.Frame(frame_tabla_card, bg='white', pady=10)
        frame_botones_accion.pack(fill=tk.X)
        
        btn_whatsapp = self.crear_boton_redondeado(frame_botones_accion, '📱 ENVIAR WHATSAPP', self.estilos['whatsapp'], self.enviar_whatsapp, width=18)
        btn_whatsapp.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_eliminar = self.crear_boton_redondeado(frame_botones_accion, '🗑️ ELIMINAR', self.estilos['peligro'], self.eliminar_turno, width=12)
        btn_eliminar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_editar = self.crear_boton_redondeado(frame_botones_accion, '📝 EDITAR', self.estilos['info'], self.editar_turno, width=12)
        btn_editar.pack(side=tk.LEFT)

    def cargar_turnos(self):
        """Cargar todos los turnos - CORREGIDO: Usa la función formatear_turno_para_tabla"""
        try:
            for item in self.tabla.get_children(): 
                self.tabla.delete(item)
            
            self.cursor.execute('SELECT * FROM turnos ORDER BY fecha ASC, hora ASC')
            turnos = self.cursor.fetchall()

            if turnos:
                for turno in turnos:
                    turno_formateado = self.formatear_turno_para_tabla(turno)
                    
                    color_fondo = self.determinar_color_turno(turno[7], turno[8])  # fecha, hora
                    item = self.tabla.insert('', tk.END, values=turno_formateado)
                    self.tabla.item(item, tags=(color_fondo,))
                    self.tabla.tag_configure(color_fondo, background=color_fondo)
            else:
                self.tabla.insert('', tk.END, values=('', 'No hay turnos registrados', '', '', '', '', '', '', ''))

        except Exception as err:
            print(f"❌ Error al cargar turnos: {err}")
            messagebox.showerror('Error BD', f'No se pudieron cargar los turnos: {err}')

    def limpiar_formulario(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_servicios.delete(0, tk.END)
        self.entry_servicios_manicura.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)
        self.combo_estilista.set('')
        self.combo_manicura.set('')

    def eliminar_turno(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning('Error', 'Seleccione un turno para eliminar')
            return

        turno_id = self.tabla.item(seleccion[0])['values'][0]
        nombre = self.tabla.item(seleccion[0])['values'][1]

        if messagebox.askyesno('Confirmar', f'¿Eliminar turno de {nombre}?'):
            try:
                self.cursor.execute('DELETE FROM turnos WHERE id = ?', (turno_id,))
                self.conexion.commit()
                messagebox.showinfo('Éxito', 'Turno eliminado correctamente')
                self.cargar_turnos()
            except Exception as err:
                messagebox.showerror('Error BD', f'No se pudo eliminar: {err}')


def main():
    try:
        root = tk.Tk()
        app = AppTurnosPeluqueria(root)
        root.mainloop()
    except Exception as e:
        print(f'ERROR: {e}')
        traceback.print_exc()

if __name__ == '__main__':
    main()