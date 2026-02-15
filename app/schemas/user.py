from typing import Optional
from pydantic import EmailStr
from sqlmodel import SQLModel

class UserCreate(SQLModel):
    matricule: str
    last_name: str
    first_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "PP Technician"

class UserRead(SQLModel):
    id: int
    matricule: str
    last_name: str
    first_name: str
    email: EmailStr
    role: str
