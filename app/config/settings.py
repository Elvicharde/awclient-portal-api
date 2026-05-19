from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "AW Client Portal API"
    app_version: str = "1.0.0"
    debug: bool = True
    database_url: str = "sqlite:///./awclient_portal.db"
    cors_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    )


settings = Settings()
