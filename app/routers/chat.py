from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Chat IA / Control LLM"])

# Estado global temporal para el control del hardware (ESP32)
ESTADO_HARDWARE = {"led": False}


class MensajeChat(BaseModel):
    mensaje: str


@router.post("/chat")
def procesar_chat(datos: MensajeChat):
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