from typing import Optional
from pydantic import EmailStr
from sqlmodel import SQLModel
from datetime import datetime

class UserCreate(SQLModel):
    matricule: str
    last_name: str
    first_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "PP Technician"

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class DFCCreate(SQLModel):
    numero_dfc: Optional[int]
    projet: Optional[str]
    famille: Optional[str]
    phase: Optional[str]
    description: Optional[str]
    date_reception: Optional[datetime]
    faisabilite: Optional[str]
    type_dfc: Optional[str]
    commentaire: Optional[str]

class DFCRead(DFCCreate):
    id: int
    date_enregistrement: Optional[datetime]
