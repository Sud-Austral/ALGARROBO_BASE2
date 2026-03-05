-- Tabla para almacenar los próximos pasos (next steps) de cada proyecto
CREATE TABLE IF NOT EXISTS proximos_pasos (
    id SERIAL PRIMARY KEY,
    proyecto_id INTEGER NOT NULL REFERENCES proyectos(id) ON DELETE CASCADE,
    comentario TEXT NOT NULL,
    descripcion TEXT, -- Detalles adicionales si es necesario
    fecha_plazo DATE NOT NULL,
    estado VARCHAR(50) DEFAULT 'PENDIENTE', -- PENDIENTE, EN_PROCESO, COMPLETADO, VENCIDO
    prioridad VARCHAR(50) DEFAULT 'MEDIA', -- ALTA, MEDIA, BAJA
    responsable VARCHAR(255), -- Nombre o entidad responsable del próximo paso
    creado_por INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices recomendados
CREATE INDEX idx_proximos_pasos_proyecto_id ON proximos_pasos(proyecto_id);
CREATE INDEX idx_proximos_pasos_fecha_plazo ON proximos_pasos(fecha_plazo);
CREATE INDEX idx_proximos_pasos_estado ON proximos_pasos(estado);

-- Trigger para actualizar fecha_actualizacion (asumiendo que function update_modified_column ya existe en la BD o se crea genéricamente)
-- CREATE TRIGGER trg_update_proximos_pasos_mod
-- BEFORE UPDATE ON proximos_pasos
-- FOR EACH ROW EXECUTE FUNCTION update_modified_column();
