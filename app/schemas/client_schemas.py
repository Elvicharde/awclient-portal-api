from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Client first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Client last name")
    email: EmailStr = Field(..., description="Unique client email address")
    phone: str | None = Field(default=None, max_length=50, description="Client phone number")


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)


class ClientResponse(ClientBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientListResponse(BaseModel):
    items: list[ClientResponse]
    page: int
    limit: int
    total: int
