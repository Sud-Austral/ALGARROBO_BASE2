"""
🚀 CHAT_ROUTES: Servicio de IA Seguro para Algarrobo
--------------------------------------------------
Este módulo centraliza las llamadas a la IA (ZhipuAI/GLM)
protegiendo la API_KEY y permitiendo auditoría de consultas.
"""
import os
import httpx
from flask import Blueprint, request, jsonify
from core.config import logger

chat_bp = Blueprint('chat', __name__)

# Configuración de IA (Mover a variables de entorno en producción)
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "1fdd53bb96924d78b1d799919a7c21e4.PgBhpSwp9Uvpi48a")
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

@chat_bp.route('/chat/completions', methods=['POST'])
def chat_completions():
    """
    Proxy seguro para la API de ZhipuAI.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Opcional: Validar token de sesión del usuario aquí para mayor seguridad
        
        # Extraer parámetros del request frontend
        model = data.get("model", "GLM-4.5-Flash")
        messages = data.get("messages", [])
        temperature = data.get("temperature", 0.1)

        # Preparar request para ZhipuAI
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {ZHIPU_API_KEY}",
            "Content-Type": "application/json"
        }

        # Realizar la llamada real (Backend a Backend)
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
