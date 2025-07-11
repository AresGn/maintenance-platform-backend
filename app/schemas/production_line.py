# Schémas pour les lignes de production
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductionLineBase(BaseModel):
    site_id: int
    name: str
    description: Optional[str] = None

class ProductionLineCreate(ProductionLineBase):
    pass

class ProductionLineUpdate(BaseModel):
    site_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None

class ProductionLineResponse(ProductionLineBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schéma avec les relations pour les détails complets
class ProductionLineWithRelations(ProductionLineResponse):
    equipment_count: Optional[int] = 0

    class Config:
        from_attributes = True
