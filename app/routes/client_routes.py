from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import client_controller
from app.schemas.client_schemas import (
    ClientCreate,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
)


router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("", response_model=ClientListResponse)
def get_clients(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
) -> ClientListResponse:
    return client_controller.list_clients(db, page=page, limit=limit, search=search)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)) -> ClientResponse:
    return client_controller.get_client(client_id, db)


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client_data: ClientCreate, db: Session = Depends(get_db)) -> ClientResponse:
    return client_controller.create_client(client_data, db)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
) -> ClientResponse:
    return client_controller.update_client(client_id, client_data, db)


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    return client_controller.delete_client(client_id, db)
