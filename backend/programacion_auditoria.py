import os
import time
import threading
import logging
from datetime import datetime
from utils.audit_tasks import run_audit_and_email_batch

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PROGRAMACIÓN
# ══════════════════════════════════════════════════════════════════════════════

# 1. Definir la fecha y hora de ejecución ("YYYY-MM-DD HH:MM:SS")
FECHA_HORA_EJECUCION = "2026-04-07 09:00:00"

# 2. El sistema pondrá esto en True cuando termine para no repetirse
ESTADO_EJECUCION = {
    "ejecutado": False,
    "ultima_ejecucion": None,
    "error": None
}

# ══════════════════════════════════════════════════════════════════════════════
# MOTOR DEL PROGRAMADOR (BACKGROUND THREAD)
# ══════════════════════════════════════════════════════════════════════════════

def _scheduler_loop():
    """Bucle infinito en segundo plano que verifica la hora."""
    logger.info(f"Programador de auditoría iniciado. Esperando a: {FECHA_HORA_EJECUCION}")
    
    while True:
        try:
            if not ESTADO_EJECUCION["ejecutado"]:
                ahora = datetime.now()
                meta  = datetime.strptime(FECHA_HORA_EJECUCION, "%Y-%m-%d %H:%M:%S")
                
                if ahora >= meta:
                    logger.info("¡Hora de ejecución alcanzada! Iniciando Auditoría y Envío por Correo...")
                    
                    try:
                        exito = run_audit_and_email_batch(
                            ejecutor_nombre="Tarea Programada (Auto)",
                            base_url="https://geoportalalgarrobo.github.io/ALGARROBO_BASE2"
                        )
                        
                        if exito:
                            ESTADO_EJECUCION["ejecutado"] = True
                            ESTADO_EJECUCION["ultima_ejecucion"] = ahora.isoformat()
                            logger.info("Tarea programada finalizada con ÉXITO.")
                        else:
                            ESTADO_EJECUCION["error"] = "Error en la ejecución. Ver logs."
                            logger.error("Tarea programada finalizada con ERROR.")
                            
                    except Exception as e:
                        ESTADO_EJECUCION["error"] = str(e)
                        logger.error(f"Error crítico en scheduler_loop: {e}")

        except Exception as e:
            logger.error(f"Error en bucle de programación: {e}")

        # Dormir 1 minuto antes de volver a verificar
        time.sleep(60)

def iniciar_programador():
    """Lanza el hilo del programador."""
    t = threading.Thread(target=_scheduler_loop, daemon=True)
    t.start()
    return t
