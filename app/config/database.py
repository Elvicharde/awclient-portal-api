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
    _ensure_client_columns()
    _ensure_report_columns()


def _ensure_client_columns() -> None:
    inspector = inspect(engine)

    if "clients" not in inspector.get_table_names():
        return

    column_names = {column["name"] for column in inspector.get_columns("clients")}

    column_sql = {
        "middle_name": "ALTER TABLE clients ADD COLUMN middle_name VARCHAR(100)",
        "date_of_birth": "ALTER TABLE clients ADD COLUMN date_of_birth DATE",
        "ssn_last_four": "ALTER TABLE clients ADD COLUMN ssn_last_four VARCHAR(4)",
        "marital_status": "ALTER TABLE clients ADD COLUMN marital_status VARCHAR(20) NOT NULL DEFAULT 'single'",
        "spouse_first_name": "ALTER TABLE clients ADD COLUMN spouse_first_name VARCHAR(100)",
        "spouse_middle_name": "ALTER TABLE clients ADD COLUMN spouse_middle_name VARCHAR(100)",
        "spouse_last_name": "ALTER TABLE clients ADD COLUMN spouse_last_name VARCHAR(100)",
        "spouse_date_of_birth": "ALTER TABLE clients ADD COLUMN spouse_date_of_birth DATE",
        "spouse_ssn_last_four": "ALTER TABLE clients ADD COLUMN spouse_ssn_last_four VARCHAR(4)",
        "spouse_email": "ALTER TABLE clients ADD COLUMN spouse_email VARCHAR(255)",
        "spouse_phone": "ALTER TABLE clients ADD COLUMN spouse_phone VARCHAR(50)",
        "client_1_monthly_salary_after_tax": "ALTER TABLE clients ADD COLUMN client_1_monthly_salary_after_tax FLOAT",
        "client_1_monthly_expense_budget": "ALTER TABLE clients ADD COLUMN client_1_monthly_expense_budget FLOAT",
        "client_2_monthly_salary_after_tax": "ALTER TABLE clients ADD COLUMN client_2_monthly_salary_after_tax FLOAT",
        "client_2_monthly_expense_budget": "ALTER TABLE clients ADD COLUMN client_2_monthly_expense_budget FLOAT",
        "private_reserve_target": "ALTER TABLE clients ADD COLUMN private_reserve_target FLOAT",
        "insurance_deductible_total": "ALTER TABLE clients ADD COLUMN insurance_deductible_total FLOAT",
        "retirement_accounts_json": "ALTER TABLE clients ADD COLUMN retirement_accounts_json JSON",
        "non_retirement_accounts_json": "ALTER TABLE clients ADD COLUMN non_retirement_accounts_json JSON",
        "trust_details_json": "ALTER TABLE clients ADD COLUMN trust_details_json JSON",
        "liabilities_json": "ALTER TABLE clients ADD COLUMN liabilities_json JSON",
    }

    with engine.begin() as connection:
        for column_name, statement in column_sql.items():
            if column_name not in column_names:
                connection.execute(text(statement))


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
