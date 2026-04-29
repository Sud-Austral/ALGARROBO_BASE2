"""
Configuración centralizada de la aplicación.
Carga .env, configura logging, CORS y constantes globales.
"""
import os
import logging
from dotenv import load_dotenv

# ─── Cargar .env ───────────────────────────────────────────────
load_dotenv()

# ─── Entorno ───────────────────────────────────────────────────
FLASK_ENV = os.getenv("FLASK_ENV", "development")

# ─── JWT ───────────────────────────────────────────────────────
# SEGURIDAD: Se usa valor por defecto para asegurar el inicio en Railway (solicitado por usuario).
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "9a15f0d2c0b4e3e3b3c3d3e3f3g3h3i3j3k3l3m3n3o3p3q3r3s3t3u3v3w3x3y3z")

# ─── Base de Datos ─────────────────────────────────────────────
# SEGURIDAD: Se usa valor por defecto para asegurar el inicio en Railway (solicitado por usuario).
DB_CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql://postgres:RPyLEhcXstDJBrMoVMMgzkpbMPyZLIHl@crossover.proxy.rlwy.net:55112/neondb")

# ─── Servidor ──────────────────────────────────────────────────
APP_HOST = os.getenv("APP_HOST", "algarrobobase2-production-4ab9.up.railway.app")
APP_PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")

# ─── CORS ──────────────────────────────────────────────────────
# SEGURIDAD: Se permite wildcard o lista hardcodeada por solicitud del usuario.
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_raw == "*":
    ALLOWED_ORIGINS = ["*"]
elif allowed_origins_raw:
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]
else:
    ALLOWED_ORIGINS = ["*"]

# ─── Sesiones ──────────────────────────────────────────────────
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", 24))

# ─── Archivos ─────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
