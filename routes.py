from flask import jsonify, request, render_template
from app import app, get_db_connection # Importamos get_db_connection
import datetime
import json # Para jsonify resultados de consultas

@app.route('/')
def index():
    return render_template('index.html')

# Función auxiliar para ejecutar consultas y manejar la conexión
def execute_query(query, params=None, fetch_one=False, commit=False):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        if commit:
            conn.commit()
        if fetch_one:
            return cur.fetchone()
        else:
            return cur.fetchall()
    except Exception as e:
        conn.rollback() # Revierte cambios en caso de error
        print(f"Error executing query: {e}") # Log del error
        raise e # Relanza la excepción para que Flask la maneje
    finally:
        cur.close()


# a. Petición para mostrar datos de un empleado por ID de usuario
@app.route('/api/empleados/<int:usuario_id>', methods=['GET'])
def get_empleado_data(usuario_id):
    try:
        # Consulta para obtener datos del usuario y empleado, incluyendo centro y rol
        query = """
            SELECT
                u.id AS usuario_id,
                u.nombre_completo,
                u.email,
                r.nombre AS rol_nombre,
                ct.nombre AS centro_trabajo_nombre,
                e.id AS empleado_id,
                e.jornada_semanal_horas,
                e.jornada_anual_horas,
                e.dias_vacaciones_asignados
            FROM
                usuarios u
            JOIN
                roles r ON u.rol_id = r.id
            LEFT JOIN -- LEFT JOIN para centros_trabajo porque puede ser NULL para administradores
                centros_trabajo ct ON u.centro_id = ct.id
            LEFT JOIN -- LEFT JOIN porque no todos los usuarios son empleados
                empleados e ON u.id = e.usuario_id
            WHERE
                u.id = %s;
        """
        result = execute_query(query, (usuario_id,), fetch_one=True)

        if not result:
            return jsonify({"message": "Usuario o empleado no encontrado"}), 404

        # Mapear los resultados a un diccionario legible
        empleado_data = {
            "usuario_id": result[0],
            "nombre_completo": result[1],
            "email": result[2],
            "rol": result[3],
            "centro_de_trabajo": result[4] if result[4] else "No asignado",
            "empleado_id": result[5],
            "jornada_semanal_horas": float(result[6]), # Convertir de Decimal a float
            "jornada_anual_horas": float(result[7]),   # Convertir de Decimal a float
            "dias_vacaciones_asignados": result[8]
        }
        return jsonify(empleado_data)

    except Exception as e:
        return jsonify({"message": f"Error al obtener datos del empleado: {str(e)}"}), 500


# b. Petición para mostrar calendario de un empleado por ID de usuario
@app.route('/api/calendario/<int:usuario_id>', methods=['GET'])
def get_calendario_empleado(usuario_id):
    try:
        # Primero, obtener el empleado y su centro de trabajo
        user_employee_query = """
            SELECT
                u.nombre_completo,
                e.id AS empleado_id,
                u.centro_id
            FROM
                usuarios u
            LEFT JOIN empleados e ON u.id = e.usuario_id
            WHERE u.id = %s;
        """
        user_employee_data = execute_query(user_employee_query, (usuario_id,), fetch_one=True)

        if not user_employee_data or user_employee_data[1] is None: # Si no hay datos de usuario o no es empleado
            return jsonify({"message": "Usuario no encontrado o no es un empleado con calendario"}), 404

        nombre_empleado = user_employee_data[0]
        empleado_id = user_employee_data[1]
        centro_id = user_employee_data[2]

        calendario = {
            "nombre_empleado": nombre_empleado,
            "horarios_semanales": [],
            "festivos_aplicables": [],
            "vacaciones_registradas": []
        }

        # 1. Horarios Semanales
        horarios_query = """
            SELECT dia_semana, hora_entrada, hora_salida
            FROM horarios_empleado
            WHERE empleado_id = %s
            ORDER BY dia_semana;
        """
        horarios_results = execute_query(horarios_query, (empleado_id,))
        dias_semana_map = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
        for h in horarios_results:
            calendario["horarios_semanales"].append({
                "dia_semana": dias_semana_map.get(h[0], "Desconocido"),
                "hora_entrada": str(h[1]),
                "hora_salida": str(h[2])
            })

        # 2. Festivos Aplicables
        # Festivos globales (estatales y propios de la entidad sin centro_id) y del centro del empleado
        festivos_query = """
            SELECT
                f.fecha,
                f.descripcion,
                tf.nombre AS tipo_festivo_nombre
            FROM
                festivos f
            JOIN
                tipos_festivo tf ON f.tipo_festivo_id = tf.id
            WHERE
                f.centro_id IS NULL OR f.centro_id = %s;
        """
        festivos_results = execute_query(festivos_query, (centro_id,))
        for f in festivos_results:
            calendario["festivos_aplicables"].append({
                "fecha": str(f[0]),
                "descripcion": f[1],
                "tipo": f[2]
            })
        # Opcional: Si los festivos globales y de centro pueden duplicarse y quieres un set único:
        # calendario["festivos_aplicables"] = list({json.dumps(f) for f in calendario["festivos_aplicables"]})
        # calendario["festivos_aplicables"] = [json.loads(s) for s in calendario["festivos_aplicables"]]


        # 3. Vacaciones Registradas
        vacaciones_query = """
            SELECT fecha_inicio, fecha_fin, dias_solicitados, aprobada
            FROM vacaciones_empleado
            WHERE empleado_id = %s;
        """
        vacaciones_results = execute_query(vacaciones_query, (empleado_id,))
        for v in vacaciones_results:
            calendario["vacaciones_registradas"].append({
                "fecha_inicio": str(v[0]),
                "fecha_fin": str(v[1]),
                "dias_solicitados": v[2],
                "aprobada": v[3]
            })

        return jsonify(calendario)

    except Exception as e:
        return jsonify({"message": f"Error al obtener calendario del empleado: {str(e)}"}), 500


# Lista de todos los empleados
@app.route('/api/todosEmpleados', methods=['GET'])
def get_empleados():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT 
                u.id AS usuario_id,
                u.nombre_completo,
                u.email,
                r.nombre AS rol,
                c.nombre AS centro_trabajo,
                e.jornada_semanal_horas,
                e.jornada_anual_horas,
                e.dias_vacaciones_asignados
            FROM empleados e
            JOIN usuarios u ON e.usuario_id = u.id
            JOIN roles r ON u.rol_id = r.id
            LEFT JOIN centros_trabajo c ON u.centro_id = c.id;
        """)

        rows = cur.fetchall()
        empleados = []
        for row in rows:
            empleados.append({
                "usuario_id": row[0],
                "nombre_completo": row[1],
                "email": row[2],
                "rol": row[3],
                "centro_trabajo": row[4],
                "jornada_semanal_horas": row[5],
                "jornada_anual_horas": row[6],
                "dias_vacaciones_asignados": row[7]
            })

        cur.close()
        return jsonify(empleados), 200

    except Exception as e:
        cur.close()
        return jsonify({"message": f"Error al obtener empleados: {str(e)}"}), 500
   
   ############################################
# Opcional: Ruta para crear un nuevo usuario/empleado (POST)
@app.route('/api/nuevoEmpleado', methods=['POST'])
def create_empleado():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Datos JSON no proporcionados"}), 400

    nombre_completo = data.get('nombre_completo')
    email = data.get('email')
    password_hash = data.get('password') # En una app real, ¡hashear la contraseña!
    rol_nombre = data.get('rol')
    centro_nombre = data.get('centro_trabajo')
    jornada_semanal = data.get('jornada_semanal_horas')
    jornada_anual = data.get('jornada_anual_horas')
    dias_vacaciones = data.get('dias_vacaciones_asignados')

    if not all([nombre_completo, email, password_hash, rol_nombre, jornada_semanal, jornada_anual, dias_vacaciones]):
        return jsonify({"message": "Faltan datos obligatorios"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Obtener rol_id
        cur.execute("SELECT id FROM roles WHERE nombre = %s;", (rol_nombre,))
        rol_id_row = cur.fetchone()
        if not rol_id_row:
            cur.close()
            return jsonify({"message": f"Rol '{rol_nombre}' no válido"}), 400
        rol_id = rol_id_row[0]

        # Obtener centro_id
        centro_id = None
        if centro_nombre:
            cur.execute("SELECT id FROM centros_trabajo WHERE nombre = %s;", (centro_nombre,))
            centro_id_row = cur.fetchone()
            if not centro_id_row:
                cur.close()
                return jsonify({"message": f"Centro de trabajo '{centro_nombre}' no encontrado"}), 400
            centro_id = centro_id_row[0]

        # Insertar en usuarios
        cur.execute(
            """
            INSERT INTO usuarios (nombre_completo, email, password_hash, rol_id, centro_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (nombre_completo, email, password_hash, rol_id, centro_id)
        )
        new_user_id = cur.fetchone()[0]

        # Insertar en empleados
        cur.execute(
            """
            INSERT INTO empleados (usuario_id, jornada_semanal_horas, jornada_anual_horas, dias_vacaciones_asignados)
            VALUES (%s, %s, %s, %s);
            """,
            (new_user_id, jornada_semanal, jornada_anual, dias_vacaciones)
        )

        conn.commit()
        cur.close()
        return jsonify({"message": "Empleado y usuario creados exitosamente", "usuario_id": new_user_id}), 201



    except Exception as e:
        conn.rollback()
        cur.close()
        return jsonify({"message": f"Error al crear empleado: {str(e)}"}), 500
    
   ############################################
