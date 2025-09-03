# Mock users for testing authentication
mock_users = {
    'admin@empresa.com': {
        'id': 1,
        'email': 'admin@empresa.com',
        'password': 'admin123',  # In production, use hashed passwords
        'nombre_completo': 'Admin User',
        'rol': 'Administrador'
    },
    'responsable@empresa.com': {
        'id': 2,
        'email': 'responsable@empresa.com',
        'password': 'resp123',
        'nombre_completo': 'Responsable de Área',
        'rol': 'Responsable de Área',
        'centro_id': 1
    },
    'empleado@empresa.com': {
        'id': 3,
        'email': 'empleado@empresa.com',
        'password': 'emp123',
        'nombre_completo': 'Empleado Normal',
        'rol': 'Empleado',
        'centro_id': 1
    }
}

def get_user_by_email(email):
    """
    Get user by email from mock database
    """
    return mock_users.get(email)

def get_user_by_id(user_id):
    """
    Get user by ID from mock database
    """
    for user in mock_users.values():
        if user['id'] == user_id:
            return user
    return None