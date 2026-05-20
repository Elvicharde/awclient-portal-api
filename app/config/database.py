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
    _ensure_report_columns()


def _ensure_report_columns() -> None:
    inspector = inspect(engine)

    if "reports" not in inspector.get_table_names():
        return

    column_names = {column["name"] for column in inspector.get_columns("reports")}

    column_sql = {
        "status": "ALTER TABLE reports ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'pending'",
        "quarter": "ALTER TABLE reports ADD COLUMN quarter VARCHAR(20)",
        "input_snapshot_json": "ALTER TABLE reports ADD COLUMN input_snapshot_json JSON",
        "calculated_totals_json": "ALTER TABLE reports ADD COLUMN calculated_totals_json JSON",
    }

    with engine.begin() as connection:
        for column_name, statement in column_sql.items():
            if column_name not in column_names:
                connection.execute(text(statement))
