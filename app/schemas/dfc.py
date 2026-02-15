from typing import Optional
from sqlmodel import SQLModel
from datetime import datetime
from pydantic import computed_field

class DFCCreate(SQLModel):
    numero_dfc: Optional[int] = None
    projet: Optional[str] = None
    famille: Optional[str] = None
    phase: Optional[str] = None
    responsable_id: Optional[int] = None  # User FK
    description: Optional[str] = None
    date_reception: Optional[datetime] = None
    faisabilite: Optional[str] = None
    type_dfc: Optional[str] = None
    statut: str = "ouvert"  # ouvert / ferme
    commentaire: Optional[str] = None

class DFCRead(SQLModel):
    id: int
    numero_dfc: Optional[int]
    projet: Optional[str] = None
    famille: Optional[str] = None
    phase: Optional[str] = None
    responsable_id: Optional[int] = None
    description: Optional[str] = None
    date_reception: Optional[datetime] = None
    date_enregistrement: Optional[datetime] = None
    date_reponse: Optional[datetime] = None
    faisabilite: Optional[str] = None
    type_dfc: Optional[str] = None
    statut: str
    numero_derogation: Optional[int]
    date_application_estimee: Optional[datetime] = None
    date_application_effective: Optional[datetime] = None
    commentaire: Optional[str] = None
    
    @computed_field
    @property
    def delai(self) -> Optional[int]:
        """Calculate delay dynamically in days between reception and response."""
        if self.date_reception and self.date_reponse:
            return (self.date_reponse - self.date_reception).days
        return None

    @computed_field
    @property
    def projet_name(self) -> Optional[str]:
        # expose projet name from relationship when available
        ref = getattr(self, "projet_ref", None)
        if ref:
            return getattr(ref, "name", None)
        return None

    @computed_field
    @property
    def famille_name(self) -> Optional[str]:
        ref = getattr(self, "famille_ref", None)
        if ref:
            return getattr(ref, "name", None)
        return None

    @computed_field
    @property
    def phase_name(self) -> Optional[str]:
        ref = getattr(self, "phase_ref", None)
        if ref:
            return getattr(ref, "name", None)
        return None
