from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import Base, engine
from app.config.settings import settings
from app.models import client_model, log_model, report_model
from app.routes import client_routes, log_routes, report_routes


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(client_routes.router)
app.include_router(log_routes.router)
app.include_router(report_routes.router)


@app.on_event("startup")
def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
