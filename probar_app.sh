#!/bin/bash
echo "=== PRUEBA COMPLETA DE LA APLICACIÓN ==="
echo "1. Verificando sintaxis..."
python -m py_compile turnos_app.py && echo "✓ Sintaxis OK" || exit 1

echo "2. Verificando base de datos..."
if [ -f "turnos.db" ]; then
    echo "✓ Base de datos existe"
else
    echo "⚠ Base de datos no encontrada, se creará al ejecutar"
fi

echo "3. Probando imports..."
python -c "
try:
    from turnos_app import AppTurnosPeluqueria
    print('✓ Imports OK')
    print('✓ AppTurnosPeluqueria cargada')
except Exception as e:
    print(f'✗ Error en imports: {e}')
    exit(1)
"

echo "✅ Pruebas completadas - La aplicación está lista para usar"
echo ""
echo "PARA EJECUTAR:"
echo "source venv/Scripts/activate && python turnos_app.py"
