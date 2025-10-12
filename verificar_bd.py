import sqlite3
import os

def verificar_estructura_bd():
    try:
        db_path = 'turnos_peluqueria.db'
        
        if not os.path.exists(db_path):
            print(f"❌ No se encuentra la base de datos: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ver estructura de la tabla
        cursor.execute("PRAGMA table_info(turnos)")
        columnas = cursor.fetchall()
        
        print("🔍 ESTRUCTURA ACTUAL DE LA TABLA 'turnos':")
        print("=" * 50)
        for col in columnas:
            print(f"Columna {col[0]}: {col[1]} ({col[2]})")
        
        # Ver algunos datos de ejemplo
        print("\n📊 PRIMEROS 3 REGISTROS:")
        print("=" * 50)
        cursor.execute("SELECT * FROM turnos LIMIT 3")
        filas = cursor.fetchall()
        
        for i, fila in enumerate(filas):
            print(f"Fila {i+1}: {fila}")
        
        # Ver total de registros
        cursor.execute("SELECT COUNT(*) FROM turnos")
        total = cursor.fetchone()[0]
        print(f"\n📈 TOTAL DE REGISTROS: {total}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_estructura_bd()
    input("\nPresiona Enter para salir...")