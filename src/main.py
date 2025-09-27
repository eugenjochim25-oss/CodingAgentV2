import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse

# -----------------------------
# Haupt-App-Konfiguration
# -----------------------------

# Initialisiere den Logger
logger = logging.getLogger('CodingAgentV2')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logger.error("❌ Kein GEMINI_API_KEY gefunden! Bitte .env prüfen.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events go here
    logger.info("✅ Anwendung wird gestartet.")
    yield
    # Shutdown events go here
    logger.info("❌ Anwendung wird heruntergefahren.")

app = FastAPI(lifespan=lifespan)

# -----------------------------
# Router für die Hauptseite
# -----------------------------

# Erstelle einen Router für die Hauptseite
home_router = APIRouter()

@home_router.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Diese Route dient der Hauptseite.
    Sie gibt eine einfache HTML-Seite zurück, um die Funktionalität zu testen.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CodingAgentV2</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #f0f2f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background-color: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            h1 {
                color: #333;
            }
            p {
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Willkommen zu CodingAgentV2!</h1>
            <p>Die Anwendung läuft erfolgreich. Du kannst jetzt die API-Endpunkte testen.</p>
        </div>
    </body>
    </html>
    """
    return html_content

# -----------------------------
# Router für die API
# -----------------------------

# Erstelle einen neuen APIRouter mit dem Präfix /api
api_router = APIRouter()

# Definiere einen einfachen Endpunkt, um den Status der API zu überprüfen
@api_router.get("/status")
async def get_api_status():
    """
    Dieser Endpunkt gibt den aktuellen Status der API zurück.
    Er hilft zu bestätigen, dass der Router korrekt geladen wurde.
    """
    return {"status": "OK", "message": "API ist erfolgreich geladen."}

# -----------------------------
# Router in die App einbinden
# -----------------------------
app.include_router(home_router)
app.include_router(api_router, prefix="/api")
