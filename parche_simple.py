# Leer líneas
with open('turnos_app.py', 'r') as f:
    lines = f.readlines()

# Encontrar agregar_turno y reemplazar
new_lines = []
i = 0
while i < len(lines):
    if 'def agregar_turno(self):' in lines[i]:
        # Saltar la función vieja hasta encontrar la siguiente función
        while i < len(lines) and not lines[i].startswith('def cargar_turnos(self):'):
            i += 1
            if i >= len(lines):
                break
        
        # Insertar la nueva función
        new_lines.append('    def agregar_turno(self):\\n')
        new_lines.append('        nombre = self.entry_nombre.get().strip()\\n')
        new_lines.append('        telefono = self.entry_telefono.get().strip()\\n')
        new_lines.append('        servicio = self.combo_servicio.get().strip()\\n')
        new_lines.append('        estilista = self.combo_estilista.get().strip()\\n')
        new_lines.append('        manicura = self.combo_manicura.get().strip()\\n')
        new_lines.append('        \\n')
        new_lines.append('        # Convertir fecha de dd/mm/aaaa a aaaa-mm-dd para SQLite\\n')
        new_lines.append('        fecha_str = self.entry_fecha.get()\\n')
        new_lines.append('        try:\\n')
        new_lines.append('            fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")\\n')
        new_lines.append('            fecha = fecha_obj.strftime("%Y-%m-%d")\\n')
        new_lines.append('        except ValueError:\\n')
        new_lines.append('            messagebox.showwarning("Error", "Formato de fecha invalido. Use DD/MM/AAAA")\\n')
        new_lines.append('            return\\n')
        new_lines.append('        \\n')
        new_lines.append('        hora = self.entry_hora.get().strip()\\n')
        new_lines.append('        \\n')
        new_lines.append('        if not all([nombre, servicio, hora]):\\n')
        new_lines.append('            messagebox.showwarning("Error", "Complete los campos obligatorios: Nombre, Servicio y Hora")\\n')
        new_lines.append('            return\\n')
        new_lines.append('        \\n')
        new_lines.append('        if not self.validar_hora(hora):\\n')
        new_lines.append('            messagebox.showwarning("Error", "Formato de hora invalido.\\\\\\\\nUse HH:MM (ej: 09:30, 14:15)")\\n')
        new_lines.append('            return\\n')
        new_lines.append('        \\n')
        new_lines.append('        # VERIFICACION 1: Turno duplicado para el mismo cliente\\n')
        new_lines.append('        if self.verificar_turno_existente(nombre, fecha, hora):\\n')
        new_lines.append('            messagebox.showwarning(\\n')
        new_lines.append('                "Turno Duplicado", \\n')
        new_lines.append('                f"ATENCION: Ya existe un turno para:\\\\\\\\\\\\\\\\n"\\n')
        new_lines.append('                f"Cliente: {nombre}\\\\\\\\\\\\\\\\\\\\n"\\n')
        new_lines.append('                f"Fecha: {fecha_str}\\\\\\\\\\\\\\\\\\\\n"\\n')
        new_lines.append('                f"Hora: {hora}\\\\\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n"\\n')
        new_lines.append('                f"Por favor, verifique los datos o elija otra hora."\\n')
        new_lines.append('            )\\n')
        new_lines.append('            return\\n')
        new_lines.append('        \\n')
        new_lines.append('        # VERIFICACION 2: Estilista ya ocupado en ese horario\\n')
        new_lines.append('        if self.verificar_disponibilidad_estilista(fecha, hora, estilista):\\n')
        new_lines.append('            messagebox.showwarning(\\n')
        new_lines.append('                "Estilista No Disponible", \\n')
        new_lines.append('                f"ATENCION: El estilista {estilista} ya tiene un turno:\\\\\\\\\\\\\\\\n"\\n')
        new_lines.append('                f"Fecha: {fecha_str}\\\\\\\\\\\\\\\\\\\\n"\\n')
        new_lines.append('                f"Hora: {hora}\\\\\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n"\\n')
        new_lines.append('                f"Por favor, elija otro horario u otro estilista."\\n')
        new_lines.append('            )\\n')
        new_lines.append('            return\\n')
        new_lines.append('        \\n')
        new_lines.append('        try:\\n')
        new_lines.append('            self.cursor.execute(\\'\\'\\'INSERT INTO turnos (nombre, telefono, servicio, estilista, manicura, fecha, hora) VALUES (?, ?, ?, ?, ?, ?, ?)\\'\\'\\', (nombre, telefono, servicio, estilista, manicura, fecha, hora))\\n')
        new_lines.append('            \\n')
        new_lines.append('            self.conexion.commit()\\n')
        new_lines.append('            print(f"Turno guardado: {nombre} - {fecha} {hora}")\\n')
        new_lines.append('            messagebox.showinfo("Exito", "Turno agregado correctamente")\\n')
        new_lines.append('            self.limpiar_formulario()\\n')
        new_lines.append('            self.cargar_turnos()\\n')
        new_lines.append('        except Exception as err:\\n')
        new_lines.append('            print(f"Error al guardar turno: {err}")\\n')
        new_lines.append('            messagebox.showerror("Error BD", f"No se pudo agregar: {err}")\\n')
        new_lines.append('\\n')
        
        # Continuar desde cargar_turnos
        if i < len(lines):
            new_lines.append(lines[i])
            i += 1
    else:
        new_lines.append(lines[i])
        i += 1

# Guardar
with open('turnos_app.py', 'w') as f:
    f.writelines(new_lines)

print("Parche aplicado")
