from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class DFC(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero_dfc: Optional[int] = Field(index=True, unique=True)
    
    # Foreign key to Reference for project
    projet_id: Optional[int] = Field(default=None, foreign_key="reference.id")
    projet_ref: Optional["Reference"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[DFC.projet_id]"})
    
    # Foreign key to Reference for family
    famille_id: Optional[int] = Field(default=None, foreign_key="reference.id")
    famille_ref: Optional["Reference"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[DFC.famille_id]"})
    
    # Foreign key to Reference for phase
    phase_id: Optional[int] = Field(default=None, foreign_key="reference.id")
    phase_ref: Optional["Reference"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[DFC.phase_id]"})
    
    # Foreign key to User for responsible person
    responsable_id: Optional[int] = Field(default=None, foreign_key="user.id")
    responsable: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[DFC.responsable_id]"})
    
    description: Optional[str] = None
    date_reception: Optional[datetime] = None
    date_enregistrement: Optional[datetime] = Field(default_factory=datetime.utcnow)
    faisabilite: Optional[str] = None
    date_reponse: Optional[datetime] = None
    type_dfc: Optional[str] = None
    statut: str = Field(default="ouvert", index=True)  # ouvert / ferme
    numero_derogation: Optional[int] = None
    date_application_estimee: Optional[datetime] = None
    date_application_effective: Optional[datetime] = None
    commentaire: Optional[str] = None


# Import statements needed for type hints
from .reference import Reference
from .user import User
