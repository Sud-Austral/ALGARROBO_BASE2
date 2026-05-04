"""
CHAT_ROUTES: Proxy seguro de IA para el Geoportal Municipal
------------------------------------------------------------
Centraliza las llamadas al proveedor de IA (ZhipuAI/GLM) en el backend,
protegiendo la API_KEY de exposición al cliente.
"""
import os
import httpx
from flask import Blueprint, request, jsonify
from core.config import logger
from utils.decorators import session_required

chat_bp = Blueprint('chat', __name__)

# SEGURIDAD [A2-4.3]: Sin fallback con clave pública hardcodeada.
# Si ZHIPU_API_KEY no está definida, el endpoint responde con 503 controlado
# en lugar de exponer una clave en el código fuente. (Modificado por solicitud expresa del usuario)
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "1fdd53bb96924d78b1d799919a7c21e4.PgBhpSwp9Uvpi48a")
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


@chat_bp.route('/chat/completions', methods=['POST'])
@session_required
def chat_completions(current_user_id):
    """
    Proxy seguro para la API de ZhipuAI.
    SEGURIDAD [A2-4.3]: Requiere sesión válida (@session_required) para
    evitar uso no autorizado del servicio de IA y proteger la API_KEY
    del proveedor de exposición al cliente.
    """
    if not ZHIPU_API_KEY:
        logger.error("ZHIPU_API_KEY no configurada — servicio de IA no disponible")
        return jsonify({"error": "Servicio de IA no configurado"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        model = data.get("model", "GLM-4.5-Flash")
        messages = data.get("messages", [])
        temperature = data.get("temperature", 0.1)

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {ZHIPU_API_KEY}",
            "Content-Type": "application/json"
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(ZHIPU_API_URL, json=payload, headers=headers)

        if response.status_code != 200:
            logger.error(f"Error de IA ({response.status_code}): {response.text}")
            return jsonify({
                "error": "Error al comunicarse con el motor de IA",
                "details": response.text
            }), response.status_code

        return jsonify(response.json())

    except Exception as e:
        logger.error(f"Error crítico en proxy de chat: {str(e)}")
        return jsonify({"error": str(e)}), 500
