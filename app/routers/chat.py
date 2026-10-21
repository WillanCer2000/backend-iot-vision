import json
import os
import requests
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Chat con IA"])

class MensajeChat(BaseModel):
    mensaje: str

ESTADO_HARDWARE = {"led": False}

SYSTEM_PROMPT = """
Eres la IA de un sistema IoT de Calidad de Agua. Clasifica la intencion del usuario:
1. "encender_led": si pide encender, prender, activar la luz, LED, bombillo, o si dice que hay oscuridad, falta luz o no se ve nada.
2. "apagar_led": si pide apagar o desactivar la luz / LED.
3. "leer_sensor": si pregunta por la temperatura, lectura o calidad del agua.
4. "ultimo_registro": si pide el historial o ultimo registro.
5. "desconocido": cualquier otro tema.

RESPONDE EXCLUSIVAMENTE EN FORMATO JSON (SIN MARKDOWN NI TEXTO ADICIONAL):
{"intencion": "<nombre>", "respuesta_conversacional": "<mensaje>"}
"""

# Lista de modelos según la documentación de tus compañeros
MODELO_PRINCIPAL = "openai/gpt-oss-120b"
MODELO_RESPALDO = "openai/gpt-oss-20b"

@router.post("/chat")
def procesar_chat(datos: MensajeChat):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            return {
                "status": "error",
                "intencion_detectada": "desconocido",
                "respuesta": "Falta la variable GROQ_API_KEY en Render.",
                "estado_led": ESTADO_HARDWARE["led"],
                "motor_ia": "Error Config"
            }
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Intentar primero con el modelo principal
        payload = {
            "model": MODELO_PRINCIPAL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": datos.mensaje}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        r = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Si el modelo principal falla, intenta inmediatamente con el de respaldo
        if r.status_code != 200:
            payload["model"] = MODELO_RESPALDO
            r = requests.post(url, json=payload, headers=headers, timeout=10)

        if r.status_code == 200:
            res_data = r.json()
            raw_text = res_data["choices"][0]["message"]["content"]
            data_json = json.loads(raw_text)

            intencion = data_json.get("intencion", "desconocido")
            respuesta_texto = data_json.get("respuesta_conversacional", "Procesado por la IA.")

            if intencion == "encender_led":
                ESTADO_HARDWARE["led"] = True
            elif intencion == "apagar_led":
                ESTADO_HARDWARE["led"] = False

            return {
                "status": "success",
                "intencion_detectada": intencion,
                "respuesta": respuesta_texto,
                "estado_led": ESTADO_HARDWARE["led"],
                "motor_ia": f"Groq ({payload['model']})"
            }
        else:
            return {
                "status": "error",
                "intencion_detectada": "desconocido",
                "respuesta": f"Error Groq ({r.status_code}): {r.text}",
                "estado_led": ESTADO_HARDWARE["led"],
                "motor_ia": "Error API"
            }

    except Exception as e:
        return {
            "status": "error",
            "intencion_detectada": "desconocido",
            "respuesta": f"Excepción backend: {str(e)}",
            "estado_led": ESTADO_HARDWARE["led"],
            "motor_ia": "Error Backend"
        }

@router.get("/esp32/estado-led")
def obtener_estado_led():
    return {"led": ESTADO_HARDWARE["led"]}