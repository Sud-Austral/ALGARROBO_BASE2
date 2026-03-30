# Propuesta de Remediación Técnica – Auditoría Geoportal Municipal

Esta propuesta aborda sistemáticamente cada observación identificada en el informe de auditoría (`INSUMO/revision.md`), proporcionando una solución técnica basada en las mejores prácticas de seguridad, arquitectura y gobernanza de datos.

---

## 3. Seguridad y Control de Acceso

### 3.1 Control de Acceso (Rutas)
**Solución:** Implementar un middleware de autorización en el back-end (`Flask`) que verifique el rol del usuario contra una lista permitida antes de procesar cualquier solicitud sensible.  
- **Código:** Crear un decorador `@roles_required(['admin', 'secplac'])` que se aplicará a todas las rutas de `/api/`.
- **Frontend:** Modificar `router.js` para interceptar cambios de ruta y redirigir si el token no posee los permisos necesarios decodificados en el `claims` del JWT.

### 3.2 Principio de Menor Privilegio
**Solución:** Reestructurar el modelo de datos de `users` para que el campo `nivel_acceso` sea granular (ej. 1: Lectura, 2: Edición, 3: Admin).  
- **Código:** Ajustar `app21.py` para que, en la creación de usuarios, el valor por defecto sea el de menor privilegio (Lectura).
- **Frontend:** Ocultar elementos de la UI basándose en roles reales devueltos por la API, no en lógicas de fallback de `layout.js`.

### 3.3 Configuración Permisiva de CORS
**Solución:** Restringir el acceso cruzado únicamente a dominios de confianza.  
- **Código:** Cambiar `CORS(app)` por `CORS(app, resources={r"/api/*": {"origins": [os.getenv("ALLOWED_ORIGINS")]}})` en `app21.py:49`.

### 3.4 Rutas API sin uso (Shadow APIs)
**Solución:** Auditar y consolidar los archivos `app21.py` y `neon.py`.  
- **Acción:** Eliminar endpoints duplicados como `login2` y cualquier ruta que no sea invocada por el frontend actual, reduciendo la superficie de ataque.

### 3.5 Asignación Insegura por Defecto
**Solución:** Eliminar la asignación de `'admin_general'` en `layout.js:34` cuando no hay datos de rol.  
- **Código:** El sistema debe fallar de forma segura (cerrar sesión o restringir toda funcionalidad) si los datos del usuario son incompletos.

---

## 4. Resultados de Análisis Estático (SAST)

### 4.1 Inyección SQL
**Solución:** Eliminar cualquier construcción de consultas dinámicas mediante f-strings o concatenación.  
- **Código:** Asegurar que el 100% de las consultas utilicen marcadores de posición `%s` y pasar los datos como tuplas: `cur.execute("UPDATE projects SET status=%s", (new_status,))`.

### 4.2 XSS (Cross-Site Scripting)
**Solución:** Migrar de `.innerHTML` al uso de métodos seguros.  
- **Código:** Reemplazar `.innerHTML` por `.textContent` para datos de texto o utilizar una librería de sanitización como `DOMPurify` para contenido HTML controlado.

### 4.3 Integridad de Dependencias (SRI)
**Solución:** Implementar Subresource Integrity (SRI) en todas las librerías externas.  
- **Código:** Incluir el atributo `integrity` y `crossorigin` en todas las etiquetas `<script>` y `<link>` que apunten a CDNs en los archivos `.html`.

---

## 5. Infraestructura y Gobernanza de Datos

### 5.1 Connection Pool
**Solución:** Robustecer la gestión de conexiones a NeonDB.  
- **Código:** Añadir un `validation_query="SELECT 1"` al pool para descartar conexiones inactivas y configurar un `max_overflow` adecuado para picos de tráfico.

### 5.2 Seguridad en IA (Chatbot)
**Solución:** Centralizar las llamadas a la IA en el back-end.  
- **Código:** Crear un proxy en `Flask` que reciba la consulta, le añada la API Key (almacenada en `.env`) y haga la petición al proveedor externo, devolviendo solo la respuesta al cliente.

### 5.3 Filtración de Credenciales
**Solución:** Saneamiento profundo del repositorio.  
- **Acción:** Mover `.env` y archivos de conexión a `.gitignore`. Rotar inmediatamente todas las claves expuestas (`DATABASE_URL`, `BREVO_SMTP_KEY`).

### 5.4 Transaccionalidad (Operaciones Atómicas)
**Solución:** Envolver procesos fragmentados en bloques `TRY/EXCEPT` con transacciones de base de datos (`Commit` / `Rollback`).

### 5.5 Manejo de Sesiones (Persistencia)
**Solución:** Migrar de sesiones volátiles en memoria a un almacenamiento persistente.  
- **Código:** Configurar `Flask-Session` con `Redis` o una tabla `sessions` en PostgreSQL para que las sesiones no se pierdan al reiniciar el contenedor o el servidor.

---

## 6. Higiene del Repositorio y Deuda Técnica

### 6.1 Archivos Residuales
**Acción:** Eliminar los scripts `test_script_0.js` a `test_script_9.js`, `notebook/` y archivos `.env` redundantes.

### 6.2 Hardcoding de IP
**Solución:** Migrar direcciones IP a variables de entorno.  
- **Código:** Reemplazar `http://186.67.61.251:8000` por una variable `API_URL` gestionada centralizadamente.

### 6.3 Sobrescritura de Contraseñas
**Solución:** Validar la entrada de contraseñas en el backend.  
- **Código:** En `update_user`, ignorar el campo si está vacío en lugar de generar un nuevo hash para una cadena vacía.

### 6.4 Manejo de Errores y Exposición de Datos
**Solución:** Captura genérica de errores en producción.  
- **Código:** Configurar el error handler global para registrar el traceback detallado interno, pero devolver al usuario un código de error y un mensaje amigable (ej. "An internal error occurred").

---

## 7. Documentación y Otros

- **JWT:** Implementar `flask-jwt-extended` para cumplir con la arquitectura declarada en la documentación técnica.
- **Mobile UI:** Refactorizar el menú lateral y tablas usando clases responsivas de CSS/Tailwind para asegurar operatividad en dispositivos móviles.
- **Scope:** Evaluar y podar módulos no solicitados para reducir el mantenimiento y la superficie de ataque del sistema.
