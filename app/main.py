from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.include_router(analisis.router)

@app.get("/")
def root():
    return {"mensaje": "Backend IoT + Vision activo y listo"}