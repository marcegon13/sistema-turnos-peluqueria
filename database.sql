-- Crear base de datos para Turnos de Peluquería
CREATE DATABASE IF NOT EXISTS Turnos;
USE Turnos;

-- Crear tabla de turnos con todas las columnas necesarias
CREATE TABLE IF NOT EXISTS turnos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    servicio VARCHAR(100) NOT NULL,
    estilista VARCHAR(100),
    manicura VARCHAR(100),
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de ejemplo
INSERT INTO turnos (nombre, telefono, servicio, estilista, manicura, fecha, hora) VALUES
('María González', '11-1234-5678', 'Corte de Cabello', 'Ana García', 'No aplica', CURDATE(), '10:00:00'),
('Carlos López', '11-2345-6789', 'Coloración', 'Carlos López', 'No aplica', CURDATE(), '11:30:00'),
('Ana Martínez', '11-3456-7890', 'Manicura Spa', 'No aplica', 'Sofía Hernández', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:00:00');

SELECT '✅ Base de datos creada correctamente' as Estado;