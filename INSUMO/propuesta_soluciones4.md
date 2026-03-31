# Matriz de Correcciones y Mitigaciones - Geoportal Municipal (Veredicto: NO APTO PARA PRODUCCIÓN)

Basado en la auditoría exhaustiva del archivo `revision.md` cruzado minuciosamente con el código actual (`app21.py`, `frontend/`, `layout.js`, etc.), presento el plan de acción final categorizado. El objetivo de este documento es establecer una ruta crítica de remediación para que el proyecto obtenga la certificación de "Apto para Entornos Institucionales".

---

## 🟢 1. Hallazgos Ya Solucionados (Refactorización Reciente)

El equipo de desarrollo (nosotros) ya abordó exitosamente las vulnerabilidades de control fundamentales durante esta sesión:

*   **[H-05] Autorización Rota en CRUD Usuarios (Bloqueante):** **RESUELTO.** Se programó e inyectó el decorador `@admin_required` (validando `nivel_acceso >= 10` a nivel Base de Datos) en todos los endpoints de manipulación en `app21.py` (`POST /users`, `PUT /users/<id>`, `DELETE`). Un usuario no puede auto-elevarse.
*   **[Bug Lógica] Sobrescritura de claves mudas (No tabulado pero corregido):** **RESUELTO.** Ya interceptamos la iteración en `update_user` para que omita claves vacías `""` enviadas desde el frontend y evite disrupciones de acceso.
*   **[H-13] IPs Hardcodeadas en Frontend (Media):** **MITIGADO/PARCIAL.** Se ejecutó el reemplazo masivo de `186.67.61.251:8000` en pro de `window.API_BASE_URL` en archivos JS base, aunque algunos remanentes en HTML pueden requerir segunda revisión.

---

## 🔴 2. Plan de Refactorización "Zero-Day" (Lo que PODEMOS y DEBEMOS modificar hoy en el código)

Las siguientes vulnerabilidades son bloqueantes/altas pero pueden corregirse inmediatamente mediante ajustes en el backend o scripts de eliminación.

### A. Riesgos Criptográficos y Credenciales
*   **[H-01] Claves API de IA Expuestas (ZhipuAI):**
    *   **Solución factible:** Eliminar la ridícula "ofuscación XOR" de `ia.js` y borrar la variable quemada en `chat.html`.
    *   **Implementación:** Trasladar la inyección directiva al Backend (`app21.py`), creando un Endpoint de Proxy Inverso (`POST /api/chat/proxy`) que tome la `ZHIPU_API_KEY` puramente de las Variables de Entorno del sistema y enmascare al emisor real de la petición.
*   **[H-02] Secreto JWT por Defecto:**
    *   **Solución factible:** Remover el valor inyectado `fallback-secret-for-dev-123456` de la L25 de `app21.py`. Añadir lógica para que la aplicación haga `raise Exception("No JWT Secret!")` si el proveedor en la nube no lo declara.
*   **[H-04] Data Leak de Correos Institucionales:**
    *   **Solución factible:** Borrar el archivo en limpio `backend/config_correo.json` e incorporarlo al `.gitignore`. Trasladar temporalmente su lógica a la Base de Datos o a una variable inyectada.

### B. Fallas Arquitectónicas Backend (Flask / Postgres)
*   **[H-03] Permisividad CORS Extrema (`*`):**
    *   **Solución factible:** Denegar el "fallback" general en `CORS(app)`. Cuando la V. Entorno no detecte un dominio, el backend se levantará rechazando todas las conexiones Web externas en lugar de permitiéndolas todas.
*   **[H-06] Modo Debug en Producción:**
    *   **Solución factible:** Invertir la sentencia Booleana en `app21.py`. Hacer que por defecto cargue `False` anulando el modo terminal interactivo que permite inyección de comando remoto ante un *Error 500*.
*   **[H-07] Inyección SQL por nombre de Tabla (`crud_simple` / `generic_delete`):**
    *   **Solución factible:** Sustituir en `app21.py` la concatenación pura (`"SELECT * FROM " + tabla`) por una validación superior ("Lista Blanca") con un diccionario inmutable de Tablas permitidas (`ALLOWED_TABLES_READ`).
*   **[H-08] Zip Slip (Manipulación de Rutas en Uploads):**
    *   **Solución factible:** Rehacer la línea 5729 (`zf.extractall`) en la extracción del `volume`. Interceptar cada archivo extraído comprobando iterativamente que su ruta real `os.path.realpath` converja dentro del directorio inyectado.
*   **[H-10] Exposición de Excepciones del Servidor (`str(e)`):**
    *   **Solución factible:** Reemplazar de forma masiva en `app21.py` el modelo riesgoso actual `return jsonify({"detail": str(e)})` por una envoltura de seguridad `return jsonify({"message": "Error logueado para auditoria. Servidor no respondio"})`.

### C. Higiene y Reglas de Negocio
*   **[H-09] Endpoints Sin Autenticación (Fuga Publica):** Acceso público directo en Reportes, Descarga de Licitaciones y Mapas. Solución: Adosar nuestro nuevo tag `@session_required` a dichas rutas de la línea 2805 y 1671.
*   **[H-20] Limpieza de Sesiones Rota (Bloqueo de BdD):** Incorporar un comando DELETE nativo donde hoy aparece el código muerto (`cleanup_expired_sessions()`), buscando tokens expirados en la tabla `jwt_blocklist` contra el timestamp en curso.
*   **[H-19] Archivos Residuales:** Borrar todos los `test.js`, `inject_ia.js`, `frontend/promp` descubiertos, achicando pasivamente la huella atacable del Repositorio.

---

## 🟡 3. Hallazgos Inviables (Requieren Aprobación Institucional o Rewrite Estructural)

Estas observaciones no conviene atacarlas desde la codificación pura hoy mismo, dado que escapan del marco técnico factible o conllevan re-entrenar al usuario. Proponemos mitigarlas operativamente:

*   **[H-12] Token JWT Almacenado Vulnerable en `localStorage` (XSS):**
    *   **Lo que pide M. Auditor:** Transitar a Cookies `HttpOnly`.
    *   **Por qué hoy NO SE PUEDE:** Cambiar esto quebraría los cientos de llamadas manuales `fetch` en el front-end `layout.js` y `router.js` que actualmente envuelven el header `Authorization: Bearer + token`. La refactorización sería gigantesca para un Vanilla JS sin Axios globalizado (rompe el SLA).
    *   **Mitigación Parcial:** Mantener Storage temporalmente, inyectar el Header de Seguridad CSP (Content Security Policy) para reducir la inserción de scripts externos maliciosos.
