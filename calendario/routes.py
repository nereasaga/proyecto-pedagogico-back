from flask import Blueprint, jsonify, request
from db import execute_query

calendario_bp = Blueprint('calendario_bp', __name__)
festivos_bp = Blueprint('festivos_bp', __name__)

@calendario_bp.route('/api/calendario/<int:usuario_id>', methods=['GET'])
def get_calendario_empleado(usuario_id):
    try:
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

        if not user_employee_data or user_employee_data[1] is None:
            return jsonify({"message": "Usuario no encontrado o no es un empleado con calendario"}), 404

        nombre_empleado, empleado_id, centro_id = user_employee_data

        calendario = {
            "nombre_empleado": nombre_empleado,
            "horarios_semanales": [],
            "festivos_aplicables": [],
            "vacaciones_registradas": []
        }

        # Horarios semanales
        horarios_query = """
            SELECT dia_semana, hora_entrada, hora_salida
            FROM horarios_empleado
            WHERE empleado_id = %s
            ORDER BY dia_semana;
        """
        horarios = execute_query(horarios_query, (empleado_id,))
        dias_semana = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
        for dia, entrada, salida in horarios:
            calendario["horarios_semanales"].append({
                "dia_semana": dias_semana.get(dia, "Desconocido"),
                "hora_entrada": str(entrada),
                "hora_salida": str(salida)
            })

        # Festivos
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
        festivos = execute_query(festivos_query, (centro_id,))
        for fecha, descripcion, tipo in festivos:
            calendario["festivos_aplicables"].append({
                "fecha": str(fecha),
                "descripcion": descripcion,
                "tipo": tipo
            })

        # Vacaciones
        vacaciones_query = """
            SELECT fecha_inicio, fecha_fin, dias_solicitados, aprobada
            FROM vacaciones_empleado
            WHERE empleado_id = %s;
        """
        vacaciones = execute_query(vacaciones_query, (empleado_id,))
        for inicio, fin, dias, aprobada in vacaciones:
            calendario["vacaciones_registradas"].append({
                "fecha_inicio": str(inicio),
                "fecha_fin": str(fin),
                "dias_solicitados": dias,
                "aprobada": aprobada
            })

                  
            

        return jsonify(calendario)

    except Exception as e:
        return jsonify({"message": f"Error al obtener calendario del empleado: {str(e)}"}), 500
    
@festivos_bp.route('/api/festivos', methods=['GET'])
def get_all_festivos():
    """
    Obtiene todos los días festivos registrados en la base de datos.
    Se pueden filtrar por centro_id opcionalmente.
    """
    try:
        centro_id = request.args.get('centro_id', type=int)

        query = """
            SELECT
                f.fecha,
                f.descripcion,
                tf.nombre AS tipo_festivo_nombre,
                f.centro_id
            FROM
                festivos f
            JOIN
                tipos_festivo tf ON f.tipo_festivo_id = tf.id
        """
        params = []

        if centro_id:
            query += " WHERE f.centro_id IS NULL OR f.centro_id = %s"
            params.append(centro_id)

        festivos_data = execute_query(query, tuple(params))

        if not festivos_data:
            return jsonify({"message": "No se encontraron días festivos."}), 404

        festivos_list = []
        for fecha, descripcion, tipo_nombre, centro_id_festivo in festivos_data:
            festivos_list.append({
                "fecha": str(fecha),
                "descripcion": descripcion,
                "tipo": tipo_nombre,
                "centro_id_aplicable": centro_id_festivo
            })

        return jsonify(festivos_list), 200

    except Exception as e:
        return jsonify({"message": f"Error al obtener los días festivos: {str(e)}"}), 500