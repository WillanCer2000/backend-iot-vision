from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.routers import analisis

app = FastAPI(title="API Backend - Taller IoT + YOLO")

# Configurar CORS para permitir peticiones desde el Frontend
app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# Incluir las rutas existentes de visión, telemetría y PDF
app.include_router(analisis.router)

@app.get("/")
def root():
return {"mensaje": "Backend IoT + Vision activo y listo"}

# --- MODELO Y ENDPOINT DE CONTROL REMOTO (Frecuencia ESP32) ---
class FrecuenciaRequest(BaseModel):
intervalo_segundos: int

@app.post("/api/control/frecuencia")
def cambiar_frecuencia(data: FrecuenciaRequest):
"""
Recibe la orden de cambiar el intervalo de muestreo del ESP32 desde iot_control.js
"""
return {
"status": "success",
"mensaje": f"Frecuencia actualizada a {data.intervalo_segundos} segundos.",
"frecuencia_actual": data.intervalo_segundos,
"timestamp": datetime.now().isoformat()
}

# --- ENDPOINT DE BITÁCORA / INCIDENTES ---
@app.get("/api/incidentes")
def obtener_incidentes():
"""
Retorna la lista de eventos e incidentes registrados
"""
return [
{
"id": 1,
"timestamp": datetime.now().isoformat(),
"tipo": "ALERTA_TURBIDEZ",
"descripcion": "Nivel de turbidez elevado detectado en tanque principal (NTU > 15)",
"gravedad": "ALTA"
},
{
"id": 2,
"timestamp": datetime.now().isoformat(),
"tipo": "DETECCION_VISUAL",
"descripcion": "Residuo plástico detectado por visión artificial (Confianza: 94%)",
"gravedad": "MEDIA"
}
]
