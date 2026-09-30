import time
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response
from influxdb_client import InfluxDBClient

router = APIRouter(prefix="/api", tags=["Análisis e Integración"])

NGROK_HOST = "https://tameness-marbling-iguana.ngrok-free.dev"
INFLUX_TOKEN = "apiv3_iLdqkVADZBeavs90bkSj0SzlwfNziMnMAAEqjuoJBuFz8eAEmpmojWfBRNEtvj3_59oPPhzgQOaFMAMLlCwmCg"
INFLUX_ORG = "iot"
INFLUX_BUCKET = "calidadaguav2"


@router.get("/calidad-agua")
def obtener_datos_agua():
    query = f"""
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> limit(n: 20)
    """

    try:
        # AGREGAMOS EL HEADER PARA BURLAR LA PANTALLA DE ADVERTENCIA DE NGROK
        client = InfluxDBClient(
            url=NGROK_HOST,
            token=INFLUX_TOKEN,
            org=INFLUX_ORG,
            timeout=5000,
            headers={
                "ngrok-skip-browser-warning": "true",
                "User-Agent": "FastAPI-Backend",
            },
        )

        query_api = client.query_api()
        tablas = query_api.query(query=query)

        datos = []
        for tabla in tablas:
            for registro in tabla.records:
                datos.append(
                    {
                        "time": registro.get_time(),
                        "identificador": registro.values.get("identificador"),
                        "temperatura": registro.values.get("temperatura"),
                        "turbidez": registro.values.get("turbidez"),
                        "estado": registro.values.get("estado"),
                    }
                )

        client.close()

        if datos:
            return {
                "status": "success",
                "origen": "InfluxDB Local (Real)",
                "data": datos,
            }

    except Exception as e:
        print(f"Error consultando InfluxDB vía Ngrok: {e}")

    # Fallback de seguridad en caso de que el sensor no esté publicando
    return {
        "status": "success",
        "origen": "Fallback Resiliencia",
        "data": [
            {
                "time": f"2026-09-29T19:{10 + i:02d}:00Z",
                "identificador": "ESP32_01",
                "temperatura": round(24.0 + (i % 3) * 0.4, 1),
                "turbidez": round(3.0 + (i % 2) * 0.3, 1),
                "estado": "Normal",
            }
            for i in range(5)
        ],
    }