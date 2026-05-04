# Manual de Instalación — Plataforma Algarrobo BASE2 (Geoportal Municipal)
## Guía Técnica Paso a Paso — Ingeniería de Despliegue

**Elaborado para:** I. Municipalidad de Algarrobo, Unidad de Informática  
**Versión del sistema:** Algarrobo BASE2  
**Fecha:** Mayo 2026  
**Contexto:** Despliegue sobre infraestructura Proxmox con modelo de segregación por capas

---

## Visión General de la Arquitectura

Antes de ejecutar cualquier comando, es fundamental entender qué se va a construir. La plataforma no es una aplicación monolítica: es un sistema distribuido en 4 capas de aislamiento.

```
Internet
   ↓
[Capa 1] Nginx CT (LXC en Proxmox) — Proxy inverso + TLS + Cloudflare Tunnel
   ↓
[Capa 2] VM Docker (en Proxmox) — Docker Engine + Portainer
   ├── Contenedor: geoportal_frontend (Nginx interno, puerto 80)
   └── Contenedor: geoportal_backend  (Gunicorn, puerto 8000)
         ↓
[Capa 3] PostgreSQL CT (LXC en Proxmox) — Base de datos aislada
```

**Stack tecnológico:**
- **Backend:** Python 3.10 + Flask + Gunicorn
- **Frontend:** HTML/JS estático servido por Nginx
- **Base de datos:** PostgreSQL (contenedor LXC independiente)
- **Orquestación:** Docker Compose gestionado desde Portainer
- **Proxy externo:** Nginx en LXC CT + Cloudflare Tunnel
- **Variables de entorno:** Inyectadas desde Portainer (no desde archivo `.env`)

---

## Prerrequisitos del Entorno

Antes de comenzar, verificar que se tienen disponibles:

| Recurso | Requerimiento mínimo |
|---|---|
| Hipervisor | Proxmox VE 7.x o superior |
| VM Docker | Ubuntu 22.04 LTS, 4 vCPU, 8 GB RAM, 50 GB disco |
| LXC Nginx | Ubuntu 22.04, 1 vCPU, 512 MB RAM |
| LXC PostgreSQL | Ubuntu 22.04, 2 vCPU, 2 GB RAM, 20 GB disco |
| Red interna | Los tres nodos deben comunicarse entre sí por IP privada |
| Dominio DNS | `geoportal.munialgarrobo.cl` apuntando a Cloudflare |
| Cuenta Cloudflare | Con acceso al tunnel (cloudflared) |
| Repositorio Git | Acceso de lectura al repositorio ALGARROBO_BASE2 |

---

## FASE 1 — Preparación de la Base de Datos (LXC PostgreSQL)

Esta fase se realiza en el contenedor LXC dedicado a PostgreSQL. La base de datos debe existir y estar accesible **antes** de levantar los contenedores de la aplicación.

### 1.1 Acceder al CT de PostgreSQL

Desde la consola de Proxmox o vía SSH al nodo:

```bash
# Reemplazar 101 por el ID real del CT de PostgreSQL en Proxmox
pct enter 101
```

### 1.2 Instalar PostgreSQL

```bash
apt-get update && apt-get upgrade -y
apt-get install -y postgresql postgresql-contrib
systemctl enable postgresql
systemctl start postgresql
```

### 1.3 Crear base de datos y usuario

```bash
# Entrar al shell de postgres
su - postgres
psql
```

Dentro de psql, ejecutar:

```sql
-- Crear usuario dedicado (reemplazar 'PASSWORD_SEGURO' por una contraseña real)
CREATE USER geoportal_user WITH PASSWORD 'PASSWORD_SEGURO';

-- Crear base de datos
CREATE DATABASE geoportal_db OWNER geoportal_user;

-- Verificar
\l
\q
```

Salir del shell postgres:

```bash
exit
```

### 1.4 Configurar acceso remoto desde la VM Docker

PostgreSQL por defecto solo acepta conexiones locales. Hay que habilitarlo para la red interna.

**Editar `postgresql.conf`:**

```bash
nano /etc/postgresql/14/main/postgresql.conf
```

Buscar y modificar:

```
listen_addresses = '*'
```

**Editar `pg_hba.conf`:**

```bash
nano /etc/postgresql/14/main/pg_hba.conf
```

Agregar al final (reemplazar `192.168.1.0/24` por la subred interna real):

```
# Permitir conexiones desde la VM Docker
host    geoportal_db    geoportal_user    192.168.1.0/24    md5
```

**Reiniciar PostgreSQL:**

```bash
systemctl restart postgresql
```

### 1.5 Verificar conectividad desde la VM Docker

Esta verificación se hace después de tener la VM levantada. Anotar la IP del CT de PostgreSQL (ejemplo: `192.168.1.50`).

```bash
# Desde la VM Docker, verificar que llega al puerto 5432
nc -zv 192.168.1.50 5432
```

Si responde `Connection to 192.168.1.50 5432 port [tcp/postgresql] succeeded!`, la red interna está correcta.

### 1.6 Construir el esquema de la base de datos

El sistema asume que las tablas ya existen. Aplicar el script SQL del repositorio:

```bash
# Desde la VM Docker (o cualquier host con psql instalado)
psql "postgresql://geoportal_user:PASSWORD_SEGURO@192.168.1.50:5432/geoportal_db" \
  -f /ruta/al/script_schema.sql
```

> **Nota:** Si el equipo de desarrollo no ha entregado el script de esquema, solicitar el archivo SQL de inicialización antes de continuar. El sistema no puede arrancar sin las tablas requeridas por el backend.

---

## FASE 2 — Preparación de la VM Docker

Esta fase se realiza en la máquina virtual que ejecutará Docker Engine y Portainer. Es el nodo central de la Capa 2.

### 2.1 Actualizar el sistema operativo

```bash
apt-get update && apt-get upgrade -y
apt-get install -y curl git ca-certificates gnupg lsb-release
```

### 2.2 Instalar Docker Engine

No instalar Docker desde el repositorio `snap` ni desde `apt` directamente — usar el repositorio oficial de Docker para asegurar compatibilidad.

```bash
# Agregar clave GPG oficial de Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Agregar repositorio
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verificar
docker --version
docker compose version
```

### 2.3 Habilitar Docker en el inicio del sistema

```bash
systemctl enable docker
systemctl start docker
```

### 2.4 Instalar Portainer

Portainer se despliega como un contenedor Docker que gestiona los demás stacks. Es la interfaz desde donde se desplegará la aplicación.

```bash
# Crear volumen persistente para Portainer
docker volume create portainer_data

# Ejecutar Portainer
docker run -d \
  --name portainer \
  --restart=always \
  -p 9000:9000 \
  -p 9443:9443 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

**Acceder a Portainer:**

Desde un navegador en la red interna, navegar a:

```
http://<IP_VM_DOCKER>:9000
```

En el primer acceso, Portainer pedirá crear un usuario administrador. Definir credenciales seguras y anotarlas.

> **Importante:** Portainer es el panel de control de toda la infraestructura Docker. Nunca exponer el puerto 9000 a internet directamente. El acceso debe ser solo desde la red interna.

### 2.5 Configurar Portainer para el entorno local

1. En Portainer, seleccionar **"Get Started"**
2. Seleccionar el entorno **"local"** (el Docker Engine de la misma VM)
3. Verificar que aparece el entorno con estado **"Running"**

---

## FASE 3 — Preparación del Repositorio y Dockerfiles

Los Dockerfiles definen cómo se construyen las imágenes del backend y del frontend. Deben existir en el repositorio Git antes de crear el Stack en Portainer.

### 3.1 Verificar la estructura requerida del repositorio

El repositorio debe tener la siguiente estructura mínima:

```
ALGARROBO_BASE2/
├── backend.Dockerfile        ← Imagen del backend (Python/Gunicorn)
├── frontend.Dockerfile       ← Imagen del frontend (Nginx)
├── nginx.conf                ← Configuración del Nginx interno
├── docker-compose.yml        ← Orquestación de servicios
├── backend/
│   ├── requirements.txt      ← Dependencias Python
│   ├── app_railway.py        ← Punto de entrada de la app Flask
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   └── routes/
│       └── ...
└── frontend/
    ├── index.html
    └── ...
```

### 3.2 Contenido del `backend.Dockerfile`

Este archivo define la imagen del backend. Debe existir en la raíz del repositorio con exactamente este contenido:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Dependencias del sistema: libpq para PostgreSQL, gcc para compilar,
# poppler-utils y tesseract para OCR de documentos PDF
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio del volumen persistente
RUN mkdir -p /data

# Instalar dependencias Python primero (aprovechar caché de Docker)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ ./backend/

WORKDIR /app/backend

EXPOSE 8000

# 4 workers, 2 threads por worker, timeout de 300s para operaciones OCR/PDF
CMD ["gunicorn", "app_railway:app", "--bind", "0.0.0.0:8000", \
     "--workers", "4", "--threads", "2", "--timeout", "300"]
```

**Por qué `--timeout 300`:** El sistema realiza procesamiento OCR con Tesseract y generación de reportes PDF, operaciones que pueden tardar entre 30 y 120 segundos. Con el timeout por defecto de Gunicorn (30s), estas operaciones serían abortadas con error 504 antes de completarse.

### 3.3 Contenido del `frontend.Dockerfile`

```dockerfile
FROM nginx:alpine

# Configuración del proxy interno (ruteo /api/ al backend)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Archivos estáticos del frontend
COPY frontend/ /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 3.4 Contenido del `nginx.conf` (Nginx interno del contenedor)

Este Nginx actúa como servidor de archivos estáticos Y como proxy inverso interno hacia el backend. No es el Nginx externo del CT de Proxmox.

```nginx
server {
    listen 80;

    # Redirección exacta /frontend → /frontend/
    location = /frontend {
        return 301 /frontend/;
    }

    location /frontend/ {
        alias /usr/share/nginx/html/;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Servir archivos estáticos del frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy inverso: redirigir /api/ al contenedor backend
    # "backend" resuelve por DNS interno de Docker (nombre del servicio en docker-compose)
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;
    }
}
```

**Punto clave:** `proxy_pass http://backend:8000` funciona porque Docker Compose crea una red interna donde cada servicio se resuelve por su nombre. El contenedor frontend puede alcanzar al contenedor backend usando el hostname `backend`.

### 3.5 Contenido del `docker-compose.yml`

```yaml
version: "3.8"

services:
  backend:
    build:
      context: .
      dockerfile: backend.Dockerfile
    container_name: geoportal_backend
    restart: always
    volumes:
      - geoportal_data:/data
    networks:
      - geoportal_net

  frontend:
    build:
      context: .
      dockerfile: frontend.Dockerfile
    container_name: geoportal_frontend
    restart: always
    depends_on:
      - backend
    ports:
      - "${FRONTEND_DOCKER_PORT}:80"
    networks:
      - geoportal_net

networks:
  geoportal_net:
    driver: bridge

volumes:
  geoportal_data:
```

**Por qué el backend no expone puertos directamente:** El backend solo es accesible dentro de la red `geoportal_net` de Docker. El único punto de entrada externo es el puerto `FRONTEND_DOCKER_PORT` del frontend, que a su vez hace proxy al backend. Esto implementa el principio de superficie de ataque mínima.

---

## FASE 4 — Despliegue desde Portainer (Stack)

Portainer gestiona el despliegue completo. No se ejecuta `docker compose up` manualmente.

### 4.1 Crear el Stack en Portainer

1. En Portainer, ir a **Stacks → Add stack**
2. Seleccionar **"Repository"** como método de despliegue
3. Completar los campos:

| Campo | Valor |
|---|---|
| Name | `geoportal` |
| Repository URL | URL del repositorio Git |
| Repository reference | `refs/heads/main` (o la rama de producción) |
| Compose path | `docker-compose.yml` |
| Authentication | Activar si el repositorio es privado |
| Git credentials | Usuario y token de acceso al repositorio |

4. Habilitar **"Automatic updates"** solo si se desea redeploy automático al hacer push.

### 4.2 Configurar las variables de entorno en Portainer

**Este es el paso más crítico.** Las variables de entorno no se definen en archivos `.env` en el servidor; se inyectan directamente desde la interfaz de Portainer en la sección **"Environment variables"** del Stack.

Definir las siguientes variables:

| Variable | Descripción | Ejemplo de valor |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión completa a PostgreSQL | `postgresql://geoportal_user:PASSWORD@192.168.1.50:5432/geoportal_db` |
| `JWT_SECRET_KEY` | Clave secreta para firmar tokens JWT (mínimo 32 caracteres aleatorios) | `(generar con: openssl rand -hex 32)` |
| `ALLOWED_ORIGINS` | Dominios permitidos para CORS (separados por coma) | `https://geoportal.munialgarrobo.cl` |
| `FLASK_ENV` | Entorno de ejecución | `production` |
| `FLASK_DEBUG` | Modo debug (siempre `False` en producción) | `False` |
| `PORT` | Puerto interno del backend (no cambiar) | `8000` |
| `FRONTEND_DOCKER_PORT` | Puerto de la VM expuesto al CT Nginx | `8080` |
| `APP_HOST` | Hostname público de la aplicación | `geoportal.munialgarrobo.cl` |
| `SESSION_EXPIRY_HOURS` | Horas de validez de sesión JWT | `24` |
| `AUDIT_OUT_DIR` | Directorio de reportes de auditoría | `/data/auditoria_reportes` |
| `MAX_UPLOAD_MB` | Límite de subida de archivos (MB) | `50` |

**Generar `JWT_SECRET_KEY` de forma segura:**

```bash
# Ejecutar en cualquier terminal Linux/Mac
openssl rand -hex 32
```

> **Advertencia crítica:** Nunca reutilizar el valor de `JWT_SECRET_KEY` entre entornos. Si este valor es comprometido, un atacante puede forjar tokens de sesión con cualquier identidad. Rotar esta clave invalida todas las sesiones activas.

### 4.3 Desplegar el Stack

Hacer clic en **"Deploy the stack"**.

Portainer ejecutará internamente:
1. `git clone` del repositorio en la VM
2. `docker build` de las imágenes (backend y frontend)
3. `docker compose up -d` para levantar los contenedores

Este proceso puede tomar **5 a 15 minutos** la primera vez, principalmente por la descarga de la imagen base `python:3.10-slim` y la compilación de dependencias con gcc.

### 4.4 Monitorear el proceso de construcción

En Portainer, ir al Stack recién creado y hacer clic en **"Logs"** para ver la salida en tiempo real.

Señales de éxito:
```
Successfully built <hash>
Successfully tagged geoportal_backend:latest
Container geoportal_backend  Started
Container geoportal_frontend Started
```

Señales de error comunes y solución:

| Error | Causa | Solución |
|---|---|---|
| `DATABASE_URL no está configurada` | Variable no definida o con typo | Revisar Portainer → Stack → Environment variables |
| `JWT_SECRET_KEY no está configurada` | Ídem | Ídem |
| `connection refused 5432` | PostgreSQL CT no accesible | Verificar IP del CT y reglas `pg_hba.conf` |
| `No space left on device` | Disco de la VM lleno | Liberar espacio o ampliar disco |

---

## FASE 5 — Configuración del Volumen Persistente

El backend almacena documentos, fotos de reportes y reportes de auditoría en un volumen Docker. Si el volumen no está correctamente montado, en producción el sistema falla al arrancar (comportamiento intencional para evitar pérdida silenciosa de datos).

### 5.1 Verificar que el volumen fue creado

```bash
# Ejecutar en la VM Docker
docker volume ls | grep geoportal
```

Debe aparecer: `local     geoportal_geoportal_data`

### 5.2 Verificar la estructura interna del volumen

```bash
# Inspeccionar el punto de montaje real del volumen
docker volume inspect geoportal_geoportal_data

# Entrar al contenedor backend y verificar directorios
docker exec -it geoportal_backend ls -la /data/
```

Los directorios esperados dentro de `/data/`:
```
/data/docs/
/data/fotos_reportes/
/data/auditoria_reportes/
```

Si no existen, el backend los crea al iniciar (el código usa `os.makedirs(exist_ok=True)`).

### 5.3 Verificar que el backend detectó el volumen

```bash
docker logs geoportal_backend | grep -i storage
```

Debe aparecer:
```
STORAGE: /data/docs
```

Si aparece `STORAGE WARNING: Usando almacenamiento local`, significa que el volumen no está montado. En `FLASK_ENV=production`, el sistema directamente no arrancará con ese error.

---

## FASE 6 — Configuración del Proxy Inverso Externo (LXC CT Nginx)

Este Nginx corre en un contenedor LXC separado en Proxmox. Es el punto de entrada público de la plataforma. Termina TLS (certificados SSL) y redirige el tráfico a la VM Docker.

### 6.1 Instalar Nginx en el CT

```bash
# Acceder al CT de Nginx desde Proxmox
pct enter 100   # Reemplazar 100 por el ID real

apt-get update && apt-get install -y nginx
systemctl enable nginx
systemctl start nginx
```

### 6.2 Crear la configuración del Geoportal

```bash
nano /etc/nginx/sites-available/geoportal.conf
```

Contenido del archivo (reemplazar `<IP_VM_DOCKER>` y `<FRONTEND_DOCKER_PORT>` por los valores reales):

```nginx
# Redirigir HTTP → HTTPS
server {
    listen 80;
    server_name geoportal.munialgarrobo.cl;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name geoportal.munialgarrobo.cl;

    # Certificados SSL (ver sección 6.3 para obtenerlos)
    ssl_certificate     /etc/nginx/ssl/geoportal.crt;
    ssl_certificate_key /etc/nginx/ssl/geoportal.key;

    # Límite de subida de archivos (debe coincidir con MAX_UPLOAD_MB del backend)
    client_max_body_size 50M;

    # Recuperar IP real del cliente desde Cloudflare
    real_ip_header CF-Connecting-IP;
    set_real_ip_from 127.0.0.1;
    real_ip_recursive on;

    location / {
        # Apunta a la VM Docker en el puerto expuesto por el frontend
        proxy_pass http://<IP_VM_DOCKER>:<FRONTEND_DOCKER_PORT>;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Propagar IP original de Cloudflare al backend
        proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;

        # Timeouts extendidos para operaciones OCR y generación de PDF
        proxy_connect_timeout 90s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

### 6.3 Configurar certificados SSL

**Opción A — Certificados gestionados por Cloudflare (recomendado):**

Si se usa Cloudflare Tunnel, Cloudflare gestiona el TLS hacia el exterior. El certificado del CT Nginx puede ser auto-firmado o un certificado de origen de Cloudflare:

```bash
mkdir -p /etc/nginx/ssl

# Generar certificado de origen en Cloudflare:
# Dashboard Cloudflare → SSL/TLS → Origin Server → Create Certificate
# Copiar el certificado y clave al CT y guardarlos como:
# /etc/nginx/ssl/geoportal.crt
# /etc/nginx/ssl/geoportal.key
```

**Opción B — Let's Encrypt (si el CT tiene IP pública directa):**

```bash
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d geoportal.munialgarrobo.cl
```

### 6.4 Activar la configuración y recargar Nginx

```bash
ln -s /etc/nginx/sites-available/geoportal.conf /etc/nginx/sites-enabled/
nginx -t   # Verificar sintaxis
systemctl reload nginx
```

La salida de `nginx -t` debe ser:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

## FASE 7 — Configuración de Cloudflare Tunnel

Cloudflare Tunnel permite exponer la plataforma a internet sin abrir puertos en el firewall perimetral. El tráfico fluye desde el CT Nginx hacia Cloudflare a través de un canal seguro saliente.

### 7.1 Instalar cloudflared en el CT Nginx

```bash
# Descargar e instalar cloudflared
curl -L --output cloudflared.deb \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared.deb
cloudflared --version
```

### 7.2 Autenticar con Cloudflare

```bash
cloudflared tunnel login
```

Esto abrirá una URL. Acceder desde un navegador, seleccionar el dominio `munialgarrobo.cl` y autorizar. Cloudflare creará un archivo de credenciales en `~/.cloudflared/`.

### 7.3 Crear el tunnel

```bash
cloudflared tunnel create geoportal-tunnel
```

Esto genera un ID de tunnel y un archivo de credenciales JSON.

### 7.4 Configurar el tunnel

```bash
mkdir -p /etc/cloudflared
nano /etc/cloudflared/config.yml
```

Contenido:

```yaml
tunnel: <ID_DEL_TUNNEL>
credentials-file: /root/.cloudflared/<ID_DEL_TUNNEL>.json

ingress:
  - hostname: geoportal.munialgarrobo.cl
    service: https://localhost:443
    originRequest:
      noTLSVerify: true   # Solo si se usa certificado auto-firmado internamente
  - service: http_status:404
```

### 7.5 Crear el registro DNS en Cloudflare

```bash
cloudflared tunnel route dns geoportal-tunnel geoportal.munialgarrobo.cl
```

### 7.6 Instalar como servicio del sistema

```bash
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared
systemctl status cloudflared
```

---

## FASE 8 — Validación del Despliegue

Una vez completadas todas las fases, verificar sistemáticamente cada componente.

### 8.1 Verificar contenedores Docker

```bash
# En la VM Docker
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Salida esperada:
```
NAMES                  STATUS          PORTS
geoportal_frontend     Up X minutes    0.0.0.0:8080->80/tcp
geoportal_backend      Up X minutes
portainer              Up X minutes    0.0.0.0:9000->9000/tcp
```

### 8.2 Verificar el health check del backend

```bash
curl http://localhost:<FRONTEND_DOCKER_PORT>/health
```

Respuesta esperada (HTTP 200):
```json
{
  "status": "healthy",
  "database": {"status": "connected"},
  "storage": {"active_root": "/data/docs"},
  "railway_optimized": true
}
```

Si `"status": "unhealthy"`, el backend no pudo conectarse a PostgreSQL. Verificar:
1. La variable `DATABASE_URL` en Portainer
2. La conectividad de red entre la VM Docker y el CT PostgreSQL
3. Las reglas de `pg_hba.conf` en el CT PostgreSQL

### 8.3 Verificar acceso al frontend

```bash
curl -I http://localhost:<FRONTEND_DOCKER_PORT>/
```

Respuesta esperada: `HTTP/1.1 200 OK`

### 8.4 Verificar proxy /api/ al backend

```bash
curl http://localhost:<FRONTEND_DOCKER_PORT>/api/
```

Respuesta esperada:
```json
{
  "message": "SECPLAC ALGARROBO API - Railway Edition",
  "storage_mode": "Volume /data",
  "status": "online"
}
```

### 8.5 Verificar acceso externo (desde internet)

Una vez configurado Cloudflare Tunnel:

```bash
curl -I https://geoportal.munialgarrobo.cl/
```

Respuesta esperada: `HTTP/2 200`

Verificar también que el header `CF-Connecting-IP` está siendo propagado correctamente en los logs del backend:

```bash
docker logs geoportal_backend | tail -20
```

### 8.6 Verificar persistencia de datos

```bash
# Verificar que el volumen está montado correctamente en el backend
docker exec geoportal_backend ls -la /data/

# Verificar que el backend está escribiendo logs correctamente
docker exec geoportal_backend cat /app/backend/municipal_api.log | tail -5
```

---

## FASE 9 — Procedimiento de Actualización

Las actualizaciones del sistema se realizan sin comandos manuales en el servidor.

### 9.1 Flujo de actualización estándar

1. El equipo de desarrollo hace `git push` de los cambios al repositorio
2. En Portainer, ir a **Stacks → geoportal**
3. Hacer clic en **"Pull and redeploy"**
4. Portainer descarga los cambios del repositorio, reconstruye las imágenes y reinicia los contenedores

El tiempo de downtime durante la actualización es de aproximadamente 30-60 segundos (el tiempo que tarda en rebuildar las imágenes y reiniciar los contenedores).

### 9.2 Rollback de emergencia

Si una actualización produce un fallo, Portainer permite hacer rollback:

1. En Portainer, ir a **Stacks → geoportal → Editor**
2. Cambiar el campo "Repository reference" a la rama o commit anterior
3. Hacer clic en **"Update the stack"**

Alternativamente, desde la VM Docker:

```bash
# Ver imágenes Docker disponibles (incluyendo versiones anteriores)
docker images | grep geoportal

# Si hay una imagen anterior etiquetada, editar el docker-compose.yml
# para apuntar a ella y redeplegar desde Portainer
```

---

## FASE 10 — Consideraciones de Seguridad Operacional

### Variables de entorno

- **Nunca** almacenar variables en archivos `.env` dentro del repositorio Git
- Rotar `JWT_SECRET_KEY` periódicamente (invalidará todas las sesiones activas)
- Rotar la contraseña de PostgreSQL si hay sospecha de compromiso

### Acceso a Portainer

- El puerto 9000 de Portainer debe ser accesible solo desde la red interna municipal
- Usar contraseñas fuertes y únicas para la cuenta admin de Portainer
- Activar autenticación en dos pasos si la versión de Portainer lo soporta

### Logs y monitoreo

```bash
# Ver logs del backend en tiempo real
docker logs -f geoportal_backend

# Ver logs del frontend (Nginx interno)
docker logs -f geoportal_frontend

# Ver logs del Nginx externo (CT Nginx)
# Acceder al CT y ejecutar:
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Backup de la base de datos

```bash
# Ejecutar desde el CT PostgreSQL o cualquier host con acceso
pg_dump "postgresql://geoportal_user:PASSWORD@192.168.1.50:5432/geoportal_db" \
  -Fc -f /backups/geoportal_$(date +%Y%m%d).dump
```

Programar este comando como cron diario con retención de 30 días.

### Backup del volumen Docker

```bash
# Comprimir el volumen de datos
docker run --rm \
  -v geoportal_geoportal_data:/data \
  -v /backups:/backup \
  alpine tar czf /backup/geoportal_data_$(date +%Y%m%d).tar.gz /data
```

---

## Referencia Rápida de Puertos y Comunicaciones

| Origen | Destino | Puerto | Protocolo | Propósito |
|---|---|---|---|---|
| Internet | Cloudflare | 443 | HTTPS | Tráfico público |
| Cloudflare | CT Nginx | 443 | HTTPS | Tunnel Cloudflare |
| CT Nginx | VM Docker | `FRONTEND_DOCKER_PORT` | HTTP | Proxy al frontend |
| Contenedor Frontend | Contenedor Backend | 8000 | HTTP (interno Docker) | API |
| Contenedor Backend | CT PostgreSQL | 5432 | PostgreSQL | Base de datos |
| Admin (red interna) | VM Docker | 9000 | HTTP | Panel Portainer |

---

## Resumen de Archivos de Configuración

| Archivo | Ubicación | Propósito |
|---|---|---|
| `backend.Dockerfile` | Raíz del repositorio | Imagen del backend Python/Gunicorn |
| `frontend.Dockerfile` | Raíz del repositorio | Imagen del frontend Nginx |
| `nginx.conf` | Raíz del repositorio | Nginx interno del contenedor |
| `docker-compose.yml` | Raíz del repositorio | Orquestación de servicios |
| `geoportal.conf` | `/etc/nginx/sites-available/` en CT Nginx | Proxy inverso externo |
| `/etc/cloudflared/config.yml` | CT Nginx | Configuración del tunnel |

---

*Manual elaborado a partir de la Guía de Despliegue y Arquitectura Institucional — Geoportal Municipal (Abril 2026)*  
*I. Municipalidad de Algarrobo — Unidad de Informática*
