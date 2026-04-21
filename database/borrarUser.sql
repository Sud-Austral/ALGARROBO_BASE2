-- ============================================================
-- borrarUser.sql  v5 — Eliminación SEGURA de uno o varios usuarios
--
-- USO:  Cambia el array v_user_ids con los IDs a eliminar.
--       Ejemplo: ARRAY[42, 55, 78]
--
-- ESTRATEGIA:
--   • Columnas NOT NULL  → reasignar a user_id = 1 (admin sistema)
--   • Columnas NULL      → SET NULL
--   • Filas propias del user (comentarios, roles) → DELETE
--   • Proyectos, hitos, observaciones, docs → NO se borran nunca
--   • Logs de auditoría → NO se borran (trazabilidad)
--   • Tablas opcionales → chequeadas con IF EXISTS antes de operar
-- ============================================================

DO $$
DECLARE
    v_user_ids  INT[] := ARRAY[999];  -- ← CAMBIA AQUÍ: ARRAY[42, 55, 78]
    v_admin_id  INT   := 1;           -- Usuario "sistema" para referencias NOT NULL
    v_count     INT;

BEGIN

    -- ── Guardia 1: v_admin_id no puede estar en la lista a borrar ─
    IF v_admin_id = ANY(v_user_ids) THEN
        RAISE EXCEPTION 
            'El usuario "admin sistema" (v_admin_id=%) está incluido en los IDs a eliminar. '
            'Cambia v_admin_id a otro usuario que NO vaya a borrarse (ej: un admin que permanezca en la BD).',
            v_admin_id;
    END IF;

    -- ── Guardia 2: todos los usuarios existen ──────────────────
    SELECT COUNT(*) INTO v_count
      FROM users
     WHERE user_id = ANY(v_user_ids);

    IF v_count <> array_length(v_user_ids, 1) THEN
        RAISE EXCEPTION 'Uno o más IDs no existen en users: %', v_user_ids;
    END IF;

    RAISE NOTICE '>> Iniciando limpieza para user_ids = %', v_user_ids;

    -- ══════════════════════════════════════════════════════════
    -- PROYECTOS  (NOT NULL → reasignar al admin)
    -- ══════════════════════════════════════════════════════════
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'proyectos') THEN
        UPDATE proyectos SET user_id        = v_admin_id WHERE user_id        = ANY(v_user_ids);
        UPDATE proyectos SET actualizado_por = v_admin_id WHERE actualizado_por = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'proyectos_hitos') THEN
        UPDATE proyectos_hitos SET creado_por = v_admin_id WHERE creado_por = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'proyectos_observaciones') THEN
        UPDATE proyectos_observaciones SET creado_por = v_admin_id WHERE creado_por = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'calendario_eventos') THEN
        UPDATE calendario_eventos SET creado_por = v_admin_id WHERE creado_por = ANY(v_user_ids);
    END IF;

    -- ══════════════════════════════════════════════════════════
    -- LICITACIONES  (nullable → SET NULL)
    -- ══════════════════════════════════════════════════════════
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'licitaciones') THEN
        UPDATE licitaciones SET usuario_creador = NULL WHERE usuario_creador = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'licitacion_workflow') THEN
        UPDATE licitacion_workflow SET usuario_id = NULL WHERE usuario_id = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'licitaciones_documentos') THEN
        UPDATE licitaciones_documentos SET usuario_subida = NULL WHERE usuario_subida = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'licitaciones_biblioteca') THEN
        UPDATE licitaciones_biblioteca SET usuario_subida = NULL WHERE usuario_subida = ANY(v_user_ids);
    END IF;

    -- ══════════════════════════════════════════════════════════
    -- REPORTES CIUDADANOS  (mobile)
    -- ══════════════════════════════════════════════════════════
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reportes_fotos') THEN
        UPDATE reportes_fotos SET subido_por = NULL WHERE subido_por = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reportes_ciudadanos') THEN
        UPDATE reportes_ciudadanos SET actualizado_por = NULL  WHERE actualizado_por = ANY(v_user_ids);
        UPDATE reportes_ciudadanos SET reportado_por   = v_admin_id WHERE reportado_por = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reportes_comentarios') THEN
        DELETE FROM reportes_comentarios WHERE user_id = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reportes_verificaciones') THEN
        DELETE FROM reportes_verificaciones WHERE verificado_por = ANY(v_user_ids);
    END IF;

    -- ══════════════════════════════════════════════════════════
    -- PRÓXIMOS PASOS
    -- ══════════════════════════════════════════════════════════
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'proximos_pasos') THEN
        UPDATE proximos_pasos SET creado_por = NULL WHERE creado_por = ANY(v_user_ids);
    END IF;

    -- ══════════════════════════════════════════════════════════
    -- LOGS DE AUDITORÍA  (nullable — NO se borran nunca)
    -- ══════════════════════════════════════════════════════════
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'control_actividad') THEN
        UPDATE control_actividad SET user_id = NULL WHERE user_id = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'control_sesiones') THEN
        UPDATE control_sesiones SET user_id = NULL WHERE user_id = ANY(v_user_ids);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'auditoria') THEN
        UPDATE auditoria SET user_id = NULL WHERE user_id = ANY(v_user_ids);
    END IF;

    -- ══════════════════════════════════════════════════════════
    -- BORRAR USUARIOS (user_roles → CASCADE automático)
    -- ══════════════════════════════════════════════════════════
    DELETE FROM users WHERE user_id = ANY(v_user_ids);

    RAISE NOTICE '>> Usuarios % eliminados exitosamente. Referencias NOT NULL → user_id = %.', v_user_ids, v_admin_id;

END $$;