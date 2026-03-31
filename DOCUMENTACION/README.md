# 🏛️ Geoportal Municipal y Sistema de Control SECPLAC Algarrobo

[![Estado](https://img.shields.io/badge/Estado-Producci%C3%B3n-success?style=for-the-badge)](https://geoportalalgarrobo.github.io/ALGARROBO_BASE2)
[![Backend](https://img.shields.io/badge/Backend-Flask_Modular-blue?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Base de Datos](https://img.shields.io/badge/PostgreSQL-Managed-336791?style=for-the-badge&logo=postgresql)](https://postgresql.org)
[![Seguridad](https://img.shields.io/badge/Seguridad-JWT_RBAC-orange?style=for-the-badge)](https://jwt.io/)

## 📌 1. Propósito y Visión Estratégica
El **Geoportal Municipal de Algarrobo** no es solo un visor cartográfico; es el sistema de registro (System of Record) y control de gestión centralizado de la Secretaría Comunal de Planificación (SECPLAC). Su propósito fundamental es ofrecer un motor multi-dimensional para la **auditoría integral de la calidad de los proyectos municipales**.

### Objetivos Clave:
*   **Gestión del Portafolio de Inversión:** Centralización de fichas de proyectos, presupuestos y cronogramas.
*   **Auditoría Automatizada:** Motor de reglas que escanea la integridad de los datos y genera reportes PDF de cumplimiento.
*   **Control de Licitaciones:** Trazabilidad total de procesos administrativos, desde la preparación hasta la adjudicación.
*   **Inteligencia Territorial:** Capas GIS (Sistema de Información Geográfica) para la toma de decisiones basada en la ubicación.
*   **Transparencia Institucional:** Acceso diferenciado para funcionarios, directivos y personal técnico con auditoría de cambios en tiempo real.

---

## 🏗️ 2. Arquitectura de Sistemas Relacional
El sistema emplea un patrón Cliente-Servidor desacoplado (JAMStack / RESTful API) diseñado para operar en entornos de alta disponibilidad y bajo consumo de recursos:

1.  **Capa de Presentación (Frontend SPA):**
    *   Construida 100% en **JavaScript Vanilla (ES6+)**, eliminando la necesidad de frameworks pesados como React o Angular que introducen complejidad de compilación.
    *   Utiliza **TailwindCSS** para un diseño responsivo y moderno, inyectado mediante configuración dinámica.
    *   Comunicación asíncrona mediante `fetch` API con manejo estricto de estados de carga y errores.

2.  **Capa Lógica (Backend API):**
    *   Motor robusto en **Python 3.11+** utilizando **Flask 3**.
    *   Arquitectura **Modular por Blueprints**: Cada dominio funcional (Usuarios, Proyectos, Mapas) reside en su propio submódulo, facilitando el mantenimiento y la escalabilidad.
    *   **Stateless Authentication**: Implementación de **JWT (JSON Web Tokens)** almacenados en cookies seguras (HttpOnly/SameSite), permitiendo escalabilidad horizontal sin necesidad de sesiones en base de datos.

3.  **Capa de Datos y Persistencia:**
    *   **PostgreSQL (Managed por Neon/Railway)**: Motor relacional con soporte nativo para datos geopespaciales (PostGIS).
    *   **Connection Pooling**: Uso de `ThreadedConnectionPool` para gestionar eficientemente las conexiones y evitar el agotamiento de recursos.
    *   **Almacenamiento de Archivos (Object Storage/Volumes)**: Los documentos se gestionan en un volumen persistente (`/data`), separando los archivos binarios del código fuente.

---

## 🗺️ 3. Mapa de Navegación del Backend (Módulos)
El servidor central (`app_railway.py` / `app21.py`) actúa como el bus de datos que registra los siguientes Blueprints:

| Módulo | Descripción Técnica y Funcional | Endpoints Base |
| :--- | :--- | :--- |
| 🛡️ `auth_routes` | Gestión de identidad, login con Bcrypt, emisión de JWT y revocación selectiva. | `/auth/login`, `/auth/logout` |
| 👥 `users_routes` | Administración de usuarios, asignación de roles jerárquicos y gestión de divisiones. | `/users/*`, `/roles/*` |
| 🏗️ `proyectos_routes` | Core del sistema: gestión de fichas, estados de avance y presupuestos proyectados. | `/proyectos/*` |
| 📍 `documentos_routes` | (Geomapas) Manejo de capas GeoJSON, visualización cartográfica e hitos temporales. | `/geomapas/*`, `/hitos/*` |
| 📑 `documentos_file` | API de gestión de archivos, OCR de documentos antiguos e indexación de PDFs. | `/documentos/*`, `/docs/*` |
| 📊 `control_routes` | Dashboard gerencial, cálculo de KPIs en tiempo real e historial de actividad global. | `/control/*` |
| 🔍 `auditoria_routes` | Generador de reportes masivos por lote y tareas de verificación de integridad. | `/auditoria/*` |
| ⚖️ `licitaciones_routes`| Control de flujos de licitación, hitos administrativos y adjudicaciones. | `/licitaciones/*` |

---

## 🔒 4. Protocolos de Seguridad y Cumplimiento
*   **Encriptación de Datos:** Todas las contraseñas se almacenan usando `Bcrypt` con un factor de trabajo (salt) dinámico.
*   **Defensa en Profundidad:** 
    *   Validación de tipo de archivo y tamaño en uploads.
    *   Sanitización de nombres de archivo mediante `secure_filename`.
    *   Protección contra inyección SQL mediante el uso de consultas parametrizadas en la capa de datos.
*   **Control de Acceso (RBAC):** Sistema de permisos basado en niveles (Acceso 1 a 10) y roles específicos que limitan la visibilidad de los datos según el departamento (SECPLAC, DOM, etc.).
*   **Trazabilidad:** Cada acción de escritura es registrada en el módulo de control (Activity Log), capturando el usuario, la IP, el cambio realizado y la marca de tiempo.

---

## 🛠️ 5. Flujo de Datos Típico (Request Lifecycle)
1.  **Cliente:** Usuario hace clic en "Ver Proyecto". El JS del frontend adjunta el JWT de la cookie.
2.  **API Gateway:** Flask recibe la petición. El decorador `@session_required` valida la firma del JWT.
3.  **Controller:** El Blueprint de proyectos recibe la petición, valida los parámetros (ej. ID sea entero).
4.  **Data Layer:** Se solicita la conexión al Pool. Se ejecuta la consulta parametrizada a PostgreSQL.
5.  **Audit:** Se registra la lectura si el endpoint es sensible.
6.  **Response:** La API retorna un objeto JSON limpio que el frontend renderiza dinámicamente.

---

## 🚀 6. Evolución del Sistema (Roadmap)
*   **Fase 1 (Completada):** Migración del monolito a arquitectura modular. Implementación de JWT.
*   **Fase 2 (Actual):** Despliegue en Railway con volúmenes persistentes. Sistema de auditoría automática.
*   **Fase 3 (Próxima):** Integración nativa con servicios de mapas externos (IDE Chile), optimización de OCR basado en IA y módulo de notificaciones push móviles.
