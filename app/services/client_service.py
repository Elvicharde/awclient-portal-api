from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.client_model import Client
from app.schemas.client_schemas import ClientCreate, ClientUpdate


def get_clients(
    db: Session,
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
) -> dict[str, Any]:
    query = db.query(Client)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Client.first_name.ilike(search_term),
                Client.last_name.ilike(search_term),
                Client.email.ilike(search_term),
            )
        )

    total = query.count()
    items = (
        query.order_by(Client.created_at.desc())
        .offset(_get_offset(page, limit))
        .limit(limit)
        .all()
    )

    return {"items": items, "page": page, "limit": limit, "total": total}


def get_client_by_id(db: Session, client_id: int) -> Client | None:
    return db.query(Client).filter(Client.id == client_id).first()


def create_client(db: Session, client_data: ClientCreate) -> Client:
    _ensure_email_is_unique(db, str(client_data.email))
    client_values = client_data.model_dump()
    client_values["email"] = str(client_data.email).lower()
    client = Client(**client_values)

    try:
        db.add(client)
        db.commit()
        db.refresh(client)
    except SQLAlchemyError:
        db.rollback()
        raise

    return client


def update_client(db: Session, client_id: int, client_data: ClientUpdate) -> Client | None:
    client = get_client_by_id(db, client_id)

    if not client:
        return None

    update_data = client_data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:
        _ensure_email_is_unique(db, str(update_data["email"]), exclude_client_id=client_id)
        update_data["email"] = str(update_data["email"]).lower()

    for field, value in update_data.items():
        setattr(client, field, value)

    try:
        db.commit()
        db.refresh(client)
    except SQLAlchemyError:
        db.rollback()
        raise

    return client


def delete_client(db: Session, client_id: int) -> bool:
    client = get_client_by_id(db, client_id)

    if not client:
        return False

    if client.logs or client.reports:
        raise ValueError("Client has related logs or reports and cannot be deleted")

    try:
        db.delete(client)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def _ensure_email_is_unique(
    db: Session,
    email: str,
    exclude_client_id: int | None = None,
) -> None:
    query = db.query(Client).filter(func.lower(Client.email) == email.lower())

    if exclude_client_id is not None:
        query = query.filter(Client.id != exclude_client_id)

    if query.first():
        raise ValueError("Client email already exists")


def _get_offset(page: int, limit: int) -> int:
    return (page - 1) * limit
