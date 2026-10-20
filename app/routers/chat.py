import json
import base64
from fastapi import APIRouter
from pydantic import BaseModel
import google.generativeai as genai

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

# Tu clave de Gemini codificada previamente en Base64
CLAVE_B64 = "QVEuQWI4Uk42S1gyLS1SQUh1TWM1cm5RTGdvZFlFWERVUEplN2VoTjBfYm1pNGdsVUJFY3c="

@router.post("/chat")
def procesar_chat(datos: MensajeChat):
    try:
        # Decodificación y configuración dentro del endpoint para garantizar el inicio de Uvicorn
        api_key = base64.b64decode(CLAVE_B64).decode("utf-8")
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json", "temperature": 0.1}
        )

        response = model.generate_content(datos.mensaje)
        content = response.text.replace("```json", "").replace("```", "").strip()
        data_json = json.loads(content)

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
            "motor_ia": "Gemini-1.5-Flash (SDK)"
        }

    except Exception as e:
        return {
            "status": "error",
            "intencion_detectada": "desconocido",
            "respuesta": f"Excepcion SDK: {str(e)}",
            "estado_led": ESTADO_HARDWARE["led"],
            "motor_ia": "Falla IA"
        }

@router.get("/esp32/estado-led")
def obtener_estado_led():
    return {"led": ESTADO_HARDWARE["led"]}