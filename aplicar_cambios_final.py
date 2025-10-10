import re

def leer_archivo():
    with open('turnos_app.py', 'r', encoding='utf-8') as f:
        return f.read()

def guardar_archivo(content):
    with open('turnos_app.py', 'w', encoding='utf-8') as f:
        f.write(content)

# Leer archivo
content = leer_archivo()

# PATRÓN 1: Encontrar y reemplazar agregar_turno
# Buscar desde def agregar_turno hasta def cargar_turnos
patron_agregar = r'(def agregar_turno\(self\):.*?)(?=def cargar_turnos\(self\):)'

nuevo_agregar_turno = '''def agregar_turno(self):
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
            messagebox.showwarning("Error", "Formato de fecha invalido. Use DD/MM/AAAA")
            return
        
        hora = self.entry_hora.get().strip()
        
        if not all([nombre, servicio, hora]):
            messagebox.showwarning("Error", "Complete los campos obligatorios: Nombre, Servicio y Hora")
            return
        
        if not self.validar_hora(hora):
            messagebox.showwarning("Error", "Formato de hora invalido.\\\\nUse HH:MM (ej: 09:30, 14:15)")
            return
        
        # VERIFICACION 1: Turno duplicado para el mismo cliente
        if self.verificar_turno_existente(nombre, fecha, hora):
            messagebox.showwarning(
                "Turno Duplicado", 
                f"ATENCION: Ya existe un turno para:\\\\n"
                f"Cliente: {nombre}\\\\n"
                f"Fecha: {fecha_str}\\\\n"
                f"Hora: {hora}\\\\n\\\\n"
                f"Por favor, verifique los datos o elija otra hora."
            )
            return
        
        # VERIFICACION 2: Estilista ya ocupado en ese horario
        if self.verificar_disponibilidad_estilista(fecha, hora, estilista):
            messagebox.showwarning(
                "Estilista No Disponible", 
                f"ATENCION: El estilista {estilista} ya tiene un turno:\\\\n"
                f"Fecha: {fecha_str}\\\\n"
                f"Hora: {hora}\\\\n\\\\n"
                f"Por favor, elija otro horario u otro estilista."
            )
            return
        
        try:
            self.cursor.execute('''INSERT INTO turnos (nombre, telefono, servicio, estilista, manicura, fecha, hora) VALUES (?, ?, ?, ?, ?, ?, ?)''', (nombre, telefono, servicio, estilista, manicura, fecha, hora))
            
            self.conexion.commit()
            print(f"Turno guardado: {nombre} - {fecha} {hora}")
            messagebox.showinfo("Exito", "Turno agregado correctamente")
            self.limpiar_formulario()
            self.cargar_turnos()
        except Exception as err:
            print(f"Error al guardar turno: {err}")
            messagebox.showerror("Error BD", f"No se pudo agregar: {err}")
'''

# Reemplazar
nuevo_content = re.sub(patron_agregar, nuevo_agregar_turno + '\\\\n\\\\n', content, flags=re.DOTALL)

guardar_archivo(nuevo_content)
print("Cambios aplicados correctamente")
