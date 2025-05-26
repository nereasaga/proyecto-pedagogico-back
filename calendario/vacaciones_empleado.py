from flask import Blueprint, request, jsonify
from db import execute_query
from datetime import date

vacaciones_bp = Blueprint('vacaciones_bp', __name__)

@vacaciones_bp.route('/api/vacaciones', methods=['POST'])
def crear_vacaciones():
    try:
        data = request.get_json()

        empleado_id = data.get("empleado_id")
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        dias_solicitados = data.get("dias_solicitados")
        aprobada = data.get("aprobada", False)

        if not all([empleado_id, fecha_inicio, fecha_fin, dias_solicitados]):
            return jsonify({"message": "Faltan campos obligatorios."}), 400

       
        try:
            fecha_inicio_dt = date.fromisoformat(fecha_inicio)
            fecha_fin_dt = date.fromisoformat(fecha_fin)
        except ValueError:
            return jsonify({"message": "Formato de fecha inválido. Use YYYY-MM-DD."}), 400

        insert_query = """
            INSERT INTO vacaciones_empleado (empleado_id, fecha_inicio, fecha_fin, dias_solicitados, aprobada)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        result = execute_query(insert_query, (empleado_id, fecha_inicio_dt, fecha_fin_dt, dias_solicitados, aprobada), fetch_one=True, commit=True)

        return jsonify({"message": "Vacaciones creadas exitosamente.", "id": result[0]}), 201

    except Exception as e:
        return jsonify({"message": f"Error al crear vacaciones: {str(e)}"}), 500


@vacaciones_bp.route('/api/vacaciones/<int:vacacion_id>', methods=['GET'])
def obtener_vacacion(vacacion_id):
    try:
        query = """
            SELECT id, empleado_id, fecha_inicio, fecha_fin, dias_solicitados, aprobada
            FROM vacaciones_empleado
            WHERE id = %s;
        """
        result = execute_query(query, (vacacion_id,), fetch_one=True)

        if not result:
            return jsonify({"message": "Vacaciones no encontradas."}), 404

        id_, empleado_id, fecha_inicio, fecha_fin, dias, aprobada = result
        return jsonify({
            "id": id_,
            "empleado_id": empleado_id,
            "fecha_inicio": str(fecha_inicio),
            "fecha_fin": str(fecha_fin),
            "dias_solicitados": dias,
            "aprobada": aprobada
        }), 200

    except Exception as e:
        return jsonify({"message": f"Error al obtener vacaciones: {str(e)}"}), 500


@vacaciones_bp.route('/api/vacaciones/empleado/<int:empleado_id>', methods=['GET'])
def listar_vacaciones_empleado(empleado_id):
    try:
        query = """
            SELECT id, fecha_inicio, fecha_fin, dias_solicitados, aprobada
            FROM vacaciones_empleado
            WHERE empleado_id = %s
            ORDER BY fecha_inicio DESC;
        """
        results = execute_query(query, (empleado_id,), fetch_all=True)

        vacaciones = []
        for id_, inicio, fin, dias, aprobada in results:
            vacaciones.append({
                "id": id_,
                "fecha_inicio": str(inicio),
                "fecha_fin": str(fin),
                "dias_solicitados": dias,
                "aprobada": aprobada
            })

        return jsonify(vacaciones), 200

    except Exception as e:
        return jsonify({"message": f"Error al listar vacaciones: {str(e)}"}), 500


@vacaciones_bp.route('/api/vacaciones/<int:vacacion_id>', methods=['PUT'])
def actualizar_vacacion(vacacion_id):
    try:
        data = request.get_json()
        campos = []

        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        dias_solicitados = data.get("dias_solicitados")
        aprobada = data.get("aprobada")

        valores = []
        if fecha_inicio:
            campos.append("fecha_inicio = %s")
            valores.append(date.fromisoformat(fecha_inicio))
        if fecha_fin:
            campos.append("fecha_fin = %s")
            valores.append(date.fromisoformat(fecha_fin))
        if dias_solicitados is not None:
            campos.append("dias_solicitados = %s")
            valores.append(dias_solicitados)
        if aprobada is not None:
            campos.append("aprobada = %s")
            valores.append(aprobada)

        if not campos:
            return jsonify({"message": "No se proporcionaron campos para actualizar."}), 400

        query = f"""
            UPDATE vacaciones_empleado
            SET {', '.join(campos)}
            WHERE id = %s;
        """
        valores.append(vacacion_id)
        execute_query(query, tuple(valores), commit=True,)

        return jsonify({"message": "Vacaciones actualizadas correctamente."}), 200

    except Exception as e:
        return jsonify({"message": f"Error al actualizar vacaciones: {str(e)}"}), 500


@vacaciones_bp.route('/api/vacaciones/<int:vacacion_id>', methods=['DELETE'])
def eliminar_vacacion(vacacion_id):
    try:
        query = "DELETE FROM vacaciones_empleado WHERE id = %s;"
        execute_query(query, (vacacion_id,), commit=True)

        return jsonify({"message": "Vacaciones eliminadas correctamente."}), 200

    except Exception as e:
        return jsonify({"message": f"Error al eliminar vacaciones: {str(e)}"}), 500
