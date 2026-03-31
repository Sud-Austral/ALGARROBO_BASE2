# ⚙️ Manual de Instalación y Operaciones (Despliegue)

Este manual dicta el procedimiento metodológico estricto sobre cómo levantar localmente el sistema completo **ALGARROBO_BASE2** y cómo orquestar su despliegue dentro del perímetro de operaciones en la nube (Railway).

---

## 📋 1. Requisitos Fundamentales del Sistema

Para el correcto funcionamiento del core necesitas de:

- **Intérprete Core**: `Python 3.11+` (Se recomienda 3.11.7 para consistencia con el contenedor).
- **Gestor Dependencias**: `pip` (v23.0+).
- **Entorno Binario de Procesamiento (Indispensable para auditoría)**: 
    - `antiword`: Utilizado para la extracción de texto de archivos `.doc` heredados.
    - `tesseract-ocr`: Motor de reconocimiento óptico de caracteres.
    - `tesseract-ocr-spa`: Paquete de idioma español para Tesseract.
- **Control de Versiones**: `Git`
- **Base de Datos**: PostgreSQL 15 o superior.

> [!NOTE]
> Si trabajas desde un servidor Windows en entorno local puro, las librerías binarias como `antiword` y `tesseract` deben instalarse mediante ejecutables específicos o `msys2`. En Linux/Docker, estas se instalan vía `apt-get`.

---

## 💻 2. Instalación en Entorno Local (Desarrollo)

### Clonar el Proyecto y Preparar Virtual Environment
```bash
git clone https://github.com/geoportalalgarrobo/ALGARROBO_BASE2.git
cd ALGARROBO_BASE2

# Crear ambiente virtual para aislar dependencias
python -m venv venv

# Activación - Windows
venv\Scripts\activate
# Activación - MacOS/Linux
source venv/bin/activate
```

### Instalar el Motor de Dependencias
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### Inicializar el Backend Server
```bash
# Estando dentro de la carpeta /backend
# Modo development (con recarga automática)
python app21.py
```

### Iniciar el Frontend Estático 
*(En otra terminal, corre cualquier servidor estático apuntando a la raíz del repositorio)*
```bash
# Opción A: Usando npx (Node.js)
npx http-server ./ -p 5504 --cors

# Opción B: Usando python
python -m http.server 5504
```

*Visita `http://localhost:5504` para acceder a la interfaz.*

---

## 🔑 3. Matriz de Variables de Entorno (`.env`)

Crea un archivo `.env` en la carpeta `backend/`. El sistema fallará al iniciar si faltan variables críticas.

| Variable | Descripción | Ejemplo / Valor |
| :--- | :--- | :--- |
| `DATABASE_URL` | String de conexión oficial. | `postgresql://user:pass@host/db` |
| `JWT_SECRET_KEY` | Clave maestra para tokens. | `un-hash-muy-largo-y-seguro` |
| `ALLOWED_ORIGINS` | Orígenes permitidos (CORS). | `https://portal.algarrobo.cl` |
| `BREVO_SMTP_KEY` | API Key de correos masivos. | `xkeysib-xxxx-xxxx` |
| `PORT` | Puerto de escucha (Railway lo asigna). | `8080` |
| `AUDIT_DATA_PATH` | Ruta para volúmenes persistentes. | `/data` |

---

## ☁️ 4. Despliegue en Railway (Producción)

Railway es la plataforma preferida por su soporte nativo de Docker y persistencia.

### Configuración del Dockerfile Multi-Stage
El proyecto incluye un `Dockerfile` optimizado:
1.  **Stage 1 (Build):** Instala compiladores y dependencias de Python.
2.  **Stage 2 (Runtime):** Instala solo los binarios necesarios (`tesseract`, `antiword`) y copia las librerías de Python ya compiladas, reduciendo el tamaño de la imagen en un 60%.

### Pasos para el Deploy:
1.  **Montaje de Volumen:**
    *   Ve a la pestaña **Settings** en Railway.
    *   En la sección **Volumes**, crea uno nuevo.
    *   **Mount Path**: `/data`. Esto es CRÍTICO para que los documentos subidos y reportes no se borren en cada reinicio.
2.  **Variables de Entorno:**
    *   Carga la matriz del punto (3) en la pestaña **Variables**.
3.  **Configuración de Red:**
    *   Genera un dominio público (`.up.railway.app`) en Settings > Domains.

---

## 🛠️ 5. Guía de Resolución de Problemas (Troubleshooting)

### Error: "Library not found: antiword / tesseract"
*   **Causa:** El backend intenta procesar un documento pero los binarios no están en el PATH.
*   **Solución:** En local, asegúrate de tener instalados los programas. En producción, verifica que el `Dockerfile` haya terminado la fase de instalación correctamente.

### Error: "CORS Policy blocked request"
*   **Causa:** El frontend y backend están en dominios distintos y `ALLOWED_ORIGINS` no coincide.
*   **Solución:** Verifica que el valor en `.env` incluya exactamente el protocolo y puerto (ej. `http://localhost:5504`).

### Error: "502 Bad Gateway" en Railway
*   **Causa:** El proceso Gunicorn tardó más de 30s en iniciar o crasheó por memoria.
*   **Solución:** Aumenta el `timeout` en el comando de inicio o revisa el `ConnectionPool` en los logs (buscando "Too many connections").

### Problemas de Base de Datos (PostgreSQL)
*   **Síntoma:** "Connection Timeout".
*   **Solución:** Verifica que el backend tenga acceso al origen de la base de datos y que las credenciales sean correctas. El pool de conexiones intentará reconectar automáticamente si hay una desconexión temporal.

---

## 📈 6. Mejores Prácticas de Operación
*   **Respaldos:** Se recomienda realizar respaldos periódicos del esquema y data (`pg_dump`) mensualmente.
*   **Logs:** Utiliza `railway logs -f` para monitorear intentos de login fallidos o errores de procesamiento de PDF en tiempo real.
*   **Seguridad:** Rota la `JWT_SECRET_KEY` cada 6 meses. Esto forzará que todos los usuarios vuelvan a loguearse pero invalidará cualquier token potencialmente comprometido.
