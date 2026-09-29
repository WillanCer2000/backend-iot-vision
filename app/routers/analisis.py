from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response
from influxdb_client_3 import InfluxDBClient3

from app.services.pdf_service import generar_pdf_reporte
from app.services.yolo_service import procesar_imagen_yolo

router = APIRouter(prefix="/api", tags=["Análisis e Integración"])

# 1. Configuración del Cliente InfluxDB v3 mediante el túnel Ngrok
NGROK_INFLUX_HOST = "https://tameness-marbling-iguana.ngrok-free.dev"
INFLUX_TOKEN = "apiv3_iLdqkVADZBeavs90bkSj0SzlwfNziMnMAAEqjuoJBuFz8eAEmpmojWfBRNEtvj3_59oPPhzgQOaFMAMLlCwmCg"
INFLUX_DATABASE = "calidadaguav2"

try:
    influx_client = InfluxDBClient3(
        host=NGROK_INFLUX_HOST,
        token=INFLUX_TOKEN,
        database=INFLUX_DATABASE,
    )
except Exception as e:
    influx_client = None


# --- NUEVO ENDPOINT: CONSULTA NATIVA A INFLUXDB VÍA NGROK ---
@router.get("/calidad-agua")
def obtener_datos_agua():
    if not influx_client:
        return {
            "status": "error",
            "message": "Cliente InfluxDB no inicializado.",
        }

    query = """
    SELECT time, temperatura, turbidez, estado 
    FROM mqtt_consumer 
    ORDER BY time DESC 
    LIMIT 15
    """

    try:
        tabla = influx_client.query(query=query, language="sql")
        datos = tabla.to_pandas().to_dict(orient="records")
        return {"status": "success", "data": datos}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- ENDPOINTS EXISTENTES (Mantenidos intactos) ---
@router.get("/telemetria")
def get_telemetria():
    # Intenta obtener datos de InfluxDB si el cliente responde
    if influx_client:
        try:
            query = "SELECT time, temperatura, turbidez, estado FROM mqtt_consumer ORDER BY time DESC LIMIT 1"
            tabla = influx_client.query(query=query, language="sql")
            datos = tabla.to_pandas().to_dict(orient="records")
            if datos:
                return datos[0]
        except Exception:
            pass

    # Fallback/Mock data para resiliencia
    return {
        "temperatura": 24.5,
        "turbidez": 3.2,
        "estado": "Normal",
        "fuente": "mock_data",
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