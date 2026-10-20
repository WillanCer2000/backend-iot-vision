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

RESPONDE EXCLUSIVAMENTE EN FORMATO JSON (SIN MARKDOWN):
{"intencion": "<nombre>", "respuesta_conversacional": "<mensaje>"}
"""


@router.post("/chat")
def procesar_chat(datos: MensajeChat):
    api_key = os.getenv(
        "GROQ_API_KEY",
        "gsk_9sARGBRV2ColAIUQEZvWGdyb3FYWUdgX38wHCLRpNbjPFc6vQB",
    ).strip()

    # Peticion HTTP directa a Groq Llama 3.1
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": datos.mensaje},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        res = requests.post(url, headers=headers, json=payload, timeout=8)

        if res.status_code == 200:
            content = res.json()["choices"][0]["message"]["content"]
            data_json = json.loads(content)
            intencion = data_json.get("intencion", "desconocido")
            respuesta_texto = data_json.get(
                "respuesta_conversacional", "Procesado por la IA."
            )

            if intencion == "encender_led":
                ESTADO_HARDWARE["led"] = True
            elif intencion == "apagar_led":
                ESTADO_HARDWARE["led"] = False

            return {
                "status": "success",
                "intencion_detectada": intencion,
                "respuesta": respuesta_texto,
                "estado_led": ESTADO_HARDWARE["led"],
                "motor_ia": "Llama-3.1-8B-Groq",
            }
        else:
            print(f"Error Groq HTTP status: {res.status_code}")
    except Exception as e:
        print(f"Error en peticion Groq: {e}")

    # Fallback local
    texto = datos.mensaje.lower().strip()
    if any(
        w in texto for w in ["enciende", "prende", "encender", "activa", "oscuro"]
    ) and any(w in texto for w in ["led", "luz", "bombillo", "tanque"]):
        ESTADO_HARDWARE["led"] = True
        return {
            "status": "success",
            "intencion_detectada": "encender_led",
            "respuesta": "¡Entendido! He encendido el LED del ESP32.",
            "estado_led": True,
            "motor_ia": "Fallback Local",
        }
    elif any(
        w in texto for w in ["apaga", "desactiva", "apagar"]
    ) and any(w in texto for w in ["led", "luz", "bombillo"]):
        ESTADO_HARDWARE["led"] = False
        return {
            "status": "success",
            "intencion_detectada": "apagar_led",
            "respuesta": "Entendido, he apagado el LED del ESP32.",
            "estado_led": False,
            "motor_ia": "Fallback Local",
        }
    else:
        return {
            "status": "unrecognized",
            "intencion_detectada": "desconocido",
            "respuesta": "No reconozco esa instrucción.",
            "estado_led": ESTADO_HARDWARE["led"],
            "motor_ia": "Fallback Local",
        }


@router.get("/esp32/estado-led")
def obtener_estado_led():
    return {"led": ESTADO_HARDWARE["led"]}