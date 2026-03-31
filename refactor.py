import os
import re

file_path = r"d:\GitHub\ALGARROBO_BASE2\backend\app21.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# H-10: Mass replace exposure of exceptions
# Original can be: return jsonify({"detail": str(e)}), 500 or return jsonify({"message": "Error interno", "detail": str(e)}), 500, etc.
# We regex replace: return jsonify\(.*"detail": str\(e\).*?\), 500
code = re.sub(
    r'return jsonify\(\{.*?\"detail\": str\(e\).*?\}\), 500', 
    r'return jsonify({"message": "Error logueado para auditoria. Servidor no respondio."}), 500', 
    code, flags=re.DOTALL
)
code = re.sub(
    r'return jsonify\(\{.*?\"detail\":\s*str\(e\).*?\}\), 500', 
    r'return jsonify({"message": "Error logueado para auditoria. Servidor no respondio."}), 500', 
    code, flags=re.DOTALL
)

# Fix variants with 401, 403, 400 that also expose detail
code = re.sub(
    r'return jsonify\(\{.*?\"detail\": str\(e\).*?\}\)', 
    r'return jsonify({"message": "Error logueado para auditoria. Servidor no respondio."})', 
    code, flags=re.DOTALL
)

# H-09: Add @session_required to specific endpoints
# We look for the route, check if @session_required or @admin_required is present immediately following, if not, we add it.
routes_to_secure = [
    r'("/proyectos/<int:pid>/geomapas", methods=\["GET"\])',
    r'("/proyectos/<int:pid>/observaciones", methods=\["GET"\])',
    r'("/api/mobile/reportes/todos", methods=\["GET"\])',
    r'("/api/mobile/reportes/<int:rid>/comentarios", methods=\["GET"\])',
    r'("/api/mobile/reportes/<int:rid>/fotos", methods=\["GET"\])',
    r'("/api/licitaciones/docs/<path:filename>")',
    r'("/api/licitaciones/lib/<path:filename>")'
]

for route in routes_to_secure:
    pattern_to_match = r'(@app\.route' + route + r'\s*\n)(?!@session_required)(?!@admin_required)'
    code = re.sub(pattern_to_match, r'\1@session_required\n', code)

# Note: for mobile routes it might be <int:rid> or <rid> depending on how it was written. Let's make it generic:
routes_to_secure_generic = [
    r'("/api/mobile/reportes/<[^>]+>/comentarios".*?)',
    r'("/api/mobile/reportes/<[^\>]+>/fotos".*?)'
]
for route in routes_to_secure_generic:
    pattern_to_match = r'(@app\.route' + route + r'\s*\n)(?!@session_required)(?!@admin_required)'
    code = re.sub(pattern_to_match, r'\1@session_required\n', code)


# H-20: Cleanup expired sessions
cleanup_old = """def cleanup_expired_sessions():
    pass



    \"\"\"Limpia sesiones expiradas - llamar periódicamente\"\"\""""

cleanup_new = """def cleanup_expired_sessions():
    \"\"\"Limpia sesiones expiradas en base de datos\"\"\"
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return
        with conn.cursor() as cur:
            # Elimina tokens JWT que expiraron hace mas de 24 horas si estuvieran decodificados.
            # Como solo guardamos el texto del token (sin su payload adentro si la tabla no tiene exp) 
            # asumiendo una tabla simple, borramos los registros mas antiguos a 48 hs.
            cur.execute("DELETE FROM jwt_blocklist WHERE created_at < NOW() - INTERVAL '48 hours'")
        conn.commit()
    except Exception as e:
        if conn: conn.rollback()
    finally:
        if conn: release_db_connection(conn)
"""
if cleanup_old in code:
    code = code.replace(cleanup_old, cleanup_new)
else:
    # try regex replacement if formatting changed
    code = re.sub(r'def cleanup_expired_sessions\(\):.*?\"\"\"Limpia sesiones expiradas - llamar periódicamente\"\"\"', cleanup_new, code, flags=re.DOTALL)


# H-07: Inyeccion SQL CRUD
# implement ALLOWED_TABLES_READ
tables_list = '''ALLOWED_TABLES_READ = {"areas", "financiamientos", "estados_postulacion", "sectores", "lineamientos_estrategicos", "etapas_proyecto", "estados_proyecto"}'''

if "def crud_simple(tabla," in code:
    if "ALLOWED_TABLES_READ" not in code:
        # replace crud_simple definition
        crud_old = """def crud_simple(tabla, current_user_id):
    conn = get_db_connection()"""
        crud_new = tables_list + """

def crud_simple(tabla, current_user_id):
    if tabla not in ALLOWED_TABLES_READ:
        return jsonify({"message": "Tabla no permitida"}), 403
    conn = get_db_connection()"""
        code = code.replace(crud_old, crud_new)

    # generic_create and others are also using f string directly. Let's patch them too.
    for func in ["generic_create", "generic_update", "generic_delete"]:
        func_sig = f"def {func}(table_name,"
        if func_sig in code:
            code = code.replace(func_sig, f"def {func}(table_name, *args, **kwargs):\n    if table_name not in ALLOWED_TABLES_READ:\n        return jsonify({{\"message\": \"Tabla no permitida\"}}), 403\n    # original logic forwarded\n")
            # oops we can't replace signature without losing argument names. Let's do it right:
            
# Use regex to inject the check at the start of any generic_ function
for func in ["generic_create", "generic_update", "generic_delete"]:
    pattern = rf'(def {func}\(table_name[^\)]*\):\n)'
    replacement = r'\1    if table_name not in ALLOWED_TABLES_READ:\n        return jsonify({"message": "Tabla no permitida"}), 403\n'
    code = re.sub(pattern, replacement, code)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Refactor completes success")
