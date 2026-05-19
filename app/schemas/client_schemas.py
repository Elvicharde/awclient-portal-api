from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None


class ClientResponse(ClientBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
