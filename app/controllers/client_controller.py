from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.client_schemas import ClientCreate, ClientUpdate
from app.services import client_service


def list_clients(db: Session) -> list[Any]:
    try:
        return client_service.get_clients(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve clients",
        ) from exc


def get_client(client_id: int, db: Session) -> Any:
    client = client_service.get_client_by_id(db, client_id)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    return client


def create_client(client_data: ClientCreate, db: Session) -> Any:
    try:
        return client_service.create_client(db, client_data)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create client",
        ) from exc


def update_client(client_id: int, client_data: ClientUpdate, db: Session) -> Any:
    try:
        client = client_service.update_client(db, client_id, client_data)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update client",
        ) from exc

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    return client


def delete_client(client_id: int, db: Session) -> dict[str, str]:
    try:
        deleted = client_service.delete_client(db, client_id)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to delete client",
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    return {"status": "deleted"}
