from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "AW Client Portal API"
    app_version: str = "1.0.0"
    debug: bool = True
    database_url: str = "sqlite:///./awclient_portal.db"
    report_output_dir: Path = Path("reports/output")
    template_dir: Path = Path("app/templates")
    cors_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:5500",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:4173",
        "https://awclient-portal-frontend.vercel.app",
        "awclient-web-portal.vercel.app"
    )


settings = Settings()
