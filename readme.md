# Calendario Laboral - Backend

Sistema de gestión de calendarios laborales para empleados - Componente Backend

## Descripción

Este proyecto implementa una API REST para gestionar calendarios laborales de empleados, incluyendo:
- Gestión de empleados
- Gestión de centros de trabajo
- Calendarios laborales
- Festivos y días especiales
- Horarios de trabajo
- Sistema de autenticación y autorización

## Tecnologías

- Python 3.12+
- Flask
- PostgreSQL
- JWT para autenticación

## Requisitos

- Python 3.12 o superior
- PostgreSQL
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/proyecto-pedagogico.git
cd proyecto-pedagogico-back
```

2. Crear y activar entorno virtual:
```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar la base de datos:
   - Crear base de datos PostgreSQL siguiendo las instrucciones en `data/como-ejecutar-script.txt`
   - Ejecutar el script SQL en `data/employeeCalendar.sql`

5. Configurar variables de entorno (opcional):
   - Crear archivo `.env` basado en `.env.example`
   - Ajustar configuración según sea necesario

## Ejecución

```bash
python app.py
```

La API estará disponible en http://localhost:5000

## Estructura del Proyecto

```
proyecto-pedagogico-back/
├── calendario/             # Módulo de calendario
│   ├── routes.py
│   ├── horarios_routes.py
│   └── vacaciones_routes.py
├── data/                   # Datos y scripts SQL
│   └── employeeCalendar.sql
├── empleados/              # Módulo de empleados
│   └── routes.py
├── templates/              # Plantillas HTML
│   └── index.html
├── app.py                  # Punto de entrada de la aplicación
├── config.py               # Configuración de la aplicación
├── auth.py                 # Sistema de autenticación
├── db.py                   # Conexión a base de datos
├── readme.md                   # Conexión a base de datos
└── requirements.txt        # Dependencias
```

## API Endpoints

### Autenticación
- `POST /api/login` - Iniciar sesión y obtener tokens JWT
- `POST /api/refresh` - Renovar token de acceso
- `GET /api/test-auth` - Endpoint de prueba para autenticación

### Empleados
- `GET /api/todosEmpleados` - Listar todos los empleados
- `GET /api/empleados/<id>` - Obtener detalles de un empleado
- `POST /api/empleados` - Crear nuevo empleado
- `PUT /api/empleados/<id>` - Actualizar empleado
- `DELETE /api/empleados/<id>` - Eliminar empleado

### Centros de Trabajo
- `GET /api/centros` - Listar centros de trabajo
- `GET /api/centros/<id>` - Obtener detalles de un centro
- `POST /api/centros` - Crear nuevo centro
- `PUT /api/centros/<id>` - Actualizar centro
- `DELETE /api/centros/<id>` - Eliminar centro

### Calendario
- `GET /api/calendario/<id>` - Obtener calendario de un empleado
- `GET /api/festivos` - Listar días festivos
- `POST /api/festivos` - Añadir día festivo

## Usuarios de Prueba

| Email | Contraseña | Rol |
|-------|------------|-----|
| admin@empresa.com | admin123 | Administrador |
| responsable@empresa.com | resp123 | Responsable de Área |
| empleado@empresa.com | emp123 | Empleado |

## Permisos por Rol

- **Administrador**: Acceso completo a todas las funcionalidades
- **Responsable de Área**: Gestión de empleados y calendarios de su centro
- **Empleado**: Visualización de su propio calendario y solicitud de vacaciones

## Licencia

Este proyecto está licenciado bajo [MIT License](LICENSE).