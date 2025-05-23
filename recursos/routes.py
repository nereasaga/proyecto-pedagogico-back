from flask import Blueprint, jsonify, request
from db import execute_query

recursos_bp = Blueprint('recursos_bp', __name__)

# Roles endpoints
@recursos_bp.route('/api/roles', methods=['GET'])
def get_roles():
    """
    Obtiene todos los roles disponibles en el sistema.
    """
    try:
        query = "SELECT id, nombre FROM roles ORDER BY id;"
        roles_data = execute_query(query)
        
        roles_list = []
        for id, nombre in roles_data:
            roles_list.append({
                "id": id,
                "nombre": nombre
            })
            
        return jsonify(roles_list), 200
        
    except Exception as e:
        return jsonify({"message": f"Error al obtener roles: {str(e)}"}), 500

# Centros de trabajo endpoints
@recursos_bp.route('/api/centros', methods=['GET'])
def get_centros():
    """
    Obtiene todos los centros de trabajo.
    """
    try:
        query = "SELECT id, nombre, ubicacion FROM centros_trabajo ORDER BY nombre;"
        centros_data = execute_query(query)
        
        centros_list = []
        for id, nombre, ubicacion in centros_data:
            centros_list.append({
                "id": id,
                "nombre": nombre,
                "ubicacion": ubicacion
            })
            
        return jsonify(centros_list), 200
        
    except Exception as e:
        return jsonify({"message": f"Error al obtener centros de trabajo: {str(e)}"}), 500

@recursos_bp.route('/api/centros', methods=['POST'])
def create_centro():
    """
    Crea un nuevo centro de trabajo.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Se requiere un cuerpo de solicitud JSON."}), 400
            
        nombre = data.get('nombre')
        ubicacion = data.get('ubicacion')
        
        if not nombre:
            return jsonify({"message": "El campo 'nombre' es obligatorio."}), 400
            
        # Verificar si ya existe un centro con ese nombre
        check_query = "SELECT id FROM centros_trabajo WHERE nombre = %s;"
        existing = execute_query(check_query, (nombre,), fetch_one=True)
        
        if existing:
            return jsonify({"message": f"Ya existe un centro de trabajo con el nombre '{nombre}'."}), 409
            
        # Insertar nuevo centro
        insert_query = """
            INSERT INTO centros_trabajo (nombre, ubicacion)
            VALUES (%s, %s)
            RETURNING id;
        """
        new_id = execute_query(insert_query, (nombre, ubicacion), fetch_one=True, commit=True)[0]
        
        return jsonify({
            "message": "Centro de trabajo creado exitosamente.",
            "id": new_id,
            "nombre": nombre,
            "ubicacion": ubicacion
        }), 201
        
    except Exception as e:
        return jsonify({"message": f"Error al crear centro de trabajo: {str(e)}"}), 500

@recursos_bp.route('/api/centros/<int:centro_id>', methods=['PUT'])
def update_centro(centro_id):
    """
    Actualiza un centro de trabajo existente.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Se requiere un cuerpo de solicitud JSON."}), 400
            
        # Verificar que el centro existe
        check_query = "SELECT id FROM centros_trabajo WHERE id = %s;"
        centro = execute_query(check_query, (centro_id,), fetch_one=True)
        
        if not centro:
            return jsonify({"message": f"El centro de trabajo con ID {centro_id} no existe."}), 404
            
        nombre = data.get('nombre')
        ubicacion = data.get('ubicacion')
        
        if nombre:
            # Verificar si ya existe otro centro con ese nombre
            check_name_query = "SELECT id FROM centros_trabajo WHERE nombre = %s AND id != %s;"
            existing = execute_query(check_name_query, (nombre, centro_id), fetch_one=True)
            
            if existing:
                return jsonify({"message": f"Ya existe otro centro de trabajo con el nombre '{nombre}'."}), 409
        
        # Construir consulta dinámica
        update_fields = []
        update_values = []
        
        if nombre:
            update_fields.append("nombre = %s")
            update_values.append(nombre)
            
        if ubicacion is not None:
            update_fields.append("ubicacion = %s")
            update_values.append(ubicacion)
            
        if not update_fields:
            return jsonify({"message": "No se proporcionaron campos para actualizar."}), 400
            
        update_values.append(centro_id)
        update_query = f"UPDATE centros_trabajo SET {', '.join(update_fields)} WHERE id = %s RETURNING id;"
        
        updated = execute_query(update_query, tuple(update_values), fetch_one=True, commit=True)
        
        # Obtener datos actualizados
        get_query = "SELECT nombre, ubicacion FROM centros_trabajo WHERE id = %s;"
        updated_data = execute_query(get_query, (centro_id,), fetch_one=True)
        
        return jsonify({
            "message": "Centro de trabajo actualizado correctamente.",
            "id": centro_id,
            "nombre": updated_data[0],
            "ubicacion": updated_data[1]
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error al actualizar centro de trabajo: {str(e)}"}), 500

@recursos_bp.route('/api/centros/<int:centro_id>', methods=['DELETE'])
def delete_centro(centro_id):
    """
    Elimina un centro de trabajo existente.
    """
    try:
        # Verificar que el centro existe
        check_query = "SELECT id FROM centros_trabajo WHERE id = %s;"
        centro = execute_query(check_query, (centro_id,), fetch_one=True)
        
        if not centro:
            return jsonify({"message": f"El centro de trabajo con ID {centro_id} no existe."}), 404
            
        # Verificar si hay empleados asociados a este centro
        check_empleados = "SELECT COUNT(*) FROM usuarios WHERE centro_id = %s;"
        empleados_count = execute_query(check_empleados, (centro_id,), fetch_one=True)[0]
        
        if empleados_count > 0:
            return jsonify({
                "message": f"No se puede eliminar el centro de trabajo porque tiene {empleados_count} empleados asociados."
            }), 400
            
        # Eliminar centro
        delete_query = "DELETE FROM centros_trabajo WHERE id = %s RETURNING id;"
        deleted = execute_query(delete_query, (centro_id,), fetch_one=True, commit=True)
        
        return jsonify({"message": f"Centro de trabajo con ID {centro_id} eliminado correctamente."}), 200
        
    except Exception as e:
        return jsonify({"message": f"Error al eliminar centro de trabajo: {str(e)}"}), 500