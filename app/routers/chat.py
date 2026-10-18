import json
import os
from fastapi import APIRouter
from groq import Groq
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Chat IA / Control LLM"])

# Estado global temporal para el control del hardware (ESP32)
ESTADO_HARDWARE = {"led": False}


# Modelo de datos que enviará el usuario
class MensajeChat(BaseModel):
    mensaje: str


# System Prompt estricto para forzar al LLM a devolver JSON con intenciones
SYSTEM_PROMPT = """
Eres el motor de Inteligencia Artificial para un sistema IoT de calidad de agua.
Tu tarea es analizar la orden del usuario y clasificarla ÚNICAMENTE en una de las siguientes intenciones:

1. "encender_led": cuando el usuario pida prender, encender, activar la luz, LED o bombillo.
2. "apagar_led": cuando el usuario pida apagar, desactivar la luz, LED o bombillo.
3. "leer_sensor": cuando pregunte por el valor actual del sensor, la lectura de agua, temperatura o turbidez.
4. "ultimo_registro": cuando pregunte por el historial reciente, el último dato o registro guardado.
5. "desconocido": para cualquier otro tema no relacionado con el sistema IoT.

DEBES RESPONDER EXCLUSIVAMENTE EN FORMATO JSON CON ESTA ESTRUCTURA (SIN TEXTO ADICIONAL, NADA DE MARKDOWN):
{
  "intencion": "<nombre_de_la_intencion>",
  "respuesta_conversacional": "<respuesta amigable en español dirigida al usuario explicando la acción>"
}
"""


@router.post("/chat")
def procesar_chat(datos: MensajeChat):
    api_key = os.getenv(
        "GROQ_API_KEY", "gsk_V0f0Kx7xLp1T123456789abcdefghijklmnopqrstuvwxyz"
    )

    try:
        client = Groq(api_key=api_key)

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": datos.mensaje},
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        respuesta_json = json.loads(chat_completion.choices[0].message.content)
        intencion = respuesta_json.get("intencion", "desconocido")
        respuesta_texto = respuesta_json.get(
            "respuesta_conversacional", "Procesado correctamente."
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
        }

    except Exception as e:
        # Fallback de resiliencia si la clave no está lista o hay fallo de red
        texto = datos.mensaje.lower()
        if (
            any(w in texto for w in ["enciende", "prende", "encender"])
            and "led" in texto
        ):
            ESTADO_HARDWARE["led"] = True
            return {
                "status": "success",
                "intencion_detectada": "encender_led",
                "respuesta": "Entendido, he encendido el LED del ESP32.",
                "estado_led": True,
            }
        elif (
            any(w in texto for w in ["apaga", "desactiva", "apagar"])
            and "led" in texto
        ):
            ESTADO_HARDWARE["led"] = False
            return {
                "status": "success",
                "intencion_detectada": "apagar_led",
                "respuesta": "Entendido, he apagado el LED del ESP32.",
                "estado_led": False,
            }

        return {
            "status": "error",
            "mensaje_error": str(e),
            "respuesta": "Ocurrió un inconveniente al procesar la solicitud.",
        }


@router.get("/esp32/estado-led")
def obtener_estado_led():
    return {"led": ESTADO_HARDWARE["led"]}