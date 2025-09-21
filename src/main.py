import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings
from src.routes.api import router as api_router
from src.routes.main import router as main_router
from src.utils.logging_config import setup_logging

# Application setup
settings = get_settings()
app = FastAPI(
    title="CodingAgentV2",
    description="An AI-powered code execution and analysis agent",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
setup_logging(settings.LOG_LEVEL)

# Include routers
app.include_router(main_router)
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)