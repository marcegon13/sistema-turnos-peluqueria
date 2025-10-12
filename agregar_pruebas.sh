#!/bin/bash

# Script para agregar generaci√≥n de turnos de prueba a turnos_app_prueba.py

ARCHIVO="turnos_app_prueba.py"

echo "Ì¥ß Verificando archivo $ARCHIVO..."

# Verificar si el archivo existe
if [ ! -f "$ARCHIVO" ]; then
    echo "‚ùå Error: El archivo $ARCHIVO no existe"
    echo "Ì≥Å Archivos en el directorio:"
    ls -la *.py
    exit 1
fi

echo "‚úÖ Archivo encontrado: $ARCHIVO"

# Crear copia de seguridad
echo "Ì≥¶ Creando copia de seguridad..."
cp "$ARCHIVO" "${ARCHIVO}.backup"
echo "‚úÖ Copia de seguridad creada: ${ARCHIVO}.backup"

# Crear archivo temporal con la nueva funci√≥n
cat > temp_function.py << 'FUNC_EOF'
    def generar_turnos_prueba(self):
        """Genera 40 turnos de prueba para testing"""
        import random
        from datetime import datetime, timedelta
        
        # Datos de prueba
        nombres = [
            'Maria Gonzalez', 'Juan Perez', 'Ana Rodriguez', 'Carlos Lopez', 'Laura Martinez',
            'Diego Sanchez', 'Sofia Fernandez', 'Miguel Torres', 'Elena Ramirez', 'Pablo Diaz',
            'Carmen Ruiz', 'Javier Castro', 'Isabel Morales', 'Ricardo Ortiz', 'Patricia Silva',
            'Fernando Vargas', 'Lucia Herrera', 'Roberto Medina', 'Teresa Rios', 'Sergio Castro',
            'Monica Vega', 'Alberto Reyes', 'Raquel Ponce', 'Oscar Acosta', 'Veronica Flores',
            'Gabriel Molina', 'Adriana Leon', 'Hector Guerrero', 'Silvia Campos', 'Mario Soto',
            'Natalia Vargas', 'Andres Mendez', 'Eva Rojas', 'Francisco Ledesma', 'Rosa Figueroa',
            'Daniel Paredes', 'Olga Salazar', 'Jorge Miranda', 'Lorena Cordoba', 'Victor Aguirre'
        ]
        
        servicios_peluqueria = [
            'Corte + Lavado', 'Corte + Peinado', 'Tintura', 'Reflejos', 'Alisado',
            'Brushing', 'Tratamiento', 'Corte masculino', 'Corte femenino', 'Mechas',
            'Balayage', 'Corte + Color', 'Peinado festejo', 'Recogido', 'Ondas'
        ]
        
        servicios_manicura_lista = [
            'Esmaltado semi', 'Kapping', 'Esmaltado tradicional', 'U√±as esculpidas',
            'Manicura rusa', 'Pedicura', 'Esmaltado gel', 'Decoraci√≥n', 'French'
        ]
        
        try:
            # Generar 40 turnos
            for i in range(40):
                nombre = random.choice(nombres)
                telefono = f'11{random.randint(3000, 9999)}{random.randint(1000, 9999)}'
                servicio = random.choice(servicios_peluqueria)
                estilista = random.choice(self.estilistas)
                manicura = random.choice(self.manicuras)
                servicios_manicura = random.choice(servicios_manicura_lista)
                
                # Fecha aleatoria en los pr√≥ximos 30 d√≠as
                fecha_base = datetime.now() + timedelta(days=random.randint(1, 30))
                fecha = fecha_base.strftime('%Y-%m-%d')
                
                # Hora aleatoria entre 9:00 y 20:00
                hora = f"{random.randint(9, 19):02d}:{random.choice(['00', '30'])}"
                
                # Insertar en la base de datos
                self.cursor.execute('''
                    INSERT INTO turnos (nombre, telefono, servicio, estilista, manicura, servicios_manicura, fecha, hora)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nombre, telefono, servicio, estilista, manicura, servicios_manicura, fecha, hora))
            
            self.conexion.commit()
            messagebox.showinfo('√âxito', '40 turnos de prueba generados correctamente')
            self.cargar_turnos()
            
        except Exception as err:
            messagebox.showerror('Error', f'No se pudieron generar los turnos: {err}')
FUNC_EOF

echo "Ì≥ù Agregando funci√≥n de generaci√≥n de pruebas..."

# Insertar la funci√≥n despu√©s de crear_boton_redondeado
awk '
/def crear_boton_redondeado.*:/ {
    print
    while (getline line < "temp_function.py") {
        print line
    }
    close("temp_function.py")
    next
}
/def buscar_turnos/ {
    # Asegurarse de que no agregamos duplicados
    if (!added) {
        print
        added = 1
    }
    next
}
{
    print
}
' "$ARCHIVO" > "${ARCHIVO}.new" && mv "${ARCHIVO}.new" "$ARCHIVO"

echo "Ì¥ò Agregando bot√≥n en la interfaz..."

# Agregar el bot√≥n despu√©s de btn_actualizar
sed -i '/btn_actualizar.pack(side=tk.LEFT)/a\        btn_prueba = tk.Button(frame_botones, text="GENERAR PRUEBA", bg="#6f42c1", fg="white", font=("Arial", 8, "bold"), relief="flat", bd=0, padx=8, pady=4, command=self.generar_turnos_prueba)\n        btn_prueba.pack(side=tk.LEFT, padx=(8, 0))' "$ARCHIVO"

# Limpiar archivos temporales
rm -f temp_function.py

echo "‚úÖ Modificaciones completadas!"
echo "ÌæØ Nuevas funcionalidades agregadas:"
echo "   - Funci√≥n: generar_turnos_prueba()"
echo "   - Bot√≥n: 'GENERAR PRUEBA' (color p√∫rpura)"
echo ""
echo "Ì∫Ä Para probar:"
echo "   1. Ejecuta: python turnos_app_prueba.py"
echo "   2. Haz clic en 'GENERAR PRUEBA'"
echo "   3. Se crear√°n 40 turnos de prueba autom√°ticamente"
echo ""
echo "Ì≥ä Podr√°s probar b√∫squedas por:"
echo "   - Nombre (Maria, Juan, Ana, etc.)"
echo "   - Estilista (Walter Tejada, Jorgelina Silvero, etc.)"
echo "   - Manicura (Liliana Pavon, Noelia Leguizamon)"
echo "   - Servicios (Corte, Color, Alisado, etc.)"

# Verificar cambios
if grep -q "generar_turnos_prueba" "$ARCHIVO"; then
    echo "‚úÖ Verificaci√≥n: Funci√≥n agregada correctamente"
else
    echo "‚ùå Verificaci√≥n: Error al agregar la funci√≥n"
fi

if grep -q "GENERAR PRUEBA" "$ARCHIVO"; then
    echo "‚úÖ Verificaci√≥n: Bot√≥n agregado correctamente"
else
    echo "‚ùå Verificaci√≥n: Error al agregar el bot√≥n"
fi
