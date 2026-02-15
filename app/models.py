from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    matricule: str = Field(index=True, unique=True)
    last_name: str
    first_name: str
    email: str = Field(index=True, unique=True)
    role: str = Field(default="PP Technician")
    hashed_password: str

class DFC(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero_dfc: Optional[int] = Field(index=True, unique=True)
    projet: Optional[str] = None
    famille: Optional[str] = None
    phase: Optional[str] = None
    description: Optional[str] = None
    date_reception: Optional[datetime] = None
    date_enregistrement: Optional[datetime] = Field(default_factory=datetime.utcnow)
    faisabilite: Optional[str] = None
    date_reponse: Optional[datetime] = None
    type_dfc: Optional[str] = None
    numero_derogation: Optional[int] = None
    date_application_estimee: Optional[datetime] = None
    date_application_effective: Optional[datetime] = None
    commentaire: Optional[str] = None
