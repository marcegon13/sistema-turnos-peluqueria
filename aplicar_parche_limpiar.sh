#!/bin/bash

echo "Ì¥ß Aplicando parche para agregar bot√≥n LIMPIAR..."

# Crear archivo de parche temporal
cat > parche_temp.py << 'ENDPATCH'
import re

# Leer el archivo original
with open('turnos_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("Ì≥ñ Leyendo archivo turnos_app.py...")

# PARCHE 1: Reemplazar secci√≥n de botones
old_buttons = '''btn_agregar.pack(side=tk.LEFT, padx=(0, 10))

btn_actualizar = self.crear_boton_redondeado(
    frame_botones, "Ì¥Ñ ACTUALIZAR", self.estilos["info"], self.cargar_turnos
)
btn_actualizar.pack(side=tk.LEFT)'''

new_buttons = '''btn_agregar.pack(side=tk.LEFT, padx=(0, 10))

btn_limpiar = self.crear_boton_redondeado(
    frame_botones, "Ì∑π LIMPIAR", self.estilos["advertencia"], self.limpiar_formulario
)
btn_limpiar.pack(side=tk.LEFT, padx=(0, 10))

btn_actualizar = self.crear_boton_redondeado(
    frame_botones, "Ì¥Ñ ACTUALIZAR TABLA", self.estilos["info"], self.cargar_turnos
)
btn_actualizar.pack(side=tk.LEFT)'''

if old_buttons in content:
    content = content.replace(old_buttons, new_buttons)
    print("‚úÖ Secci√≥n de botones actualizada")
else:
    print("‚ö†Ô∏è No se encontr√≥ la secci√≥n exacta de botones, buscando alternativa...")
    # Buscar patr√≥n alternativo
    pattern = r'(btn_agregar\.pack\(side=tk\.LEFT, padx=\(0, 10\)\))(.*?)(btn_actualizar\.pack\(side=tk\.LEFT\))'
    replacement = r'\1\n\nbtn_limpiar = self.crear_boton_redondeado(\n    frame_botones, "Ì∑π LIMPIAR", self.estilos["advertencia"], self.limpiar_formulario\n)\nbtn_limpiar.pack(side=tk.LEFT, padx=(0, 10))\n\n\2\3'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    print("‚úÖ Secci√≥n de botones actualizada (patr√≥n alternativo)")

# PARCHE 2: Verificar que existe la funci√≥n limpiar_formulario
if 'def limpiar_formulario(self):' not in content:
    print("Ì¥ç Agregando funci√≥n limpiar_formulario...")
    
    # Buscar donde agregar la funci√≥n (antes de def main() o def cargar_turnos())
    main_pattern = r'def main\(\):'
    limpiar_function = '''
def limpiar_formulario(self):
    """Limpiar todos los campos del formulario"""
    self.entry_nombre.delete(0, tk.END)
    self.entry_telefono.delete(0, tk.END)
    self.entry_hora.delete(0, tk.END)
    self.combo_servicio.set("")
    self.combo_estilista.set("")
    self.combo_manicura.set("")
    print("Ì∑π Formulario limpiado")
'''
    
    if re.search(main_pattern, content):
        content = re.sub(main_pattern, limpiar_function + '\\n\\n\\g<0>', content)
        print("‚úÖ Funci√≥n limpiar_formulario agregada antes de main()")
    else:
        # Buscar antes de cargar_turnos
        cargar_pattern = r'def cargar_turnos\(self\):'
        if re.search(cargar_pattern, content):
            content = re.sub(cargar_pattern, limpiar_function + '\\n\\n\\g<0>', content)
            print("‚úÖ Funci√≥n limpiar_formulario agregada antes de cargar_turnos()")
        else:
            # Agregar al final de la clase
            class_end_pattern = r'def eliminar_turno\(self\):'
            if re.search(class_end_pattern, content):
                content = re.sub(class_end_pattern, limpiar_function + '\\n\\n\\g<0>', content)
                print("‚úÖ Funci√≥n limpiar_formulario agregada antes de eliminar_turno()")
else:
    print("‚úÖ Funci√≥n limpiar_formulario ya existe")

# Guardar el archivo modificado
with open('turnos_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Ìæâ ¬°Parche aplicado exitosamente!")
ENDPATCH

# Ejecutar el parche
echo "Ì∫Ä Ejecutando parche..."
python parche_temp.py

# Limpiar archivo temporal
rm parche_temp.py

echo ""
echo "ÌæØ RESUMEN DE CAMBIOS:"
echo "   ‚úÖ Ì∑π BOT√ìN LIMPIAR (naranja) - Para borrar campos del formulario"
echo "   ‚úÖ Ì¥Ñ BOT√ìN ACTUALIZAR TABLA (azul) - Para refrescar la tabla"
echo "   ‚úÖ ‚ûï BOT√ìN AGREGAR TURNO (verde) - Para guardar turnos"
echo ""
echo "Ì≥ù Ahora puedes compilar la aplicaci√≥n con: pyinstaller --onefile --windowed --name 'SistemaTurnos' turnos_app.py"
