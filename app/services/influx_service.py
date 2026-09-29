import os
from influxdb_client import InfluxDBClient

# Configuración de conexión (puedes ajustar las variables de entorno o valores por defecto)
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "TU_TOKEN_DE_INFLUXDB_AQUI")
INFLUX_ORG = os.getenv("INFLUX_ORG", "mi_organizacion")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "sensores")

def obtener_telemetria_reciente(limit: int = 10):
    """
    Consulta las últimas lecturas de los sensores desde InfluxDB.
    """
    try:
        client = InfluxDBClient(
            url=INFLUX_URL,
            token=INFLUX_TOKEN,
            org=INFLUX_ORG
        )
        
        # Consulta Flux para extraer telemetría reciente
        query_api = client.query_api()
        query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
          |> limit(n: {limit})
        '''
        
        result = query_api.query(org=INFLUX_ORG, query=query)
        registros = []
        
        for table in result:
            for record in table.records:
                registros.append({
                    "tiempo": record.get_time(),
                    "campo": record.get_field(),
                    "valor": record.get_value(),
                    "sensor": record.values.get("sensor", "desconocido")
                })
                
        client.close()
        return registros

    except Exception as e:
        print(f"[ERROR InfluxDB]: {e}")
        # Retorno de datos de respaldo (Mock) mientras el hardware no esté conectado
        return [
            {"sensor": "Temperatura", "campo": "valor", "valor": 26.5, "unidad": "°C"},
            {"sensor": "Humedad", "campo": "valor", "valor": 65.0, "unidad": "%"}
        ]