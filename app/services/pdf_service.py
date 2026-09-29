import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generar_pdf_reporte(datos_iot: list, detecciones_vision: list, criterios: dict) -> bytes:
    """Genera un archivo PDF dinámico evaluando al menos 3 criterios."""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Reporte Integrado: IoT + Visión por Computador")
    
    p.setFont("Helvetica", 10)
    p.drawString(100, 730, "---------------------------------------------------------------------------------")
    
    # Criterio 1: Evaluación del estado ambiental / sensor
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 700, f"1. Estado de Telemetría: {criterios.get('estado_telemetria', 'N/A')}")
    
    # Criterio 2: Presencia de anomalías por visión
    p.drawString(100, 680, f"2. Detección de Eventos Visuales: {criterios.get('estado_vision', 'N/A')}")
    
    # Criterio 3: Fusión Sensorial y Toma de Decisiones
    p.drawString(100, 660, f"3. Diagnóstico Integrado: {criterios.get('diagnostico', 'N/A')}")
    
    p.setFont("Helvetica", 10)
    y = 620
    p.drawString(100, y, "Últimas lecturas de telemetría:")
    y -= 15
    for item in datos_iot[:5]:
        p.drawString(120, y, f"- Temp: {item.get('temp', 'N/A')} °C | Hum: {item.get('hum', 'N/A')} % | Fecha: {item.get('time', 'N/A')}")
        y -= 15
        
    y -= 20
    p.drawString(100, y, "Detecciones de Objetos (YOLO):")
    y -= 15
    for det in detecciones_vision:
        p.drawString(120, y, f"- Clase: {det['clase']} | Confianza: {det['confianza']*100}%")
        y -= 15

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()