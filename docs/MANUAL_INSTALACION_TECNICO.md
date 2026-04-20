# MANUAL TÉCNICO DE INSTALACIÓN
## Sistema SECPLAC — Geoportal Municipal de Algarrobo
### Versión 2.0 | Abril 2026

---

> **LOGO MUNICIPAL** — *(Insertar aquí el escudo o logo oficial de la Municipalidad de Algarrobo)*

---

**Elaborado por:** Equipo de Desarrollo SECPLAC  
**Versión del documento:** 2.0  
**Fecha de emisión:** 20 de abril de 2026  
**Clasificación:** Uso interno — Equipo TI Municipal  

---

## ÍNDICE

1. [Introducción y Objetivo](#1-introducción-y-objetivo)
2. [Información Requerida de la Contraparte Técnica](#2-información-requerida-de-la-contraparte-técnica)
3. [Descripción General de la Aplicación](#3-descripción-general-de-la-aplicación)
4. [Requisitos Previos](#4-requisitos-previos)
5. [Preparación del Servidor](#5-preparación-del-servidor)
6. [Instalación de Dependencias del Sistema](#6-instalación-de-dependencias-del-sistema)
7. [Clonado y Configuración del Proyecto](#7-clonado-y-configuración-del-proyecto)
8. [Variables de Entorno](#8-variables-de-entorno)
9. [Configuración de Base de Datos](#9-configuración-de-base-de-datos)
10. [Build y Despliegue](#10-build-y-despliegue)
11. [Configuración como Servicio del Sistema](#11-configuración-como-servicio-del-sistema)
12. [Configuración de Servidor Web Inverso y SSL](#12-configuración-de-servidor-web-inverso-y-ssl)
13. [Verificación Post-Instalación](#13-verificación-post-instalación)
14. [Problemas Frecuentes y Soluciones](#14-problemas-frecuentes-y-soluciones)
15. [Mantenimiento](#15-mantenimiento)
16. [Anexo: Glosario y Comandos Útiles](#16-anexo-glosario-y-comandos-útiles)

---

## 1. Introducción y Objetivo

Este documento describe el procedimiento técnico completo para instalar, configurar y poner en producción el **Sistema SECPLAC — Geoportal Municipal de Algarrobo** (repositorio `ALGARROBO_BASE2`) en la infraestructura del servidor municipal.

El sistema es una plataforma web de gestión de proyectos municipales para la Secretaría Comunal de Planificación (SECPLAC). Está compuesta por:

- Un **backend API REST** desarrollado en Python/Flask, servido mediante Gunicorn.
- Un **frontend estático** en JavaScript Vanilla (sin compilación especial).
- Una **base de datos** PostgreSQL 15+.
- Un sistema de **almacenamiento de archivos** (documentos, reportes, fotos) en disco local.

**Audiencia:** Personal TI de la Municipalidad de Algarrobo con conocimientos intermedios de administración de servidores Linux o Windows Server.

**Objetivo:** Al finalizar este manual, el lector habrá instalado y verificado el sistema funcionando en el servidor municipal designado.

---

## 2. Información Requerida de la Contraparte Técnica

> **IMPORTANTE:** Antes de ejecutar cualquier paso de este manual, la contraparte técnica municipal debe confirmar los siguientes puntos. Marcar cada ítem antes de proceder.

### 2.1 Checklist de Información del Servidor

| # | Ítem | Valor a confirmar | Confirmado |
|---|------|-------------------|:----------:|
| 1 | Sistema Operativo del servidor | Ubuntu Server 22.04 LTS / Windows Server 2019 / 2022 | ☐ |
| 2 | Versión exacta del SO | Ej: `Ubuntu 22.04.3 LTS` | ☐ |
| 3 | Arquitectura del procesador | x86_64 / ARM64 | ☐ |
| 4 | RAM disponible para la aplicación | Mínimo 2 GB recomendado | ☐ |
| 5 | Espacio en disco disponible | Mínimo 20 GB recomendado | ☐ |
| 6 | Dirección IP del servidor | `<IP_SERVIDOR>` | ☐ |
| 7 | ¿El servidor tiene acceso a Internet? | Sí / No (necesario para clonar repo y descargar paquetes) | ☐ |
| 8 | ¿El servidor tiene Docker instalado? | Sí / No (cambia el procedimiento de instalación) | ☐ |
| 9 | ¿Hay un proxy corporativo? | Sí / No. Si sí: URL y puerto del proxy | ☐ |
| 10 | Puerto que usará la aplicación | Por defecto: `8000`. ¿Hay restricciones de firewall? | ☐ |
| 11 | Dominio o subdominio asignado | Ej: `secplac.algarrobo.cl` o solo IP | ☐ |
| 12 | ¿Se usará HTTPS/SSL? | Sí / No. Si sí: ¿certificado propio o Let's Encrypt? | ☐ |
| 13 | Nombre de usuario del servidor (sudo) | `<USUARIO_SERVIDOR>` | ☐ |
| 14 | Ruta de instalación deseada | Por defecto: `/opt/secplac` (Linux) o `C:\secplac` (Windows) | ☐ |
| 15 | Credenciales de base de datos existente (si aplica) | Host, usuario, contraseña, nombre de BD | ☐ |
| 16 | ¿Se usará PostgreSQL local o externo (cloud)? | Local / Externo (URL de conexión) | ☐ |
| 17 | Cuenta de correo para notificaciones del sistema | `<EMAIL_REMITENTE>` | ☐ |
| 18 | ¿Existe un proveedor SMTP? | Brevo / Gmail / SMTP propio | ☐ |

### 2.2 Decisiones de Arquitectura Previas

Antes de comenzar, el equipo técnico debe decidir la **ruta de instalación**:

| Ruta | Descripción | Recomendada para |
|------|-------------|-----------------|
| **Ruta A: Docker (recomendada)** | Usa el `Dockerfile` incluido. Aísla la app del SO. | Servidores Linux con Docker instalado |
| **Ruta B: Instalación directa Linux** | Instala Python y dependencias directamente en Ubuntu. | Servidores Linux sin Docker |
| **Ruta C: Windows Server** | Instalación directa en Windows con IIS o servicio Windows. | Servidores Windows Server |

> A lo largo del manual se indican con etiquetas `[RUTA A]`, `[RUTA B]` y `[RUTA C]` los pasos específicos de cada ruta.

---

## 3. Descripción General de la Aplicación

### 3.1 ¿Qué hace el sistema?

El **Geoportal SECPLAC** es la plataforma de gestión y control centralizado de la Secretaría Comunal de Planificación. Sus funciones principales son:

- **Gestión de Proyectos Municipales:** Fichas de proyectos, estados de avance, presupuestos y cronogramas.
- **Control de Licitaciones:** Trazabilidad de procesos administrativos desde preparación hasta adjudicación.
- **Auditoría Automatizada:** Motor de reglas que verifica integridad de datos y genera reportes PDF.
- **Geoportal / Mapas:** Capas GIS con información territorial del municipio usando Leaflet.js.
- **Módulo Móvil:** API para aplicación móvil de fiscalizadores en terreno.
- **Gestión de Documentos:** Carga, visualización y OCR de documentos (PDF, DOCX, imágenes).

### 3.2 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      NAVEGADOR WEB                          │
│          (Frontend: HTML/JS Vanilla + TailwindCSS)          │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              SERVIDOR WEB INVERSO (Nginx)                   │
│    - Sirve archivos estáticos del frontend                  │
│    - Redirige /api/* al backend Python                      │
│    - Gestiona SSL/TLS                                       │
└────────────┬──────────────────────────────┬────────────────┘
             │ Proxy /api/*                  │ Estáticos
             ▼                              ▼
┌────────────────────────┐    ┌─────────────────────────┐
│   BACKEND PYTHON       │    │   ARCHIVOS ESTÁTICOS     │
│   Flask 3 + Gunicorn   │    │   /frontend/*.html       │
│   Puerto: 8000         │    │   /frontend/*.js         │
│   4 workers, 2 threads │    │   /frontend/*.css        │
└──────────┬─────────────┘    └─────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    POSTGRESQL 15+                           │
│              (local o servicio externo cloud)               │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│              ALMACENAMIENTO DE ARCHIVOS                     │
│    /data/docs/               — Documentos subidos           │
│    /data/auditoria_reportes/ — Reportes PDF generados       │
│    /data/fotos_reportes/     — Fotos de fiscalización       │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Módulos del Backend (Blueprints)

| Módulo | Descripción | Ruta API |
|--------|-------------|----------|
| `auth_routes` | Login, logout, emisión y validación de JWT | `/api/auth/login`, `/api/auth/logout` |
| `users_routes` | Gestión de usuarios y roles RBAC | `/api/users/*`, `/api/roles/*` |
| `proyectos_routes` | Fichas de proyectos y estados de avance | `/api/proyectos/*` |
| `licitaciones_routes` | Control de licitaciones y adjudicaciones | `/api/licitaciones/*` |
| `documentos_routes` | Mapas GeoJSON e hitos geográficos | `/api/geomapas/*`, `/api/hitos/*` |
| `control_routes` | Dashboard gerencial y KPIs | `/api/control/*` |
| `auditoria_routes` | Generación masiva de reportes PDF | `/api/auditoria/*` |
| `calendario_routes` | Gestión de calendario de actividades | `/api/calendario/*` |
| `mobile_routes` | API para app móvil de fiscalizadores | `/api/mobile/*` |

### 3.4 Puertos y Endpoints Importantes

| Servicio | Puerto | URL |
|----------|--------|-----|
| Backend API (Gunicorn) | `8000` | `http://localhost:8000` |
| Frontend (Nginx) | `80` / `443` | `http://<IP_SERVIDOR>` |
| PostgreSQL | `5432` | Solo acceso interno |
| Health Check | `8000` | `http://localhost:8000/health` |

---

## 4. Requisitos Previos

### 4.1 Hardware Mínimo Recomendado

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 2 núcleos | 4 núcleos |
| RAM | 2 GB | 4 GB |
| Disco | 20 GB | 50 GB (para almacenamiento de documentos) |
| Red | 10 Mbps | 100 Mbps |

### 4.2 Software Requerido

| Software | Versión mínima | Notas |
|----------|----------------|-------|
| Sistema Operativo | Ubuntu 22.04 LTS o Windows Server 2019 | Ver rutas A/B/C |
| Python | 3.11 | Obligatorio. 3.10 funciona pero no es recomendado |
| pip | 23.0+ | Viene con Python |
| PostgreSQL | 15 | Puede ser local o servicio externo |
| Git | 2.x | Para clonar el repositorio |
| Nginx | 1.18+ | Servidor web inverso (recomendado) |
| Docker | 24.x | Solo para Ruta A |
| Tesseract OCR | 4.1+ | Para procesamiento de documentos escaneados |

### 4.3 Puertos que Deben Estar Abiertos en el Firewall

| Puerto | Protocolo | Dirección | Descripción |
|--------|-----------|-----------|-------------|
| `80` | TCP | Entrada | HTTP (Nginx) |
| `443` | TCP | Entrada | HTTPS (Nginx con SSL) |
| `8000` | TCP | Solo local | Backend Python (NO exponer a internet) |
| `5432` | TCP | Solo local | PostgreSQL (NO exponer a internet) |

> **ADVERTENCIA:** Los puertos `8000` y `5432` NO deben estar expuestos a internet directamente. Solo deben ser accesibles internamente desde el mismo servidor.

### 4.4 Permisos de Usuario

Se necesita un usuario con permisos `sudo` para la instalación. Posteriormente, la aplicación se ejecutará con un usuario de sistema sin privilegios elevados para mayor seguridad.

---

## 5. Preparación del Servidor

### 5.1 [RUTA B] Preparación en Ubuntu Server 22.04 LTS

#### 5.1.1 Actualizar el Sistema

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 5.1.2 Crear Usuario de Aplicación

```bash
# Crear usuario de sistema para ejecutar la aplicación (sin shell de login)
sudo useradd --system --no-create-home --shell /bin/false secplac

# Crear la carpeta de instalación
sudo mkdir -p /opt/secplac
sudo chown secplac:secplac /opt/secplac

# Crear la carpeta de datos persistentes
sudo mkdir -p /data/docs /data/auditoria_reportes /data/fotos_reportes
sudo chown -R secplac:secplac /data
```

#### 5.1.3 Configurar el Firewall (ufw)

```bash
# Permitir SSH (para administración remota)
sudo ufw allow OpenSSH

# Permitir tráfico HTTP y HTTPS (Nginx)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activar el firewall
sudo ufw enable

# Verificar estado
sudo ufw status
```

### 5.2 [RUTA C] Preparación en Windows Server 2019/2022

#### 5.2.1 Configurar el Firewall de Windows

Abrir el **Panel de Control → Sistema y Seguridad → Firewall de Windows Defender → Configuración avanzada**:

1. Hacer clic en **Reglas de entrada** → **Nueva regla...**
2. Seleccionar **Puerto** → TCP → Puertos específicos locales: `80, 443`
3. Seleccionar **Permitir la conexión**
4. Aplicar a: Dominio, Privado, Público
5. Nombre: `SECPLAC HTTP/HTTPS`
6. Hacer clic en **Finalizar**

#### 5.2.2 Crear Carpetas de Instalación

Abrir PowerShell como Administrador:

```powershell
# Crear carpeta de instalación
New-Item -ItemType Directory -Force -Path "C:\secplac"
New-Item -ItemType Directory -Force -Path "C:\secplac\data\docs"
New-Item -ItemType Directory -Force -Path "C:\secplac\data\auditoria_reportes"
New-Item -ItemType Directory -Force -Path "C:\secplac\data\fotos_reportes"
```

---

## 6. Instalación de Dependencias del Sistema

### 6.1 [RUTA A] Con Docker (Ubuntu)

#### 6.1.1 Instalar Docker

```bash
# Instalar dependencias de Docker
sudo apt-get install -y ca-certificates curl gnupg

# Agregar clave GPG oficial de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Agregar repositorio de Docker
echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Actualizar e instalar Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verificar instalación
sudo docker run hello-world
```

#### 6.1.2 Instalar Nginx

```bash
sudo apt-get install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 6.2 [RUTA B] Instalación Directa en Ubuntu

#### 6.2.1 Instalar Python 3.11

```bash
# Agregar repositorio de Python más reciente
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update

# Instalar Python 3.11 y herramientas
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# Verificar versión
python3.11 --version
# Salida esperada: Python 3.11.x
```

#### 6.2.2 Instalar Dependencias de Sistema para el Backend

```bash
# Instalar bibliotecas del sistema requeridas
sudo apt-get install -y \
    libpq-dev \
    gcc \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    antiword \
    git \
    nginx

# Verificar Tesseract
tesseract --version
# Salida esperada: tesseract 4.x.x o 5.x.x

# Verificar que el idioma español está disponible
tesseract --list-langs
# Debe incluir "spa" en la lista
```

#### 6.2.3 Instalar PostgreSQL (si se usará local)

```bash
# Agregar repositorio oficial de PostgreSQL
sudo apt-get install -y curl ca-certificates
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc

# Agregar el repositorio
sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

# Instalar PostgreSQL 15
sudo apt-get update
sudo apt-get install -y postgresql-15 postgresql-client-15

# Iniciar y habilitar el servicio
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Verificar versión
psql --version
# Salida esperada: psql (PostgreSQL) 15.x
```

### 6.3 [RUTA C] Instalación en Windows Server

#### 6.3.1 Instalar Python 3.11

1. Abrir el navegador y descargar desde: `https://www.python.org/downloads/` el instalador de **Python 3.11.x** para Windows (64-bit).
2. Ejecutar el instalador `.exe` como Administrador.
3. **IMPORTANTE:** Marcar la casilla **"Add Python to PATH"** antes de hacer clic en Install Now.
4. Verificar en PowerShell:

```powershell
python --version
# Salida esperada: Python 3.11.x

pip --version
# Salida esperada: pip 23.x.x from ...
```

#### 6.3.2 Instalar Git

1. Descargar desde: `https://git-scm.com/download/win`
2. Ejecutar el instalador como Administrador.
3. Dejar las opciones por defecto.
4. Verificar:

```powershell
git --version
# Salida esperada: git version 2.x.x.windows.x
```

#### 6.3.3 Instalar Tesseract OCR en Windows

1. Descargar el instalador desde: `https://github.com/UB-Mannheim/tesseract/wiki`
2. Ejecutar el instalador. Seleccionar idioma adicional: **Spanish**.
3. Anotar la ruta de instalación (por defecto: `C:\Program Files\Tesseract-OCR\`).
4. Agregar a la variable de entorno PATH:

```powershell
# Agregar Tesseract al PATH del sistema
$env:PATH += ";C:\Program Files\Tesseract-OCR"
[System.Environment]::SetEnvironmentVariable("PATH", $env:PATH, [System.EnvironmentVariableTarget]::Machine)
```

#### 6.3.4 Instalar PostgreSQL en Windows (si se usará local)

1. Descargar desde: `https://www.postgresql.org/download/windows/`
2. Ejecutar el instalador de **PostgreSQL 15** como Administrador.
3. Durante la instalación:
   - Puerto: `5432` (por defecto)
   - Anotar la contraseña del usuario `postgres`
4. Verificar en PowerShell:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" --version
```

---

## 7. Clonado y Configuración del Proyecto

### 7.1 Clonar el Repositorio

#### [RUTA B] En Ubuntu:

```bash
# Ir a la carpeta de instalación
cd /opt/secplac

# Clonar el repositorio
sudo -u secplac git clone https://github.com/geoportalalgarrobo/ALGARROBO_BASE2.git .

# Verificar que los archivos están presentes
ls -la /opt/secplac/
# Deben aparecer las carpetas: backend/, frontend/, database/, docs/
```

#### [RUTA C] En Windows Server:

```powershell
# Ir a la carpeta de instalación
cd C:\secplac

# Clonar el repositorio
git clone https://github.com/geoportalalgarrobo/ALGARROBO_BASE2.git .

# Verificar que los archivos están presentes
dir C:\secplac
```

### 7.2 Crear el Entorno Virtual de Python

Un entorno virtual aísla las dependencias de Python de esta aplicación para que no entren en conflicto con otras instalaciones del sistema.

#### [RUTA B] En Ubuntu:

```bash
# Posicionarse en la carpeta raíz del proyecto
cd /opt/secplac

# Crear el entorno virtual con Python 3.11
sudo -u secplac python3.11 -m venv venv

# Activar el entorno virtual
source venv/bin/activate

# Verificar que se activó correctamente (debe aparecer "(venv)" al inicio del prompt)
which python
# Salida esperada: /opt/secplac/venv/bin/python
```

#### [RUTA C] En Windows Server:

```powershell
# Posicionarse en la carpeta raíz del proyecto
cd C:\secplac

# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# Si aparece error de permisos de ejecución, ejecutar primero:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verificar que se activó (debe aparecer "(venv)" al inicio del prompt)
where python
```

### 7.3 Instalar Dependencias de Python

```bash
# [RUTA B] Ubuntu — con el entorno virtual activado:
cd /opt/secplac
pip install --upgrade pip
pip install -r backend/requirements.txt
```

```powershell
# [RUTA C] Windows — con el entorno virtual activado:
cd C:\secplac
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

> **NOTA:** Este proceso puede tomar entre 2 y 5 minutos dependiendo de la velocidad de internet. Se instalarán las siguientes bibliotecas principales: Flask 3.0, Gunicorn 21.2, psycopg2 (cliente PostgreSQL), bcrypt, PyJWT, ReportLab, pytesseract, python-docx, openpyxl, entre otras.

---

## 8. Variables de Entorno

Las variables de entorno son parámetros de configuración que la aplicación lee al iniciar. Se deben definir en un archivo `.env` dentro de la carpeta `backend/`.

### 8.1 Crear el Archivo `.env`

#### [RUTA B] En Ubuntu:

```bash
# Crear el archivo .env en la carpeta backend
sudo -u secplac nano /opt/secplac/backend/.env
```

#### [RUTA C] En Windows Server:

```powershell
# Crear el archivo .env con el Bloc de Notas
notepad C:\secplac\backend\.env
```

### 8.2 Contenido del Archivo `.env`

Copiar el siguiente contenido y reemplazar los placeholders con los valores reales:

```dotenv
# ============================================================
# ARCHIVO DE CONFIGURACIÓN — SISTEMA SECPLAC ALGARROBO
# ============================================================
# IMPORTANTE: Este archivo contiene información sensible.
# NO subir este archivo a GitHub ni compartirlo.

# --- Base de Datos (OBLIGATORIO) ---
# Formato: postgresql://USUARIO:CONTRASEÑA@HOST:PUERTO/NOMBRE_BD
DATABASE_URL=postgresql://<USUARIO_BD>:<PASSWORD_BD>@<HOST_BD>:5432/<NOMBRE_BD>

# --- Seguridad JWT (OBLIGATORIO) ---
# Clave secreta para firmar los tokens de sesión.
# DEBE ser una cadena aleatoria larga (mínimo 64 caracteres).
# Generarla con: python -c "import secrets; print(secrets.token_hex(64))"
JWT_SECRET_KEY=<GENERAR_CLAVE_ALEATORIA_LARGA>

# --- CORS: Orígenes permitidos (OBLIGATORIO en producción) ---
# El dominio o IP desde donde accederán los usuarios.
# Ejemplo: https://secplac.algarrobo.cl
# Para múltiples orígenes: https://dominio1.cl,https://dominio2.cl
ALLOWED_ORIGINS=http://<DOMINIO_O_IP_SERVIDOR>

# --- Puerto de escucha (OPCIONAL, por defecto 8000) ---
PORT=8000

# --- Correo electrónico para notificaciones (OPCIONAL) ---
# Si se usará la función de envío de correos del sistema
BREVO_SMTP_LOGIN=<LOGIN_SMTP>
BREVO_SMTP_KEY=<API_KEY_BREVO>
REMITENTE=<EMAIL_REMITENTE>
REPLY_TO=<EMAIL_REPLY_TO>

# --- Directorio de archivos persistentes ---
# En Linux: /data (ruta absoluta recomendada)
# En Windows: C:\secplac\data
AUDIT_OUT_DIR=/data/auditoria_reportes

# --- Modo debug (SIEMPRE False en producción) ---
FLASK_DEBUG=False

# --- Tiempo de expiración de sesión (en horas) ---
SESSION_EXPIRY_HOURS=24
```

### 8.3 Descripción de Variables de Entorno

| Variable | Obligatoria | Descripción | Ejemplo |
|----------|:-----------:|-------------|---------|
| `DATABASE_URL` | **Sí** | Cadena de conexión a PostgreSQL. Incluye usuario, contraseña, host, puerto y nombre de la BD. | `postgresql://secplac_user:pass123@localhost:5432/secplac_db` |
| `JWT_SECRET_KEY` | **Sí** | Clave criptográfica para firmar tokens de sesión. Si se cambia, todos los usuarios deberán volver a iniciar sesión. | Cadena aleatoria de 64+ caracteres |
| `ALLOWED_ORIGINS` | **Sí** | Dominio(s) desde donde se permite el acceso al API (CORS). En producción debe ser el dominio real, no `*`. | `https://secplac.algarrobo.cl` |
| `PORT` | No | Puerto en que escuchará Gunicorn. | `8000` |
| `BREVO_SMTP_LOGIN` | No | Login del servidor SMTP de Brevo para envío de correos. | `usuario@smtp-brevo.com` |
| `BREVO_SMTP_KEY` | No | API Key del servicio de correos Brevo. | `xsmtpsib-...` |
| `REMITENTE` | No | Dirección de correo que aparece como remitente en las notificaciones. | `secplac@algarrobo.cl` |
| `REPLY_TO` | No | Dirección de respuesta en los correos enviados. | `secplac@algarrobo.cl` |
| `AUDIT_OUT_DIR` | No | Ruta del directorio donde se guardan los reportes de auditoría generados. | `/data/auditoria_reportes` |
| `FLASK_DEBUG` | No | Activa/desactiva el modo debug de Flask. **SIEMPRE `False` en producción.** | `False` |
| `SESSION_EXPIRY_HOURS` | No | Horas de validez de la sesión de usuario. | `24` |

### 8.4 Cómo Generar la `JWT_SECRET_KEY`

```bash
# [RUTA B] En Ubuntu, ejecutar este comando para generar una clave segura:
python3 -c "import secrets; print(secrets.token_hex(64))"

# Copiar el resultado y pegarlo como valor de JWT_SECRET_KEY en el .env
```

```powershell
# [RUTA C] En Windows PowerShell:
python -c "import secrets; print(secrets.token_hex(64))"
```

---

## 9. Configuración de Base de Datos

### 9.1 Opción A: PostgreSQL Local (Ubuntu)

#### 9.1.1 Crear la Base de Datos y el Usuario

```bash
# Cambiar al usuario postgres del sistema
sudo -u postgres psql

# Dentro de la consola de PostgreSQL (el prompt cambia a "postgres=#"):

# Crear usuario para la aplicación
CREATE USER <USUARIO_BD> WITH PASSWORD '<PASSWORD_BD>';

# Crear la base de datos
CREATE DATABASE <NOMBRE_BD> OWNER <USUARIO_BD>;

# Otorgar todos los permisos al usuario en la base de datos
GRANT ALL PRIVILEGES ON DATABASE <NOMBRE_BD> TO <USUARIO_BD>;

# Salir de la consola de PostgreSQL
\q
```

#### 9.1.2 Verificar la Conexión

```bash
# Probar la conexión con el usuario creado
psql -U <USUARIO_BD> -d <NOMBRE_BD> -h localhost -W

# Si se conecta correctamente, aparecerá el prompt: <NOMBRE_BD>=#
# Salir con:
\q
```

#### 9.1.3 Cargar el Esquema Inicial de la Base de Datos

```bash
# Cargar el esquema principal
psql -U <USUARIO_BD> -d <NOMBRE_BD> -h localhost -W -f /opt/secplac/database/database.sql

# Cargar scripts de módulos adicionales (en este orden):
psql -U <USUARIO_BD> -d <NOMBRE_BD> -h localhost -W -f /opt/secplac/database/login.sql
psql -U <USUARIO_BD> -d <NOMBRE_BD> -h localhost -W -f /opt/secplac/database/proyectos.sql
psql -U <USUARIO_BD> -d <NOMBRE_BD> -h localhost -W -f /opt/secplac/database/licitaciones.sql
psql -U <USUARIO_BD> -d <NOMBRE_BD> -h localhost -W -f /opt/secplac/database/control.sql
psql -U <USUARIO_BD> -d <NOMBRE_BD> -h localhost -W -f /opt/secplac/database/triggers.sql
```

### 9.2 Opción B: PostgreSQL en Windows Server

```powershell
# Abrir la consola de PostgreSQL como administrador
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres

# Dentro de la consola de PostgreSQL:
# (Reemplazar <USUARIO_BD>, <PASSWORD_BD> y <NOMBRE_BD> con valores reales)
```

```sql
-- Crear usuario para la aplicación
CREATE USER secplac_user WITH PASSWORD 'contraseña_segura_aqui';

-- Crear la base de datos
CREATE DATABASE secplac_db OWNER secplac_user;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE secplac_db TO secplac_user;

-- Salir
\q
```

```powershell
# Cargar el esquema
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U secplac_user -d secplac_db -h localhost -f "C:\secplac\database\database.sql"
```

### 9.3 Opción C: Base de Datos Externa (Cloud)

Si la municipalidad ya tiene una instancia de PostgreSQL en la nube (AWS RDS, Azure PostgreSQL, Neon.tech, etc.), solo se debe configurar la `DATABASE_URL` en el archivo `.env` con la cadena de conexión proporcionada por el proveedor.

El formato es:
```
postgresql://USUARIO:CONTRASEÑA@HOST_EXTERNO:PUERTO/NOMBRE_BD?sslmode=require
```

> **NOTA:** Para bases de datos en la nube, es habitual que la URL incluya `?sslmode=require` al final, lo cual fuerza el uso de SSL en la conexión. Esto es correcto y obligatorio para la seguridad.

---

## 10. Build y Despliegue

### 10.1 [RUTA A] Despliegue con Docker

#### 10.1.1 Construir la Imagen Docker

```bash
# Posicionarse en la raíz del proyecto
cd /opt/secplac

# Construir la imagen Docker
# Este proceso tomará 5-10 minutos la primera vez
sudo docker build -t secplac-algarrobo:latest .

# Verificar que la imagen fue creada
sudo docker images | grep secplac
```

#### 10.1.2 Ejecutar el Contenedor

```bash
# Ejecutar el contenedor con las variables de entorno y el volumen de datos
sudo docker run -d \
    --name secplac-backend \
    --restart unless-stopped \
    --env-file /opt/secplac/backend/.env \
    -p 127.0.0.1:8000:8000 \
    -v /data:/data \
    secplac-algarrobo:latest

# Verificar que el contenedor está corriendo
sudo docker ps | grep secplac

# Ver los logs en tiempo real (presionar Ctrl+C para salir)
sudo docker logs -f secplac-backend
```

> **IMPORTANTE:** El parámetro `-p 127.0.0.1:8000:8000` enlaza el puerto solo a la interfaz local (`127.0.0.1`). Esto significa que el backend NO es accesible directamente desde internet, solo a través de Nginx. Esto es una medida de seguridad obligatoria.

### 10.2 [RUTA B] Despliegue Directo en Ubuntu

#### 10.2.1 Prueba de Inicio Manual

Antes de configurar el servicio, verificar que la aplicación inicia correctamente:

```bash
# Activar el entorno virtual
cd /opt/secplac
source venv/bin/activate

# Ir a la carpeta backend
cd backend

# Iniciar Gunicorn manualmente (modo prueba)
gunicorn app_railway:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 300 \
    --log-level info

# Dejar corriendo y en otra terminal probar:
# curl http://localhost:8000/health
# Presionar Ctrl+C para detener
```

#### 10.2.2 Verificar la Respuesta

```bash
# En una segunda terminal (mientras Gunicorn está corriendo):
curl http://localhost:8000/health

# La respuesta debe ser similar a:
# {"status": "healthy", "database": {"status": "connected"}, ...}
```

### 10.3 [RUTA C] Despliegue en Windows Server

```powershell
# Activar el entorno virtual
cd C:\secplac
.\venv\Scripts\Activate.ps1

# Ir a la carpeta backend
cd backend

# Iniciar Gunicorn manualmente (modo prueba)
gunicorn app_railway:app --bind 0.0.0.0:8000 --workers 2 --threads 2 --timeout 300

# En otra ventana de PowerShell, probar:
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

> **NOTA para Windows:** Gunicorn tiene soporte limitado en Windows. Si presenta problemas, se puede usar `waitress` como alternativa:
> ```powershell
> pip install waitress
> waitress-serve --listen=0.0.0.0:8000 --threads=4 app_railway:app
> ```

---

## 11. Configuración como Servicio del Sistema

Configurar la aplicación como servicio permite que se inicie automáticamente cuando el servidor se reinicia.

### 11.1 [RUTA B] Servicio systemd en Ubuntu

#### 11.1.1 Crear el Archivo de Servicio

```bash
# Crear el archivo de definición del servicio
sudo nano /etc/systemd/system/secplac.service
```

Pegar el siguiente contenido (reemplazar los placeholders):

```ini
[Unit]
Description=SECPLAC Algarrobo — Backend API
Documentation=https://github.com/geoportalalgarrobo/ALGARROBO_BASE2
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=secplac
Group=secplac
WorkingDirectory=/opt/secplac/backend
Environment="PATH=/opt/secplac/venv/bin"
EnvironmentFile=/opt/secplac/backend/.env
ExecStart=/opt/secplac/venv/bin/gunicorn app_railway:app \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 300 \
    --log-level info \
    --access-logfile /var/log/secplac/access.log \
    --error-logfile /var/log/secplac/error.log
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

#### 11.1.2 Crear Carpeta de Logs y Activar el Servicio

```bash
# Crear la carpeta de logs
sudo mkdir -p /var/log/secplac
sudo chown secplac:secplac /var/log/secplac

# Recargar la configuración de systemd
sudo systemctl daemon-reload

# Habilitar el servicio (se inicia automáticamente con el servidor)
sudo systemctl enable secplac

# Iniciar el servicio ahora
sudo systemctl start secplac

# Verificar el estado del servicio
sudo systemctl status secplac

# La salida debe mostrar: Active: active (running)
```

#### 11.1.3 Comandos de Gestión del Servicio

```bash
# Iniciar el servicio
sudo systemctl start secplac

# Detener el servicio
sudo systemctl stop secplac

# Reiniciar el servicio (por ejemplo, tras cambiar el .env)
sudo systemctl restart secplac

# Ver los logs en tiempo real
sudo journalctl -u secplac -f

# Ver los últimos 100 líneas del log
sudo journalctl -u secplac -n 100
```

### 11.2 [RUTA C] Servicio Windows con NSSM

NSSM (Non-Sucking Service Manager) permite registrar cualquier ejecutable como servicio de Windows.

#### 11.2.1 Instalar NSSM

1. Descargar desde: `https://nssm.cc/download`
2. Extraer y copiar `nssm.exe` a `C:\Windows\System32\`

#### 11.2.2 Registrar la Aplicación como Servicio

```powershell
# Abrir PowerShell como Administrador

# Registrar el servicio
nssm install SECPLAC "C:\secplac\venv\Scripts\gunicorn.exe"

# Configurar argumentos
nssm set SECPLAC AppParameters "app_railway:app --bind 127.0.0.1:8000 --workers 2 --threads 2 --timeout 300"

# Configurar directorio de trabajo
nssm set SECPLAC AppDirectory "C:\secplac\backend"

# Configurar variables de entorno
nssm set SECPLAC AppEnvironmentExtra "PYTHONPATH=C:\secplac\backend"

# Configurar logs
nssm set SECPLAC AppStdout "C:\secplac\logs\secplac.log"
nssm set SECPLAC AppStderr "C:\secplac\logs\secplac_error.log"

# Crear carpeta de logs
New-Item -ItemType Directory -Force -Path "C:\secplac\logs"

# Iniciar el servicio
nssm start SECPLAC

# Verificar estado
nssm status SECPLAC
```

---

## 12. Configuración de Servidor Web Inverso y SSL

Nginx actúa como intermediario entre internet y la aplicación Python. Se encarga de servir los archivos estáticos del frontend directamente (sin pasar por Python) y de redirigir las peticiones de la API al backend.

### 12.1 [RUTA B] Configuración de Nginx en Ubuntu

#### 12.1.1 Crear el Archivo de Configuración de Nginx

```bash
# Crear el archivo de configuración
sudo nano /etc/nginx/sites-available/secplac
```

Pegar el siguiente contenido (reemplazar `<DOMINIO>` o `<IP_SERVIDOR>`):

```nginx
server {
    listen 80;
    server_name <DOMINIO> <IP_SERVIDOR>;

    # Logs de acceso y error
    access_log /var/log/nginx/secplac_access.log;
    error_log /var/log/nginx/secplac_error.log;

    # Tamaño máximo de subida de archivos (1 GB para migración de archivos históricos)
    client_max_body_size 1000M;

    # ── Frontend estático ──────────────────────────────────────
    root /opt/secplac/frontend;
    index index.html;

    # Servir archivos estáticos del frontend directamente
    location / {
        try_files $uri $uri/ /index.html;
    }

    # ── Backend API Python ─────────────────────────────────────
    # Redirigir todas las peticiones /api/* al servidor Gunicorn
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 75s;
        proxy_read_timeout 300s;
    }

    # Health check del backend
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Servir fotos de reportes desde el volumen de datos
    location /fotos_reportes/ {
        alias /data/fotos_reportes/;
    }
}
```

#### 12.1.2 Activar el Sitio

```bash
# Crear enlace simbólico para activar el sitio
sudo ln -s /etc/nginx/sites-available/secplac /etc/nginx/sites-enabled/secplac

# Remover el sitio por defecto de Nginx (opcional pero recomendado)
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar que la configuración de Nginx es válida
sudo nginx -t
# Salida esperada: 
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# Recargar Nginx para aplicar los cambios
sudo systemctl reload nginx
```

### 12.2 Configuración de SSL/HTTPS con Let's Encrypt (si aplica)

> **NOTA:** Esta sección aplica solo si el servidor tiene un dominio público (ej: `secplac.algarrobo.cl`) y acceso a internet. Si el servidor es solo interno (red LAN municipal), se debe usar un certificado propio emitido por la CA de la municipalidad.

```bash
# Instalar Certbot (cliente de Let's Encrypt)
sudo apt-get install -y certbot python3-certbot-nginx

# Obtener e instalar el certificado SSL automáticamente
# Reemplazar <DOMINIO> con el dominio real
sudo certbot --nginx -d <DOMINIO>

# Certbot modificará automáticamente el archivo de configuración de Nginx
# para añadir HTTPS en el puerto 443 y redirigir HTTP a HTTPS.

# Verificar renovación automática
sudo certbot renew --dry-run
```

---

## 13. Verificación Post-Instalación

Ejecutar cada verificación en orden. Marcar cada ítem al completarlo.

### 13.1 Checklist de Verificación

| # | Verificación | Comando / Acción | Estado |
|---|-------------|-----------------|:------:|
| 1 | El servicio `secplac` está activo | `sudo systemctl status secplac` → debe decir `Active: active (running)` | ☐ |
| 2 | El servicio `nginx` está activo | `sudo systemctl status nginx` → `Active: active (running)` | ☐ |
| 3 | El servicio `postgresql` está activo | `sudo systemctl status postgresql` | ☐ |
| 4 | El health check responde | `curl http://localhost:8000/health` → `{"status": "healthy"}` | ☐ |
| 5 | La base de datos está conectada | En la respuesta del health check: `"database": {"status": "connected"}` | ☐ |
| 6 | Nginx sirve el frontend | Abrir `http://<IP_SERVIDOR>` en el navegador → debe cargar la interfaz | ☐ |
| 7 | El login funciona | Ir a la página de login e ingresar con credenciales de administrador | ☐ |
| 8 | Los directorios de datos existen | `ls /data/docs /data/auditoria_reportes /data/fotos_reportes` (Linux) | ☐ |
| 9 | Los permisos son correctos | `ls -la /data/` → el propietario debe ser `secplac` | ☐ |
| 10 | El módulo de auditoría carga | Navegar al módulo de Auditoría en la interfaz web | ☐ |
| 11 | Los logs no muestran errores críticos | `sudo journalctl -u secplac -n 50 \| grep -i error` → no debe haber errores | ☐ |
| 12 | HTTPS funciona (si aplica) | Abrir `https://<DOMINIO>` → candado verde en el navegador | ☐ |

### 13.2 Comandos de Verificación Detallados

```bash
# 1. Probar el health check completo
curl -s http://localhost:8000/health | python3 -m json.tool

# 2. Verificar que la API responde en la ruta base
curl -s http://localhost:8000/ | python3 -m json.tool
# Salida esperada:
# {
#   "message": "SECPLAC ALGARROBO API - Railway Edition",
#   "status": "online",
#   ...
# }

# 3. Verificar que Nginx redirige correctamente al backend
curl -s http://<IP_SERVIDOR>/health

# 4. Verificar los logs del backend
sudo journalctl -u secplac -n 20

# 5. Verificar el espacio en disco
df -h /data
```

---

## 14. Problemas Frecuentes y Soluciones

### 14.1 Error: `psycopg2.OperationalError: could not connect to server`

**Síntoma:** El servicio inicia pero el health check muestra `"database": {"status": "error"}` o el backend no arranca.

**Causa probable:** La cadena de conexión `DATABASE_URL` en el archivo `.env` es incorrecta, o PostgreSQL no está escuchando.

**Solución:**
```bash
# 1. Verificar que PostgreSQL está activo
sudo systemctl status postgresql

# 2. Verificar la conexión con los mismos parámetros que usa el .env
psql "postgresql://<USUARIO_BD>:<PASSWORD_BD>@<HOST_BD>:5432/<NOMBRE_BD>"

# 3. Si es local, verificar que PostgreSQL escucha en todas las interfaces
sudo nano /etc/postgresql/15/main/postgresql.conf
# Buscar y modificar: listen_addresses = 'localhost'
# Reiniciar: sudo systemctl restart postgresql

# 4. Verificar el archivo pg_hba.conf para permisos de conexión
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

---

### 14.2 Error: `ModuleNotFoundError: No module named 'flask'`

**Síntoma:** Al iniciar el servicio, falla con un error de módulo no encontrado.

**Causa probable:** El servicio systemd no está usando el entorno virtual de Python donde están instaladas las dependencias.

**Solución:**
```bash
# Verificar la ruta del entorno virtual en el servicio
sudo nano /etc/systemd/system/secplac.service

# Asegurarse de que estas líneas están presentes:
# Environment="PATH=/opt/secplac/venv/bin"
# ExecStart=/opt/secplac/venv/bin/gunicorn ...
# (La ruta debe apuntar al gunicorn DEL entorno virtual, no al del sistema)

# Recargar y reiniciar
sudo systemctl daemon-reload
sudo systemctl restart secplac
```

---

### 14.3 Error: `CORS Policy blocked request` en el navegador

**Síntoma:** La interfaz carga pero las peticiones al backend fallan con un error de CORS en la consola del navegador.

**Causa probable:** La variable `ALLOWED_ORIGINS` en el `.env` no coincide con el dominio desde donde se accede.

**Solución:**
```bash
# Editar el archivo .env
sudo nano /opt/secplac/backend/.env

# Cambiar ALLOWED_ORIGINS al dominio exacto con protocolo:
# ALLOWED_ORIGINS=http://192.168.1.100
# o
# ALLOWED_ORIGINS=https://secplac.algarrobo.cl

# Reiniciar el servicio
sudo systemctl restart secplac
```

---

### 14.4 Error: `[Errno 13] Permission denied` en la carpeta `/data`

**Síntoma:** El backend inicia pero falla al intentar guardar documentos o generar reportes.

**Causa probable:** El usuario `secplac` no tiene permisos de escritura en `/data`.

**Solución:**
```bash
# Cambiar el propietario de la carpeta /data al usuario secplac
sudo chown -R secplac:secplac /data

# Verificar permisos
ls -la /data/
# El propietario debe ser secplac:secplac

# Reiniciar el servicio
sudo systemctl restart secplac
```

---

### 14.5 Error: `tesseract is not installed or it's not in your PATH`

**Síntoma:** El módulo de procesamiento de documentos (OCR) falla al procesar imágenes o PDFs escaneados.

**Causa probable:** Tesseract OCR no está instalado o no está en el PATH del usuario `secplac`.

**Solución:**
```bash
# Verificar si Tesseract está instalado
which tesseract
tesseract --version

# Si no está instalado:
sudo apt-get install -y tesseract-ocr tesseract-ocr-spa

# Verificar que el idioma español está disponible
tesseract --list-langs
# Debe incluir "spa"

# Reiniciar el servicio
sudo systemctl restart secplac
```

---

### 14.6 Error: `502 Bad Gateway` en Nginx

**Síntoma:** Nginx responde con error 502 al acceder a rutas de la API (`/api/*`).

**Causa probable:** El backend Python (Gunicorn) no está corriendo, o hay un error al iniciarlo.

**Solución:**
```bash
# 1. Verificar el estado del servicio backend
sudo systemctl status secplac

# 2. Ver los últimos errores del backend
sudo journalctl -u secplac -n 50

# 3. Verificar que Gunicorn está escuchando en el puerto 8000
sudo ss -tlnp | grep 8000
# Debe aparecer una línea con 127.0.0.1:8000

# 4. Si el servicio está caído, intentar iniciarlo manualmente para ver el error
cd /opt/secplac/backend
source /opt/secplac/venv/bin/activate
gunicorn app_railway:app --bind 127.0.0.1:8000
```

---

### 14.7 Error: `JWT decode error` / `Token inválido`

**Síntoma:** Los usuarios no pueden iniciar sesión o sus sesiones expiran inmediatamente después de un reinicio del servicio.

**Causa probable:** La `JWT_SECRET_KEY` cambió (o no estaba definida y se usó la fallback), invalidando todos los tokens existentes.

**Solución:**
```bash
# Verificar que JWT_SECRET_KEY está definida en el .env
grep JWT_SECRET_KEY /opt/secplac/backend/.env

# Si está vacía o usa el valor por defecto del código, generar una nueva:
python3 -c "import secrets; print(secrets.token_hex(64))"

# Pegar el resultado en el .env
sudo nano /opt/secplac/backend/.env

# Reiniciar (esto forzará a todos los usuarios a volver a loguearse)
sudo systemctl restart secplac
```

---

### 14.8 Error: `Too many connections` en PostgreSQL

**Síntoma:** El sistema funciona bien al inicio pero comienza a mostrar errores de conexión bajo carga.

**Causa probable:** El pool de conexiones (`maxconn=20`) está agotado porque PostgreSQL tiene un límite bajo de conexiones simultáneas.

**Solución:**
```bash
# Verificar el límite actual de conexiones en PostgreSQL
sudo -u postgres psql -c "SHOW max_connections;"

# Si es bajo (ej: 100), aumentarlo
sudo nano /etc/postgresql/15/main/postgresql.conf

# Buscar y modificar:
# max_connections = 200

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# También verificar el número de conexiones activas en este momento
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

---

### 14.9 Error: El Frontend Carga pero la Interfaz Aparece en Blanco

**Síntoma:** Nginx devuelve el HTML pero la interfaz no renderiza contenido.

**Causa probable:** Los archivos JavaScript están intentando conectarse a una URL de backend incorrecta (hardcodeada a `railway.app` en lugar de la IP del servidor municipal).

**Solución:**
```bash
# Buscar referencias hardcodeadas al dominio antiguo de Railway
grep -r "railway.app" /opt/secplac/frontend/

# Si se encuentran referencias, reemplazarlas con la nueva URL
# (el equipo de desarrollo debe proporcionar instrucciones específicas)
```

---

### 14.10 Error: `gunicorn: command not found` al iniciar el servicio

**Síntoma:** El servicio systemd falla con `gunicorn: command not found`.

**Causa probable:** El archivo `.service` apunta al `gunicorn` del sistema en lugar del del entorno virtual.

**Solución:**
```bash
# Verificar la ubicación correcta de gunicorn en el entorno virtual
ls /opt/secplac/venv/bin/gunicorn

# Editar el servicio para usar la ruta absoluta
sudo nano /etc/systemd/system/secplac.service

# La línea ExecStart DEBE comenzar con la ruta absoluta:
# ExecStart=/opt/secplac/venv/bin/gunicorn app_railway:app ...

# Recargar y reiniciar
sudo systemctl daemon-reload
sudo systemctl restart secplac
```

---

## 15. Mantenimiento

### 15.1 Respaldos

#### 15.1.1 Respaldo de la Base de Datos

```bash
# Crear respaldo de la base de datos en formato comprimido
pg_dump -U <USUARIO_BD> -h localhost -d <NOMBRE_BD> -Fc -f /backup/secplac_$(date +%Y%m%d_%H%M).dump

# Verificar que el archivo fue creado
ls -lh /backup/secplac_*.dump
```

#### 15.1.2 Automatizar Respaldos con Cron (Ubuntu)

```bash
# Editar el crontab del usuario postgres
sudo crontab -e

# Agregar esta línea para hacer respaldo diario a las 2:00 AM:
0 2 * * * pg_dump -U <USUARIO_BD> -h localhost -d <NOMBRE_BD> -Fc -f /backup/secplac_$(date +\%Y\%m\%d).dump && find /backup -name "secplac_*.dump" -mtime +30 -delete
```

> Este comando hace el respaldo diariamente y elimina respaldos con más de 30 días automáticamente.

#### 15.1.3 Respaldo de Archivos de Datos

```bash
# Respaldo del directorio de datos (documentos, reportes, fotos)
tar -czf /backup/secplac_data_$(date +%Y%m%d).tar.gz /data/

# Verificar el respaldo
ls -lh /backup/secplac_data_*.tar.gz
```

### 15.2 Monitoreo de Logs

```bash
# Ver logs del backend en tiempo real
sudo journalctl -u secplac -f

# Buscar errores en los últimos logs
sudo journalctl -u secplac --since "1 hour ago" | grep -i error

# Ver logs de acceso de Nginx
sudo tail -f /var/log/nginx/secplac_access.log

# Ver logs de error de Nginx
sudo tail -f /var/log/nginx/secplac_error.log
```

### 15.3 Actualización de la Aplicación

```bash
# 1. Hacer respaldo antes de cualquier actualización
pg_dump -U <USUARIO_BD> -h localhost -d <NOMBRE_BD> -Fc -f /backup/secplac_pre_update_$(date +%Y%m%d).dump

# 2. Detener el servicio
sudo systemctl stop secplac

# 3. Actualizar el código desde el repositorio
cd /opt/secplac
sudo -u secplac git pull origin main

# 4. Activar el entorno virtual y actualizar dependencias (si cambiaron)
source venv/bin/activate
pip install -r backend/requirements.txt

# 5. Reiniciar el servicio
sudo systemctl start secplac

# 6. Verificar que funciona correctamente
sudo systemctl status secplac
curl http://localhost:8000/health
```

### 15.4 Rotación de la Clave JWT

Se recomienda rotar la `JWT_SECRET_KEY` cada 6 meses. Esto invalida todas las sesiones activas (los usuarios deberán volver a iniciar sesión).

```bash
# 1. Generar una nueva clave
NEW_KEY=$(python3 -c "import secrets; print(secrets.token_hex(64))")
echo "Nueva clave generada: $NEW_KEY"

# 2. Editar el .env con la nueva clave
sudo nano /opt/secplac/backend/.env
# Reemplazar el valor de JWT_SECRET_KEY

# 3. Reiniciar el servicio
sudo systemctl restart secplac
```

---

## 16. Anexo: Glosario y Comandos Útiles

### 16.1 Glosario

| Término | Definición |
|---------|-----------|
| **API REST** | Interfaz de programación que permite la comunicación entre el frontend y el backend mediante peticiones HTTP. |
| **Backend** | La parte del sistema que se ejecuta en el servidor. Contiene la lógica de negocio y accede a la base de datos. |
| **Blueprint** | Módulo de Flask que agrupa rutas relacionadas. En este sistema, cada área funcional (proyectos, usuarios, etc.) tiene su propio Blueprint. |
| **CORS** | Cross-Origin Resource Sharing. Mecanismo de seguridad que controla qué dominios pueden hacer peticiones a la API. |
| **DNS** | Domain Name System. Sistema que traduce nombres de dominio (ej: `secplac.algarrobo.cl`) a direcciones IP. |
| **Docker** | Plataforma de contenerización que empaqueta la aplicación y sus dependencias en un entorno aislado. |
| **Frontend** | La parte del sistema que se ejecuta en el navegador del usuario (archivos HTML, JavaScript y CSS). |
| **Gunicorn** | Servidor WSGI de Python que ejecuta la aplicación Flask en producción, manejando múltiples peticiones simultáneas. |
| **JWT** | JSON Web Token. Formato estándar para tokens de autenticación. Contiene información del usuario firmada criptográficamente. |
| **Nginx** | Servidor web de alto rendimiento usado como proxy inverso. Recibe las peticiones de los usuarios y las distribuye al backend o sirve los archivos estáticos. |
| **OCR** | Optical Character Recognition. Tecnología para extraer texto de imágenes y documentos escaneados. |
| **Pool de conexiones** | Conjunto de conexiones a la base de datos que se reutilizan para mejorar el rendimiento. |
| **PostgreSQL** | Sistema de gestión de base de datos relacional usado por este sistema. |
| **Proxy inverso** | Servidor que recibe peticiones en nombre del backend. Nginx actúa como proxy inverso en esta arquitectura. |
| **RBAC** | Role-Based Access Control. Sistema de control de acceso donde los permisos se asignan según el rol del usuario. |
| **SSL/TLS** | Protocolo de seguridad que cifra las comunicaciones entre el navegador y el servidor (HTTPS). |
| **Systemd** | Sistema de gestión de servicios en Linux. Permite iniciar, detener y monitorear la aplicación. |
| **Tesseract** | Motor de OCR de código abierto desarrollado por Google. Usado para extraer texto de documentos escaneados. |
| **Variables de entorno** | Parámetros de configuración externos al código. Se almacenan en el archivo `.env` y contienen datos sensibles como contraseñas. |
| **Entorno virtual (venv)** | Entorno aislado de Python donde se instalan las dependencias del proyecto sin afectar el sistema. |
| **WSGI** | Web Server Gateway Interface. Estándar de Python para la comunicación entre servidores web y aplicaciones. |

### 16.2 Referencia Rápida de Comandos

#### Gestión del Servicio Backend

```bash
# Estado del servicio
sudo systemctl status secplac

# Iniciar
sudo systemctl start secplac

# Detener
sudo systemctl stop secplac

# Reiniciar
sudo systemctl restart secplac

# Ver logs en tiempo real
sudo journalctl -u secplac -f

# Ver últimas 100 líneas de log
sudo journalctl -u secplac -n 100
```

#### Gestión de Nginx

```bash
# Verificar configuración
sudo nginx -t

# Recargar configuración (sin cortar conexiones activas)
sudo systemctl reload nginx

# Reiniciar completamente
sudo systemctl restart nginx

# Ver logs de error
sudo tail -f /var/log/nginx/secplac_error.log
```

#### Gestión de PostgreSQL

```bash
# Conectarse a la base de datos
psql -U <USUARIO_BD> -d <NOMBRE_BD> -h localhost

# Hacer respaldo
pg_dump -U <USUARIO_BD> -h localhost -d <NOMBRE_BD> -Fc -f respaldo.dump

# Restaurar desde respaldo
pg_restore -U <USUARIO_BD> -h localhost -d <NOMBRE_BD> respaldo.dump

# Ver conexiones activas
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Ver tamaño de la base de datos
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('<NOMBRE_BD>'));"
```

#### Verificación Rápida del Sistema

```bash
# Verificar que todos los servicios están activos
sudo systemctl is-active secplac nginx postgresql

# Probar el health check de la API
curl -s http://localhost:8000/health | python3 -m json.tool

# Ver el espacio en disco
df -h /data /opt/secplac

# Ver el uso de memoria
free -h

# Ver los procesos de la aplicación
ps aux | grep gunicorn
```

---

*Fin del Manual Técnico de Instalación — Sistema SECPLAC Geoportal Municipal de Algarrobo — v2.0*

---

> **Soporte técnico:** Para consultas sobre este manual, contactar al equipo de desarrollo SECPLAC.  
> **Fecha de revisión:** Este documento debe revisarse cada vez que se realice una actualización mayor del sistema.
