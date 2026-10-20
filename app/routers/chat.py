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

RESPONDE EXCLUSIVAMENTE EN FORMATO JSON (SIN MARKDOWN NI TEXTO ADICIONAL):
{"intencion": "<nombre>", "respuesta_conversacional": "<mensaje>"}
"""

# Tu API key de Groq codificada en Base64
CLAVE_GROQ_B64 = "Z3NrX3ZyTkloS0E5TFFxcjhqZEt0UE5OV0dkeWIzRllZOTFQbWlhOXVFYnNaaUpEdWFhUTlYOTZD"

@router.post("/chat")
def procesar_chat(datos: MensajeChat):
    try:
        api_key = base64.b64decode(CLAVE_GROQ_B64).decode("utf-8")
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": datos.mensaje}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

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
                "motor_ia": "Llama 3.3 70B (Groq IA Real)"
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