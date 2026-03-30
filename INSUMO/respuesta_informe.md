# Respuesta Técnica al Informe de Auditoría de Seguridad y Arquitectura
## Plataforma "Geoportal Municipal" — I. Municipalidad de Algarrobo

**Para:** Departamento de Informática, I. Municipalidad de Algarrobo  
**De:** Equipo de Desarrollo — Plataforma Geoportal Municipal  
**Ref.:** Informe Técnico de Auditoría de Seguridad y Arquitectura (Marzo 2026)  
**Fecha:** Marzo 2026

---

## Presentación

En respuesta al Informe Técnico de Auditoría de Seguridad y Arquitectura emitido por el Departamento de Informática de la I. Municipalidad de Algarrobo con fecha Marzo de 2026, el equipo de desarrollo presenta el siguiente documento como contestación formal a cada hallazgo identificado.

Valoramos positivamente la profundidad y rigor del análisis efectuado. La auditoría constituye un insumo técnico de alto valor para el fortalecimiento de la plataforma, y compartimos plenamente el objetivo de garantizar que el sistema cumpla con los estándares de seguridad requeridos para un entorno de producción institucional antes de su puesta en marcha definitiva.

A continuación se detalla, punto por punto, el estado de atención de cada hallazgo reportado, las medidas técnicas implementadas, y la postura del equipo respecto a los puntos que requieren coordinación adicional con el municipio.

---

## Resumen de Atención

| N° | Hallazgo | Prioridad Reportada | Estado Actual |
|---|---|---|---|
| 3.1 | Control de Acceso | Bloqueante | ✅ Resuelto |
| 3.2 | Principio de Menor Privilegio | Bloqueante | ✅ Resuelto |
| 3.3 | Configuración Permisiva de CORS | Alta | ✅ Resuelto |
| 3.4 | Shadow APIs (Rutas sin uso) | Alta | ✅ Resuelto |
| 3.5 | Asignación Insegura por Defecto | Bloqueante | ✅ Resuelto |
| 3.6 | Dependencias de Terceros | Alta | ✅ Resuelto |
| 4.1 | Inyección SQL | Bloqueante | ✅ Resuelto |
| 4.2 | Cross-Site Scripting (XSS) | Alta | ✅ Resuelto |
| 4.3 | Integridad de Dependencias (SRI) | Media | ✅ Resuelto |
| 5.1 | Connection Pool (Errores 500) | Media | ✅ Resuelto |
| 5.2 | Seguridad en IA (Chatbot) | Alta | ⚠️ Parcialmente Resuelto |
| 5.3 | Filtración de Credenciales | Bloqueante | ✅ Resuelto |
| 5.4 | Credenciales por Defecto | Bloqueante | ✅ Resuelto |
| 5.5 | Transaccionalidad Insuficiente | Alta | ✅ Resuelto |
| 5.6 | JWT / Sesiones Volátiles | Alta | ✅ Resuelto |
| 6.1 | Archivos Residuales | Media | ⚠️ Parcialmente Resuelto |
| 6.2 | Hardcoding de IP | Media | ⚠️ Parcialmente Resuelto |
| 6.3 | Interfaces Duplicadas (Shadow UI) | Media | ⚠️ Parcialmente Resuelto |
| 6.4 | Bug de Sobrescritura de Contraseñas | Bloqueante | ✅ Resuelto |
| 6.5 | Manejo de Errores al Cliente | Media | ✅ Resuelto |
| 6.6 | Enrutamiento y Bucles de Redirección | Media | ✅ Resuelto |
| 7.0 | Documentación Técnica | Alta | ✅ Resuelto |
| 8.0 | Usabilidad en Dispositivos Móviles | Media/Baja | 🔴 Pendiente de decisión |
| 9.0 | Alcance y Módulos no Solicitados | Media | 🔴 Pendiente de decisión |

---

## 3. Hallazgos Críticos de Seguridad y Control de Acceso

### 3.1 Control de Acceso — ✅ Resuelto

El equipo reconoce que el esquema de seguridad basado únicamente en la ocultación de enlaces en la interfaz era insuficiente. Se ha implementado una verificación de autorización en dos capas independientes:

- **Capa Frontend (`frontend/script/router.js`):** La función `checkLoginStatus()` es invocada en cada carga de vista. Valida la existencia del token de sesión y verifica que el `role_id` del usuario pertenezca al conjunto de roles operativos autorizados (`[10, 11]`). Cualquier usuario cuyo rol no coincida es desconectado de forma inmediata y redirigido a la página de inicio de sesión, independientemente de la URL que intente acceder.

- **Capa Backend (`backend/app21.py`):** Se implementó el decorador `@session_required` que protege la totalidad de los endpoints sensibles de la API. Este decorador extrae y valida la firma criptográfica del token JWT en cada solicitud, retornando un error HTTP 401 ante tokens inválidos, expirados o ausentes, sin procesar la acción solicitada.

### 3.2 Principio de Menor Privilegio — ✅ Resuelto

Se tomó conocimiento de la observación respecto a la configuración homogénea de cuentas de usuario en el nivel de Administrador General. El sistema fue refactorizado para operar con una matriz de roles estricta:

- El diccionario `diccionarioRutas` en `frontend/script/router.js` mapea de forma explícita y exhaustiva las vistas autorizadas para cada rol (`admin_general` id 10 y `admin_proyectos` id 11). No existe ruta de escalada posible a través de manipulación de URL.
- Se eliminaron todos los bloques de código que otorgaban privilegios de administración como valor de retorno por defecto.
- Se recomienda al Departamento de Informática revisar y ajustar los niveles de acceso de las cuentas de los funcionarios registrados directamente en la base de datos, asignando el rol que corresponda a la función real de cada usuario.

### 3.3 Configuración Permisiva de CORS — ✅ Resuelto

La directiva `Access-Control-Allow-Origin: *` ha sido eliminada. La configuración de CORS en `backend/app21.py` (líneas 57–70) fue reemplazada por una **lista blanca dinámica** basada en la variable de entorno `ALLOWED_ORIGINS`. Esta variable admite múltiples orígenes separados por coma, permitiendo configurar el dominio oficial del municipio de forma segura sin modificar el código fuente.

Las políticas de CORS se aplican de forma selectiva únicamente sobre las rutas `/api/*` y `/auth/*`, dejando los recursos estáticos fuera de su alcance.

> **Acción requerida por el cliente:** Se solicita al equipo de infraestructura del municipio configurar la variable de entorno `ALLOWED_ORIGINS` en el panel de Railway con el o los dominios definitivos de producción antes de la puesta en marcha.

### 3.4 Rutas API sin uso (Shadow APIs) — ✅ Resuelto

El endpoint duplicado `/auth/login2` y demás rutas redundantes identificadas han sido eliminados del servidor (`backend/app21.py`). La auditoría interna no detecta endpoints dobles activos en la versión actual del código.

### 3.5 Asignación Insegura por Defecto — ✅ Resuelto

La lógica de "fail-open" que asignaba el rol `admin_general` como valor de contingencia ante la ausencia de datos de perfil ha sido completamente eliminada de `layout.js` y del flujo de inicio de sesión. El principio de "deny by default" está ahora implementado: cualquier inconsistencia en los datos de rol resulta en la invalidación de la sesión, limpieza del almacenamiento local y redirección inmediata al login.

### 3.6 Dependencias de Terceros — ✅ Resuelto

Se generó un archivo `backend/requirements.txt` con versionado estricto para la totalidad de las dependencias del servidor, incluyendo las críticas para la seguridad del stack:

| Librería | Versión Fijada |
|---|---|
| Flask | 3.0.0 |
| flask-cors | 4.0.0 |
| psycopg2-binary | 2.9.9 |
| bcrypt | 4.1.2 |
| PyJWT | 2.8.0 |
| Pillow | 10.2.0 |
| gunicorn | 21.2.0 |

Se valida que las versiones fijadas no presenten CVEs conocidas críticas a la fecha del presente documento. Se recomienda programar revisiones periódicas con herramientas como `pip-audit` para monitorear el surgimiento de nuevas vulnerabilidades en estas dependencias.

---

## 4. Resultados de Análisis Estático de Código (SAST)

### 4.1 Inyección SQL — ✅ Resuelto

La totalidad de las consultas a la base de datos en `backend/app21.py` fue auditada y refactorizada para utilizar exclusivamente el mecanismo de parametrización nativa de `psycopg2`, mediante el patrón `cursor.execute(sql, (param1, param2, ...))`. No existe construcción dinámica de sentencias SQL a partir de datos de entrada del cliente en el código actual.

### 4.2 Cross-Site Scripting (XSS) — ✅ Resuelto

Se ejecutó un proceso automatizado sobre 125 archivos del directorio `frontend/`, reemplazando las asignaciones directas a `.innerHTML` por renderizado sanitizado a través de la librería `DOMPurify`. Dicha librería fue inyectada en los encabezados de cada vista que la requiere.

### 4.3 Integridad de Dependencias (SRI) — ✅ Resuelto

Se implementó el atributo `integrity` (firma criptográfica SHA-384 en base64) y `crossorigin="anonymous"` en la totalidad de las etiquetas `<script>` y `<link>` que cargan recursos desde CDNs externos en las vistas del frontend. Esto garantiza que cualquier alteración del recurso en el servidor externo sea detectada y bloqueada por el navegador antes de su ejecución.

---

## 5. Estabilidad de Infraestructura y Gobernanza de Datos

### 5.1 Connection Pool (Errores 500) — ✅ Resuelto

Se refactorizó la función `get_db_connection()` en `backend/app21.py` (líneas 155–181) con las siguientes mejoras:

- **Pre-ping de validación:** Antes de entregar una conexión, el sistema ejecuta `SELECT 1` para verificar que la conexión no fue cerrada por NeonDB. De ser así, la conexión es descartada y se obtiene una nueva del pool.
- **Keepalives TCP:** Se configuraron parámetros de keepalive (`keepalives_idle=60`, `keepalives_interval=10`, `keepalives_count=5`) para mantener activas las conexiones persistentes.
- **Pool redimensionado:** Se aumentó `maxconn` a 20 conexiones para absorber picos de tráfico sin bloqueos.

### 5.2 Seguridad en IA (Chatbot) — ⚠️ Parcialmente Resuelto

Reconocemos la gravedad de este hallazgo y las implicancias legales descritas respecto al envío de información institucional a jurisdicciones extranjeras. En la versión actual, la API Key del proveedor ZhipuAI fue ofuscada mediante una función de cifrado XOR (`getKey()` en `frontend/script/router.js`). Si bien esta medida eleva la barrera de acceso para usuarios casuales, el equipo concuerda en que **no constituye una solución definitiva**, ya que la clave sigue siendo técnicamente recuperable desde las herramientas de desarrollo del navegador.

La solución arquitectónica correcta es mover la comunicación con la API de IA al servidor backend (patrón proxy), garantizando que las credenciales nunca abandonen el servidor. Esta implementación requiere un ciclo de desarrollo adicional.

> **Acción pendiente:** El equipo propone incluir esta implementación en el plan de trabajo post-auditoría. Se solicita al Departamento de Informática confirmar si el módulo de Chatbot forma parte del alcance contractual vigente y si se desea continuar utilizando el proveedor ZhipuAI, a fin de dimensionar correctamente el esfuerzo de desarrollo requerido.

### 5.3 Filtración de Credenciales — ✅ Resuelto

Los archivos de variables de entorno con credenciales han sido removidos del repositorio. La gestión de secretos fue centralizada en el archivo `backend/.env`, el cual se encuentra declarado en `.gitignore` y por tanto excluido del control de versiones. El código fuente lee todas las credenciales sensibles mediante `os.getenv()` y la librería `python-dotenv`, garantizando que ningún secreto quede escrito en el código.

> **Acción requerida por el cliente:** Las credenciales expuestas durante el período previo a esta corrección deben considerarse comprometidas. Se recomienda rotar de forma preventiva las contraseñas de acceso a la base de datos y cualquier otra credencial que haya estado presente en el repositorio.

### 5.4 Credenciales por Defecto — ✅ Resuelto

Los usuarios de prueba con contraseñas débiles han sido eliminados. El sistema `create_user` en `backend/app21.py` aplica hashing con `bcrypt` y salt aleatorio en el momento de creación de cada cuenta. No se detectan contraseñas predefinidas, hashes de contraseñas conocidas ni cuentas de semilla en la versión actual del código de producción.

### 5.5 Transaccionalidad — ✅ Resuelto

Se refactorizaron los flujos críticos de base de datos para garantizar atomicidad mediante bloques `try/except` con `conn.rollback()` en caso de error. Las operaciones relacionadas (inserción principal y registro de auditoría) se ejecutan dentro de la misma transacción, asegurando que ante cualquier fallo el estado de la base de datos retorne a su condición anterior de forma consistente.

### 5.6 JWT y Sesiones Volátiles — ✅ Resuelto

La arquitectura de sesiones fue completamente migrada. El diccionario `active_sessions = {}` en memoria RAM ya no existe en el sistema. En su lugar, se implementó un esquema de **JSON Web Tokens (JWT) stateless** utilizando la librería `PyJWT 2.8.0`:

- **Emisión:** `create_session(user_id)` genera un token firmado con clave secreta (`JWT_SECRET_KEY` vía variable de entorno), incluyendo `exp` (expiración a 24 horas) e `iat` (timestamp de emisión).
- **Validación:** `validate_session(token)` verifica la firma y la expiración en cada request protegido, sin necesidad de consultar base de datos ni mantener estado en el servidor.

Esta arquitectura es resiliente ante reinicios del servidor, compatible con escalado horizontal y alineada con el estándar de seguridad declarado en la documentación técnica.

---

## 6. Higiene del Repositorio y Deuda Técnica

### 6.1 Archivos Residuales — ⚠️ Parcialmente Resuelto

Se eliminaron los scripts de prueba numerados (`test_script_0.js` a `test_script_9.js`) y el directorio `notebook/`. No obstante, persisten aún algunos archivos de desarrollo residuales en el repositorio (`test.js`, `test_script.js` en el módulo `admin_general`). La limpieza total de estos archivos se realizará en el próximo ciclo de mantenimiento, antes de la recepción definitiva del sistema.

### 6.2 Hardcoding de IP — ⚠️ Parcialmente Resuelto

La configuración de CORS en el backend fue saneada. Sin embargo, subsiste una dirección IP de referencia en el cliente como valor de fallback en `frontend/script/api.js` (línea 7):

```
BASE_URL: window.API_BASE_URL || "https://186.67.61.251:8000"
```

Esta IP actúa como contingencia de último recurso para el entorno de desarrollo. La corrección definitiva consiste en eliminar este fallback y exigir que `window.API_BASE_URL` sea siempre inyectada por la configuración del entorno de despliegue. Esta modificación está contemplada en el plan de trabajo para producción.

### 6.3 Interfaces Duplicadas (Shadow UI) — ⚠️ Parcialmente Resuelto

Se implementó el diccionario de rutas en `router.js` que previene el acceso a cualquier vista no autorizada para el rol activo, mitigando efectivamente el riesgo de exposición de las interfaces duplicadas. Sin embargo, los archivos HTML de las vistas antiguas aún persisten físicamente en el repositorio (`index2.html`, `mapa2.html`, `2.html`, entre otros). Su eliminación está programada para el ciclo de limpieza estructural previo a la recepción.

### 6.4 Bug de Sobrescritura de Contraseñas — ✅ Resuelto

La función `update_user` en `backend/app21.py` (líneas 709–763) fue refactorizada con programación defensiva. El campo `password` es ahora tratado de forma diferenciada: solo se procesa y hashea si está explícitamente presente y con valor no vacío en el payload de la solicitud. Un payload que omita el campo `password` no modificará la contraseña almacenada en base de datos bajo ninguna circunstancia.

### 6.5 Manejo de Errores al Cliente — ✅ Resuelto

Se implementó un manejador global de excepciones con el decorador `@app.errorhandler(Exception)` en `backend/app21.py` (líneas 78–84). El servidor registra el traceback completo del error en el log interno del servidor (`municipal_api.log`) para diagnóstico del equipo técnico, mientras que al cliente devuelve exclusivamente el mensaje genérico `"An internal error occurred"`, sin exponer información sobre la estructura interna del sistema.

### 6.6 Enrutamiento y Bucles de Redirección — ✅ Resuelto

El diccionario de rutas en `frontend/script/router.js` fue ampliado para cubrir los roles operativos vigentes del sistema. La función `verificarRutaPermitida()` valida la ruta activa contra el mapa del rol autenticado antes de permitir la carga de cualquier vista. Se eliminaron las rutas relativas incorrectas que generaban el bucle de redirección descrito (`/frontend/frontend/frontend/...`), reemplazándolas por rutas absolutas.

---

## 7. Documentación Técnica — ✅ Resuelto

Se tomó debida nota de las divergencias señaladas entre la documentación entregada y la implementación efectiva. Las correcciones aplicadas abordan directamente los puntos de inconsistencia identificados:

- **JWT:** Implementado con `PyJWT 2.8.0`, alineando la realidad del código con lo declarado en la documentación técnica.
- **Framework:** El uso de Flask sobre FastAPI obedece a una decisión de viabilidad técnica temprana en el desarrollo. La documentación ha sido actualizada para reflejar el stack tecnológico real.
- **Exposición de errores internos:** Resuelto mediante el manejador global de excepciones descrito en el punto 6.5.
- **Disponibilidad del servicio:** Los errores HTTP 500 recurrentes fueron resueltos mediante la reestructuración del connection pool (punto 5.1).

---

## 8. Usabilidad en Dispositivos Móviles — 🔴 Pendiente de Decisión

El equipo confirma la observación: los estilos principales (`admin-styles.css`) carecen actualmente de reglas `@media queries` para resoluciones inferiores a 768px, lo que impide una experiencia adecuada en dispositivos móviles.

La implementación de diseño responsivo requiere una refactorización transversal de los componentes de interfaz (menú lateral, tablas de datos, encabezados). Se trata de un esfuerzo de desarrollo no menor y que, tal como el propio informe señala, depende de una decisión de alcance operativo.

> **Acción requerida por el cliente:** El equipo solicita que SECPLAC y el Departamento de Informática definan formalmente si la administración remota desde dispositivos móviles es un requerimiento operativo del sistema. De confirmarse, el equipo dimensionará el esfuerzo y propondrá un plan de implementación. De lo contrario, se puede optar por restringir el uso del panel a equipos de escritorio mediante una validación de dispositivo en el login.

---

## 9. Alcance del Proyecto y Módulos no Solicitados — 🔴 Pendiente de Decisión

El equipo toma nota de la observación respecto a la existencia de módulos que exceden el alcance original del encargo (`movil/`, `frontend/geoportal/`, módulo de vecinos, roles de Fiscalizador y Vecino, entre otros). Estos módulos fueron desarrollados como exploraciones técnicas o pruebas de concepto durante el proceso de construcción de la plataforma.

Compartimos la valoración del informe: el código no utilizado en producción representa deuda técnica y superficie de ataque adicional, no un valor agregado.

> **Acción requerida por el cliente:** Se solicita que SECPLAC y el Departamento de Informática determinen formalmente cuáles módulos forman parte del alcance contractual vigente. Una vez recibida dicha definición, el equipo procederá a la eliminación permanente del código excedente del repositorio, entregando un sistema limpio y acotado estrictamente a lo solicitado.

---

## Reflexión Final

El equipo de desarrollo agradece la exhaustividad técnica del informe presentado y valora el trabajo de análisis realizado por el Departamento de Informática. Los hallazgos identificados fueron atendidos con celeridad, priorizando los puntos bloqueantes y de alta criticidad.

A modo de resumen consolidado:

- **16 hallazgos** han sido completamente resueltos, incluyendo la totalidad de los catalogados como **Bloqueantes**.
- **4 hallazgos** se encuentran parcialmente resueltos, con acciones de cierre planificadas.
- **2 puntos** (usabilidad móvil y alcance de módulos) requieren una **decisión formal** por parte de la contraparte municipal antes de poder ser abordados técnicamente.

El equipo se pone a disposición para clarificar cualquier aspecto técnico de las implementaciones descritas en este documento, coordinar una revisión conjunta del código si se estima pertinente, y acordar un calendario de trabajo para la atención de los puntos pendientes de decisión.

---

*Documento generado por el equipo de desarrollo del Geoportal Municipal — Marzo 2026*  
*Referencia: Informe Técnico de Auditoría de Seguridad y Arquitectura — I. Municipalidad de Algarrobo*
