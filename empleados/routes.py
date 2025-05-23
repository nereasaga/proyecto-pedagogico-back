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
