from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.routers import analisis

app = FastAPI(title="API Backend - Taller IoT + YOLO")

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

app.include_router(analisis.router)


@app.get("/")
def root():
return {"mensaje": "Backend IoT + Vision activo y listo"}


class FrecuenciaRequest(BaseModel):
intervalo_segundos: int


@app.post("/api/control/frecuencia")
def cambiar_frecuencia(data: FrecuenciaRequest):
return {
"status": "success",
"mensaje": f"Frecuencia actualizada a {data.intervalo_segundos} segundos.",
"frecuencia_actual": data.intervalo_segundos,
"timestamp": datetime.now().isoformat(),
}


@app.get("/api/incidentes")
def obtener_incidentes():
return [
{
"id": 1,
"timestamp": datetime.now().isoformat(),
"tipo": "ALERTA_TURBIDEZ",
"descripcion": "Nivel de turbidez elevado detectado en tanque principal (NTU > 15)",
"gravedad": "ALTA",
},
{
"id": 2,
"timestamp": datetime.now().isoformat(),
"tipo": "DETECCION_VISUAL",
"descripcion": "Residuo plástico detectado por visión artificial (Confianza: 94%)",
"gravedad": "MEDIA",
},
]
