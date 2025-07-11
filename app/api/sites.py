# Endpoints pour les sites
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..core.database import get_db
from ..models.site import Site
from ..models.production_line import ProductionLine
from ..models.equipment import Equipment
from ..schemas.site import SiteCreate, SiteUpdate, SiteResponse, SiteWithRelations
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.get("/", response_model=List[SiteResponse])
async def get_sites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer la liste des sites"""
    sites = db.query(Site).offset(skip).limit(limit).all()
    return sites

@router.get("/{site_id}", response_model=SiteWithRelations)
async def get_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un site par son ID avec ses relations"""
    site = db.query(Site).options(
        joinedload(Site.production_lines),
        joinedload(Site.equipment)
    ).filter(Site.id == site_id).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site non trouvé"
        )
    
    # Ajouter le nombre d'équipements
    equipment_count = db.query(Equipment).filter(Equipment.site_id == site_id).count()
    site_dict = site.__dict__.copy()
    site_dict['equipment_count'] = equipment_count
    
    return site_dict

@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau site"""
    # Vérifier les permissions (seuls admin et supervisor peuvent créer)
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    # Vérifier si un site avec ce nom existe déjà
    existing_site = db.query(Site).filter(Site.name == site_data.name).first()
    if existing_site:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un site avec ce nom existe déjà"
        )
    
    db_site = Site(**site_data.dict())
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    
    return db_site

@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un site"""
    # Vérifier les permissions
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site non trouvé"
        )
    
    # Mettre à jour les champs modifiés
    update_data = site_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)
    
    db.commit()
    db.refresh(site)
    
    return site

@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un site"""
    # Seuls les admins peuvent supprimer
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent supprimer des sites"
        )
    
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site non trouvé"
        )
    
    # Vérifier s'il y a des équipements associés
    equipment_count = db.query(Equipment).filter(Equipment.site_id == site_id).count()
    if equipment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible de supprimer le site : {equipment_count} équipement(s) associé(s)"
        )
    
    db.delete(site)
    db.commit()
    
    return None
