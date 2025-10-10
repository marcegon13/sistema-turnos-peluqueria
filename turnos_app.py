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
        if not self.verificar_licencia():
            self.root.destroy()
            return
        self.configurar_interfaz()
        self.conectar_bd()
        self.cargar_profesionales()
        self.crear_componentes()
        self.cargar_turnos()
    
    def verificar_licencia(self):
        nombre_maquina = socket.gethostname()
        if nombre_maquina != 'NewStation2':
            messagebox.showerror('Error de Licencia', 'ESTA APLICACION ESTA VINCULADA A OTRA PELUQUERIA\n\nSolo puede utilizarse en:\n- NewStation2\n\nContacte al proveedor.')
            return False
        print(f'Licencia valida - Maquina: {nombre_maquina}')
        return True

    def configurar_interfaz(self):
        self.root.title('NEW STATION - Sistema de Turnos')
        self.root.geometry('1300x800')
        self.root.configure(bg='#f8f9fa')
        self.estilos = {
            'fondo': '#f8f9fa', 'primario': '#007bff', 'secundario': '#6c757d', 
            'exito': '#28a745', 'peligro': '#dc3545', 'advertencia': '#ffc107',
            'info': '#17a2b8', 'texto_oscuro': '#343a40', 'texto_claro': '#6c757d',
            'borde': '#dee2e6', 'card_bg': '#ffffff'
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
            self.conexion = sqlite3.connect(db_path)
            self.cursor = self.conexion.cursor()
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
            self.conexion.commit()
            print('Base de datos conectada')
        except Exception as e:
            print(f'Error BD: {e}')
            messagebox.showerror('Error', f'No se pudo conectar: {e}')

    def cargar_profesionales(self):
        self.estilistas = ['Alejandro Cosentini', 'Guillermo Mirabile', 'Paola Rodriguez', 
                          'Miguel Riviera', 'Fabian Gomez', 'Rodrigo Carbonero', 'Veronica Parra', 'No aplica']
        self.manicuras = ['Liliana Pavon', 'Noelia Leguizamon', 'No aplica']

    def crear_boton_redondeado(self, parent, text, color, command=None):
        return tk.Button(parent, text=text, bg=color, fg='white', font=('Arial', 10, 'bold'),
                        relief='flat', bd=0, padx=20, pady=10, command=command)
    
    def selector_hora(self):
        ventana_hora = tk.Toplevel(self.root)
        ventana_hora.title('Seleccionar Hora')
        ventana_hora.geometry('300x400')
        ventana_hora.configure(bg=self.estilos['fondo'])
        ventana_hora.transient(self.root)
        ventana_hora.grab_set()

        frame_principal = tk.Frame(ventana_hora, bg=self.estilos['fondo'], padx=20, pady=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame_principal, text='Seleccione la hora', font=('Arial', 14, 'bold'), 
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
        """Selector de fecha con año y mes como en la imagen"""
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
        dias_semana = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
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
        texto_busqueda = self.entry_busqueda.get().strip().lower()
        if not texto_busqueda:
            messagebox.showwarning('Busqueda', 'Ingrese un termino para buscar')
            return
        
        try:
            for item in self.tabla.get_children(): self.tabla.delete(item)
            self.cursor.execute('''
                SELECT * FROM turnos WHERE LOWER(nombre) LIKE ? OR LOWER(telefono) LIKE ? OR LOWER(servicio) LIKE ?
                ORDER BY fecha ASC, hora ASC
            ''', (f'%{texto_busqueda}%', f'%{texto_busqueda}%', f'%{texto_busqueda}%'))

            turnos = self.cursor.fetchall()
            if turnos:
                for turno in turnos:
                    fecha_sql = turno[6]
                    try:
                        fecha_obj = datetime.strptime(fecha_sql, '%Y-%m-%d')
                        fecha_mostrar = fecha_obj.strftime('%d/%m/%Y')
                    except: fecha_mostrar = fecha_sql

                    turno_formateado = (turno[0], turno[1], turno[2], turno[3], turno[4], turno[5], fecha_mostrar, turno[7])
                    self.tabla.insert('', tk.END, values=turno_formateado)

                self.label_estado.config(text=f'{len(turnos)} turnos encontrados', fg=self.estilos['exito'])
            else:
                self.tabla.insert('', tk.END, values=('', 'No se encontraron turnos', '', '', '', '', '', ''))
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
        tk.Label(title_frame, text='SISTEMA DE GESTION DE TURNOS', font=('Arial', 16, 'bold'), bg='white', fg=self.estilos['texto_oscuro']).pack()

        # CONTENIDO PRINCIPAL
        frame_main = tk.Frame(self.root, bg=self.estilos['fondo'])
        frame_main.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # FORMULARIO IZQUIERDA
        frame_form_container = tk.Frame(frame_main, bg=self.estilos['fondo'])
        frame_form_container.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 20))
        
        frame_form_card = tk.Frame(frame_form_container, bg='white', relief='solid', bd=1)
        frame_form_card.pack(fill=tk.BOTH, expand=True)

        frame_card_header = tk.Frame(frame_form_card, bg=self.estilos['primario'])
        frame_card_header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(frame_card_header, text='NUEVO TURNO', font=('Arial', 14, 'bold'), bg=self.estilos['primario'], fg='white', padx=20, pady=15).pack()

        frame_form_content = tk.Frame(frame_form_card, bg='white', padx=25, pady=20)
        frame_form_content.pack(fill=tk.BOTH, expand=True)

        # Campos del formulario
        campos = [
            ('Nombre Cliente:', 'entry_nombre'),
            ('Telefono:', 'entry_telefono'), 
            ('Servicio:', 'combo_servicio'),
            ('Estilista:', 'combo_estilista'),
            ('Manicura:', 'combo_manicura'),
            ('Hora:', 'entry_hora'),
            ('Fecha:', 'entry_fecha')
        ]

        for i, (label, attr) in enumerate(campos):
            frame_campo = tk.Frame(frame_form_content, bg='white')
            frame_campo.pack(fill=tk.X, pady=12)

            tk.Label(frame_campo, text=label, bg='white', font=('Arial', 10, 'bold'), 
                    fg=self.estilos['texto_oscuro'], width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 15))

            if attr == 'entry_nombre':
                self.entry_nombre = tk.Entry(frame_campo, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_nombre.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_telefono':
                self.entry_telefono = tk.Entry(frame_campo, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_telefono.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'combo_servicio':
                self.combo_servicio = ttk.Combobox(frame_campo, font=('Arial', 10), values=[
                    'Corte de Cabello', 'Coloracion', 'Peinado', 'Tratamiento Capilar', 'Lavado', 'Alisado',
                    'Manicura Basica', 'Manicura Spa', 'Esmaltado Semi', 'Pedicura', 'Unas Esculpidas'], state='readonly')
                self.combo_servicio.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'combo_estilista':
                self.combo_estilista = ttk.Combobox(frame_campo, font=('Arial', 10), values=self.estilistas, state='readonly')
                self.combo_estilista.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'combo_manicura':
                self.combo_manicura = ttk.Combobox(frame_campo, font=('Arial', 10), values=self.manicuras, state='readonly')
                self.combo_manicura.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif attr == 'entry_hora':
                frame_hora = tk.Frame(frame_campo, bg='white')
                frame_hora.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entry_hora = tk.Entry(frame_hora, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_hora.pack(side=tk.LEFT, fill=tk.X, expand=True)
                btn_selector = tk.Button(frame_hora, text='H', font=('Arial', 10), bg=self.estilos['info'], fg='white',
                                       relief='flat', bd=0, command=self.selector_hora)
                btn_selector.pack(side=tk.RIGHT, padx=(5, 0))
            elif attr == 'entry_fecha':
                frame_fecha = tk.Frame(frame_campo, bg='white')
                frame_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entry_fecha = tk.Entry(frame_fecha, font=('Arial', 10), relief='solid', bd=1, bg='white')
                self.entry_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entry_fecha.insert(0, datetime.now().strftime('%d/%m/%Y'))
                btn_calendario = tk.Button(frame_fecha, text='C', font=('Arial', 10), bg=self.estilos['primario'], fg='white',
                                         relief='flat', bd=0, command=self.selector_fecha)
                btn_calendario.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Botones del formulario
        frame_botones = tk.Frame(frame_form_content, bg='white')
        frame_botones.pack(fill=tk.X, pady=25)

        btn_agregar = self.crear_boton_redondeado(frame_botones, 'AGREGAR TURNO', self.estilos['exito'], self.agregar_turno)
        btn_agregar.pack(side=tk.LEFT, padx=(0, 10))
        btn_limpiar = self.crear_boton_redondeado(frame_botones, 'LIMPIAR', self.estilos['advertencia'], self.limpiar_formulario)
        btn_limpiar.pack(side=tk.LEFT, padx=(0, 10))
        btn_actualizar = self.crear_boton_redondeado(frame_botones, 'ACTUALIZAR TABLA', self.estilos['info'], self.cargar_turnos)
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
        self.entry_busqueda = tk.Entry(frame_busqueda, font=('Arial', 10), relief='solid', bd=1, bg='white', width=30)
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

        frame_tabla_content = tk.Frame(frame_tabla_card, bg='white')
        frame_tabla_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tabla = ttk.Treeview(frame_tabla_content, 
                                columns=('ID', 'Nombre', 'Telefono', 'Servicio', 'Estilista', 'Manicura', 'Fecha', 'Hora'), 
                                show='headings', height=15)

        columnas = [('ID', 40), ('Nombre', 100), ('Telefono', 90), ('Servicio', 120), 
                   ('Estilista', 90), ('Manicura', 90), ('Fecha', 80), ('Hora', 60)]

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

        frame_footer = tk.Frame(frame_tabla_card, bg='white', pady=15)
        frame_footer.pack(fill=tk.X)
        btn_eliminar = self.crear_boton_redondeado(frame_footer, 'ELIMINAR TURNO', self.estilos['peligro'], self.eliminar_turno)
        btn_eliminar.pack()

    def limpiar_formulario(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)
        self.combo_servicio.set('')
        self.combo_estilista.set('')
        self.combo_manicura.set('')

    def agregar_turno(self):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        servicio = self.combo_servicio.get().strip()
        estilista = self.combo_estilista.get().strip()
        manicura = self.combo_manicura.get().strip()

        fecha_str = self.entry_fecha.get()
        try:
            fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
            fecha = fecha_obj.strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning('Error', 'Formato de fecha invalido. Use DD/MM/AAAA')
            return

        hora = self.entry_hora.get().strip()

        if not all([nombre, servicio, hora]):
            messagebox.showwarning('Error', 'Complete los campos obligatorios: Nombre, Servicio y Hora')
            return

        try:
            self.cursor.execute('''
                INSERT INTO turnos (nombre, telefono, servicio, estilista, manicura, fecha, hora)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, telefono, servicio, estilista, manicura, fecha, hora))

            self.conexion.commit()
            messagebox.showinfo('Exito', 'Turno agregado correctamente')
            self.limpiar_formulario()
            self.cargar_turnos()
        except Exception as err:
            messagebox.showerror('Error BD', f'No se pudo agregar: {err}')
    
    def cargar_turnos(self):
        try:
            for item in self.tabla.get_children(): self.tabla.delete(item)
            self.cursor.execute('SELECT * FROM turnos ORDER BY fecha ASC, hora ASC')
            turnos = self.cursor.fetchall()

            if turnos:
                for turno in turnos:
                    fecha_sql = turno[6]
                    try:
                        fecha_obj = datetime.strptime(fecha_sql, '%Y-%m-%d')
                        fecha_mostrar = fecha_obj.strftime('%d/%m/%Y')
                    except: fecha_mostrar = fecha_sql

                    turno_formateado = (turno[0], turno[1], turno[2], turno[3], turno[4], turno[5], fecha_mostrar, turno[7])
                    self.tabla.insert('', tk.END, values=turno_formateado)
            else:
                self.tabla.insert('', tk.END, values=('', 'No hay turnos registrados', '', '', '', '', '', ''))

        except Exception as err:
            messagebox.showerror('Error BD', f'No se pudieron cargar los turnos: {err}')
    
    def eliminar_turno(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning('Error', 'Seleccione un turno para eliminar')
            return

        turno_id = self.tabla.item(seleccion[0])['values'][0]
        nombre = self.tabla.item(seleccion[0])['values'][1]

        if messagebox.askyesno('Confirmar', f'Eliminar turno de {nombre}?'):
            try:
                self.cursor.execute('DELETE FROM turnos WHERE id = ?', (turno_id,))
                self.conexion.commit()
                messagebox.showinfo('Exito', 'Turno eliminado correctamente')
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