"""
Configuración centralizada de la aplicación.
Carga .env, configura logging, CORS y constantes globales.
"""
import os
import logging
from dotenv import load_dotenv

# ─── Cargar .env ───────────────────────────────────────────────
load_dotenv()

# ─── JWT ───────────────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "9a15f0d2c0b4e3e3b3c3d3e3f3g3h3i3j3k3l3m3n3o3p3q3r3s3t3u3v3w3x3y3z")
if not JWT_SECRET:
    JWT_SECRET = "fallback-secret-for-demo-123456"
    logging.getLogger(__name__).warning("Usando JWT_SECRET de contingencia.")

# ─── Base de Datos ─────────────────────────────────────────────
DB_CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql://postgres:RPyLEhcXstDJBrMoVMMgzkpbMPyZLIHl@crossover.proxy.rlwy.net:55112/neondb")
if not DB_CONNECTION_STRING:
    raise ValueError("No DATABASE_URL set for Flask application")

# ─── Servidor ──────────────────────────────────────────────────
# APP_HOST se usa de forma interna y externa. En Railway, las rutas públicas ya no llevan puerto, es HTTPS (443).
APP_HOST = os.getenv("APP_HOST", "algarrobobase2-production-4ab9.up.railway.app")
# En tu backend, este puerto será solo interno. Gunicorn se enlazará usando os.getenv("PORT")
APP_PORT = int(os.getenv("PORT", 8000))
# SEGURIDAD [H-06]: Debug OFF por defecto en producción
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")

# ─── CORS ──────────────────────────────────────────────────────
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_raw:
    # Procesar lista separada por comas
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_raw.split(",")]
else:
    # SEGURIDAD [H-03]: Fallback robusto para desarrollo y producción
    ALLOWED_ORIGINS = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5501",
        "http://127.0.0.1:5501",
        "http://localhost:5505",
        "http://127.0.0.1:5505",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://algarrobobase2-production-4ab9.up.railway.app",
        "https://algarrobobase2.up.railway.app"
    ]
    logging.getLogger("municipal_api").info(
        f"ALLOWED_ORIGINS usando lista blanca por defecto: {ALLOWED_ORIGINS}"
    )

# ─── Sesiones ──────────────────────────────────────────────────
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", 24))

# ─── Archivos ─────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Esto apunta a backend/ ya que config.py está en backend/core/
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BACKEND_DIR)  # subimos de core/ a backend/

DOCS_FOLDER = os.path.join(BACKEND_DIR, "docs")
AUDIT_OUT_DIR = os.getenv(
    "AUDIT_OUT_DIR",
    os.path.join(BACKEND_DIR, "auditoria_reportes")
)

# Si estamos en Railway con volumen montado
if os.path.exists("/data") and os.path.isdir("/data"):
    DOCS_FOLDER = "/data/docs"
    AUDIT_OUT_DIR = "/data/auditoria_reportes"

os.makedirs(DOCS_FOLDER, exist_ok=True)
os.makedirs(AUDIT_OUT_DIR, exist_ok=True)

# Rutas finales (unificadas)
FOTOS_OUT_DIR = AUDIT_OUT_DIR.replace("auditoria_reportes", "fotos_reportes")
FOTOS_DIR = FOTOS_OUT_DIR  # Alias para compatibilidad con rutas móviles

os.makedirs(FOTOS_OUT_DIR, exist_ok=True)
os.makedirs(FOTOS_DIR, exist_ok=True)

# ─── Extensiones de archivo para extracción de texto (OCR/parse) ─
# Solo se usa para decidir si se intenta extraer texto del documento.
# La subida de archivos no está restringida por extensión.
ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "xls", "xlsx",
    "png", "jpg", "jpeg",
}

# ─── Tablas permitidas para CRUD genérico ──────────────────────
# SEGURIDAD [H-07]: Lista blanca de tablas para evitar SQL injection
ALLOWED_TABLES_READ = frozenset({
    "areas",
    "financiamientos",
    "estados_postulacion",
    "sectores",
    "lineamientos_estrategicos",
    "etapas_proyecto",
    "estados_proyecto",
})

# ─── Logging ───────────────────────────────────────────────────
def setup_logging():
    """Configura logging centralizado."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("municipal_api.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("municipal_api")


logger = setup_logging()
