# Endpoints pour les équipements
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
from ..core.database import get_db
from ..models.equipment import Equipment
from ..models.site import Site
from ..models.production_line import ProductionLine
from ..schemas.equipment import (
    EquipmentCreate, EquipmentUpdate, EquipmentResponse, 
    EquipmentWithRelations, EquipmentFilter, EquipmentStatus, EquipmentCriticality
)
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.get("/", response_model=List[EquipmentResponse])
async def get_equipment_list(
    site_id: Optional[int] = Query(None),
    production_line_id: Optional[int] = Query(None),
    status: Optional[EquipmentStatus] = Query(None),
    criticality: Optional[EquipmentCriticality] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer la liste des équipements avec filtres"""
    query = db.query(Equipment)
    
    # Appliquer les filtres
    if site_id:
        query = query.filter(Equipment.site_id == site_id)
    
    if production_line_id:
        query = query.filter(Equipment.production_line_id == production_line_id)
    
    if status:
        query = query.filter(Equipment.status == status)
    
    if criticality:
        query = query.filter(Equipment.criticality == criticality)
    
    if search:
        search_filter = or_(
            Equipment.name.ilike(f"%{search}%"),
            Equipment.model.ilike(f"%{search}%"),
            Equipment.manufacturer.ilike(f"%{search}%"),
            Equipment.serial_number.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    equipment_list = query.offset(skip).limit(limit).all()
    return equipment_list

@router.get("/{equipment_id}", response_model=EquipmentWithRelations)
async def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un équipement par son ID avec ses relations"""
    equipment = db.query(Equipment).options(
        joinedload(Equipment.site),
        joinedload(Equipment.production_line)
    ).filter(Equipment.id == equipment_id).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement non trouvé"
        )

    # Créer la réponse avec les noms des relations
    equipment_dict = equipment.__dict__.copy()
    equipment_dict['site_name'] = equipment.site.name if equipment.site else None
    equipment_dict['production_line_name'] = equipment.production_line.name if equipment.production_line else None

    return equipment_dict

@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    equipment_data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouvel équipement"""
    # Vérifier les permissions
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    # Vérifier que le site existe si spécifié
    if equipment_data.site_id:
        site = db.query(Site).filter(Site.id == equipment_data.site_id).first()
        if not site:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Site non trouvé"
            )
    
    # Vérifier que la ligne de production existe si spécifiée
    if equipment_data.production_line_id:
        line = db.query(ProductionLine).filter(ProductionLine.id == equipment_data.production_line_id).first()
        if not line:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ligne de production non trouvée"
            )
        
        # Vérifier que la ligne appartient au site spécifié
        if equipment_data.site_id and line.site_id != equipment_data.site_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La ligne de production ne correspond pas au site spécifié"
            )
    
    # Vérifier l'unicité du numéro de série si spécifié
    if equipment_data.serial_number:
        existing_equipment = db.query(Equipment).filter(
            Equipment.serial_number == equipment_data.serial_number
        ).first()
        if existing_equipment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un équipement avec ce numéro de série existe déjà"
            )
    
    db_equipment = Equipment(**equipment_data.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)

    return db_equipment

@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: int,
    equipment_data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un équipement"""
    # Vérifier les permissions
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )

    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement non trouvé"
        )

    # Vérifier l'unicité du numéro de série si modifié
    update_data = equipment_data.model_dump(exclude_unset=True)
    if 'serial_number' in update_data and update_data['serial_number']:
        existing_equipment = db.query(Equipment).filter(
            Equipment.serial_number == update_data['serial_number'],
            Equipment.id != equipment_id
        ).first()
        if existing_equipment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un équipement avec ce numéro de série existe déjà"
            )

    # Mettre à jour les champs modifiés
    for field, value in update_data.items():
        setattr(equipment, field, value)

    db.commit()
    db.refresh(equipment)

    return equipment

@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un équipement"""
    # Seuls les admins peuvent supprimer
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent supprimer des équipements"
        )

    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement non trouvé"
        )

    db.delete(equipment)
    db.commit()

    return None

@router.get("/stats/summary")
async def get_equipment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les statistiques des équipements"""
    total = db.query(Equipment).count()
    active = db.query(Equipment).filter(Equipment.status == EquipmentStatus.ACTIVE).count()
    maintenance = db.query(Equipment).filter(Equipment.status == EquipmentStatus.MAINTENANCE).count()
    broken = db.query(Equipment).filter(Equipment.status == EquipmentStatus.BROKEN).count()
    inactive = db.query(Equipment).filter(Equipment.status == EquipmentStatus.INACTIVE).count()

    critical = db.query(Equipment).filter(Equipment.criticality == EquipmentCriticality.CRITICAL).count()
    high = db.query(Equipment).filter(Equipment.criticality == EquipmentCriticality.HIGH).count()

    return {
        "total": total,
        "by_status": {
            "active": active,
            "maintenance": maintenance,
            "broken": broken,
            "inactive": inactive
        },
        "by_criticality": {
            "critical": critical,
            "high": high,
            "medium": db.query(Equipment).filter(Equipment.criticality == EquipmentCriticality.MEDIUM).count(),
            "low": db.query(Equipment).filter(Equipment.criticality == EquipmentCriticality.LOW).count()
        }
    }
