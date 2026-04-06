import os
import logging
import json
import psycopg2.extras
from datetime import datetime
from core.database import get_db_connection, release_db_connection
import auditoria_engine
import correo

logger = logging.getLogger(__name__)

def run_audit_and_email_batch(ejecutor_nombre="Sistema (Programado)", base_url="https://geoportalalgarrobo.github.io/ALGARROBO_BASE2"):
    """
    Ejecuta la auditoría integral y luego envía los correos a los responsables.
    Esta función es sincrónica para asegurar el orden.
    """
    logger.info(f"--- INICIANDO TAREA PROGRAMADA: {ejecutor_nombre} ---")
    
    conn = None
    try:
        # 1. Verificar estado actual del motor
        status = auditoria_engine.get_status()
        if status["running"]:
            logger.warning("Ya hay una auditoría en curso. Abortando tarea programada.")
            return False

        # 2. Paso 1: Ejecutar Auditoría Integral
        logger.info("Paso 1: Ejecutando Auditoría Integral...")
        # Invocamos el worker sincrónicamente
        auditoria_engine._worker(
            db_factory=get_db_connection,
            release_fn=release_db_connection,
            ejecutor_nombre=ejecutor_nombre,
            base_url=base_url
        )
        logger.info("Paso 1: Auditoría completada.")

        # 3. Paso 2: Enviar por Correo
        logger.info("Paso 2: Enviando Auditorías por Correo...")
        
        if not os.path.exists(auditoria_engine.AUDIT_OUT_DIR):
            logger.error("No se encontró el directorio de reportes para enviar correos.")
            return False

        files = [f for f in os.listdir(auditoria_engine.AUDIT_OUT_DIR)
                 if f.startswith("Auditoria_Proyecto_") and f.endswith(".pdf")]
        
        if not files:
            logger.warning("No se generaron reportes (.pdf) para enviar.")
            return True

        # Mapeo de ID de proyecto a nombre de archivo
        project_files = {}
        for f in files:
            try:
                pid = int(f.replace("Auditoria_Proyecto_", "").replace(".pdf", ""))
                project_files[pid] = f
            except:
                continue

        pids = list(project_files.keys())
        enviados, errores, sin_correo = 0, 0, 0

        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT id, nombre, profesional_1, profesional_2, profesional_3, profesional_4, profesional_5
                FROM proyectos WHERE id = ANY(%s)
            """, (pids,))
            proyectos = cur.fetchall()

            for p in proyectos:
                pid = p['id']
                pdf_path = os.path.join(auditoria_engine.AUDIT_OUT_DIR, project_files[pid])
                # Recopilar todos los profesionales (1 al 5)
                responsables = [p[f'profesional_{i}'] for i in range(1, 6) if p[f'profesional_{i}']]
                
                if not responsables:
                    logger.warning(f"Proyecto {pid} no tiene responsables asignados. Saltando.")
                    sin_correo += 1
                    continue

                res = correo.enviar_email_responsables(
                    proyecto_id=pid, 
                    responsables_names=responsables,
                    ruta_pdf=pdf_path, 
                    proyecto_nombre=p['nombre']
                )

                if res["success"]:
                    enviados += 1
                elif "No se encontraron correos" in res["message"]:
                    sin_correo += 1
                else:
                    errores += 1
                    logger.error(f"Error enviando correo proy {pid}: {res['message']}")

        logger.info(f"--- TAREA FINALIZADA: {enviados} enviados, {errores} errores, {sin_correo} sin correo ---")
        return True

    except Exception as e:
        logger.error(f"Error crítico en run_audit_and_email_batch: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        if conn:
            release_db_connection(conn)
