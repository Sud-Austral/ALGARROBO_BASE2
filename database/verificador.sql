-- ==============================================================================
-- MODELO DE DATOS PARA HISTORIAL DE VERIFICACIONES (AUDITORÍA INTEGRAL)
-- Permite visualizar dashboards de estado actual e histórico de cambios
-- ==============================================================================

-- Tabla para agrupar cada ejecución del script verificador.py
CREATE TABLE IF NOT EXISTS auditoria_lotes (
    id SERIAL PRIMARY KEY,
    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_ejecutor VARCHAR(100) DEFAULT 'SISTEMA',
    total_proyectos_auditados INTEGER DEFAULT 0,
    promedio_calidad_general NUMERIC(5,2) DEFAULT 0
);

-- Tabla para el resultado específico de la auditoría por proyecto
CREATE TABLE IF NOT EXISTS auditoria_proyectos (
    id SERIAL PRIMARY KEY,
    lote_id INTEGER REFERENCES auditoria_lotes(id) ON DELETE CASCADE,
    proyecto_id INTEGER REFERENCES proyectos(id) ON DELETE CASCADE,
    
    -- Campos explícitos del proyecto para seguimiento de cambios directo (Diffing en SQL)
    n_registro INT,
    nombre TEXT,
    area_id INT,
    lineamiento_estrategico_id INT,
    financiamiento_id INT,
    financiamiento_municipal VARCHAR(50),
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
    estado_proyecto_id INT,
    etapa_proyecto_id INT,
    estado_postulacion_id INT,
    fecha_postulacion DATE,
    
    dupla_profesionales TEXT,
    profesional_1 VARCHAR(150),
    profesional_2 VARCHAR(150),
    profesional_3 VARCHAR(150),
    profesional_4 VARCHAR(150),
    profesional_5 VARCHAR(150),
    
    unidad_vecinal VARCHAR(150),
    sector_id INT,
    aprobacion_dom VARCHAR(100),
    aprobacion_serviu VARCHAR(100),
    
    latitud NUMERIC(12,6),
    longitud NUMERIC(12,6),
    observaciones TEXT,
    activo BOOLEAN,

    -- Evoluciones relacionales (Tracking 1:N)
    cant_documentos INTEGER DEFAULT 0,
    cant_hitos INTEGER DEFAULT 0,
    cant_observaciones INTEGER DEFAULT 0,
    cant_proximos_pasos INTEGER DEFAULT 0,

    -- Métricas principales
    puntaje_general NUMERIC(5,2),
    puntaje_d1 NUMERIC(5,2),
    puntaje_d2 NUMERIC(5,2),
    puntaje_d3 NUMERIC(5,2),
    puntaje_d4 NUMERIC(5,2),
    puntaje_d5 NUMERIC(5,2),
    puntaje_d6 NUMERIC(5,2),
    puntaje_d7 NUMERIC(5,2),
    
    -- Snapshot de la auditoría para comparar variaciones y control de avance
    avance_declarado NUMERIC(5,2),
    etapa VARCHAR(255),
    estado VARCHAR(255),
    
    -- Contadores de alertas por severidad
    alertas_criticas INTEGER DEFAULT 0,
    alertas_altas INTEGER DEFAULT 0,
    alertas_medias INTEGER DEFAULT 0,
    alertas_bajas INTEGER DEFAULT 0,
    
    -- Json con array de alertas específicas generadas
    alertas_json JSONB,
    
    -- Análisis cualitativo generado por Inteligencia Artificial
    analisis_ia TEXT
);

-- Índices para optimizar consultas de dashboards e historiales
CREATE INDEX idx_auditoria_proyectos_lote ON auditoria_proyectos(lote_id);
CREATE INDEX idx_auditoria_proyectos_proyecto ON auditoria_proyectos(proyecto_id);
CREATE INDEX idx_auditoria_proyectos_avance ON auditoria_proyectos(avance_declarado);
