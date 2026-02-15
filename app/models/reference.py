from typing import Optional
from sqlmodel import SQLModel, Field

class Reference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str  # e.g., 'project', 'family', 'phase'
