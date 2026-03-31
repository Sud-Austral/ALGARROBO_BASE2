# 🛠️ Stack Tecnológico y Dependencias Detalladas

La plataforma ALGARROBO_BASE2 implementa tecnologías *battle-tested* y pragmáticas orientadas al alto volumen de procesamiento transaccional. A continuación, el detalle ingenieril de cada capa.

---

## 🐍 1. Stack de Backend (Lógica y API)

*   **Lenguaje:** Python 3.11+
*   **Framework:** Flask 3.0.2
    *   **Arquitectura Modular:** Uso intensivo de `Blueprints` para separar dominios. Esto permite que el sistema crezca sin que el archivo principal de la aplicación se vuelva inmanejable.
*   **Servidor de Aplicación (WSGI):** Gunicorn 21.2
    *   **Worker Model:** Se utiliza un modelo de pre-fork con hilos (`gthread`). Esto es vital para manejar las tareas de generación de PDF que consumen CPU sin bloquear las solicitudes de entrada ligeras.
*   **Seguridad y Autenticación:**
    *   **Bcrypt 4.1:** Algoritmo de hash adaptativo para contraseñas. Resistente a ataques de fuerza bruta por el uso de *salting* automático y costo computacional configurable.
    *   **PyJWT 2.8:** Implementación de JSON Web Tokens (JWT). El sistema genera tokens firmados con `HS256`. Los tokens son *stateless*, lo que significa que el servidor no guarda sesiones en memoria, facilitando el reinicio del servicio sin desconectar a los usuarios.

---

## 🎨 2. Stack de Frontend (Interfaz de Usuario)

*   **Arquitectura:** JAMStack ligero (JavaScript, APIs, Markup).
*   **Framework UI:** JS Vanilla (ES6+). No se utilizan frameworks de terceros (como Vue o React) para garantizar una carga instantánea de < 1s y evitar dependencias de compiladores complejos.
*   **Motor de Estilos:** TailwindCSS 3.4
    *   **Configuración JIT:** Los estilos se generan dinámicamente según las clases utilizadas en el HTML, manteniendo el CSS final lo más liviano posible.
*   **Componentes de Visualización:**
    *   **Chart.js 4.4:** Generación de gráficos de barras, circulares y líneas para los KPIs de SECPLAC.
    *   **Leaflet.js / OpenStreetMap:** (Módulo Geoportal) Para el renderizado de capas GeoJSON y navegación por el mapa municipal.

---

## ⚙️ 3. Motores de Procesamiento de Documentos (OCR)

El sistema procesa archivos PDF e imágenes de expedientes antiguos mediante un flujo asíncrono:

1.  **Tesseract OCR:** Utilizado para detectar texto en imágenes subidas por los técnicos en terreno. Se integra mediante la librería `pytesseract`.
2.  **Antiword:** Herramienta de línea de comandos que lee archivos binarios `.doc` (Word 97-2003). Es crítica para la migración de archivos históricos municipales que no están en formatos abiertos.
3.  **PyPDF2 / PDFMiner:** Para la extracción de metadatos y texto nativo de PDFs modernos subidos a la plataforma.
4.  **Generación de PDF (ReportLab):** Motor vectorial que construye los informes de auditoría desde cero, permitiendo incluir tablas complejas, logos institucionales y enlaces interactivos a la plataforma.

---

## 🗄️ 4. Infraestructura de Datos (Persistencia)

*   **PostgreSQL (Neon.tech):**
    *   Base de datos relacional con almacenamiento separado de la computación.
    *   Uso de esquemas relacionales estrictos para asegurar la integridad referencial de los proyectos (`FOREIGN KEY` cascade/restrict).
*   **Gestión de Conexiones:**
    *   Se implementa un `ThreadedConnectionPool` personalizado que recicla conexiones activas.
    *   **Keep-Alive:** Configuración de parámetros TCP para evitar que el firewall de Railway corte conexiones inactivas hacia el nodo de base de datos fuera del cluster.

---

## 🌐 5. Despliegue y DevOps (CI/CD)

*   **Contenerización (Docker):**
    *   **Multi-Stage Build:** El `Dockerfile` utiliza `python:3.11-slim` como base. En la primera etapa instala herramientas de compilación (`gcc`, `python3-dev`) y en la segunda etapa solo copia los binarios resultantes, minimizando la superficie de ataque y el espacio en disco.
    *   **Entornos:** Detección automática del entorno (Local vs Production) mediante variables de entorno para ajustar el nivel de log (`DEBUG` vs `INFO`).
*   **Infraestructura como Código (Railway):**
    *   `railway.json`: Define el comando de inicio, las comprobaciones de salud (Healthchecks) y el plan de recursos.
    *   **Volúmenes Persistentes:** Montaje de `/data` para asegurar que el contenido generado por los usuarios (uploads, reportes generados) sobreviva a los despliegues de nueva versión del código.
