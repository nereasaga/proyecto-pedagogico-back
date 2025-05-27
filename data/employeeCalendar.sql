--Crear la base de datos
--CREATE DATABASE "employeeCalendar";
--entrar en la base de datos
--\c "employeeCalendar"

-- Crear tabla centro_trabajo
CREATE TABLE centros_trabajo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    ubicacion VARCHAR(255)
);

INSERT INTO centros_trabajo (nombre, ubicacion) VALUES
('Barcelona', 'Av. del Bogatell, 82, Sant Martí, 08005, Barcelona'),
('Madrid', 'C. Fernando Poo, 25, Arganzuela, 28045, Madrid'),
('Málaga', 'C. dos Aceras, 23, 25, 29012, Arrabal-Málaga');


-- Crear tabla role
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO roles (nombre) VALUES
('Administrador'),
('Responsable de Área'),
('Empleado');

-- Crear tabla usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol_id INTEGER NOT NULL REFERENCES roles(id),
    centro_id INTEGER REFERENCES centros_trabajo(id)
);

-- Suponiendo que los roles y centros ya están insertados
INSERT INTO usuarios (nombre_completo, email, password_hash, rol_id, centro_id) VALUES
('Admin General', 'admin@empresa.com', 'hashed_password_admin', (SELECT id FROM roles WHERE nombre = 'Administrador'), NULL),
('Responsable Barcelona', 'resp.barcelona@empresa.com', 'hashed_password_resp_bcn', (SELECT id FROM roles WHERE nombre = 'Responsable de Área'), (SELECT id FROM centros_trabajo WHERE nombre = 'Barcelona')),
('Responsable Madrid', 'resp.madrid@empresa.com', 'hashed_password_resp_mad', (SELECT id FROM roles WHERE nombre = 'Responsable de Área'), (SELECT id FROM centros_trabajo WHERE nombre = 'Madrid')),
('Empleado Juan Pérez', 'juan.perez@empresa.com', 'hashed_password_juan', (SELECT id FROM roles WHERE nombre = 'Empleado'), (SELECT id FROM centros_trabajo WHERE nombre = 'Barcelona')),
('Empleado Ana García', 'ana.garcia@empresa.com', 'hashed_password_ana', (SELECT id FROM roles WHERE nombre = 'Empleado'), (SELECT id FROM centros_trabajo WHERE nombre = 'Madrid'));


-- Crear tabla empleados
CREATE TABLE empleados (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
    jornada_semanal_horas NUMERIC(4,2) NOT NULL,
    jornada_anual_horas NUMERIC(7,2) NOT NULL,
    dias_vacaciones_asignados INTEGER NOT NULL
);

-- Suponiendo que los usuarios ya están insertados
INSERT INTO empleados (usuario_id, jornada_semanal_horas, jornada_anual_horas, dias_vacaciones_asignados) VALUES
((SELECT id FROM usuarios WHERE email = 'juan.perez@empresa.com'), 40.00, 1780.00, 22),
((SELECT id FROM usuarios WHERE email = 'ana.garcia@empresa.com'), 35.00, 1560.00, 20);

--Crear tabla horarios_empleados
CREATE TABLE horarios_empleado (
    id SERIAL PRIMARY KEY,
    empleado_id INTEGER NOT NULL REFERENCES empleados(id),
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7), -- 1=Lunes, 7=Domingo
    hora_entrada TIME NOT NULL,
    hora_salida TIME NOT NULL
);

-- Horario para Juan Pérez (ID de usuario de Juan Pérez)
INSERT INTO horarios_empleado (empleado_id, dia_semana, hora_entrada, hora_salida) VALUES
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'juan.perez@empresa.com')), 1, '09:00:00', '18:00:00'), -- Lunes
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'juan.perez@empresa.com')), 2, '09:00:00', '18:00:00'), -- Martes
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'juan.perez@empresa.com')), 3, '09:00:00', '18:00:00'), -- Miércoles
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'juan.perez@empresa.com')), 4, '09:00:00', '18:00:00'), -- Jueves
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'juan.perez@empresa.com')), 5, '09:00:00', '14:00:00'); -- Viernes (media jornada)

-- Horario para Ana García (ID de usuario de Ana García)
INSERT INTO horarios_empleado (empleado_id, dia_semana, hora_entrada, hora_salida) VALUES
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'ana.garcia@empresa.com')), 1, '09:00:00', '17:00:00'),
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'ana.garcia@empresa.com')), 2, '09:00:00', '17:00:00'),
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'ana.garcia@empresa.com')), 3, '09:00:00', '17:00:00'),
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'ana.garcia@empresa.com')), 4, '09:00:00', '17:00:00'),
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'ana.garcia@empresa.com')), 5, '09:00:00', '14:00:00');

--Crear tablas tipos_festivos
CREATE TABLE tipos_festivo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO tipos_festivo (nombre) VALUES
('Estatal'),
('Autonómico'),
('Local'),
('Propio de la Entidad');

--Crear tabla festivos
CREATE TABLE festivos (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    tipo_festivo_id INTEGER NOT NULL REFERENCES tipos_festivo(id),
    centro_id INTEGER REFERENCES centros_trabajo(id) -- NULL para festivos estatales
);

-- Suponiendo que los tipos de festivo y centros ya están insertados
INSERT INTO festivos (fecha, descripcion, tipo_festivo_id, centro_id) VALUES
-- Festivos estatales
('2025-01-01', 'Año Nuevo', (SELECT id FROM tipos_festivo WHERE nombre = 'Estatal'), NULL),
('2025-01-06', 'Día de Reyes', (SELECT id FROM tipos_festivo WHERE nombre = 'Estatal'), NULL),
('2025-10-12', 'Fiesta Nacional de España', (SELECT id FROM tipos_festivo WHERE nombre = 'Estatal'), NULL),

-- Festivos autonómicos (ej. Cataluña, para Barcelona)
('2025-06-24', 'San Juan', (SELECT id FROM tipos_festivo WHERE nombre = 'Autonómico'), (SELECT id FROM centros_trabajo WHERE nombre = 'Barcelona')),
('2025-09-11', 'Diada Nacional de Catalunya', (SELECT id FROM tipos_festivo WHERE nombre = 'Autonómico'), (SELECT id FROM centros_trabajo WHERE nombre = 'Barcelona')),

-- Festivos locales (ej. Barcelona)
('2025-09-24', 'La Mercè', (SELECT id FROM tipos_festivo WHERE nombre = 'Local'), (SELECT id FROM centros_trabajo WHERE nombre = 'Barcelona')),

-- Festivos autonómicos (ej. Comunidad de Madrid, para Madrid)
('2025-05-02', 'Día de la Comunidad de Madrid', (SELECT id FROM tipos_festivo WHERE nombre = 'Autonómico'), (SELECT id FROM centros_trabajo WHERE nombre = 'Madrid')),
('2025-05-15', 'San Isidro Labrador', (SELECT id FROM tipos_festivo WHERE nombre = 'Local'), (SELECT id FROM centros_trabajo WHERE nombre = 'Madrid')),

-- Días de descanso propios de la entidad (ej. "Día Tomillo")
('2025-12-23', 'Día Tomillo', (SELECT id FROM tipos_festivo WHERE nombre = 'Propio de la Entidad'), NULL); -- Podría ser global o por centro

INSERT INTO usuarios (nombre_completo, email, password_hash, rol_id, centro_id) VALUES
('Admin General', 'admin@empresa.com', 'hashed_password_admin', (SELECT id FROM roles WHERE nombre = 'Administrador'), NULL),
('Empleado Juan Pérez', 'juan.perez@empresa.com', 'hashed_password_juan', (SELECT id FROM roles WHERE nombre = 'Empleado'), (SELECT id FROM centros_trabajo WHERE nombre = 'Barcelona')),

--Crear tabla vacaciones_empleado
CREATE TABLE vacaciones_empleado (
    id SERIAL PRIMARY KEY,
    empleado_id INTEGER NOT NULL REFERENCES empleados(id),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    dias_solicitados INTEGER NOT NULL,
    aprobada BOOLEAN DEFAULT FALSE
);

-- Vacaciones de ejemplo para Juan Pérez
INSERT INTO vacaciones_empleado (empleado_id, fecha_inicio, fecha_fin, dias_solicitados, aprobada) VALUES
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'juan.perez@empresa.com')), '2025-07-14', '2025-07-25', 10, TRUE),
((SELECT id FROM empleados WHERE usuario_id = (SELECT id FROM usuarios WHERE email = 'juan.perez@empresa.com')), '2025-12-26', '2025-12-31', 3, FALSE);

