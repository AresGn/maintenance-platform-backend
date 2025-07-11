# Routes API pour la maintenance
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.maintenance import (
    MaintenancePlan, MaintenanceTask, ScheduledMaintenance, 
    MaintenanceIntervention, InterventionTask
)
from app.schemas.maintenance import (
    MaintenancePlanCreate, MaintenancePlanUpdate, MaintenancePlanResponse,
    ScheduledMaintenanceCreate, ScheduledMaintenanceUpdate, ScheduledMaintenanceResponse,
    MaintenanceInterventionCreate, MaintenanceInterventionUpdate, MaintenanceInterventionResponse,
    CalendarEvent, MaintenanceStats
)

router = APIRouter()

# ===== PLANS DE MAINTENANCE =====

@router.get("/plans", response_model=List[MaintenancePlanResponse])
def get_maintenance_plans(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des plans de maintenance"""
    query = db.query(MaintenancePlan)
    
    if equipment_id:
        query = query.filter(MaintenancePlan.equipment_id == equipment_id)
    if is_active is not None:
        query = query.filter(MaintenancePlan.is_active == is_active)
    
    plans = query.offset(skip).limit(limit).all()
    return plans

@router.get("/plans/{plan_id}", response_model=MaintenancePlanResponse)
def get_maintenance_plan(plan_id: int, db: Session = Depends(get_db)):
    """Récupérer un plan de maintenance par ID"""
    plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan de maintenance non trouvé")
    return plan

@router.post("/plans", response_model=MaintenancePlanResponse)
def create_maintenance_plan(plan: MaintenancePlanCreate, db: Session = Depends(get_db)):
    """Créer un nouveau plan de maintenance"""
    # Créer le plan
    db_plan = MaintenancePlan(
        name=plan.name,
        description=plan.description,
        equipment_id=plan.equipment_id,
        maintenance_type=plan.maintenance_type,
        frequency_days=plan.frequency_days,
        estimated_duration=plan.estimated_duration,
        priority=plan.priority,
        is_active=plan.is_active
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    # Créer les tâches associées
    for task_data in plan.tasks:
        db_task = MaintenanceTask(
            maintenance_plan_id=db_plan.id,
            name=task_data.name,
            description=task_data.description,
            estimated_duration=task_data.estimated_duration,
            required_skills=task_data.required_skills,
            tools_required=task_data.tools_required,
            safety_requirements=task_data.safety_requirements,
            order=task_data.order,
            is_mandatory=task_data.is_mandatory
        )
        db.add(db_task)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.put("/plans/{plan_id}", response_model=MaintenancePlanResponse)
def update_maintenance_plan(
    plan_id: int, 
    plan_update: MaintenancePlanUpdate, 
    db: Session = Depends(get_db)
):
    """Mettre à jour un plan de maintenance"""
    db_plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan de maintenance non trouvé")
    
    update_data = plan_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_plan, field, value)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.delete("/plans/{plan_id}")
def delete_maintenance_plan(plan_id: int, db: Session = Depends(get_db)):
    """Supprimer un plan de maintenance"""
    db_plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan de maintenance non trouvé")
    
    db.delete(db_plan)
    db.commit()
    return {"message": "Plan de maintenance supprimé"}

# ===== MAINTENANCES PLANIFIÉES =====

@router.get("/scheduled", response_model=List[ScheduledMaintenanceResponse])
def get_scheduled_maintenances(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    technician_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des maintenances planifiées"""
    query = db.query(ScheduledMaintenance)
    
    if equipment_id:
        query = query.filter(ScheduledMaintenance.equipment_id == equipment_id)
    if technician_id:
        query = query.filter(ScheduledMaintenance.assigned_technician_id == technician_id)
    if status:
        query = query.filter(ScheduledMaintenance.status == status)
    if date_from:
        query = query.filter(ScheduledMaintenance.scheduled_date >= date_from)
    if date_to:
        query = query.filter(ScheduledMaintenance.scheduled_date <= date_to)
    
    maintenances = query.offset(skip).limit(limit).all()
    return maintenances

@router.get("/scheduled/{maintenance_id}", response_model=ScheduledMaintenanceResponse)
def get_scheduled_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    """Récupérer une maintenance planifiée par ID"""
    maintenance = db.query(ScheduledMaintenance).filter(
        ScheduledMaintenance.id == maintenance_id
    ).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance planifiée non trouvée")
    return maintenance

@router.post("/scheduled", response_model=ScheduledMaintenanceResponse)
def create_scheduled_maintenance(
    maintenance: ScheduledMaintenanceCreate, 
    db: Session = Depends(get_db)
):
    """Créer une nouvelle maintenance planifiée"""
    db_maintenance = ScheduledMaintenance(**maintenance.dict())
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance

# ===== INTERVENTIONS =====

@router.get("/interventions", response_model=List[MaintenanceInterventionResponse])
def get_interventions(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    technician_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des interventions"""
    query = db.query(MaintenanceIntervention)
    
    if equipment_id:
        query = query.filter(MaintenanceIntervention.equipment_id == equipment_id)
    if technician_id:
        query = query.filter(MaintenanceIntervention.technician_id == technician_id)
    if status:
        query = query.filter(MaintenanceIntervention.status == status)
    
    interventions = query.offset(skip).limit(limit).all()
    return interventions

@router.get("/interventions/{intervention_id}", response_model=MaintenanceInterventionResponse)
def get_intervention(intervention_id: int, db: Session = Depends(get_db)):
    """Récupérer une intervention par ID"""
    intervention = db.query(MaintenanceIntervention).filter(
        MaintenanceIntervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")
    return intervention

@router.post("/interventions", response_model=MaintenanceInterventionResponse)
def create_intervention(
    intervention: MaintenanceInterventionCreate, 
    db: Session = Depends(get_db)
):
    """Créer une nouvelle intervention"""
    db_intervention = MaintenanceIntervention(**intervention.dict())
    db.add(db_intervention)
    db.commit()
    db.refresh(db_intervention)
    return db_intervention

@router.post("/interventions/{intervention_id}/start")
def start_intervention(intervention_id: int, db: Session = Depends(get_db)):
    """Démarrer une intervention"""
    intervention = db.query(MaintenanceIntervention).filter(
        MaintenanceIntervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")
    
    intervention.status = "in_progress"
    intervention.actual_start_time = datetime.now()
    db.commit()
    db.refresh(intervention)
    return intervention

@router.post("/interventions/{intervention_id}/complete")
def complete_intervention(
    intervention_id: int, 
    completion_data: dict,
    db: Session = Depends(get_db)
):
    """Terminer une intervention"""
    intervention = db.query(MaintenanceIntervention).filter(
        MaintenanceIntervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")
    
    intervention.status = "completed"
    intervention.actual_end_time = datetime.now()
    intervention.work_performed = completion_data.get("work_performed")
    intervention.issues_found = completion_data.get("issues_found")
    intervention.recommendations = completion_data.get("recommendations")
    
    db.commit()
    db.refresh(intervention)
    return intervention

# ===== CALENDRIER =====

@router.get("/calendar", response_model=List[CalendarEvent])
def get_calendar_events(
    start_date: str = Query(...),
    end_date: str = Query(...),
    equipment_id: Optional[int] = None,
    technician_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Récupérer les événements du calendrier"""
    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    # Récupérer les maintenances planifiées
    query = db.query(ScheduledMaintenance).filter(
        ScheduledMaintenance.scheduled_date >= start_dt,
        ScheduledMaintenance.scheduled_date <= end_dt
    )
    
    if equipment_id:
        query = query.filter(ScheduledMaintenance.equipment_id == equipment_id)
    if technician_id:
        query = query.filter(ScheduledMaintenance.assigned_technician_id == technician_id)
    
    scheduled_maintenances = query.all()
    
    events = []
    for maintenance in scheduled_maintenances:
        # Calculer les heures de début et fin
        start_time = datetime.combine(
            maintenance.scheduled_date.date(),
            datetime.strptime(maintenance.estimated_start_time, "%H:%M:%S").time()
        )
        end_time = datetime.combine(
            maintenance.scheduled_date.date(),
            datetime.strptime(maintenance.estimated_end_time, "%H:%M:%S").time()
        )
        
        event = CalendarEvent(
            id=f"scheduled_{maintenance.id}",
            title=f"Maintenance - {maintenance.equipment.name if maintenance.equipment else 'Équipement'}",
            start=start_time,
            end=end_time,
            extendedProps={
                "type": "scheduled",
                "status": maintenance.status,
                "priority": maintenance.priority,
                "equipment_name": maintenance.equipment.name if maintenance.equipment else "Équipement",
                "technician_name": f"{maintenance.assigned_technician.first_name} {maintenance.assigned_technician.last_name}" if maintenance.assigned_technician else None
            }
        )
        events.append(event)
    
    return events

# ===== STATISTIQUES =====

@router.get("/stats", response_model=MaintenanceStats)
def get_maintenance_stats(
    equipment_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Récupérer les statistiques de maintenance"""
    # Statistiques basiques (à implémenter selon les besoins)
    total_scheduled = db.query(ScheduledMaintenance).count()
    
    # Maintenances terminées ce mois
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    completed_this_month = db.query(MaintenanceIntervention).filter(
        MaintenanceIntervention.status == "completed",
        MaintenanceIntervention.actual_end_time >= current_month_start
    ).count()
    
    # Maintenances en retard
    overdue = db.query(ScheduledMaintenance).filter(
        ScheduledMaintenance.scheduled_date < datetime.now(),
        ScheduledMaintenance.status == "scheduled"
    ).count()
    
    # Maintenances en cours
    in_progress = db.query(MaintenanceIntervention).filter(
        MaintenanceIntervention.status == "in_progress"
    ).count()
    
    return MaintenanceStats(
        total_scheduled=total_scheduled,
        completed_this_month=completed_this_month,
        overdue=overdue,
        in_progress=in_progress,
        by_type={"preventive": 0, "corrective": 0, "predictive": 0, "emergency": 0},
        by_priority={"low": 0, "medium": 0, "high": 0, "critical": 0},
        average_completion_time=0.0,
        mttr=0.0,
        mtbf=0.0
    )
