from fastapi import APIRouter, UploadFile, File, Response
from app.services.influx_service import obtener_telemetria_reciente
from app.services.yolo_service import analizar_imagen_bytes
from app.services.pdf_service import generar_pdf_reporte

router = APIRouter(prefix="/api", tags=["Análisis e Integración"])

@router.get("/telemetria")
def get_telemetria():
    return obtener_telemetria_reciente()

@router.post("/vision/predict")
async def predict_imagen(file: UploadFile = File(...)):
    contents = await file.read()
    detecciones = analizar_imagen_bytes(contents)
    return {"detecciones": detecciones}

@router.post("/reporte-pdf")
async def descargar_reporte(file: UploadFile = File(...)):
    contents = await file.read()
    detecciones = analizar_imagen_bytes(contents)
    telemetria = obtener_telemetria_reciente()
    
    # Aplicar 3 Criterios de Evaluación
    temp_prom = sum([t.get('temp', 0) for t in telemetria]) / max(len(telemetria), 1)
    
    criterios = {
        "estado_telemetria": "Anómalo" if temp_prom > 35 else "Normal",
        "estado_vision": f"Se detectaron {len(detecciones)} objeto(s)",
        "diagnostico": "Alerta Crítica Requiere Intervención" if temp_prom > 35 and len(detecciones) > 0 else "Operación Normal"
    }
    
    pdf_bytes = generar_pdf_reporte(telemetria, detecciones, criterios)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reporte_integrado.pdf"}
    )