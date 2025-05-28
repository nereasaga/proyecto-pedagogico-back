from flask import Blueprint, jsonify, request
from db import execute_query
from flask_jwt_extended import jwt_required, get_jwt_identity

horarios_bp = Blueprint('horarios_bp', __name__)

@horarios_bp.route('/api/horariosempleado/<int:empleado_id>', methods=['GET'])
@jwt_required()  # Proteger la ruta con JWT
def get_horarios_empleado(empleado_id):
    """
    Obtiene todos los horarios de un empleado específico.
    """
    # Obtener identidad del token
    current_identity = get_jwt_identity()
    
    # Opcional: Verificar permisos (si el usuario actual puede ver estos horarios)
    # Por ejemplo, solo permitir al propio usuario o a administradores
    
    try:
        # Verificar que el empleado existe
        check_query = "SELECT id FROM empleados WHERE usuario_id = %s;"
        empleado = execute_query(check_query, (empleado_id,), fetch_one=True)
        
        if not empleado:
            return jsonify({"message": f"Empleado con ID {empleado_id} no encontrado"}), 404
            
        empleado_id_interno = empleado[0]
            
        query = """
            SELECT id, dia_semana, hora_entrada, hora_salida
            FROM horarios_empleado
            WHERE empleado_id = %s
            ORDER BY dia_semana;
        """
        horarios_data = execute_query(query, (empleado_id_interno,))
        
        dias_semana = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 
                       5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
        
        horarios_list = []
        for id, dia_semana, hora_entrada, hora_salida in horarios_data:
            horarios_list.append({
                "id": id,
                "dia_semana": dia_semana,
                "dia_nombre": dias_semana.get(dia_semana, "Desconocido"),
                "hora_entrada": str(hora_entrada),
                "hora_salida": str(hora_salida)
            })
            
        return jsonify(horarios_list), 200
        
    except Exception as e:
        return jsonify({"message": f"Error al obtener horarios del empleado: {str(e)}"}), 500

@horarios_bp.route('/api/horariosempleado', methods=['POST'])
def create_horario():
    """
    Crea un nuevo horario para un empleado.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Se requiere un cuerpo de solicitud JSON."}), 400
            
        usuario_id = data.get('usuario_id')
        dia_semana = data.get('dia_semana')
        hora_entrada = data.get('hora_entrada')
        hora_salida = data.get('hora_salida')
        
        # Validaciones básicas
        if not all([usuario_id, dia_semana, hora_entrada, hora_salida]):
            return jsonify({"message": "Faltan campos obligatorios"}), 400
            
        if not isinstance(dia_semana, int) or dia_semana < 1 or dia_semana > 7:
            return jsonify({"message": "El día de la semana debe ser un número entre 1 (Lunes) y 7 (Domingo)"}), 400
            
        # Obtener el ID interno del empleado
        check_query = "SELECT id FROM empleados WHERE usuario_id = %s;"
        empleado = execute_query(check_query, (usuario_id,), fetch_one=True)
        
        if not empleado:
            return jsonify({"message": f"Empleado con ID de usuario {usuario_id} no encontrado"}), 404
            
        empleado_id = empleado[0]
            
        # Verificar si ya existe un horario para ese día
        check_horario = """
            SELECT id FROM horarios_empleado 
            WHERE empleado_id = %s AND dia_semana = %s;
        """
        existing = execute_query(check_horario, (empleado_id, dia_semana), fetch_one=True)
        
        if existing:
            return jsonify({
                "message": f"Ya existe un horario para el día {dia_semana} para este empleado. Use PUT para actualizarlo."
            }), 409
            
        # Insertar nuevo horario
        insert_query = """
            INSERT INTO horarios_empleado (empleado_id, dia_semana, hora_entrada, hora_salida)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        new_id = execute_query(insert_query, (empleado_id, dia_semana, hora_entrada, hora_salida), 
                              fetch_one=True, commit=True)[0]
        
        dias_semana = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 
                       5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
                       
        return jsonify({
            "message": "Horario creado exitosamente",
            "id": new_id,
            "usuario_id": usuario_id,
            "dia_semana": dia_semana,
            "dia_nombre": dias_semana.get(dia_semana, "Desconocido"),
            "hora_entrada": hora_entrada,
            "hora_salida": hora_salida
        }), 201
        
    except Exception as e:
        return jsonify({"message": f"Error al crear horario: {str(e)}"}), 500

@horarios_bp.route('/api/horariosempleado/<int:horario_id>', methods=['PUT'])
def update_horario(horario_id):
    """
    Actualiza un horario existente.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Se requiere un cuerpo de solicitud JSON."}), 400
            
        # Verificar que el horario existe
        check_query = """
            SELECT empleado_id, dia_semana 
            FROM horarios_empleado 
            WHERE id = %s;
        """
        horario = execute_query(check_query, (horario_id,), fetch_one=True)
        
        if not horario:
            return jsonify({"message": f"Horario con ID {horario_id} no encontrado"}), 404
            
        empleado_id = horario[0]  # Mantener el empleado_id original
        dia_semana = data.get('dia_semana', horario[1])
        hora_entrada = data.get('hora_entrada')
        hora_salida = data.get('hora_salida')
        
        # Validaciones
        if dia_semana and (not isinstance(dia_semana, int) or dia_semana < 1 or dia_semana > 7):
            return jsonify({"message": "El día de la semana debe ser un número entre 1 (Lunes) y 7 (Domingo)"}), 400
            
        # Si cambia el día, verificar que no exista otro horario para ese día
        if dia_semana != horario[1]:
            check_dia = """
                SELECT id FROM horarios_empleado 
                WHERE empleado_id = %s AND dia_semana = %s AND id != %s;
            """
            existing = execute_query(check_dia, (empleado_id, dia_semana, horario_id), fetch_one=True)
            
            if existing:
                return jsonify({
                    "message": f"Ya existe un horario para el día {dia_semana} para este empleado."
                }), 409
        
        # Construir consulta dinámica
        update_fields = []
        update_values = []
        
        if dia_semana:
            update_fields.append("dia_semana = %s")
            update_values.append(dia_semana)
            
        if hora_entrada:
            update_fields.append("hora_entrada = %s")
            update_values.append(hora_entrada)
            
        if hora_salida:
            update_fields.append("hora_salida = %s")
            update_values.append(hora_salida)
            
        if not update_fields:
            return jsonify({"message": "No se proporcionaron campos para actualizar."}), 400
            
        update_values.append(horario_id)
        update_query = f"""
            UPDATE horarios_empleado 
            SET {', '.join(update_fields)} 
            WHERE id = %s
            RETURNING dia_semana, hora_entrada, hora_salida;
        """
        
        updated = execute_query(update_query, tuple(update_values), fetch_one=True, commit=True)
        
        dias_semana = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 
                       5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
                       
        return jsonify({
            "message": "Horario actualizado correctamente",
            "id": horario_id,
            "dia_semana": updated[0],
            "dia_nombre": dias_semana.get(updated[0], "Desconocido"),
            "hora_entrada": str(updated[1]),
            "hora_salida": str(updated[2])
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error al actualizar horario: {str(e)}"}), 500

@horarios_bp.route('/api/horariosempleado/<int:horario_id>', methods=['DELETE'])
def delete_horario(horario_id):
    """
    Elimina un horario existente.
    """
    try:
        # Verificar que el horario existe
        check_query = "SELECT id FROM horarios_empleado WHERE id = %s;"
        horario = execute_query(check_query, (horario_id,), fetch_one=True)
        
        if not horario:
            return jsonify({"message": f"Horario con ID {horario_id} no encontrado"}), 404
            
        # Eliminar horario
        delete_query = "DELETE FROM horarios_empleado WHERE id = %s;"
        execute_query(delete_query, (horario_id,), commit=True)
        
        return jsonify({"message": f"Horario con ID {horario_id} eliminado correctamente"}), 200
        
    except Exception as e:
        return jsonify({"message": f"Error al eliminar horario: {str(e)}"}), 500
