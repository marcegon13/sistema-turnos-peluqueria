import random
from datetime import timedelta
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import sqlite3
import traceback
import sys
import pywhatkit
import time

class AppTurnosPeluqueria:
    def __init__(self, root):
        self.root = root
        self.configurar_interfaz()
        self.conectar_bd()
        self.cargar_profesionales()
        self.crear_componentes()
        self.cargar_turnos()
        self.agregar_menu_contextual()
        self.agregar_doble_click()
    
    def configurar_interfaz(self):
        self.root.title('NEW STATION - Sistema de Turnos + WhatsApp')
        self.root.geometry('1300x800')
        self.root.configure(bg='#f8f9fa')
        self.estilos = {
            'fondo': '#f8f9fa', 'primario': '#007bff', 'secundario': '#6c757d', 
            'exito': '#28a745', 'peligro': '#dc3545', 'advertencia': '#ffc107',
            'info': '#17a2b8', 'texto_oscuro': '#343a40', 'texto_claro': '#6c757d',
            'borde': '#dee2e6', 'card_bg': '#ffffff', 'whatsapp': '#25D366'
        }

    def get_db_path(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, 'turnos_newstation_pueyrredon.db')

    def conectar_bd(self):
        try:
            db_path = self.get_db_path()
            
            # ELIMINAR BASE DE DATOS EXISTENTE para empezar desde cero
            if os.path.exists(db_path):
                os.remove(db_path)
                print("🗑️ Base de datos anterior eliminada")
            
            self.conexion = sqlite3.connect(db_path)
            self.cursor = self.conexion.cursor()
            
            # CREAR TABLA CON ORDEN CORRECTO
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS turnos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT,
                    estilista TEXT,
                    servicio TEXT,
                    manicura TEXT,
                    servicios_manicura TEXT,
                    fecha TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    whatsapp_enviado BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conexion.commit()
            print('✅ Base de datos NUEVA creada con orden correcto')
            
            # CREAR 20 TURNOS DE PRUEBA SIN SERVICIOS
            self.crear_turnos_prueba()
            
        except Exception as e:
            print(f'Error BD: {e}')
            messagebox.showerror('Error', f'No se pudo conectar: {e}')

    def crear_turnos_prueba(self):
        """Crear 20 turnos de prueba SIN servicios"""
        nombres = [
            'Ana Garcia', 'Luis Martinez', 'Maria Rodriguez', 'Carlos Lopez', 'Laura Perez',
            'Diego Sanchez', 'Sofia Fernandez', 'Miguel Torres', 'Elena Ramirez', 'Pablo Diaz',
            'Carmen Ruiz', 'Javier Castro', 'Isabel Morales', 'Ricardo Ortiz', 'Patricia Silva',
            'Fernando Vargas', 'Lucia Herrera', 'Roberto Medina', 'Teresa Rios', 'Sergio Castro'
        ]
        
        try:
            for i in range(20):
                nombre = nombres[i]
                telefono = f'11{random.randint(3000, 9999)}{random.randint(1000, 9999)}'
                
                # SIN SERVICIOS - campos vacíos o "No aplica"
                estilista = 'No aplica'
                servicio = ''
                manicura = 'No aplica'
                servicios_manicura = ''
                
                # Fecha aleatoria en los próximos 30 días
                fecha_base = datetime.now() + timedelta(days=random.randint(1, 30))
                fecha = fecha_base.strftime('%Y-%m-%d')
                
                # Hora aleatoria entre 9:00 y 20:00
                hora = f"{random.randint(9, 19):02d}:{random.choice(['00', '30'])}"
                
                # INSERT con orden CORRECTO
                self.cursor.execute('''
                    INSERT INTO turnos (nombre, telefono, estilista, servicio, manicura, servicios_manicura, fecha, hora)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nombre, telefono, estilista, servicio, manicura, servicios_manicura, fecha, hora))
            
            self.conexion.commit()
            print('✅ 20 turnos de prueba creados (sin servicios)')
            
        except Exception as err:
            print(f'Error creando turnos prueba: {err}')

    def cargar_profesionales(self):
        self.estilistas = [
            'Alejandro Cosentini', 'Guillermo Mirabile', 'Paola Rodriguez', 
            'Miguel Riviera', 'Fabian Gomez', 'Rodrigo Carbonero', 
            'Veronica Parra', 'Walter Tejada', 'Jorgelina Silvero', 'No aplica'
        ]
        self.manicuras = ['Liliana Pavon', 'Noelia Leguizamon', 'No aplica']

    def agregar_doble_click(self):
        self.tabla.bind("<Double-1>", self.mostrar_detalles_completos)

    def mostrar_detalles_completos(self, event):
        item = self.tabla.identify_row(event.y)
        if item:
            self.tabla.selection_set(item)
            valores = self.tabla.item(item, 'values')
            ventana_detalles = DetallesTurnoWindow(self, valores)

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
            messagebox.showwarning('Editar', 'Seleccione un turno para editar (click derecho)')
            return
        
        item = seleccion[0]
        valores = self.tabla.item(item, 'values')
        ventana_edicion = EditarTurnoWindow(self, valores)

    def enviar_whatsapp(self):
        """ENVÍA MENSAJE DE WHATSAPP - FUNCIÓN PRINCIPAL"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning('WhatsApp', 'Seleccione un turno para enviar WhatsApp')
            return
        
        item = seleccion[0]
        valores = self.tabla.item(item, 'values')
        
        # Extraer datos del turno
        turno_id = valores[0]
        nombre = valores[1]
        telefono = valores[2]
        estilista = valores[3]
        servicios = valores[4] or "No especificado"
        manicura = valores[5]
        servicios_manicura = valores[6] or "No especificado"
        fecha = valores[7]
        hora = valores[8]
        
        # Validar que tenga teléfono
        if not telefono or len(telefono) < 8:
            messagebox.showerror('Error', 'El turno no tiene un número de teléfono válido')
            return
        
        # Formatear teléfono (eliminar espacios y agregar código de país)
        telefono_limpio = telefono.replace(" ", "").replace("-", "")
        if not telefono_limpio.startswith("+"):
            telefono_limpio = "+54" + telefono_limpio  # Código Argentina
        
        # Crear mensaje personalizado
        mensaje = f"""¡Hola {nombre}! ✨

Confirmamos tu turno en *NEW STATION - Pueyrredon*:

📅 *Fecha:* {fecha}
🕒 *Hora:* {hora}
💇 *Estilista:* {estilista}
💅 *Manicura:* {manicura}

*Servicios:* {servicios}
*Servicios de manicura:* {servicios_manicura}

📍 *Dirección:* [Tu dirección aquí]
📞 *Teléfono:* [Tu teléfono aquí]

¡Te esperamos! 🎉"""
        
        try:
            # Mostrar confirmación
            confirmar = messagebox.askyesno(
                'Enviar WhatsApp', 
                f'¿Enviar confirmación a {nombre}?\n\nTeléfono: {telefono}\n\nEl sistema abrirá WhatsApp Web.'
            )
            
            if confirmar:
                # ENVIAR WHATSAPP
                self.enviar_mensaje_whatsapp(telefono_limpio, mensaje)
                
                # Marcar como enviado en la base de datos
                self.cursor.execute('UPDATE turnos SET whatsapp_enviado = 1 WHERE id = ?', (turno_id,))
                self.conexion.commit()
                
                messagebox.showinfo('Éxito', f'✅ WhatsApp enviado a {nombre}\n\nAhora puedes enviar el mensaje manualmente desde WhatsApp Web.')
                
        except Exception as e:
            messagebox.showerror('Error WhatsApp', f'No se pudo enviar el WhatsApp:\n{str(e)}')

    def enviar_mensaje_whatsapp(self, telefono, mensaje):
        """Función principal para enviar WhatsApp"""
        try:
            # pywhatkit necesita el teléfono con código de país pero sin +
            telefono_sin_plus = telefono.replace("+", "")
            
            print(f"📱 Enviando WhatsApp a: {telefono}")
            print(f"💬 Mensaje: {mensaje}")
            
            # Enviar mensaje inmediatamente
            pywhatkit.sendwhatmsg_instantly(
                phone_no=telefono_sin_plus,
                message=mensaje,
                wait_time=15,
                tab_close=True
            )
            
            print("✅ Mensaje enviado exitosamente")
            
        except Exception as e:
            print(f"❌ Error enviando WhatsApp: {e}")
            raise e

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

    def buscar_turnos(self):
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
                ORDER BY fecha ASC, hora ASC
            ''', (f'%{texto_busqueda}%', f'%{texto_busqueda}%', f'%{texto_busqueda}%',
                  f'%{texto_busqueda}%', f'%{texto_busqueda}%', f'%{texto_busqueda}%'))

            turnos = self.cursor.fetchall()
            
            if turnos:
                for turno in turnos:
                    fecha_sql = turno[7]  # Fecha en posición 7
                    try:
                        fecha_obj = datetime.strptime(fecha_sql, '%Y-%m-%d')
                        fecha_mostrar = fecha_obj.strftime('%d/%m/%Y')
                    except: 
                        fecha_mostrar = fecha_sql

                    # ORDEN CORRECTO para mostrar en tabla
                    turno_formateado = (
                        turno[0],  # ID
                        turno[1],  # Nombre
                        turno[2],  # Teléfono
                        turno[3],  # Estilista
                        turno[4],  # Servicios
                        turno[5],  # Manicura
                        turno[6],  # Servicios Manicura (TEXTO LIBRE)
                        fecha_mostrar,  # Fecha formateada
                        turno[8]   # Hora
                    )
                    self.tabla.insert('', tk.END, values=turno_formateado)

                self.label_estado.config(text=f'{len(turnos)} turnos encontrados', fg=self.estilos['exito'])
            else:
                self.tabla.insert('', tk.END, values=('', 'No se encontraron turnos', '', '', '', '', '', '', ''))
                self.label_estado.config(text='No se encontraron turnos', fg=self.estilos['peligro'])

        except Exception as err:
            messagebox.showerror('Error BD', f'No se pudieron buscar los turnos: {err}')

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
        tk.Label(title_frame, text='SISTEMA DE GESTION DE TURNOS + WHATSAPP', font=('Arial', 16, 'bold'), bg='white', fg=self.estilos['texto_oscuro']).pack()

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

        # Campos del formulario con ORDEN CORREGIDO
        campos = [
            ('Nombre Cliente*:', 'entry_nombre'),
            ('Telefono*:', 'entry_telefono'), 
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

        # TABLA DERECHA
        frame_tabla_container = tk.Frame(frame_main, bg=self.estilos['fondo'])
        frame_tabla_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        frame_tabla_card = tk.Frame(frame_tabla_container, bg='white', relief='solid', bd=1)
        frame_tabla_card.pack(fill=tk.BOTH, expand=True)
        
        frame_tabla_header = tk.Frame(frame_tabla_card, bg=self.estilos['primario'])
        frame_tabla_header.pack(fill=tk.X)
        tk.Label(frame_tabla_header, text='TURNOS REGISTRADOS', font=('Arial', 14, 'bold'), 
                bg=self.estilos['primario'], fg='white', padx=20, pady=15).pack()

        # BARRA DE BUSQUEDA
        frame_busqueda = tk.Frame(frame_tabla_card, bg='white', padx=15, pady=5)
        frame_busqueda.pack(fill=tk.X)

        tk.Label(frame_busqueda, text='Buscar:', bg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        self.entry_busqueda = tk.Entry(frame_busqueda, font=('Arial', 10), relief='solid', bd=1, bg='white', width=25)
        self.entry_busqueda.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_busqueda.bind('<Return>', lambda e: self.buscar_turnos())

        btn_buscar = tk.Button(frame_busqueda, text='BUSCAR', bg=self.estilos['info'], fg='white',
                             font=('Arial', 9, 'bold'), command=self.buscar_turnos)
        btn_buscar.pack(side=tk.LEFT, padx=(0, 5))
        btn_todos = tk.Button(frame_busqueda, text='MOSTRAR TODOS', bg=self.estilos['secundario'], fg='white',
                            font=('Arial', 9, 'bold'), command=self.mostrar_todos)
        btn_todos.pack(side=tk.LEFT)

        self.label_estado = tk.Label(frame_busqueda, text='Mostrando todos los turnos', 
                                   bg='white', font=('Arial', 9), fg=self.estilos['info'])
        self.label_estado.pack(side=tk.RIGHT)

        # TABLA CON ORDEN CORREGIDO
        frame_tabla_content = tk.Frame(frame_tabla_card, bg='white')
        frame_tabla_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tabla = ttk.Treeview(frame_tabla_content, 
                                columns=('ID', 'Nombre', 'Tel', 'Estilista', 'Servicios', 'Manicura', 'ServManicura', 'Fecha', 'Hora'), 
                                show='headings', height=15)

        # COLUMNAS CON ORDEN CORREGIDO
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

        # BOTONES DE ACCIÓN
        frame_botones_accion = tk.Frame(frame_tabla_card, bg='white', pady=15)
        frame_botones_accion.pack(fill=tk.X)
        
        btn_whatsapp = self.crear_boton_redondeado(frame_botones_accion, '📱 ENVIAR WHATSAPP', self.estilos['whatsapp'], self.enviar_whatsapp, width=18)
        btn_whatsapp.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_eliminar = self.crear_boton_redondeado(frame_botones_accion, 'ELIMINAR', self.estilos['peligro'], self.eliminar_turno, width=12)
        btn_eliminar.pack(side=tk.LEFT)

    def limpiar_formulario(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_servicios.delete(0, tk.END)
        self.entry_servicios_manicura.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)
        self.combo_estilista.set('')
        self.combo_manicura.set('')

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

        try:
            # INSERT con orden CORRECTO
            self.cursor.execute('''
                INSERT INTO turnos (nombre, telefono, estilista, servicio, manicura, servicios_manicura, fecha, hora)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, telefono, estilista, servicios, manicura, servicios_manicura, fecha, hora))

            self.conexion.commit()
            messagebox.showinfo('Éxito', 'Turno agregado correctamente')
            self.limpiar_formulario()
            self.cargar_turnos()
        except Exception as err:
            messagebox.showerror('Error BD', f'No se pudo agregar: {err}')
    
    def cargar_turnos(self):
        try:
            for item in self.tabla.get_children(): 
                self.tabla.delete(item)
            
            self.cursor.execute('SELECT * FROM turnos ORDER BY fecha ASC, hora ASC')
            turnos = self.cursor.fetchall()

            if turnos:
                for turno in turnos:
                    fecha_sql = turno[7]  # Fecha en posición 7
                    try:
                        fecha_obj = datetime.strptime(fecha_sql, '%Y-%m-%d')
                        fecha_mostrar = fecha_obj.strftime('%d/%m/%Y')
                    except: 
                        fecha_mostrar = fecha_sql

                    # ORDEN CORRECTO para mostrar en tabla
                    turno_formateado = (
                        turno[0],  # ID
                        turno[1],  # Nombre
                        turno[2],  # Teléfono
                        turno[3],  # Estilista
                        turno[4],  # Servicios
                        turno[5],  # Manicura
                        turno[6],  # Servicios Manicura (TEXTO LIBRE)
                        fecha_mostrar,  # Fecha formateada
                        turno[8]   # Hora
                    )
                    self.tabla.insert('', tk.END, values=turno_formateado)
            else:
                self.tabla.insert('', tk.END, values=('', 'No hay turnos registrados', '', '', '', '', '', '', ''))

        except Exception as err:
            messagebox.showerror('Error BD', f'No se pudieron cargar los turnos: {err}')
    
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


# Las clases DetallesTurnoWindow y EditarTurnoWindow se mantienen igual que antes
# (omitiendo por brevedad, pero están completas en el código anterior)

class DetallesTurnoWindow:
    def __init__(self, parent, valores_turno):
        self.parent = parent
        self.valores_turno = valores_turno
        
        self.ventana = tk.Toplevel(parent.root)
        self.ventana.title(f'Detalles Turno - {valores_turno[1]}')
        self.ventana.geometry('450x500')
        self.ventana.configure(bg=parent.estilos['fondo'])
        self.ventana.resizable(False, False)
        self.ventana.transient(parent.root)
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        frame_header = tk.Frame(self.ventana, bg=self.parent.estilos['primario'])
        frame_header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame_header, text='DETALLES COMPLETOS DEL TURNO', 
                font=('Arial', 14, 'bold'), bg=self.parent.estilos['primario'], 
                fg='white', padx=20, pady=12).pack()
        
        frame_content = tk.Frame(self.ventana, bg=self.parent.estilos['fondo'], 
                               padx=25, pady=20)
        frame_content.pack(fill=tk.BOTH, expand=True)
        
        # ORDEN CORREGIDO: ID, Nombre, Tel, Estilista, Servicios, Manicura, ServManicura, Fecha, Hora
        datos = [
            ('ID:', self.valores_turno[0]),
            ('👤 CLIENTE:', self.valores_turno[1]),
            ('📞 TELÉFONO:', self.valores_turno[2]),
            ('👨‍💼 ESTILISTA:', self.valores_turno[3]),
            ('💇 SERVICIOS:', self.valores_turno[4]),
            ('💅 MANICURA:', self.valores_turno[5]),
            ('🎨 SERV. MANICURA:', self.valores_turno[6]),
            ('📅 FECHA:', self.valores_turno[7]),
            ('🕒 HORA:', self.valores_turno[8])
        ]
        
        for etiqueta, valor in datos:
            self.crear_fila_dato(frame_content, etiqueta, valor)
        
        frame_botones = tk.Frame(frame_content, bg=self.parent.estilos['fondo'], pady=15)
        frame_botones.pack(fill=tk.X)
        
        btn_cerrar = tk.Button(frame_botones, text='✅ CERRAR', 
                               bg=self.parent.estilos['exito'], fg='white', 
                               font=('Arial', 11, 'bold'), relief='flat', bd=0,
                               padx=30, pady=8, command=self.ventana.destroy)
        btn_cerrar.pack()
    
    def crear_fila_dato(self, parent, etiqueta, valor):
        frame_fila = tk.Frame(parent, bg=self.parent.estilos['fondo'])
        frame_fila.pack(fill=tk.X, pady=6)
        
        tk.Label(frame_fila, text=etiqueta, bg=self.parent.estilos['fondo'],
                font=('Arial', 10, 'bold'), fg=self.parent.estilos['texto_oscuro'],
                width=16, anchor='w').pack(side=tk.LEFT)
        
        valor_texto = valor or 'No especificado'
        label_valor = tk.Label(frame_fila, text=valor_texto, bg=self.parent.estilos['card_bg'],
                              font=('Arial', 10), fg=self.parent.estilos['texto_oscuro'],
                              relief='solid', bd=1, padx=8, pady=4, width=25, anchor='w',
                              wraplength=250)
        label_valor.pack(side=tk.LEFT, fill=tk.X, expand=True)


class EditarTurnoWindow:
    def __init__(self, parent, valores_turno):
        self.parent = parent
        self.valores_turno = valores_turno
        self.turno_id = valores_turno[0]
        
        self.ventana = tk.Toplevel(parent.root)
        self.ventana.title(f'Editar Turno - {valores_turno[1]}')
        self.ventana.geometry('450x650')
        self.ventana.configure(bg=parent.estilos['fondo'])
        self.ventana.transient(parent.root)
        self.ventana.grab_set()
        self.ventana.resizable(False, False)
        
        self.crear_interfaz()
        self.cargar_datos_actuales()
    
    def crear_interfaz(self):
        frame_header = tk.Frame(self.ventana, bg=self.parent.estilos['primario'])
        frame_header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame_header, text='EDITAR TURNO', font=('Arial', 16, 'bold'), 
                bg=self.parent.estilos['primario'], fg='white', padx=20, pady=12).pack()
        
        frame_content = tk.Frame(self.ventana, bg=self.parent.estilos['fondo'], padx=25, pady=20)
        frame_content.pack(fill=tk.BOTH, expand=True)
        
        campos = [
            ('Nombre Cliente*:', 'entry_nombre'),
            ('Telefono*:', 'entry_telefono'), 
            ('Estilista*:', 'combo_estilista'),
            ('Servicios:', 'entry_servicios'),
            ('Manicura*:', 'combo_manicura'),
            ('Servicios Manicura:', 'entry_servicios_manicura'),
            ('Hora*:', 'entry_hora'),
            ('Fecha*:', 'entry_fecha')
        ]

        self.controles = {}
        
        for i, (label, attr) in enumerate(campos):
            frame_campo = tk.Frame(frame_content, bg=self.parent.estilos['fondo'])
            frame_campo.pack(fill=tk.X, pady=8)

            tk.Label(frame_campo, text=label, bg=self.parent.estilos['fondo'], 
                    font=('Arial', 10, 'bold'), fg=self.parent.estilos['texto_oscuro'], 
                    width=18, anchor='w').pack(side=tk.LEFT, padx=(0, 10))

            if attr == 'entry_nombre':
                self.controles['nombre'] = tk.Entry(frame_campo, font=('Arial', 10), 
                                                   relief='solid', bd=1, bg='white', width=25)
                self.controles['nombre'].pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_telefono':
                self.controles['telefono'] = tk.Entry(frame_campo, font=('Arial', 10), 
                                                     relief='solid', bd=1, bg='white', width=25)
                self.controles['telefono'].pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'combo_estilista':
                self.controles['estilista'] = ttk.Combobox(frame_campo, font=('Arial', 10), 
                                                          values=self.parent.estilistas, 
                                                          state='readonly', width=23)
                self.controles['estilista'].pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_servicios':
                self.controles['servicios'] = tk.Entry(frame_campo, font=('Arial', 10), 
                                                      relief='solid', bd=1, bg='white', width=25)
                self.controles['servicios'].pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'combo_manicura':
                self.controles['manicura'] = ttk.Combobox(frame_campo, font=('Arial', 10), 
                                                         values=self.parent.manicuras, 
                                                         state='readonly', width=23)
                self.controles['manicura'].pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_servicios_manicura':
                self.controles['servicios_manicura'] = tk.Entry(frame_campo, font=('Arial', 10), 
                                                               relief='solid', bd=1, bg='white', width=25)
                self.controles['servicios_manicura'].pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_hora':
                frame_hora = tk.Frame(frame_campo, bg=self.parent.estilos['fondo'])
                frame_hora.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.controles['hora'] = tk.Entry(frame_hora, font=('Arial', 10), 
                                                 relief='solid', bd=1, bg='white', width=20)
                self.controles['hora'].pack(side=tk.LEFT, fill=tk.X, expand=True)
                btn_selector = tk.Button(frame_hora, text='🕒', font=('Arial', 9), 
                                       bg=self.parent.estilos['info'], fg='white',
                                       relief='flat', bd=0, width=3, 
                                       command=self.selector_hora)
                btn_selector.pack(side=tk.RIGHT, padx=(5, 0))
            elif attr == 'entry_fecha':
                frame_fecha = tk.Frame(frame_campo, bg=self.parent.estilos['fondo'])
                frame_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.controles['fecha'] = tk.Entry(frame_fecha, font=('Arial', 10), 
                                                  relief='solid', bd=1, bg='white', width=20)
                self.controles['fecha'].pack(side=tk.LEFT, fill=tk.X, expand=True)
                btn_calendario = tk.Button(frame_fecha, text='📅', font=('Arial', 9), 
                                         bg=self.parent.estilos['primario'], fg='white',
                                         relief='flat', bd=0, width=3, 
                                         command=self.selector_fecha)
                btn_calendario.pack(side=tk.RIGHT, padx=(5, 0))
        
        frame_ayuda = tk.Frame(frame_content, bg=self.parent.estilos['fondo'], pady=10)
        frame_ayuda.pack(fill=tk.X)
        tk.Label(frame_ayuda, text='* Campos obligatorios', 
                font=('Arial', 9, 'italic'), bg=self.parent.estilos['fondo'], 
                fg=self.parent.estilos['peligro']).pack()
        
        frame_botones = tk.Frame(frame_content, bg=self.parent.estilos['fondo'], pady=20)
        frame_botones.pack(fill=tk.X)
        
        btn_guardar = tk.Button(frame_botones, text='💾 GUARDAR CAMBIOS', 
                               bg=self.parent.estilos['exito'], fg='white',
                               font=('Arial', 11, 'bold'), relief='flat', bd=0,
                               padx=25, pady=12, command=self.guardar_cambios)
        btn_guardar.pack(side=tk.LEFT, padx=(0, 15))
        
        btn_cancelar = tk.Button(frame_botones, text='❌ CANCELAR', 
                               bg=self.parent.estilos['peligro'], fg='white',
                               font=('Arial', 11, 'bold'), relief='flat', bd=0,
                               padx=25, pady=12, command=self.ventana.destroy)
        btn_cancelar.pack(side=tk.LEFT)
    
    def cargar_datos_actuales(self):
        try:
            for control in self.controles.values():
                if isinstance(control, tk.Entry):
                    control.delete(0, tk.END)
                elif isinstance(control, ttk.Combobox):
                    control.set('')
            
            self.controles['nombre'].insert(0, self.valores_turno[1] or '')
            self.controles['telefono'].insert(0, self.valores_turno[2] or '')
            self.controles['estilista'].set(self.valores_turno[3] or '')
            self.controles['servicios'].insert(0, self.valores_turno[4] or '')
            self.controles['manicura'].set(self.valores_turno[5] or '')
            self.controles['servicios_manicura'].insert(0, self.valores_turno[6] or '')
            
            fecha_original = self.valores_turno[7] or ''
            self.controles['fecha'].insert(0, fecha_original)
            
            hora_original = self.valores_turno[8] or ''
            self.controles['hora'].insert(0, hora_original)
                
        except Exception as e:
            messagebox.showerror('Error', f'Error al cargar datos: {e}')
    
    def selector_hora(self):
        original_entry = self.parent.entry_hora
        self.parent.entry_hora = self.controles['hora']
        self.parent.selector_hora()
        self.parent.entry_hora = original_entry
    
    def selector_fecha(self):
        original_entry = self.parent.entry_fecha
        self.parent.entry_fecha = self.controles['fecha']
        self.parent.selector_fecha()
        self.parent.entry_fecha = original_entry
    
    def guardar_cambios(self):
        try:
            nombre = self.controles['nombre'].get().strip()
            telefono = self.controles['telefono'].get().strip()
            servicios = self.controles['servicios'].get().strip()
            estilista = self.controles['estilista'].get().strip()
            manicura = self.controles['manicura'].get().strip()
            servicios_manicura = self.controles['servicios_manicura'].get().strip()
            hora = self.controles['hora'].get().strip()

            fecha_str = self.controles['fecha'].get().strip()
            try:
                fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
                fecha = fecha_obj.strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showwarning('Error', 'Formato de fecha inválido. Use DD/MM/AAAA')
                return

            if not all([nombre, telefono, estilista, manicura, hora]):
                messagebox.showwarning('Error', 'Complete los campos obligatorios: Nombre, Teléfono, Estilista, Manicura y Hora')
                return

            try:
                datetime.strptime(hora, '%H:%M')
            except ValueError:
                messagebox.showwarning('Error', 'Formato de hora inválido. Use HH:MM (ej: 14:30)')
                return

            if messagebox.askyesno('Confirmar', f'¿Actualizar turno de {nombre}?'):
                self.parent.cursor.execute('''
                    UPDATE turnos 
                    SET nombre=?, telefono=?, estilista=?, servicio=?, manicura=?, 
                        servicios_manicura=?, fecha=?, hora=?
                    WHERE id=?
                ''', (nombre, telefono, estilista, servicios, manicura, 
                      servicios_manicura, fecha, hora, self.turno_id))

                self.parent.conexion.commit()
                messagebox.showinfo('Éxito', 'Turno actualizado correctamente')
                self.parent.cargar_turnos()
                self.ventana.destroy()
            
        except Exception as err:
            messagebox.showerror('Error BD', f'No se pudo actualizar: {err}')


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