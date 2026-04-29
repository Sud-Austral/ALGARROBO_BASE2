"""
Decoradores de autenticación y autorización para rutas Flask.
"""
from functools import wraps
from flask import request, jsonify
from utils.auth_utils import validate_session
from core.database import get_db_connection, release_db_connection
from core.config import logger


def _extract_token():
    """Extrae el token JWT del encabezado Authorization o query string."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()
    if request.args.get("token"):
        return request.args.get("token")
    if auth:
        return auth.strip()
    return None


def session_required(f):
    """Decorador que requiere un token JWT válido."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({}), 200

        token = _extract_token()
        if not token:
            return jsonify({"message": "Token requerido"}), 401

        user_id = validate_session(token)
        if user_id is None:
            return jsonify({"message": "Sesión inválida o expirada"}), 401

        return f(user_id, *args, **kwargs)
    return decorated


def admin_required(f):
    """
    Decorador que requiere autenticación Y nivel_acceso == 10 (admin_general exclusivo).
    SEGURIDAD [A2-3.2]: Se corrigió de ">= 10" a "== 10" para que admin_proyectos (11)
    NO herede permisos de administración del sistema (gestión de usuarios, roles, etc.).
    Aplica separación de funciones entre admin_general y admin_proyectos.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({}), 200

        token = _extract_token()
        if not token:
            return jsonify({"message": "Token requerido"}), 401

        user_id = validate_session(token)
        if user_id is None:
            return jsonify({"message": "Sesión inválida o expirada"}), 401

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT nivel_acceso FROM users WHERE user_id = %s AND activo = TRUE",
                    (user_id,)
                )
                row = cur.fetchone()
                # SEGURIDAD [A2-3.2]: Exactamente nivel 10 (admin_general).
                # nivel 11 (admin_proyectos) no tiene acceso a administración del sistema.
                if not row or row[0] != 10:
                    return jsonify({
                        "message": "No autorizado. Esta operación requiere nivel admin_general (10)."
                    }), 403
        finally:
            release_db_connection(conn)

        return f(user_id, *args, **kwargs)
    return decorated


def role_required(*allowed_levels):
    """
    Decorador parametrizable para control de acceso granular por nivel.
    SEGURIDAD [A2-3.2]: Implementa el principio de menor privilegio permitiendo
    definir exactamente qué niveles pueden ejecutar cada endpoint.

    Uso:
        @role_required(10)        # solo admin_general
        @role_required(10, 11)    # admin_general y admin_proyectos
        @role_required(10, 11, 3) # más director_obras

    Niveles definidos en el sistema:
        10 = admin_general
        11 = admin_proyectos
         3 = director_obras
         1 = funcionario
         0 = vecino (app móvil)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.method == 'OPTIONS':
                return jsonify({}), 200

            token = _extract_token()
            if not token:
                return jsonify({"message": "Token requerido"}), 401

            user_id = validate_session(token)
            if user_id is None:
                return jsonify({"message": "Sesión inválida o expirada"}), 401

            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT nivel_acceso FROM users WHERE user_id = %s AND activo = TRUE",
                        (user_id,)
                    )
                    row = cur.fetchone()
                    if not row or row[0] not in allowed_levels:
                        return jsonify({
                            "message": f"No autorizado. Roles permitidos: {list(allowed_levels)}"
                        }), 403
            finally:
                release_db_connection(conn)

            return f(user_id, *args, **kwargs)
        return decorated
    return decorator
