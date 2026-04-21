-- ============================================================
-- MAESTROS Y TABLAS DE SOPORTE (CREAR PRIMERO POR DEPENDENCIAS)
-- ============================================================

CREATE TABLE IF NOT EXISTS hitoscalendario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) UNIQUE NOT NULL,
    is_hito BOOLEAN DEFAULT TRUE
);

INSERT INTO hitoscalendario (nombre, is_hito) VALUES
('RECEPCION_OBSERVACIONES', TRUE),
('RESPUESTA_OBSERVACIONES', TRUE),
('APROBACION_CONVENIO', TRUE),
('INICIO_LICITACION', TRUE),
('APROBACION_URS', TRUE),
('APROBACION_NIVEL_CENTRAL', TRUE),
('OTRO', TRUE),
('HITO_INICIO_PROYECTO', TRUE),
('HITO_TERMINO_PROYECTO', TRUE),
('ENTREGA_IMPORTANTE', TRUE),
('INAUGURACION', TRUE),
('POSTULACION_FONDO', TRUE),
('VENCIMIENTO_PERMISO', TRUE),
('PLAZO_RENDICION', TRUE),
('FECHA_ADMINISTRATIVA', FALSE),
('REUNION_COORDINACION', FALSE),
('REUNION_EQUIPO', FALSE),
('VISITA_TERRENO', FALSE),
('COORDINACION_CONTRATISTA', FALSE),
('EVENTO_MUNICIPAL', FALSE),
('CEREMONIA', FALSE),
('EVENTO_COMUNITARIO_PROYECTO', FALSE)
ON CONFLICT (nombre) DO NOTHING;

CREATE TABLE IF NOT EXISTS areas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS financiamientos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    fuente VARCHAR(100),
    anyo VARCHAR(50),
    comentario TEXT,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS etapas_proyecto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) UNIQUE NOT NULL,
    orden SMALLINT,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS estados_proyecto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) UNIQUE NOT NULL,
    color VARCHAR(30),
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS estados_postulacion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sectores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS lineamientos_estrategicos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(300) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- TABLAS PRINCIPALES
-- ============================================================

CREATE TABLE IF NOT EXISTS proyectos (
    id SERIAL PRIMARY KEY,

    user_id INT NOT NULL REFERENCES users(user_id),
    actualizado_por INT NOT NULL REFERENCES users(user_id),

    n_registro INT,

    area_id INT REFERENCES areas(id),
    lineamiento_estrategico_id INT REFERENCES lineamientos_estrategicos(id),

    financiamiento_id INT REFERENCES financiamientos(id),
    financiamiento_municipal VARCHAR(50),

    nombre TEXT,
    monto NUMERIC,

    anno_elaboracion INT,
    anno_ejecucion INT,

    topografia TEXT,
    planimetrias TEXT,
    ingenieria TEXT,
    perfil_tecnico_economico TEXT,
    documentos TEXT,

    avance_total_porcentaje NUMERIC(5,2),
    avance_total_decimal NUMERIC(10,4),

    estado_proyecto_id INT REFERENCES estados_proyecto(id),
    etapa_proyecto_id INT REFERENCES etapas_proyecto(id),
    estado_postulacion_id INT REFERENCES estados_postulacion(id),

    dupla_profesionales TEXT,
    profesional_1 VARCHAR(150),
    profesional_2 VARCHAR(150),
    profesional_3 VARCHAR(150),
    profesional_4 VARCHAR(150),
    profesional_5 VARCHAR(150),

    fecha_postulacion DATE,
    observaciones TEXT,

    unidad_vecinal VARCHAR(150),
    sector_id INT REFERENCES sectores(id),

    aprobacion_dom VARCHAR(100),
    aprobacion_serviu VARCHAR(100),

    fecha_actualizacion TIMESTAMP DEFAULT NOW(),

    latitud NUMERIC(12,6),
    longitud NUMERIC(12,6),
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS mapas (
    mapa_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS mapas_roles (
    mapa_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (mapa_id, role_id),
    CONSTRAINT fk_mapas_roles_mapa
        FOREIGN KEY (mapa_id)
        REFERENCES mapas (mapa_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_mapas_roles_role
        FOREIGN KEY (role_id)
        REFERENCES roles (role_id)
        ON DELETE CASCADE
);

INSERT INTO mapas (nombre, descripcion)
VALUES 
('Varios', '1.html'),
('Proyectos', '2.html'),
('Camara', '3.html')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS proyectos_documentos (
    documento_id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL REFERENCES proyectos(id) ON DELETE CASCADE,
    tipo_documento VARCHAR(100),
    nombre VARCHAR(255),
    descripcion TEXT,
    url TEXT,
    archivo_nombre VARCHAR(255),
    archivo_extension VARCHAR(20),
    archivo_size BIGINT,
    fecha_subida TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS proyectos_geomapas (
    geomapa_id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL REFERENCES proyectos(id) ON DELETE CASCADE,
    nombre VARCHAR(150),
    descripcion TEXT,
    geojson JSONB NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS auditoria2 (
    auditoria_id BIGSERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL DEFAULT now(),
    tabla_nombre TEXT NOT NULL,
    operacion TEXT NOT NULL,
    registro_id TEXT,
    usuario_bd TEXT DEFAULT current_user,
    ip_origen TEXT,
    aplicacion TEXT,
    query TEXT,
    datos_antes JSONB,
    datos_despues JSONB
);

CREATE TABLE IF NOT EXISTS proyectos_hitos (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL REFERENCES proyectos(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    observacion TEXT,
    categoria_calendario INT REFERENCES hitoscalendario(id),
    categoria_hito INT REFERENCES hitoscalendario(id),
    creado_por INT NOT NULL REFERENCES users(user_id),
    creado_en TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS proyectos_observaciones (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL REFERENCES proyectos(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    creado_por INT NOT NULL REFERENCES users(user_id),
    observacion TEXT,
    creado_en TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS financiamiento_plazos (
    id SERIAL PRIMARY KEY,
    financiamiento VARCHAR(50) NOT NULL,
    hito_origen VARCHAR(100) NOT NULL,
    hito_destino VARCHAR(100) NOT NULL,
    dias INT NOT NULL,
    tipo_dia VARCHAR(20) NOT NULL
);

INSERT INTO financiamiento_plazos (financiamiento, hito_origen, hito_destino, dias, tipo_dia)
VALUES
('FNDR', 'RECEPCION_OBSERVACIONES', 'RESPUESTA_OBSERVACIONES', 60, 'CORRIDOS'),
('FNDR', 'APROBACION_CONVENIO', 'INICIO_LICITACION', 90, 'CORRIDOS'),
('FRIL', 'RECEPCION_OBSERVACIONES', 'RESPUESTA_OBSERVACIONES', 20, 'HABILES'),
('FRIL', 'APROBACION_CONVENIO', 'INICIO_LICITACION', 90, 'CORRIDOS')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS calendario_eventos (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_termino TIMESTAMP,
    todo_el_dia BOOLEAN DEFAULT TRUE,
    categoria_calendario INT REFERENCES hitoscalendario(id),
    origen_tipo VARCHAR(50),
    origen_id INT,
    ubicacion VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    creado_por INT NOT NULL REFERENCES users(user_id),
    creado_en TIMESTAMP DEFAULT NOW(),
    UNIQUE (origen_tipo, origen_id)
);
