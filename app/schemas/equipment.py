# Schémas pour les équipements
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class EquipmentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    BROKEN = "broken"

class EquipmentCriticality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EquipmentBase(BaseModel):
    name: str
    model: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[date] = None
    installation_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    expected_lifespan: Optional[int] = None
    site_id: Optional[int] = None
    production_line_id: Optional[int] = None
    status: EquipmentStatus = EquipmentStatus.ACTIVE
    criticality: EquipmentCriticality = EquipmentCriticality.MEDIUM
    specifications: Optional[Dict[str, Any]] = None

class EquipmentCreate(EquipmentBase):
    @validator('serial_number')
    def validate_serial_number(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[date] = None
    installation_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    expected_lifespan: Optional[int] = None
    site_id: Optional[int] = None
    production_line_id: Optional[int] = None
    status: Optional[EquipmentStatus] = None
    criticality: Optional[EquipmentCriticality] = None
    specifications: Optional[Dict[str, Any]] = None

class EquipmentResponse(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    status_display: Optional[str] = None
    criticality_display: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schéma avec les relations pour les détails complets
class EquipmentWithRelations(EquipmentResponse):
    site_name: Optional[str] = None
    production_line_name: Optional[str] = None

    class Config:
        from_attributes = True

# Schéma pour les filtres de recherche
class EquipmentFilter(BaseModel):
    site_id: Optional[int] = None
    production_line_id: Optional[int] = None
    status: Optional[EquipmentStatus] = None
    criticality: Optional[EquipmentCriticality] = None
    search: Optional[str] = None  # Recherche dans nom, modèle, fabricant


