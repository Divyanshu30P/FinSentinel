import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.services.demo_seed import seed_demo_data
from backend.app.services.ocr_service import OCRService
from backend.app.routers import auth, dashboard, fraud, upload, analytics

# Ensure database tables and demo seed exist on module load
Base.metadata.create_all(bind=engine)
try:
    _init_db = SessionLocal()
    seed_demo_data(_init_db)
    _init_db.close()
except Exception as _e:
    print(f"DB init note: {_e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifecycle startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Financial Fraud Detection Platform for Digital Payments & Banking.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)
app.include_router(fraud.router, prefix=settings.API_PREFIX)
app.include_router(upload.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)

@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "operational",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected",
        "gemini_api_configured": bool(settings.GEMINI_API_KEY),
        "tesseract_installed": OCRService.is_tesseract_available()
    }

# Serve Frontend static assets
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
def serve_index():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Welcome to UPI Shield API. Please visit /docs for API documentation."}
