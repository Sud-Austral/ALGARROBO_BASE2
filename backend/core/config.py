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
# SEGURIDAD [A2-3.1]: Sin fallback con valor público. El sistema falla explícitamente
# si JWT_SECRET_KEY no está configurada, evitando que se use un secreto conocido en producción.
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET:
    raise ValueError(
        "JWT_SECRET_KEY no está configurada. "
        "Defina esta variable de entorno antes de iniciar la aplicación. "
        "Nunca use valores por defecto para secretos criptográficos en producción."
    )

# ─── Base de Datos ─────────────────────────────────────────────
# SEGURIDAD [A2-3.1]: Sin fallback con credenciales hardcodeadas.
# Falla explícita si DATABASE_URL no está definida.
DB_CONNECTION_STRING = os.getenv("DATABASE_URL")
if not DB_CONNECTION_STRING:
    raise ValueError(
        "DATABASE_URL no está configurada. "
        "Defina esta variable de entorno antes de iniciar la aplicación."
    )

# ─── Servidor ──────────────────────────────────────────────────
APP_HOST = os.getenv("APP_HOST", "algarrobobase2-production-4ab9.up.railway.app")
APP_PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")

# ─── CORS ──────────────────────────────────────────────────────
# SEGURIDAD [A2-3.4]: ALLOWED_ORIGINS es obligatorio en producción.
# En desarrollo se permite fallback a lista de localhost.
# Elimina el wildcard "*" como valor posible.
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_raw:
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]
elif FLASK_ENV == "production":
    raise ValueError(
        "ALLOWED_ORIGINS no está configurada en entorno de producción. "
        "Defina la lista de orígenes permitidos separada por comas."
    )
else:
    # Solo para entorno de desarrollo local — no usar en producción
    ALLOWED_ORIGINS = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5501",
        "http://127.0.0.1:5501",
        "http://localhost:5505",
        "http://127.0.0.1:5505",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    logging.getLogger("municipal_api").warning(
        "ALLOWED_ORIGINS no definida — usando lista de desarrollo local. "
        "Defina ALLOWED_ORIGINS en producción."
    )

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
