--
-- PostgreSQL database
--

-- Crear la base de datos (opcional si ya existe)
--CREATE DATABASE "proyecto-pedagogico" ENCODING 'UTF8' LC_COLLATE 'es_ES.UTF-8' LC_CTYPE 'es_ES.UTF-8' TEMPLATE template0;  

-- Conectarse a la base
--\connect proyecto_pedagogico;

-- Tablas y secuencias principales

CREATE TABLE centros_trabajo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    ubicacion VARCHAR(255)
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE tipos_festivo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol_id INTEGER NOT NULL REFERENCES roles(id),
    centro_id INTEGER REFERENCES centros_trabajo(id)
);

CREATE TABLE empleados (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
    jornada_semanal_horas NUMERIC(4,2) NOT NULL,
    jornada_anual_horas NUMERIC(7,2) NOT NULL,
    dias_vacaciones_asignados INTEGER NOT NULL
);

CREATE TABLE festivos (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    tipo_festivo_id INTEGER NOT NULL REFERENCES tipos_festivo(id),
    centro_id INTEGER REFERENCES centros_trabajo(id)
);

CREATE TABLE horarios_empleado (
    id SERIAL PRIMARY KEY,
    empleado_id INTEGER NOT NULL REFERENCES empleados(id),
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
    hora_entrada TIME NOT NULL,
    hora_salida TIME NOT NULL
);

CREATE TABLE vacaciones_empleado (
    id SERIAL PRIMARY KEY,
    empleado_id INTEGER NOT NULL REFERENCES empleados(id),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    dias_solicitados INTEGER NOT NULL,
    aprobada BOOLEAN DEFAULT FALSE
);

-- INSERCIÓN DE DATOS
-- Tabla centros_trabajo

INSERT INTO public.centros_trabajo (id, nombre, ubicacion) VALUES
(1, 'Barcelona', 'Av. del Bogatell, 82, Sant Martí, 08005, Barcelona'),
(2, 'Madrid', 'C. Fernando Poo, 25, Arganzuela, 28045, Madrid');


-- Tabla  roles

INSERT INTO public.roles (id, nombre) VALUES
(1, 'Administrador'),
(2, 'Responsable de Área'),
(3, 'Empleado');


-- Tabla tipos_festivo

INSERT INTO public.tipos_festivo (id, nombre) VALUES
(1, 'Estatal'),
(2, 'Autonómico'),
(3, 'Local'),
(4, 'Propio de la Entidad');

-- Tabla usuarios

INSERT INTO usuarios (id, nombre_completo, email, password_hash, rol_id, centro_id) VALUES
(1, 'Admin General', 'admin@empresa.com', 'hashed_password_admin', 1, NULL),
(2, 'Responsable Barcelona', 'resp.barcelona@empresa.com', 'hashed_password_resp_bcn', 2, 1),
(3, 'Responsable Madrid', 'resp.madrid@empresa.com', 'hashed_password_resp_mad', 2, 2),
(4, 'Leonor Ramirez', 'leoramirez@gmail.com', '1234', 2, 2),
(5, 'ELisa Domenech', 'elidomenech@gmail.com', '$2b$12$lTEtGyqw2.9rmkQG94xCdu6II8h1hd3gj9AoNFPhuTKdk.iJGZf72', 3, 2),
(6, 'Belen Adria Mateu', 'belenadria@gmail.com', '$2b$12$rNukG4ShEN/stz8rk7iCQOXVIwBcxVMWEkvlGgOgzI1VyGoIG8zY.', 3, 1),
(7, 'Juan Pérez', 'juan.perez@empresa.com', 'hashed_password_juan', 3, 1),
(8, 'Ana García', 'ana.garcia@empresa.com', 'hashed_password_ana', 3, 2);


-- Tabla empleados

INSERT INTO empleados (id, usuario_id, jornada_semanal_horas, jornada_anual_horas, dias_vacaciones_asignados) VALUES
(1, 5, 40.00, 1800.00, 21),
(2, 6, 40.00, 1800.00, 21),
(3, 7, 40.00, 1800.00, 21),
(4, 8, 40.00, 1800.00, 21);



-- Tabla festivos

INSERT INTO festivos (id, fecha, descripcion, tipo_festivo_id, centro_id) VALUES
(1, '2025-01-01', 'Año Nuevo', 1, NULL),
(2, '2025-01-06', 'Día de Reyes', 1, NULL),
(3, '2025-10-12', 'Fiesta Nacional de España', 1, NULL),
(4, '2025-06-24', 'San Juan', 2, 1),
(5, '2025-09-11', 'Diada Nacional de Catalunya', 2, 1),
(6, '2025-09-24', 'La Mercè', 3, 1),
(7, '2025-05-02', 'Día de la Comunidad de Madrid', 2, 2),
(8, '2025-05-15', 'San Isidro Labrador', 3, 2),
(9, '2025-12-23', 'Día Tomillo', 4, NULL),
(10, '2025-04-23', 'San Jordi', 1, 1);


-- Tabla horarios_empleado

INSERT INTO horarios_empleado (empleado_id, dia_semana, hora_entrada, hora_salida) VALUES
-- Empleado 1
(1, 1, '08:30:00', '16:30:00'),
(1, 2, '09:00:00', '18:00:00'),
(1, 3, '09:00:00', '18:00:00'),
(1, 4, '09:00:00', '18:00:00'),
(1, 5, '09:00:00', '14:00:00'),

-- Empleado 2
(2, 1, '09:00:00', '17:00:00'),
(2, 2, '09:00:00', '17:00:00'),
(2, 3, '09:00:00', '17:00:00'),
(2, 4, '09:00:00', '17:00:00'),
(2, 5, '09:00:00', '14:00:00'),

-- Empleado 3
(3, 1, '09:00:00', '16:00:00'),
(3, 2, '09:00:00', '16:00:00'),
(3, 3, '09:00:00', '16:00:00'),
(3, 4, '09:00:00', '16:00:00'),
(3, 5, '09:00:00', '14:00:00'),

-- Empleado 4
(4, 1, '06:00:00', '18:00:00'),
(4, 2, '06:00:00', '18:00:00'),
(4, 3, '09:00:00', '18:00:00'),
(4, 4, '09:00:00', '18:00:00'),
(4, 5, '09:00:00', '14:00:00');


--Tabla vacaciones_empleado

INSERT INTO vacaciones_empleado (empleado_id, fecha_inicio, fecha_fin, dias_solicitados, aprobada) VALUES
(1, '2025-07-01', '2025-07-10', 10, true),
(2, '2025-06-10', '2025-06-15', 5, true),
(1, '2025-05-28', '2025-05-29', 2, false),
(4, '2025-05-29', '2025-05-29', 1, true);