"""
Módulo de auditoría y registro de actividad.
Funciones log_control y log_auditoria centralizadas.
"""
import json as _json
from flask import request
from core.config import logger
from core.database import get_db_connection, release_db_connection


def log_control(user_id, accion, modulo='proyectos',
                entidad_tipo=None, entidad_id=None, entidad_nombre=None,
                exitoso=True, detalle=None,
                datos_antes=None, datos_despues=None):
    """
    Registra cada acción del usuario en control_actividad con contexto completo.
    Se llama desde los endpoints de API tras cada operación.
    """
    conn = None
    try:
        ip = None
        ua = None
        ep = None
        try:
            ip = request.remote_addr
            ua = request.headers.get('User-Agent', '')[:500]
            ep = request.path[:200]
        except RuntimeError:
            pass  # fuera de contexto de request (ej. triggers)

        conn = get_db_connection()
        if not conn:
            return
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO control_actividad
                    (user_id, accion, modulo,
                     entidad_tipo, entidad_id, entidad_nombre,
                     exitoso, detalle,
                     ip_origen, user_agent, endpoint,
                     datos_antes, datos_despues)
                VALUES (%s,%s,%s, %s,%s,%s, %s,%s, %s,%s,%s, %s,%s)
            """, (
                user_id, accion, modulo,
                entidad_tipo, entidad_id, entidad_nombre,
                exitoso, detalle,
                ip, ua, ep,
                _json.dumps(datos_antes, default=str) if datos_antes else None,
                _json.dumps(datos_despues, default=str) if datos_despues else None
            ))
        conn.commit()
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        logger.error(f"Error en log_control: {e}")
    finally:
        if conn:
            release_db_connection(conn)


def log_auditoria(user_id, accion, descripcion):
    """
    Registra actividad en control_actividad (único mecanismo de trazabilidad).
    SEGURIDAD [A2-5.3]: Se eliminó la escritura duplicada en la tabla legacy
    'auditoria' para evitar redundancia, bloat y desincronización.
    control_actividad es el registro oficial de auditoría del sistema.
    """
    modulo = 'auth' if any(k in accion for k in ('login', 'logout', 'password')) else \
             'usuarios' if 'user' in accion else 'proyectos'
    log_control(user_id, accion, modulo=modulo, detalle=descripcion)


# ─── Validación de archivos subidos ────────────────────────────

# SEGURIDAD [A2-3.5]: Lista blanca efectiva de extensiones permitidas para subida.
# Reemplaza la validación previa que aceptaba cualquier archivo con extensión.
UPLOAD_ALLOWED_EXTENSIONS = frozenset({
    "pdf", "doc", "docx", "xls", "xlsx",
    "png", "jpg", "jpeg", "gif",
    "txt", "csv",
})

# Mapa extensión → magic bytes para validación de contenido real del archivo
_MAGIC_BYTES: dict = {
    "pdf":  [b"%PDF"],
    "png":  [b"\x89PNG"],
    "jpg":  [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "gif":  [b"GIF87a", b"GIF89a"],
    "docx": [b"PK\x03\x04"],   # formato ZIP (docx, xlsx)
    "xlsx": [b"PK\x03\x04"],
    "xls":  [b"\xd0\xcf\x11\xe0"],  # OLE2 compound document
    "doc":  [b"\xd0\xcf\x11\xe0"],
}


def allowed_file(filename: str, file_stream=None) -> bool:
    """
    SEGURIDAD [A2-3.5]: Valida extensión contra lista blanca y opcionalmente
    verifica los magic bytes del archivo para prevenir subidas de archivos
    maliciosos renombrados con una extensión válida.

    Args:
        filename: nombre del archivo a validar
        file_stream: stream del archivo (opcional). Si se provee, se leen
                     los primeros bytes para verificar el tipo real.
    """
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in UPLOAD_ALLOWED_EXTENSIONS:
        return False

    if file_stream is not None and ext in _MAGIC_BYTES:
        header = file_stream.read(8)
        file_stream.seek(0)
        allowed_headers = _MAGIC_BYTES[ext]
        if not any(header.startswith(magic) for magic in allowed_headers):
            return False

    return True
