# Observaciones – Auditoría Geoportal Municipal

## 3. Hallazgos Críticos de Seguridad y Control de Acceso

### 3.1 Control de Acceso
El sistema carece de validación real de permisos en rutas. La seguridad se basa en ocultar enlaces en la interfaz, pero no hay control efectivo en el router ni en el back-end.

### 3.2 Principio de Menor Privilegio
Todas las cuentas de usuarios fueron configuradas con nivel de acceso de administrador general, sin distinción de funciones.

### 3.3 Configuración Permisiva de CORS
El servidor acepta solicitudes desde cualquier origen (`*`), permitiendo acceso desde dominios no autorizados.

### 3.4 Rutas API sin uso (Shadow APIs)
Existen endpoints duplicados activos, algunos sin validaciones modernas.

### 3.5 Asignación Insegura por Defecto
El sistema asigna rol de administrador por defecto cuando un usuario no tiene rol definido.

### 3.6 Dependencias de Terceros
No hay control estricto de versiones ni monitoreo de vulnerabilidades en librerías externas.

---

## 4. Resultados de Análisis Estático (SAST)

### 4.1 Inyección SQL
Se construyen consultas dinámicas usando datos del cliente sin validación estructural de campos.

### 4.2 XSS (Cross-Site Scripting)
Uso extendido de `.innerHTML` sin sanitización de datos.

### 4.3 Integridad de Dependencias
Recursos externos cargados sin Subresource Integrity (SRI).

---

## 5. Infraestructura y Gobernanza de Datos

### 5.1 Connection Pool
Errores intermitentes por uso de conexiones cerradas a la base de datos.

### 5.2 Seguridad en IA (Chatbot)
Datos sensibles enviados directamente a un proveedor externo. API Key expuesta en el cliente.

### 5.3 Filtración de Credenciales
Archivos con credenciales y conexiones a base de datos expuestos en el repositorio.

### 5.4 Credenciales por Defecto
Existencia de usuarios con contraseñas débiles predefinidas.

### 5.5 Transaccionalidad
Procesos críticos fragmentados en múltiples operaciones no atómicas.

### 5.6 Manejo de Sesiones
Sesiones almacenadas en memoria RAM sin persistencia.

---

## 6. Higiene del Repositorio y Deuda Técnica

### 6.1 Archivos Residuales
Presencia de archivos de prueba, vacíos o sin uso.

### 6.2 Hardcoding de IP
Direcciones IP escritas directamente en el código en múltiples ubicaciones.

### 6.3 Interfaces Duplicadas
Existencia de interfaces antiguas o no funcionales accesibles por URL.

### 6.4 Sobrescritura de Contraseñas
Actualizaciones de usuario permiten guardar contraseñas vacías.

### 6.5 Manejo de Errores
Errores de servidor son mostrados como credenciales inválidas.

### 6.6 Enrutamiento
Diccionario de rutas incompleto y generación de bucles de redirección.

---

## 7. Documentación Técnica

- Desalineación entre documentación y código real (JWT no implementado).
- Uso de Flask en lugar del framework declarado.
- Exposición de errores internos al cliente.
- Capacidades declaradas no coinciden con el comportamiento observado.

---

## 8. Usabilidad en Móviles

- Menú lateral inaccesible en pantallas pequeñas.
- Tablas no responsivas que rompen la interfaz.

---

## 9. Alcance del Proyecto

- Existencia de módulos no solicitados (Portal Vecino, API móvil, etc.).
- Funcionalidades incompletas o en estado de maqueta.
- Código excedente que aumenta la complejidad y superficie de ataque.