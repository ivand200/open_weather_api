from typing import List, Optional

from pydantic import BaseModel, validator, Field


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str

    @validator("password")
    def valid_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password should be at least 8 chars")
        if not any(i.isdigit() for i in value):
            raise ValueError("Password should contains at least one number")
        if not any(i.isupper() for i in value):
            raise ValueError("Password should contains at least one capital letter")
        return value


class UserPublic(UserBase):
    id: int

    class Congig:
        orm_mode = True


class ItemBase(BaseModel):
    title: str

    class Config:
        orm_mode = True


class ItemCreate(ItemBase):
    user_id: int

    class Config:
        orm_mode = True


class ItemPublic(ItemBase):
    id: int

    class Config:
        orm_mode = True


class UserItems(BaseModel):
    user: Optional[UserPublic]
    items: Optional[List[ItemPublic]]

    class Config:
        orm_mode = True
