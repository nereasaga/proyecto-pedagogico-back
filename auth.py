from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    get_jwt,
    current_user
)
from mock_users import get_user_by_email
from functools import wraps

auth_bp = Blueprint('auth_bp', __name__)

# Ruta de login para obtener tokens 
@auth_bp.route('/api/login', methods=['POST'])
def login():
    """
    Endpoint para autenticar usuarios y generar tokens JWT
    
    Recibe: JSON con email y password
    Devuelve: access_token, refresh_token y datos básicos del usuario
    """
    datos = request.get_json()
    if not datos:
        return jsonify({"mensaje": "Datos JSON no proporcionados"}), 400
    
    email = datos.get('email')
    password = datos.get('password')
    
    if not email or not password:
        return jsonify({"mensaje": "Email y contraseña son requeridos"}), 400
    
    try:
        # Obtener usuario de nuestros datos mock
        usuario = get_user_by_email(email)
        
        # Verificar si el usuario existe y la contraseña es correcta
        if not usuario or usuario['password'] != password:
            return jsonify({"mensaje": "Email o contraseña incorrectos"}), 401
        
        # Usar el ID del usuario como subject (string)
        user_id = str(usuario['id'])
        
        # Crear tokens con el ID como subject
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        
        # Incluir datos adicionales en la respuesta
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "usuario_id": usuario['id'],
            "rol": usuario['rol'],
            "nombre": usuario['nombre_completo']
        }), 200
        
    except Exception as e:
        return jsonify({"mensaje": f"Error en login: {str(e)}"}), 500

# Ruta para refrescar tokens
@auth_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Endpoint para renovar el access_token usando un refresh_token
    
    Requiere: refresh_token válido en el header Authorization
    Devuelve: nuevo access_token
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200

# Función para verificar permisos según rol
def verificar_permiso(id_usuario_actual, rol_actual, id_solicitado):
    """
    Verifica si un usuario tiene permiso para acceder a ciertos datos
    
    Args:
        id_usuario_actual: ID del usuario que hace la petición
        rol_actual: Rol del usuario que hace la petición
        id_solicitado: ID del usuario cuyos datos se solicitan
        
    Returns:
        bool: True si tiene permiso, False si no
    """
    # Administradores pueden acceder a todo
    if rol_actual == 'Administrador':
        return True
    # Responsables de Área pueden ver datos de su centro
    elif rol_actual == 'Responsable de Área':
        # Aquí podrías verificar si el usuario solicitado pertenece al mismo centro
        # que el responsable, pero necesitarías hacer una consulta adicional
        return id_usuario_actual == id_solicitado
    # Empleados solo pueden ver sus propios datos
    else:
        return id_usuario_actual == id_solicitado

# Decorador personalizado para verificar permisos
def permiso_requerido(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # Obtener identidad del token
        current_identity = get_jwt_identity()
        id_usuario_actual = current_identity['id']
        rol_actual = current_identity['rol']
        
        # Obtener ID del usuario solicitado (asumiendo que está en kwargs)
        usuario_id = kwargs.get('usuario_id')
        
        # Verificar permisos
        if not verificar_permiso(id_usuario_actual, rol_actual, usuario_id):
            return jsonify({"mensaje": "No autorizado para acceder a estos datos"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# Add a test route to verify authentication 
@auth_bp.route('/api/test-auth', methods=['GET'])
# Removed @jwt_required() decorator to make this route public que no esta protegido
def test_auth():
    """
    Endpoint de prueba para verificar que la autenticación funciona
    
    Ya no requiere token - es una ruta pública
    """
    # Get the token from the header if present (but don't require it)
    auth_header = request.headers.get('Authorization')
    user_info = {"mensaje": "Ruta pública - no requiere autenticación"}
    
    # If token is provided, try to get user info, but don't fail if no token
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            # Try to decode the token
            from flask_jwt_extended import decode_token
            decoded = decode_token(token)
            user_id = decoded['sub']
            
            # Look up the user in our mock database
            from mock_users import get_user_by_id
            usuario = get_user_by_id(int(user_id))
            
            if usuario:
                user_info = {
                    "mensaje": "Token válido detectado",
                    "usuario": {
                        "id": usuario['id'],
                        "email": usuario['email'],
                        "nombre": usuario['nombre_completo'],
                        "rol": usuario['rol']
                    }
                }
        except:
            # If token is invalid, just ignore it
            pass
    
    return jsonify(user_info), 200
