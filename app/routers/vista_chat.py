from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Interfaz Gráfica Chat"])


@router.get("/chat-gui", response_class=HTMLResponse)
def cargar_interfaz_chat():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat IA - Control IoT Calidad de Agua</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .chat-container { max-width: 600px; margin: 30px auto; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; }
            .chat-header { background: #0d6efd; color: white; padding: 15px; text-align: center; font-weight: bold; }
            .chat-box { height: 400px; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; background: #fafafa; }
            .message { max-width: 80%; padding: 10px 15px; border-radius: 18px; font-size: 14px; line-height: 1.4; }
            .message.user { background: #0d6efd; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
            .message.bot { background: #e9ecef; color: #212529; align-self: flex-start; border-bottom-left-radius: 4px; }
            .badge-status { font-size: 11px; margin-top: 4px; opacity: 0.8; display: block; }
            .hardware-status { background: #e2e3e5; padding: 10px; text-align: center; font-weight: bold; border-top: 1px solid #dee2e6; }
            .led-on { color: #198754; }
            .led-off { color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                🤖 Control por Lenguaje Natural - Sistema IoT
            </div>
            <div class="chat-box" id="chatBox">
                <div class="message bot">
                    ¡Hola! Soy la IA del sistema de Calidad de Agua. Puedes pedirme cosas como:
                    <br>• <i>"Porfa enciéndeme el led"</i>
                    <br>• <i>"¿Cuál es el valor actual del sensor?"</i>
                    <br>• <i>"Muéstrame el último registro"</i>
                </div>
            </div>
            <div class="hardware-status" id="hardwareStatus">
                Estado LED ESP32: <span id="ledState" class="led-off">🔴 APAGADO</span>
            </div>
            <div class="p-3 bg-white border-top">
                <div class="input-group">
                    <input type="text" id="userInput" class="form-control" placeholder="Escribe tu comando aquí..." onkeypress="handleKeyPress(event)">
                    <button class="btn btn-primary" onclick="enviarMensaje()">Enviar</button>
                </div>
            </div>
        </div>

        <script>
            async function enviarMensaje() {
                const input = document.getElementById('userInput');
                const mensaje = input.value.trim();
                if (!mensaje) return;

                const chatBox = document.getElementById('chatBox');

                // Mostrar mensaje del usuario
                const userDiv = document.createElement('div');
                userDiv.className = 'message user';
                userDiv.innerText = mensaje;
                chatBox.appendChild(userDiv);

                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ mensaje: mensaje })
                    });
                    const data = await response.json();

                    // Mostrar respuesta del Bot
                    const botDiv = document.createElement('div');
                    botDiv.className = 'message bot';
                    botDiv.innerHTML = `${data.respuesta} <span class="badge-status">Intención: <b>${data.intencion_detectada}</b></span>`;
                    chatBox.appendChild(botDiv);

                    // Actualizar indicador LED
                    const ledSpan = document.getElementById('ledState');
                    if (data.estado_led) {
                        ledSpan.className = 'led-on';
                        ledSpan.innerText = '🟢 ENCENDIDO';
                    } else {
                        ledSpan.className = 'led-off';
                        ledSpan.innerText = '🔴 APAGADO';
                    }

                } catch (error) {
                    const errDiv = document.createElement('div');
                    errDiv.className = 'message bot';
                    errDiv.innerText = 'Error al conectar con la API.';
                    chatBox.appendChild(errDiv);
                }
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') enviarMensaje();
            }
        </script>
    </body>
    </html>
    """
    return html_content