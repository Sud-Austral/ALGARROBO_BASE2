# Revisión de Auditoría y Propuesta de Mitigación - Geoportal Municipal (SECPLAC)

Tras un análisis **cruzado** entre el *Informe Técnico de Auditoría* y el estado real del código fuente del repositorio, presento la matriz de soluciones actualizadas. 

Esta lista discrimina claramente aquellos problemas que ya fueron abordados arquitectónicamente y detalla las medidas mitigantes exactas (con su nivel de factibilidad) para la deuda técnica crítica que permanece expuesta.

---

## 🟢 1. Hallazgos Ya Resueltos en la Estructura (Mitigados)

Durante las labores preventivas recientes, se aislaron y corrigieron las siguientes vulnerabilidades documentadas en el informe:

* **[H-4.1] Inyección SQL por Mass Assignment (Resuelto):** Los endpoints críticos `create_proyecto` y `update_proyecto` ya no confían en los datos entrantes a ciegas. Se implementó una Whitelist estricta (`ALLOWED_FIELDS`) que descarta cualquier intento de inyección de propiedades maliciosas antes de la construcción del SQL.
* **[H-5.1] Error 500 por Desconexión (Resuelto):** El mecanismo `get_db_connection` ya incluye un pulso "Pre-ping" (`SELECT 1`) que desecha y recicla silenciosamente las conexiones inactivas cortadas por NeonDB, estabilizando la disponibilidad.
* **[H-5.6] Fragilidad en Sesión y JWT Volátil (Resuelto):** Se descontinuó el diccionario en memoria RAM `active_sessions={}`. Ahora las funciones de validación utilizan firmas criptográficas JWT (`jwt.decode`) acopladas a una base de datos real (`jwt_blocklist`) para interceptar cierres de sesión robustos.
* **[H-5.3 y H-6.1] Archivos de Riesgo (Resuelto):** Los scripts con credenciales expuestas como `debug_users.py` y `test_db.py` fueron permanentemente purgados del ecosistema para frustrar escalados de infraestructura.
* **[H-6.2] Enlaces y IPs Rígidas (Resuelto):** Las inyecciones directas de la IP `.186.67.61.251` en los archivos JS (como validamos con el rastreador) fueron eliminadas, favoreciendo ahora resoluciones dinámicas dependientes del dominio.

---

## 🔴 2. Hallazgos Críticos Pendientes (Deuda Técnica Activa)

Al revisar el código actual subyacente (`app21.py`, `layout.js` y `router.js`), comprobé que existen vulnerabilidades lógicas y de control de acceso que aún **no han sido parcheadas**. Estas requieren intervención prioritaria:

### H-3.1 y H-3.5 — Autorización Inexistente y Asignación Tolerante por Defecto
* **Estado Actual:** Comprobado. En `layout.js` (Línea 38), si un funcionario inicia sesión y no tiene división asignada, el sistema de front-end hace un "fall-back" crítico asignándole estáticamente `admin_general` o `admin_proyectos`. Peor aún, en `app21.py`, la mayoría de endpoints (ej. `DELETE /users/1` o `PUT /users/1`) solo usan el decorador `@session_required`, lo que comprueba que la persona "existe", pero no valida si tiene el nivel para ejecutar la acción.
* **Medida Mitigante Puesta en Marcha:** 
  1. (Backend): Desplegar un decorador estricto (ej. `@admin_required` que valide `nivel_acceso >= 10`) y aplicarlo a todos los endpoints de manipulación de cuentas.
  2. (Frontend): Suprimir la regla de gracia en `layout.js`. Modificar la lógica para que evalúe: *Si no posee rol → Bloquear Login → Desplegar "Usuario sin permisos vinculados"*.

### H-6.4 — Bug Lógico de Sobrescritura de Contraseñas
* **Estado Actual:** Comprobado. En `app21.py` (Línea 750 de `update_user`), la rutina verifica si la llave es "password" y directamente la cifra y actualiza iterativamente. No hay escudo contra el string vacío `""`.
* **Medida Mitigante Puesta en Marcha:** Interceptar iteraciones nulas en Python agregando: `if k == "password" and v.strip() == "": continue`.

### H-5.5 — Transaccionalidad Rota (No ACID)
* **Estado Actual:** Comprobado. La función `create_user` (L705) hace un `INSERT` de usuario, comete el bloque (`conn.commit()`), y recién ahí envía la acción a `log_auditoria()` que maneja su propia conexión. Si falla algo secundario (como asignarle rol posteriormente en el front-end), el empleado queda desconectado lógicamente.
* **Medida Mitigante Puesta en Marcha:** Reprogramar los submódulos. Centralizar la creación y sus ramificaciones (logging, permisos, asignación) bajo el alero de una sola transacción `BEGIN / COMMIT`. 

### H-6.6 — Diccionario de Mapeo Incompleto
* **Estado Actual:** Comprobado. `router.js` (L13) mapea en `diccionarioRutas` estrictamente perfiles `10`, `11` y `12`. Cualquier Nivel o Sub-rol por debajo de esto originará pánicos de red.
* **Medida Mitigante Puesta en Marcha:** Reconstruir la variable de diccionario, inyectando ruteos y accesos hacia portales restringidos como Transparencia o Contraloría para todos los niveles de acceso operacionales de SECPLAC.

---

## 🟡 3. Soluciones Inviables / Que No Recomiendo Aplicar

* **[H-4.3] Subresource Integrity (SRI) en Tailwind CDN:**
  * **Problema:** Tailwind.com en su CDN no compila un motor estático, muta habitualmente. 
  * **Observación del Auditor:** Fijar un SRI absoluto en un enlace puramente dinámico de CDNs romperá silenciosamente el portal municipal a la primera actualización automática del provedor del CSS.
  * **Mitigación Oficial:** Evitar usar SRI y, como reemplazo institucional sano, recomendar compilar por CLI toda la carpeta CSS en etapas de post-producción.
* **[H-5.2] Eliminación Completa de la Arquitectura de "Vecinos" / Chatbot Chino:**
  * **Problema:** Enviar borradores a `open.bigmodel.cn`.
  * **Mitigación Oficial:** El código fuente denota una inserción masiva y artificial de la capa "vecindario" como un mock para lucir más grande. Se advierte amputar el módulo. Sin embargo, en el corto plazo, rediseñar esta estructura tomará más horas/hombre que las restantes. Recomiendo simplemente inhabilitar el botón físico de ejecución y ponerlo en mantenimiento.

*Este informe constituye el punto de verdad final de los vacíos de arquitectura de seguridad tras cotejar explícitamente el código vivo del panel.*
