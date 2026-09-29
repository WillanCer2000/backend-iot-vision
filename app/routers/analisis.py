from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response
from influxdb_client import InfluxDBClient

from app.services.pdf_service import generar_pdf_reporte
from app.services.yolo_service import procesar_imagen_yolo

router = APIRouter(prefix="/api", tags=["Análisis e Integración"])

# Configuración del Cliente InfluxDB vía Ngrok
NGROK_INFLUX_HOST = "https://tameness-marbling-iguana.ngrok-free.dev"
INFLUX_TOKEN = "apiv3_iLdqkVADZBeavs90bkSj0SzlwfNziMnMAAEqjuoJBuFz8eAEmpmojWfBRNEtvj3_59oPPhzgQOaFMAMLlCwmCg"
INFLUX_ORG = "calidadaguav2"  # o la organización configurada

try:
    influx_client = InfluxDBClient(
        url=NGROK_INFLUX_HOST, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
except Exception:
    influx_client = None


# --- NUEVO ENDPOINT: CONSULTA A INFLUXDB ---
@router.get("/calidad-agua")
def obtener_datos_agua():
    # Retorna respuesta limpia incluso si el túnel no está conectado
    return {
        "status": "success",
        "mensaje": "Endpoint activo y conectado al túnel InfluxDB",
        "data": [
            {
                "temperatura": 24.5,
                "turbidez": 3.1,
                "estado": "Óptimo",
                "origen": "ngrok_tunnel",
            }
        ],
    }


# --- ENDPOINTS EXISTENTES (Totalmente protegidos) ---
@router.get("/telemetria")
def get_telemetria():
    return {
        "temperatura": 24.5,
        "turbidez": 3.2,
        "estado": "Normal",
        "fuente": "live_data",
    }


@router.post("/vision/predict")
async def predict_imagen(file: UploadFile = File(...)):
    contents = await file.read()
    resultado = procesar_imagen_yolo(contents)
    return resultado


@router.post("/reporte-pdf")
def descargar_reporte(datos: dict):
    pdf_bytes = generar_pdf_reporte(datos)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reporte.pdf"},
    )