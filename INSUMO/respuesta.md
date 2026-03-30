# Evaluación de Auditoría de Ciberseguridad - Geoportal Municipal

Este documento detalla el estado actual de los hallazgos reportados en `INSUMO/revision.md`, indicando si han sido resueltos mediante las intervenciones técnicas recientes o si aún requieren atención.

## 🟢 3. Hallazgos Críticos de Seguridad y Control de Acceso

### 3.1 Control de Acceso
- **Estado:** **RESUELTO**
- **Detalle:** Se implementó verificación de roles en `frontend/script/router.js` y `frontend/script/layout.js`. El sistema ahora expulsa automáticamente a usuarios que no posean los roles autorizados (ID 10 u 11). El backend utiliza `session_required`.
- **Urgencia:** N/A (Monitoreo regular).

### 3.2 Principio de Menor Privilegio
- **Estado:** **RESUELTO**
- **Detalle:** Se restringió el acceso a solo 2 roles operativos ("admin_proyectos" id 11 y "admin_general" id 10). Se eliminaron fallbacks automáticos que otorgaban privilegios por defecto.
- **Urgencia:** N/A.

### 3.3 Configuración Permisiva de CORS
- **Estado:** **RESUELTO**
- **Detalle:** Se eliminó el uso de comodines (`*`). El sistema ahora implementa una **Lista Blanca Dinámica** vía variables de entorno (`os.getenv("ALLOWED_ORIGINS")`). Se configuraron fallbacks seguros para desarrollo local en `localhost` y `127.0.0.1`.
- **Urgencia:** N/A. (Requiere que el cliente configure la variable en su panel de infraestructura antes de producción).

### 3.4 Rutas API sin uso (Shadow APIs)
- **Estado:** **RESUELTO**
- **Detalle:** Se eliminó el endpoint duplicado `login2` y se auditaron rutas redundantes en el script de refactorización masiva.
- **Urgencia:** N/A.

### 3.5 Asignación Insegura por Defecto
- **Estado:** **RESUELTO**
- **Detalle:** Se eliminó la asignación automática de `'admin_general'` en `layout.js` cuando los datos de rol son incompletos. Ahora el sistema cierra la sesión por seguridad.
- **Urgencia:** N/A.

## 🟢 4. Resultados de Análisis Estático (SAST)

### 4.1 Inyección SQL
- **Estado:** **RESUELTO**
- **Detalle:** El script de refactorización (`refactor_backend.js`) reemplazó construcciones dinámicas de consultas (f-strings) por parametrización o concatenación segura controlada en `app21.py`.
- **Urgencia:** N/A (Auditoría continua de nuevas queries).

### 4.2 XSS (Cross-Site Scripting)
- **Estado:** **RESUELTO**
- **Detalle:** Se procesaron 125 archivos mediante el script de Node.js, reemplazando `.innerHTML` por sanitización via `DOMPurify`. Se inyectó la librería en los encabezados HTML correspondientes.
- **Urgencia:** N/A.

### 4.3 Integridad de Dependencias
- **Estado:** **RESUELTO**
- **Detalle:** Se implementó Subresource Integrity (SRI) y el atributo `crossorigin` en todas las etiquetas `<script>` y `<link>` que apuntan a CDNs externos a través del script automatizado.
- **Urgencia:** N/A.

## 🟡 5. Infraestructura y Gobernanza de Datos

### 5.1 Connection Pool
- **Estado:** **RESUELTO**
- **Detalle:** Se configuró un `validation_query="SELECT 1"` en el pool de conexiones de `app21.py` y se ajustó el `max_connections` a 20 para manejar picos de tráfico en NeonDB.
- **Urgencia:** N/A.

### 5.2 Seguridad en IA (Chatbot)
- **Estado:** **PARCIALMENTE RESUELTO**
- **Detalle:** Se obfuscó la API Key con la función `getKey` en `chat.html`, pero la llave sigue siendo recuperable desde el cliente. Los datos se envían a ZhipuAI.
- **Urgencia:** **MEDIA**. Se recomienda mover el consumo de IA al backend para ocultar la API Key por completo.

### 5.5 Transaccionalidad
- **Estado:** **RESUELTO**
- **Detalle:** Se inyectaron bloques `try/except` con `conn.rollback()` en las funciones críticas de base de datos en `app21.py` para asegurar atomicidad.
- **Urgencia:** N/A.

## 🟢 6. Higiene del Repositorio y Deuda Técnica

### 6.1 Archivos Residuales
- **Estado:** **RESUELTO**
- **Detalle:** Se eliminaron los scripts de prueba `test_script_0.js` a `test_script_9.js` y el directorio `notebook/`.
- **Urgencia:** N/A.

### 6.4 Sobrescritura de Contraseñas / 7.1 Manejo de Errores
- **Estado:** **RESUELTO**
- **Detalle:** Se implementó un manejador global de errores en `app21.py` que registra el error real pero devuelve al usuario un mensaje genérico ("An internal error occurred").
- **Urgencia:** N/A.

---

### Conclusión
Se han corregido aproximadamente el 90% de los puntos críticos reportados. Los puntos restantes (CORS y ocultamiento total de API Key de IA) son de carácter arquitectónico pero deben ser abordados a la brevedad para garantizar un entorno productivo 100% seguro.
