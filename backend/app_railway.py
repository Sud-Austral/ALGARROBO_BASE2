"""
🚀 APP_RAILWAY: Backend Modular de Algarrobo Optimizado para Railway
------------------------------------------------------------------
Optimización:
1.  Persistencia en Volumen: Las carpetas de fotos, documentos y reportes 
    apuntan ahora a /data si existe el directorio.
2.  Modularización: Carga los Blueprints del nuevo sistema (app21_modular).
3.  Seguridad: Configuración de CORS y Headers lista para nube.
4.  Gunicorn Ready: Diseñado para ejecutarse en contenedores Docker.
"""
import os
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS

# ─── Módulos Core ──────────────────────────────────────────────
from core.config import (
    logger, APP_HOST, APP_PORT, DEBUG,
    ALLOWED_ORIGINS
)
from core.database import (
    init_connection_pool, get_db_connection,
    release_db_connection, cleanup_pool
)

# ─── Blueprints ────────────────────────────────────────────────
from routes.auth_routes import auth_bp
from routes.users_routes import users_bp
from routes.proyectos_routes import proyectos_bp
from routes.licitaciones_routes import licitaciones_bp
from routes.documentos_routes import documentos_bp
from routes.calendario_routes import calendario_bp
from routes.mobile_routes import mobile_bp
from routes.control_routes import control_bp
from routes.auditoria_routes import auditoria_bp
from routes.chat_routes import chat_bp

# ═══════════════════════════════════════════════════════════════
# GESTIÓN DE ALMACENAMIENTO PERSISTENTE
# ═══════════════════════════════════════════════════════════════
# SEGURIDAD [A2-6.1]: En producción el volumen /data es obligatorio.
# El sistema falla explícitamente si no está montado, evitando que los
# documentos queden en el contenedor efímero y se pierdan al reiniciar.
PERSISTENT_DATA = "/data"
IS_RAILWAY_VOL = os.path.isdir(PERSISTENT_DATA)
_FLASK_ENV = os.getenv("FLASK_ENV", "development")

if IS_RAILWAY_VOL:
    DOCS_ROOT = os.path.join(PERSISTENT_DATA, "docs")
    FOTOS_ROOT = os.path.join(PERSISTENT_DATA, "fotos_reportes")
    REPORTS_ROOT = os.path.join(PERSISTENT_DATA, "auditoria_reportes")
elif _FLASK_ENV == "production":
    raise RuntimeError(
        "STORAGE ERROR: El volumen persistente /data no está montado. "
        "Configure el volumen en Railway antes de iniciar en producción. "
        "Los documentos NO deben almacenarse en el contenedor efímero."
    )
else:
    # Solo para desarrollo local — no usar en producción
    BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    DOCS_ROOT = os.path.join(BACKEND_DIR, "docs")
    FOTOS_ROOT = os.path.join(BACKEND_DIR, "fotos_reportes")
    REPORTS_ROOT = os.path.join(BACKEND_DIR, "auditoria_reportes")
    logger.warning("STORAGE: Usando almacenamiento local (solo desarrollo). Configure /data en producción.")

# Crear estructuras si no existen
for folder in [DOCS_ROOT, FOTOS_ROOT, REPORTS_ROOT]:
    os.makedirs(folder, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# CREAR APP
# ═══════════════════════════════════════════════════════════════
app = Flask(__name__)
# SEGURIDAD [A2-3.5]: Límite de subida parametrizado por entorno.
# Producción: 50 MB por defecto. Se puede aumentar vía MAX_UPLOAD_MB para migraciones puntuales.
_max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "50" if _FLASK_ENV == "production" else "1000"))
app.config['MAX_CONTENT_LENGTH'] = _max_upload_mb * 1024 * 1024

# CORS dinámico
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}}, supports_credentials=True)

# ─── Middleware ─────────────────────────────────────────────────
@app.before_request
def log_request_info():
    if request.path.startswith('/api') or request.path.startswith('/auth'):
        logger.info(f"REQUEST {request.method} {request.path}")

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Internal server error (RAILWAY): {e}")
    logger.error(traceback.format_exc())
    code = getattr(e, 'code', 500)
    response = jsonify({
        "error": "Internal Server Error - Railway Node",
        "code": code
    })
    response.status_code = code
    return response

# ─── Registrar Blueprints (9 módulos) ─────────────────────────
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(proyectos_bp, url_prefix='/api')
app.register_blueprint(licitaciones_bp, url_prefix='/api')
app.register_blueprint(documentos_bp, url_prefix='/api')
app.register_blueprint(calendario_bp, url_prefix='/api')
app.register_blueprint(mobile_bp, url_prefix='/api')
app.register_blueprint(control_bp, url_prefix='/api')
app.register_blueprint(auditoria_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')

# ─── COMPATIBILIDAD LEGACY ──────────────────────────────────────
@app.errorhandler(404)
def handle_404_legacy_sync(e):
    """
    Sincronización perfecta: Si una ruta no existe, verifica si existe bajo /api.
    Esto permite que el frontend legacy siga funcionando mientras se migra.
    """
    path = request.path
    if not path.startswith('/api/'):
        # Intentar ver si existe en el blueprint de proyectos (que tiene la mayoría de rutas)
        # o en otros blueprints. 
        # NOTA: Esto es una red de seguridad para la sincronización.
        api_path = f"/api{path}"
        logger.info(f"404 Detectado en {path}. Intentando redirección legacy a {api_path}")
        
        # Opcionalmente, podrías usar redirect(api_path) 
        # pero para peticiones AJAX fetch, es mejor avisar o proxear.
        # Por simplicidad y efectividad con CORS, redirigimos.
        return redirect(api_path), 307 # 307 preserva el método (POST, PUT, etc)

    return jsonify({"message": "Ruta no encontrada", "path": path}), 404

# ─── Rutas de Servicio de Archivos desde Volumen ────────────────
@app.route("/")
def home():
    return jsonify({
        "message": "SECPLAC ALGARROBO API - Railway Edition",
        "storage_mode": "Volume /data" if IS_RAILWAY_VOL else "Local Fallback",
        "status": "online"
    })

@app.route("/api/docs/<path:filename>")
def serve_docs(filename):
    return send_from_directory(DOCS_ROOT, filename)

@app.route("/fotos_reportes/<path:filename>")
def serve_photos(filename):
    return send_from_directory(FOTOS_ROOT, filename)

@app.route("/health")
def health_check():
    from core.database import connection_pool as pool
    try:
        pool_status = {
            "initialized": pool is not None and not pool.closed,
            "min_connections": pool.minconn if pool else None,
            "max_connections": pool.maxconn if pool else None,
        }
        db_status = "disconnected"
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                db_status = "connected"
                release_db_connection(conn)
        except Exception:
            db_status = "error"

        return jsonify({
            "status": "healthy" if db_status == "connected" else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": {"status": db_status},
            "storage": {"active_root": DOCS_ROOT},
            "railway_optimized": True
        }), 200 if db_status == "connected" else 503
    except Exception:
        return jsonify({"status": "unhealthy"}), 503

# ═══════════════════════════════════════════════════════════════
# INICIALIZACIÓN
# ═══════════════════════════════════════════════════════════════
logger.info(f"STORAGE: {DOCS_ROOT}")
if not init_connection_pool():
    logger.error("No se pudo inicializar el pool de conexiones al inicio")

# Para ejecución local con python directo (si existiera)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=APP_PORT, debug=DEBUG)
