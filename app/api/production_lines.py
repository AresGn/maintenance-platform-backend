# Endpoints pour les lignes de production
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..core.database import get_db
from ..models.production_line import ProductionLine
from ..models.site import Site
from ..models.equipment import Equipment
from ..schemas.production_line import ProductionLineCreate, ProductionLineUpdate, ProductionLineResponse, ProductionLineWithRelations
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.get("/", response_model=List[ProductionLineResponse])
async def get_production_lines(
    site_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer la liste des lignes de production"""
    query = db.query(ProductionLine)
    
    if site_id:
        query = query.filter(ProductionLine.site_id == site_id)
    
    production_lines = query.offset(skip).limit(limit).all()
    return production_lines

@router.get("/{line_id}", response_model=ProductionLineWithRelations)
async def get_production_line(
    line_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer une ligne de production par son ID avec ses relations"""
    line = db.query(ProductionLine).options(
        joinedload(ProductionLine.site),
        joinedload(ProductionLine.equipment)
    ).filter(ProductionLine.id == line_id).first()
    
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligne de production non trouvée"
        )
    
    # Ajouter le nombre d'équipements
    equipment_count = db.query(Equipment).filter(Equipment.production_line_id == line_id).count()
    line_dict = line.__dict__.copy()
    line_dict['equipment_count'] = equipment_count
    
    return line_dict

@router.post("/", response_model=ProductionLineResponse, status_code=status.HTTP_201_CREATED)
async def create_production_line(
    line_data: ProductionLineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle ligne de production"""
    # Vérifier les permissions
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    # Vérifier que le site existe
    site = db.query(Site).filter(Site.id == line_data.site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Site non trouvé"
        )
    
    # Vérifier si une ligne avec ce nom existe déjà dans ce site
    existing_line = db.query(ProductionLine).filter(
        ProductionLine.site_id == line_data.site_id,
        ProductionLine.name == line_data.name
    ).first()
    if existing_line:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une ligne de production avec ce nom existe déjà dans ce site"
        )
    
    db_line = ProductionLine(**line_data.dict())
    db.add(db_line)
    db.commit()
    db.refresh(db_line)
    
    return db_line

@router.put("/{line_id}", response_model=ProductionLineResponse)
async def update_production_line(
    line_id: int,
    line_data: ProductionLineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour une ligne de production"""
    # Vérifier les permissions
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligne de production non trouvée"
        )
    
    # Mettre à jour les champs modifiés
    update_data = line_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(line, field, value)
    
    db.commit()
    db.refresh(line)
    
    return line

@router.delete("/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_production_line(
    line_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer une ligne de production"""
    # Seuls les admins peuvent supprimer
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent supprimer des lignes de production"
        )
    
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligne de production non trouvée"
        )
    
    # Vérifier s'il y a des équipements associés
    equipment_count = db.query(Equipment).filter(Equipment.production_line_id == line_id).count()
    if equipment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible de supprimer la ligne : {equipment_count} équipement(s) associé(s)"
        )
    
    db.delete(line)
    db.commit()
    
    return None
