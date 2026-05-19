from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import client_controller
from app.schemas.client_schemas import ClientCreate, ClientResponse, ClientUpdate


router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("", response_model=list[ClientResponse])
def get_clients(db: Session = Depends(get_db)) -> list[ClientResponse]:
    return client_controller.list_clients(db)


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
