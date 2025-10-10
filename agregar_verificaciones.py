import re

# Leer el archivo actual
with open('turnos_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Las nuevas funciones a agregar
nuevas_funciones = '''
    def verificar_turno_existente(self, nombre, fecha, hora):
        """Verificar si ya existe un turno con los mismos datos"""
        try:
            self.cursor.execute(\'''
                SELECT COUNT(*) FROM turnos 
                WHERE nombre = ? AND fecha = ? AND hora = ?
            \''', (nombre, fecha, hora))
            
            return self.cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"Error verificando turno: {e}")
            return False

    def verificar_disponibilidad_estilista(self, fecha, hora, estilista):
        """Verificar si el estilista ya tiene un turno en esa fecha/hora"""
        if estilista in ["", "No aplica"]:
            return False
        try:
            self.cursor.execute(\'''
                SELECT COUNT(*) FROM turnos 
                WHERE fecha = ? AND hora = ? AND estilista = ?
            \''', (fecha, hora, estilista))
            
            return self.cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"Error verificando estilista: {e}")
            return False
'''

# Encontrar dónde agregar las funciones (después de validar_hora)
patron = r'(def validar_hora\(self, hora\):.*?return False\n)'
match = re.search(patron, content, re.DOTALL)

if match:
    # Insertar las nuevas funciones después de validar_hora
    posicion = match.end()
    nuevo_content = content[:posicion] + nuevas_funciones + content[posicion:]
    
    # Guardar el archivo modificado
    with open('turnos_app.py', 'w', encoding='utf-8') as f:
        f.write(nuevo_content)
    print("✅ Funciones de verificación agregadas correctamente")
else:
    print("❌ No se pudo encontrar la función validar_hora")
