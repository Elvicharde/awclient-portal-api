from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config.settings import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def initialize_database_schema() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_report_status_column()


def _ensure_report_status_column() -> None:
    inspector = inspect(engine)

    if "reports" not in inspector.get_table_names():
        return

    column_names = {column["name"] for column in inspector.get_columns("reports")}

    if "status" in column_names:
        return

    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE reports ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'pending'")
        )
