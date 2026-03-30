# Propuesta de Solución y Análisis de Complejidad - Auditoría Geoportal

Basado en el Informe Técnico de Auditoría, a continuación se presenta un estimado de la complejidad y la solución técnica propuesta para cada uno de los hallazgos identificados en el código fuente.

**Análisis General de Complejidad:**
Solucionar todos los problemas requiere un esfuerzo **Medio-Alto**, principalmente debido a los hallazgos H-05 (RBAC), H-15 (Blocklist de JWT), y H-19 (Migración a Cookies HttpOnly). Sin embargo, casi todos los hallazgos críticos (H-01 a H-04, H-06) son de complejidad **Baja** y pueden resolverse rápidamente, permitiendo levantar los bloqueos operativos en corto tiempo.


## Hallazgos Bloqueantes y Críticos

### H-01 — Credenciales de Base de Datos en Repositorio Público
- **Complejidad:** Baja (Técnica) / Alta (Operacional)
- **Solución:** Eliminar `backend/debug_users.py`. Utilizar `git filter-repo` para purgar el archivo del historial de Git. Rotar inmediatamente la contraseña en el panel de Neon.tech.

### H-02 — Endpoints de Migración de Volumen Sin Autenticación
- **Complejidad:** Baja
- **Solución:** Agregar el decorador `@session_required` a las 3 rutas en `app21.py` (`/api/volume/gui`, `/api/volume/export`, `/api/volume/import`). Adicionalmente, verificar que `current_user['nivel_acceso'] >= 10`.



---

## Hallazgos de Prioridad Alta

### H-06 — Endpoints de Datos Sensibles Sin Autenticación
- **Complejidad:** Baja
- **Solución:** Restablecer el decorador `@session_required` en las rutas mencionadas (geomapas, documentos, reportes ciudadanos, licitaciones).

### H-07 — Inyección SQL Vía Mass Assignment
- **Complejidad:** Media
- **Solución:** En las funciones `create_proyecto` y `update_proyecto`, definir un `ALLOWED_FIELDS = {'nombre', 'monto', 'descripcion', ...}`. Iterar y construir el SQL únicamente intersectando las llaves del request con este diccionario de lista blanca.

### H-08 — Enumeración de Usuarios en `/auth/login`
- **Complejidad:** Baja
- **Solución:** Unificar las respuestas 404, 403 y 401 del endpoint de login a retornar genéricamente `{"message": "Credenciales inválidas"}` con código 401.

### H-09 — IP Hardcodeada (186.67.61.251)
- **Complejidad:** Media (por la cantidad de modificaciones)
- **Solución:** Hacer un buscar y reemplazar masivo (Grep/Sed o script automatizado) a través del repositorio reemplazando la IP por llamadas relativas (ej: `/api/...`) o utilizando una variable inyectada globalmente mediante `window.API_BASE_URL`.


### H-11 — Ausencia de SRI en CDN
- **Complejidad:** Baja
- **Solución:** Obtener los hashes SHA384 de las dependencias usadas (Tailwind, FontAwesome, Chart.js) y agregar el parámetro `integrity="sha384-..."` y `crossorigin="anonymous"` en los `<script>` y `<link>` base del proyecto.

---

## Hallazgos de Prioridad Media y Baja



### H-13 — Decorador Comentado (`listar_documentos`)
- **Complejidad:** Muy Baja
- **Solución:** Descomentar `#@session_required` y ajustar la firma de la función.

### H-14 — Logs Sensibles
- **Complejidad:** Baja
- **Solución:** Cambiar el log de `"User {u['email']}"` a `"User ID: {u['user_id']}"`.

### H-15 — Logout no invalida token JWT
- **Complejidad:** Alta
- **Solución:** Crear una tabla `jwt_blocklist` en base de datos. Al hacer logout, guardar el `jti` del token emitido. Modificar el middleware para rechazar cualquier token registrado en esta tabla.

### H-16 — Concatenación de nombres de tabla
- **Complejidad:** Media
- **Solución:** Establecer un diccionario o set con `ALLOWED_TABLES` validadas estáticamente antes de permitir la inserción del nombre de la tabla en el string de la consulta.

### H-17 & H-18 — Archivos de Prueba y Deprecados
- **Complejidad:** Baja
- **Solución:** Eliminar scripts como `debug_users.py`, `test_db.py`, `test_bcrypt.py` y vistas terminadas en `_deprecated.html`.

### H-19 — JWT en LocalStorage (XSS Risk)
- **Complejidad:** Alta
- **Solución:** Modificar `login()` en backend para retornar el token mediante `Set-Cookie: authToken=...; HttpOnly; Secure; SameSite=Strict`. Ajustar el frontend para remover las referencias a `localStorage.getItem('token')` y procesar todo usando requests autenticados cross-origen con credenciales incluidas.

### Observaciones Finales (H-20 a H-24)
- Estas abarcan decisiones de diseño (responsive), ajustes SQL simples (`ORDER BY`), y alineación organizativa con respecto al alcance. Son abordables a largo plazo pero no representan un riesgo cibernético inmediato agudo como los primeros 8 puntos.
