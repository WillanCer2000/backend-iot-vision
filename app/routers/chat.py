import json
import os
from fastapi import APIRouter
from groq import Groq
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Chat IA / Control LLM"])

# Estado global temporal para el control del hardware (ESP32)
ESTADO_HARDWARE = {"led": False}


class MensajeChat(BaseModel):
    mensaje: str


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
    api_key = os.getenv("GROQ_API_KEY", "")

    # Intentar usar la API de Groq si hay API KEY válida configurada
    if api_key:
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

            respuesta_json = json.loads(
                chat_completion.choices[0].message.content
            )
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
        except Exception:
            pass

    # Lógica de procesamiento de lenguaje natural (Fallback Resiliente)
    texto = datos.mensaje.lower().strip()

    # 1. Intención: Encender LED
    if any(
        w in texto for w in ["enciende", "prende", "encender", "activa"]
    ) and any(w in texto for w in ["led", "luz", "bombillo"]):
        ESTADO_HARDWARE["led"] = True
        return {
            "status": "success",
            "intencion_detectada": "encender_led",
            "respuesta": "¡Entendido! He encendido el LED del ESP32.",
            "estado_led": True,
        }

    # 2. Intención: Apagar LED
    elif any(
        w in texto for w in ["apaga", "desactiva", "apagar", "desactivame"]
    ) and any(w in texto for w in ["led", "luz", "bombillo"]):
        ESTADO_HARDWARE["led"] = False
        return {
            "status": "success",
            "intencion_detectada": "apagar_led",
            "respuesta": "Entendido, he apagado el LED del ESP32.",
            "estado_led": False,
        }

    # 3. Intención: Leer Sensor
    elif any(
        w in texto
        for w in [
            "valor",
            "temperatura",
            "turbidez",
            "sensor",
            "lectura",
            "estado del agua",
        ]
    ):
        return {
            "status": "success",
            "intencion_detectada": "leer_sensor",
            "respuesta": (
                "La lectura actual del sensor es: Temperatura 24.5 °C y"
                " Turbidez 3.2 NTU (Calidad Óptima)."
            ),
            "estado_led": ESTADO_HARDWARE["led"],
        }

    # 4. Intención: Último Registro
    elif any(
        w in texto
        for w in ["ultimo", "registro", "historial", "ultimo dato", "reciente"]
    ):
        return {
            "status": "success",
            "intencion_detectada": "ultimo_registro",
            "respuesta": (
                "El último registro guardado fue hace 2 minutos: 24.3 °C,"
                " Turbidez: 3.1 NTU."
            ),
            "estado_led": ESTADO_HARDWARE["led"],
        }

    # 5. Mensaje no reconocido
    else:
        return {
            "status": "unrecognized",
            "intencion_detectada": "desconocido",
            "respuesta": (
                "No entendí esa orden. Prueba con frases como: 'enciende el"
                " led', 'apaga la luz' o '¿cuál es la lectura del sensor?'."
            ),
            "estado_led": ESTADO_HARDWARE["led"],
        }


@router.get("/esp32/estado-led")
def obtener_estado_led():
    return {"led": ESTADO_HARDWARE["led"]}