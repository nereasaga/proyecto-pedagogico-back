from flask import Blueprint, jsonify, request
from db import execute_query
from datetime import date
import logging

calendario_bp = Blueprint('calendario_bp', __name__)
festivos_bp = Blueprint('festivos_bp', __name__)
roles_bp = Blueprint('roles_bp', __name__)

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
   #festivos 
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

        if centro_id is not None:
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
        logging.info("Error en GET /api/festivos")
        
        return jsonify(festivos_list), 200

       

    except Exception as e:
        return jsonify({"message": f"Error al obtener los días festivos: {str(e)}"}), 500
    
@festivos_bp.route('/api/festivos', methods=['POST'])
def add_new_festivo():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Se requiere un cuerpo de solicitud JSON."}), 400

        fecha_str = data.get('fecha')
        descripcion = data.get('descripcion')
        tipo_festivo_id = data.get('tipo_festivo_id')
        centro_id = data.get('centro_id')

        print("DATA RECIBIDA:", data)
        print("fecha_str:", fecha_str)
        print("descripcion:", descripcion)
        print("tipo_festivo_id:", tipo_festivo_id)
        print("centro_id:", centro_id)

        if not all([fecha_str, descripcion, tipo_festivo_id]):
            return jsonify({"message": "Faltan campos obligatorios."}), 400

        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            return jsonify({"message": "Formato de fecha inválido. Use YYYY-MM-DD."}), 400

        # Convertir tipo_festivo_id a entero y validar
        try:
            tipo_festivo_id = int(tipo_festivo_id)
        except (ValueError, TypeError):
            return jsonify({"message": "El campo tipo_festivo_id debe ser un número válido."}), 400

        # Validar y normalizar centro_id
        if centro_id in [None, '', 'null']:
            centro_id = None
        else:
            try:
                centro_id = int(centro_id)
            except (ValueError, TypeError):
                return jsonify({"message": "El campo centro_id debe ser un número válido o nulo."}), 400

        # Validar tipo_festivo_id existe
        tipo_exists = execute_query(
            "SELECT id FROM tipos_festivo WHERE id = %s;", (tipo_festivo_id,), fetch_one=True
        )
        if not tipo_exists:
            return jsonify({"message": f"El tipo_festivo_id {tipo_festivo_id} no existe."}), 404

        # Validar centro_id existe solo si no es None
        if centro_id is not None:
            centro_exists = execute_query(
                "SELECT id FROM centros_trabajo WHERE id = %s;", (centro_id,), fetch_one=True
            )
            if not centro_exists:
                return jsonify({"message": f"El centro_id {centro_id} no existe."}), 404

        insert_query = """
            INSERT INTO festivos (fecha, descripcion, tipo_festivo_id, centro_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        new_festivo = execute_query(insert_query, (fecha, descripcion, tipo_festivo_id, centro_id), fetch_one=True, commit=True)


        if new_festivo:
            return jsonify({
                "message": "Día festivo agregado exitosamente.",
                "id": new_festivo[0],
                "fecha": str(fecha),
                "descripcion": descripcion,
                "tipo_festivo_id": tipo_festivo_id,
                "centro_id": centro_id
            }), 201
        else:
            return jsonify({"message": "Error al agregar el día festivo."}), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Error en el servidor: {str(e)}"}), 500


@festivos_bp.route('/api/festivos/<int:festivo_id>', methods=['PUT'])
def update_festivo(festivo_id):
    """
    Actualiza un día festivo existente en la base de datos.
    Requiere 'fecha', 'descripcion', y 'tipo_festivo_id' en el cuerpo de la solicitud JSON.
    'centro_id' es opcional.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"message": "Se requiere un cuerpo de solicitud JSON."}), 400

        fecha_str = data.get('fecha')
        descripcion = data.get('descripcion')
        tipo_festivo_id = data.get('tipo_festivo_id')
        centro_id = data.get('centro_id')  # Opcional

        if not all([fecha_str, descripcion, tipo_festivo_id]):
            return jsonify({"message": "Faltan campos obligatorios: 'fecha', 'descripcion', 'tipo_festivo_id'."}), 400

        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            return jsonify({"message": "Formato de fecha inválido. Use YYYY-MM-DD."}), 400

        # Verifica existencia del festivo
        festivo_exist_query = "SELECT id FROM festivos WHERE id = %s;"
        if not execute_query(festivo_exist_query, (festivo_id,), fetch_one=True):
            return jsonify({"message": f"El festivo con ID {festivo_id} no existe."}), 404

        # Verifica tipo_festivo
        tipo_check_query = "SELECT id FROM tipos_festivo WHERE id = %s;"
        if not execute_query(tipo_check_query, (tipo_festivo_id,), fetch_one=True):
            return jsonify({"message": f"El tipo_festivo_id {tipo_festivo_id} no existe."}), 404

        # Verifica centro_id si se proporciona
        if centro_id is not None:
            centro_check_query = "SELECT id FROM centros_trabajo WHERE id = %s;"
            if not execute_query(centro_check_query, (centro_id,), fetch_one=True):
                return jsonify({"message": f"El centro_id {centro_id} no existe."}), 404

        update_query = """
            UPDATE festivos
            SET fecha = %s, descripcion = %s, tipo_festivo_id = %s, centro_id = %s
            WHERE id = %s;
        """
        execute_query(update_query, (fecha, descripcion, tipo_festivo_id, centro_id, festivo_id), commit=True)

        return jsonify({"message": "Día festivo actualizado correctamente."}), 200

    except Exception as e:
        return jsonify({"message": f"Error al actualizar el día festivo: {str(e)}"}), 500

@festivos_bp.route('/api/festivos/<int:festivo_id>', methods=['DELETE'])
def delete_festivo(festivo_id):
    """
    Elimina un día festivo existente en la base de datos por su ID.
    """
    try:
        # Verifica existencia
        festivo_exist_query = "SELECT id FROM festivos WHERE id = %s;"
        if not execute_query(festivo_exist_query, (festivo_id,), fetch_one=True):
            return jsonify({"message": f"El festivo con ID {festivo_id} no existe."}), 404

        delete_query = "DELETE FROM festivos WHERE id = %s;"
        execute_query(delete_query, (festivo_id,), commit=True)

        return jsonify({"message": f"Día festivo con ID {festivo_id} eliminado correctamente."}), 200

    except Exception as e:
        return jsonify({"message": f"Error al eliminar el día festivo: {str(e)}"}), 500


@festivos_bp.route('/api/festivos/<int:festivo_id>', methods=['GET'])
def get_festivo_by_id(festivo_id):
    """
    Obtiene un día festivo específico por su ID.
    """
    try:
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
            WHERE
                f.id = %s;
        """
        festivo_data = execute_query(query, (festivo_id,), fetch_one=True)

        if not festivo_data:
            return jsonify({"message": "Día festivo no encontrado."}), 404

        fecha, descripcion, tipo_nombre, centro_id_festivo = festivo_data
        festivo = {
            "id": festivo_id,
            "fecha": str(fecha),
            "descripcion": descripcion,
            "tipo": tipo_nombre,
            "centro_id_aplicable": centro_id_festivo
        }

        return jsonify(festivo), 200

    except Exception as e:
        return jsonify({"message": f"Error al obtener el día festivo: {str(e)}"}), 500
    
#roles
@roles_bp.route('/api/roles', methods=['GET'])
def get_roles():
    """
    Obtiene todos los roles de la base de datos.
    """
    try:
        query = "SELECT id, nombre FROM roles;"
        roles = execute_query(query)

        if not roles:
            return jsonify({"message": "No se encontraron roles."}), 404

        roles_list = [{"id": r[0], "nombre": r[1]} for r in roles]
        return jsonify(roles_list), 200

    except Exception as e:
        return jsonify({"message": f"Error al obtener los roles: {str(e)}"}), 500
        
@roles_bp.route('/api/roles', methods=['POST'])
def create_rol():
    """
    Crea un nuevo rol.
    Requiere 'nombre' en el cuerpo JSON.
    """
    try:
        data = request.get_json()
        nombre = data.get('nombre')

        if not nombre:
            return jsonify({"message": "El campo 'nombre' es obligatorio."}), 400

        insert_query = "INSERT INTO roles (nombre) VALUES (%s) RETURNING id;"
        new_rol_id = add_new_festivo(insert_query, (nombre,))  # Usa tu función de inserción aquí

        return jsonify({
            "message": "Rol creado exitosamente.",
            "id": new_rol_id,
            "nombre": nombre
        }), 201

    except Exception as e:
        return jsonify({"message": f"Error al crear el rol: {str(e)}"}), 500

@roles_bp.route('/api/roles/<int:rol_id>', methods=['PUT'])
def update_rol(rol_id):
    """
    Actualiza el nombre de un rol.
    Requiere 'nombre' en el cuerpo JSON.
    """
    try:
        data = request.get_json()
        nombre = data.get('nombre')

        if not nombre:
            return jsonify({"message": "El campo 'nombre' es obligatorio."}), 400

        # Verifica si existe el rol
        check_query = "SELECT id FROM roles WHERE id = %s;"
        if not execute_query(check_query, (rol_id,), fetch_one=True):
            return jsonify({"message": f"El rol con ID {rol_id} no existe."}), 404

        update_query = "UPDATE roles SET nombre = %s WHERE id = %s;"
        execute_query(update_query, (nombre, rol_id),commit=True)

        return jsonify({"message": "Rol actualizado correctamente."}), 200

    except Exception as e:
        return jsonify({"message": f"Error al actualizar el rol: {str(e)}"}), 500

@roles_bp.route('/api/roles/<int:rol_id>', methods=['PUT'])
def update_rol(rol_id):
    """
    Actualiza el nombre de un rol.
    Requiere 'nombre' en el cuerpo JSON.
    """
    try:
        data = request.get_json()
        nombre = data.get('nombre')

        if not nombre:
            return jsonify({"message": "El campo 'nombre' es obligatorio."}), 400

        # Verifica si existe el rol
        check_query = "SELECT id FROM roles WHERE id = %s;"
        if not execute_query(check_query, (rol_id,), fetch_one=True):
            return jsonify({"message": f"El rol con ID {rol_id} no existe."}), 404

        update_query = "UPDATE roles SET nombre = %s WHERE id = %s;"
        execute_query(update_query, (nombre, rol_id),commit=True)

        return jsonify({"message": "Rol actualizado correctamente."}), 200

    except Exception as e:
        return jsonify({"message": f"Error al actualizar el rol: {str(e)}"}), 500

@roles_bp.route('/api/roles/<int:rol_id>', methods=['DELETE'])
def delete_rol(rol_id):
    """
    Elimina un rol por su ID.
    """
    try:
        # Verifica si existe el rol
        check_query = "SELECT id FROM roles WHERE id = %s;"
        if not execute_query(check_query, (rol_id,), fetch_one=True):
            return jsonify({"message": f"El rol con ID {rol_id} no existe."}), 404

        delete_query = "DELETE FROM roles WHERE id = %s;"
        execute_query(delete_query, (rol_id,),commit=True)

        return jsonify({"message": f"Rol con ID {rol_id} eliminado correctamente."}), 200

    except Exception as e:
        return jsonify({"message": f"Error al eliminar el rol: {str(e)}"}), 500
