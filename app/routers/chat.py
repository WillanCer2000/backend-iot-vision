import json
import base64
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

RESPONDE EXCLUSIVAMENTE EN FORMATO JSON (SIN MARKDOWN):
{"intencion": "<nombre>", "respuesta_conversacional": "<mensaje>"}
"""

# Clave de Gemini codificada en Base64
CLAVE_B64 = "QVEuQWI4Uk42S1gyLS1SQUh1TWM1cm5RTGdvZFlFWERVUEp1N2VoTjBfYm1pNGlUBEcw"

@router.post("/chat")
def procesar_chat(datos: MensajeChat):
    try:
        gemini_api_key = base64.b64decode(CLAVE_B64).decode("utf-8")
        
        # Endpoint oficial directo al modelo activo gemini-2.5-flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
        
        prompt = f"{SYSTEM_PROMPT}\n\nMensaje del usuario: {datos.mensaje}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}

        r = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if r.status_code == 200:
            res_data = r.json()
            raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            data_json = json.loads(clean_text)

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
                "motor_ia": "Gemini 2.5 Flash (IA Real)"
            }
        else:
            return {
                "status": "error",
                "intencion_detectada": "desconocido",
                "respuesta": f"Error de IA ({r.status_code}): {r.text}",
                "estado_led": ESTADO_HARDWARE["led"],
                "motor_ia": "Error API"
            }

    except Exception as e:
        return {
            "status": "error",
            "intencion_detectada": "desconocido",
            "respuesta": f"Excepción de conexión: {str(e)}",
            "estado_led": ESTADO_HARDWARE["led"],
            "motor_ia": "Error Backend"
        }

@router.get("/esp32/estado-led")
def obtener_estado_led():
    return {"led": ESTADO_HARDWARE["led"]}