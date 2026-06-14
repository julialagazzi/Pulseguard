import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, empresas, reclamacoes, dashboard, alertas, relatorios, seed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PulseGuard API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.onrender.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    inicio = time.time()
    response = await call_next(request)
    duracao = time.time() - inicio
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({duracao:.3f}s)")
    return response

app.include_router(auth.router, prefix="/api/v1")
app.include_router(empresas.router, prefix="/api/v1")
app.include_router(reclamacoes.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(alertas.router, prefix="/api/v1")
app.include_router(relatorios.router, prefix="/api/v1")
app.include_router(seed.router, prefix="/api/v1")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "PulseGuard API v2.0.0", "docs": "/docs"}
