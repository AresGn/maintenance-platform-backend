# Schémas pour les sites
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SiteBase(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None

class SiteCreate(SiteBase):
    pass

class SiteUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class SiteResponse(SiteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schéma avec les relations pour les détails complets
class SiteWithRelations(SiteResponse):
    equipment_count: Optional[int] = 0

    class Config:
        from_attributes = True
