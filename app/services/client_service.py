from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.client_model import Client
from app.schemas.client_schemas import ClientCreate, ClientUpdate


def get_clients(db: Session) -> list[Client]:
    return db.query(Client).order_by(Client.created_at.desc()).all()


def get_client_by_id(db: Session, client_id: int) -> Client | None:
    return db.query(Client).filter(Client.id == client_id).first()


def create_client(db: Session, client_data: ClientCreate) -> Client:
    client = Client(**client_data.model_dump())

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

    try:
        db.delete(client)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return True
