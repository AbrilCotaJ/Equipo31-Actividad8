"""
Flask REST API for tbl_users (Backendless Integration)
Author: ChatGPT
Date: 2025-10-25
"""

from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ add this import
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)  # ✅ enable CORS for all routes

# ==============================
# CONFIGURACIÓN
# ==============================

BASE_URL = "https://amatoryrabbit-us.backendless.app/api/data/tbl_users"

HEADERS = {
    "Content-Type": "application/json",
    # Si tu app necesita autenticación, descomenta y agrega tus claves:
    # "application-id": "YOUR_APP_ID",
    # "secret-key": "YOUR_REST_API_KEY"
}

# ==============================
# RUTAS CRUD
# ==============================

# @app.route('/users', methods=['POST'])
# def create_user():
#     """
#     Crea un nuevo usuario en tbl_users (Backendless)
#     """
#     data = request.get_json()

#     # Agregar timestamps
#     data["created_at"] = datetime.now().isoformat()
#     data["last_login"] = None

#     response = requests.post(BASE_URL, json=data, headers=HEADERS)
#     return jsonify(response.json()), response.status_code


@app.route('/users', methods=['GET'])
def get_users():
    """
    Obtiene todos los usuarios
    """
    response = requests.get(BASE_URL, headers=HEADERS)
    return jsonify(response.json()), response.status_code


@app.route('/users/<object_id>', methods=['GET'])
def get_user_by_id(object_id):
    """
    Obtiene un usuario por su objectId
    """
    response = requests.get(f"{BASE_URL}/{object_id}", headers=HEADERS)
    return jsonify(response.json()), response.status_code


@app.route('/users/<object_id>', methods=['PUT'])
def update_user(object_id):
    """
    Actualiza un usuario existente
    """
    data = request.get_json()
    response = requests.put(f"{BASE_URL}/{object_id}", json=data, headers=HEADERS)
    return jsonify(response.json()), response.status_code


@app.route('/users/<object_id>', methods=['DELETE'])
def delete_user(object_id):
    """
    Elimina un usuario
    """
    response = requests.delete(f"{BASE_URL}/{object_id}", headers=HEADERS)
    if response.status_code in [200, 204]:
        return jsonify({"message": "Usuario eliminado correctamente"}), 200
    else:
        return jsonify({"error": "Error al eliminar usuario"}), response.status_code


@app.route('/login', methods=['POST'])
def login_user():
    """
    Verifica las credenciales de un usuario en la tabla tbl_users.
    Busca por email y password, y devuelve el username si las credenciales son válidas.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    # Buscar usuario por email
    query = f"?where=email%3D'{email}'"  # URL encoded: ?where=email='{email}'
    response = requests.get(f"{BASE_URL}{query}", headers=HEADERS)

    if response.status_code != 200:
        return jsonify({"error": "Error al acceder a la base de datos"}), 500

    users = response.json()

    if not users:
        return jsonify({"error": "Usuario no encontrado"}), 404

    user = users[0]

    # Validar la contraseña (sin hashing por ahora)
    if user.get("password") != password:
        return jsonify({"error": "Contraseña incorrecta"}), 401

    # Actualizar el último login
    update_data = {"last_login": datetime.now().isoformat()}
    requests.put(f"{BASE_URL}/{user['objectId']}", json=update_data, headers=HEADERS)

    # Retornar información del usuario
    return jsonify({
        "message": "Inicio de sesión exitoso",
        "user": {
            "objectId": user["objectId"],
            "username": user.get("username"),
            "email": user.get("email"),
            "last_login": update_data["last_login"]
        }
    }), 200

@app.route('/create_user', methods=['POST'])
def create_user():
    """
    Crea un nuevo usuario en tbl_users (Backendless)
    Verifica que todos los datos estén presentes y que el usuario no exista ya
    """
    data = request.get_json()

    # ✅ Check required fields
    required_fields = ["email", "password", "username"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    email = data["email"]

    # ✅ Check if user already exists
    query_url = f"{BASE_URL}?where=email='{email}'"
    response = requests.get(query_url, headers=HEADERS)
    if response.status_code != 200:
        return jsonify({"error": "Error querying the database"}), response.status_code

    existing_users = response.json()
    if existing_users:
        return jsonify({"error": "User with this email already exists"}), 409

    # ✅ Add timestamps
    data["created_at"] = datetime.now().isoformat()
    data["last_login"] = None

    # ✅ Create user in Backendless
    create_response = requests.post(BASE_URL, json=data, headers=HEADERS)

    if create_response.status_code not in [200, 201]:
        return jsonify({"error": "Failed to create user"}), create_response.status_code

    return jsonify({
        "message": "User created successfully",
        "user": create_response.json()
    }), 201

# ==============================
# EJECUCIÓN LOCAL
# ==============================

if __name__ == '__main__':
    app.run(debug=True)