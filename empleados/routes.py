from flask import Blueprint, jsonify, request
from db import execute_query

empleados_bp = Blueprint('empleados_bp', __name__) 

@empleados_bp.route('/api/todosEmpleados', methods=['GET'])
def get_empleados():
    try:
        query = """
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
        """
        result = execute_query(query)
        empleados = [
            {
                "usuario_id": row[0],
                "nombre_completo": row[1],
                "email": row[2],
                "rol": row[3],
                "centro_trabajo": row[4],
                "jornada_semanal_horas": float(row[5]),
                "jornada_anual_horas": float(row[6]),
                "dias_vacaciones_asignados": row[7]
            }
            for row in result
        ]
        return jsonify(empleados)
    except Exception as e:
        return jsonify({"message": f"Error al obtener empleados: {str(e)}"}), 500
    
@empleados_bp.route('/api/empleados/<int:usuario_id>', methods=['GET'])
def get_empleado(usuario_id):
    try:
        query = """
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
            LEFT JOIN centros_trabajo c ON u.centro_id = c.id
            WHERE u.id = %s;
        """
        row = execute_query(query, (usuario_id,), fetch_one=True)
        if not row:
            return jsonify({"message": "Empleado no encontrado"}), 404

        empleado = {
            "usuario_id": row[0],
            "nombre_completo": row[1],
            "email": row[2],
            "rol": row[3],
            "centro_trabajo": row[4],
            "jornada_semanal_horas": float(row[5]),
            "jornada_anual_horas": float(row[6]),
            "dias_vacaciones_asignados": row[7]
        }
        return jsonify(empleado)
    except Exception as e:
        return jsonify({"message": f"Error al obtener empleado: {str(e)}"}), 500


@empleados_bp.route('/api/empleados', methods=['POST'])
def create_empleado():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Datos JSON no proporcionados"}), 400

        nombre_completo = data.get('nombre_completo')
        email = data.get('email')
        password_hash = data.get('password')  # OJO: en producción hashea esta contraseña
        rol_nombre = data.get('rol')
        centro_nombre = data.get('centro_trabajo')  # opcional
        jornada_semanal = data.get('jornada_semanal_horas')
        jornada_anual = data.get('jornada_anual_horas')
        dias_vacaciones = data.get('dias_vacaciones_asignados')

        if not all([nombre_completo, email, password_hash, rol_nombre, jornada_semanal, jornada_anual, dias_vacaciones]):
            return jsonify({"message": "Faltan datos obligatorios"}), 400

        rol_query = "SELECT id FROM roles WHERE nombre = %s;"
        rol_result = execute_query(rol_query, (rol_nombre,), fetch_one=True)
        if not rol_result:
            return jsonify({"message": f"Rol '{rol_nombre}' no válido"}), 400
        rol_id = rol_result[0]

        centro_id = None
        if centro_nombre:
            centro_query = "SELECT id FROM centros_trabajo WHERE nombre = %s;"
            centro_result = execute_query(centro_query, (centro_nombre,), fetch_one=True)
            if not centro_result:
                return jsonify({"message": f"Centro de trabajo '{centro_nombre}' no encontrado"}), 400
            centro_id = centro_result[0]

        insert_usuario = """
            INSERT INTO usuarios (nombre_completo, email, password_hash, rol_id, centro_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        new_user_id = execute_query(insert_usuario, (nombre_completo, email, password_hash, rol_id, centro_id), fetch_one=True, commit=True)[0]

        insert_empleado = """
            INSERT INTO empleados (usuario_id, jornada_semanal_horas, jornada_anual_horas, dias_vacaciones_asignados)
            VALUES (%s, %s, %s, %s);
        """
        execute_query(insert_empleado, (new_user_id, jornada_semanal, jornada_anual, dias_vacaciones), commit=True)

        return jsonify({"message": "Empleado creado exitosamente", "usuario_id": new_user_id}), 201

    except Exception as e:
        return jsonify({"message": f"Error al crear empleado: {str(e)}"}), 500
    

@empleados_bp.route('/api/empleados/<int:usuario_id>', methods=['PUT'])
def update_empleado(usuario_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Datos JSON no proporcionados"}), 400

        nombre_completo = data.get('nombre_completo')
        email = data.get('email')
        rol_nombre = data.get('rol')
        centro_nombre = data.get('centro_trabajo')
        jornada_semanal = data.get('jornada_semanal_horas')
        jornada_anual = data.get('jornada_anual_horas')
        dias_vacaciones = data.get('dias_vacaciones_asignados')

        # Validar existencia empleado
        user_check = execute_query("SELECT id FROM usuarios WHERE id = %s;", (usuario_id,), fetch_one=True)
        if not user_check:
            return jsonify({"message": "Empleado no encontrado"}), 404

        # Actualizar tabla usuarios
        if rol_nombre:
            rol_result = execute_query("SELECT id FROM roles WHERE nombre = %s;", (rol_nombre,), fetch_one=True)
            if not rol_result:
                return jsonify({"message": f"Rol '{rol_nombre}' no válido"}), 400
            rol_id = rol_result[0]
        else:
            rol_id = None

        centro_id = None
        if centro_nombre:
            centro_result = execute_query("SELECT id FROM centros_trabajo WHERE nombre = %s;", (centro_nombre,), fetch_one=True)
            if not centro_result:
                return jsonify({"message": f"Centro de trabajo '{centro_nombre}' no encontrado"}), 400
            centro_id = centro_result[0]

        # Construir update dinámico para usuarios
        update_usuario_fields = []
        update_usuario_values = []

        if nombre_completo:
            update_usuario_fields.append("nombre_completo = %s")
            update_usuario_values.append(nombre_completo)
        if email:
            update_usuario_fields.append("email = %s")
            update_usuario_values.append(email)
        if rol_id is not None:
            update_usuario_fields.append("rol_id = %s")
            update_usuario_values.append(rol_id)
        if centro_id is not None:
            update_usuario_fields.append("centro_id = %s")
            update_usuario_values.append(centro_id)

        if update_usuario_fields:
            update_usuario_values.append(usuario_id)
            query_usuario = f"UPDATE usuarios SET {', '.join(update_usuario_fields)} WHERE id = %s;"
            execute_query(query_usuario, update_usuario_values, commit=True)

        # Actualizar tabla empleados
        update_empleado_fields = []
        update_empleado_values = []

        if jornada_semanal is not None:
            update_empleado_fields.append("jornada_semanal_horas = %s")
            update_empleado_values.append(jornada_semanal)
        if jornada_anual is not None:
            update_empleado_fields.append("jornada_anual_horas = %s")
            update_empleado_values.append(jornada_anual)
        if dias_vacaciones is not None:
            update_empleado_fields.append("dias_vacaciones_asignados = %s")
            update_empleado_values.append(dias_vacaciones)

        if update_empleado_fields:
            update_empleado_values.append(usuario_id)
            query_empleado = f"UPDATE empleados SET {', '.join(update_empleado_fields)} WHERE usuario_id = %s;"
            execute_query(query_empleado, update_empleado_values, commit=True)

        return jsonify({"message": "Empleado actualizado correctamente"})

    except Exception as e:
        return jsonify({"message": f"Error al actualizar empleado: {str(e)}"}), 500


@empleados_bp.route('/api/empleados/<int:usuario_id>', methods=['DELETE'])
def delete_empleado(usuario_id):
    try:
        # Validar que exista el usuario
        user_check = execute_query("SELECT id FROM usuarios WHERE id = %s;", (usuario_id,), fetch_one=True)
        if not user_check:
            return jsonify({"message": "Empleado no encontrado"}), 404

        # Primero eliminar empleado (tabla dependiente)
        execute_query("DELETE FROM empleados WHERE usuario_id = %s;", (usuario_id,), commit=True)

        # Luego eliminar usuario
        execute_query("DELETE FROM usuarios WHERE id = %s;", (usuario_id,), commit=True)

        return jsonify({"message": "Empleado eliminado correctamente"})
    except Exception as e:
        return jsonify({"message": f"Error al eliminar empleado: {str(e)}"}), 500
