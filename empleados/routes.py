from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import execute_query
from auth import permiso_requerido

empleados_bp = Blueprint('empleados_bp', __name__)

# Ruta protegida con verificación de permisos personalizada
@empleados_bp.route('/api/empleados/<int:usuario_id>', methods=['GET'])
@permiso_requerido
def get_empleado(usuario_id):
    """
    Obtiene datos de un empleado específico
    Requiere autenticación y permisos adecuados
    """
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
        result = execute_query(query, (usuario_id,), fetch_one=True)
        
        if not result:
            return jsonify({"mensaje": "Empleado no encontrado"}), 404
            
        empleado = {
            "usuario_id": result[0],
            "nombre_completo": result[1],
            "email": result[2],
            "rol": result[3],
            "centro_trabajo": result[4],
            "jornada_semanal_horas": float(result[5]),
            "jornada_anual_horas": float(result[6]),
            "dias_vacaciones_asignados": result[7]
        }
        
        return jsonify(empleado)
    except Exception as e:
        return jsonify({"mensaje": f"Error al obtener empleado: {str(e)}"}), 500

# Ruta protegida con verificación de permisos básica
@empleados_bp.route('/api/todosEmpleados', methods=['GET'])
@jwt_required()
def get_empleados():
    """
    Obtiene lista de todos los empleados
    Solo accesible para administradores y responsables
    """
    # Obtener identidad del token
    current_identity = get_jwt_identity()
    rol_actual = current_identity['rol']
    
    # Verificar si tiene permisos para ver todos los empleados
    if rol_actual not in ['Administrador', 'Responsable de Área']:
        return jsonify({"mensaje": "No autorizado para ver todos los empleados"}), 403
    
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
