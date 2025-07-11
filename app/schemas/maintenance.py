# Schémas pour la maintenance
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MaintenanceType(str, Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    PREDICTIVE = "predictive"
    EMERGENCY = "emergency"

class MaintenanceStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class InterventionStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VALIDATED = "validated"
    REJECTED = "rejected"

class MaintenancePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Schémas pour MaintenanceTask
class MaintenanceTaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    estimated_duration: int
    required_skills: Optional[List[str]] = None
    tools_required: Optional[List[str]] = None
    safety_requirements: Optional[List[str]] = None
    order: int = 1
    is_mandatory: bool = True

class MaintenanceTaskCreate(MaintenanceTaskBase):
    maintenance_plan_id: int

class MaintenanceTaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    estimated_duration: Optional[int] = None
    required_skills: Optional[List[str]] = None
    tools_required: Optional[List[str]] = None
    safety_requirements: Optional[List[str]] = None
    order: Optional[int] = None
    is_mandatory: Optional[bool] = None

class MaintenanceTaskResponse(MaintenanceTaskBase):
    id: int
    maintenance_plan_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schémas pour MaintenancePlan
class MaintenancePlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    equipment_id: int
    maintenance_type: MaintenanceType = MaintenanceType.PREVENTIVE
    frequency_days: int
    estimated_duration: int
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    is_active: bool = True

class MaintenancePlanCreate(MaintenancePlanBase):
    tasks: Optional[List[MaintenanceTaskBase]] = []

class MaintenancePlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    maintenance_type: Optional[MaintenanceType] = None
    frequency_days: Optional[int] = None
    estimated_duration: Optional[int] = None
    priority: Optional[MaintenancePriority] = None
    is_active: Optional[bool] = None

class MaintenancePlanResponse(MaintenancePlanBase):
    id: int
    next_due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    tasks: List[MaintenanceTaskResponse] = []
    
    class Config:
        from_attributes = True

# Schémas pour ScheduledMaintenance
class ScheduledMaintenanceBase(BaseModel):
    maintenance_plan_id: int
    equipment_id: int
    scheduled_date: datetime
    estimated_start_time: str
    estimated_end_time: str
    assigned_technician_id: Optional[int] = None
    status: MaintenanceStatus = MaintenanceStatus.SCHEDULED
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    notes: Optional[str] = None

class ScheduledMaintenanceCreate(ScheduledMaintenanceBase):
    pass

class ScheduledMaintenanceUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    estimated_start_time: Optional[str] = None
    estimated_end_time: Optional[str] = None
    assigned_technician_id: Optional[int] = None
    status: Optional[MaintenanceStatus] = None
    priority: Optional[MaintenancePriority] = None
    notes: Optional[str] = None

class ScheduledMaintenanceResponse(ScheduledMaintenanceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schémas pour InterventionTask
class InterventionTaskBase(BaseModel):
    intervention_id: int
    maintenance_task_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    is_completed: bool = False
    completion_notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    order: int = 1

class InterventionTaskCreate(InterventionTaskBase):
    pass

class InterventionTaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    completion_notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    order: Optional[int] = None

class InterventionTaskResponse(InterventionTaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schémas pour MaintenanceIntervention
class MaintenanceInterventionBase(BaseModel):
    equipment_id: int
    technician_id: int
    maintenance_type: MaintenanceType
    status: InterventionStatus = InterventionStatus.PENDING
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    description: str
    scheduled_date: Optional[datetime] = None

class MaintenanceInterventionCreate(MaintenanceInterventionBase):
    scheduled_maintenance_id: Optional[int] = None

class MaintenanceInterventionUpdate(BaseModel):
    status: Optional[InterventionStatus] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    downtime_start: Optional[datetime] = None
    downtime_end: Optional[datetime] = None
    work_performed: Optional[str] = None
    issues_found: Optional[str] = None
    recommendations: Optional[str] = None
    labor_cost: Optional[int] = None
    parts_cost: Optional[int] = None
    validation_notes: Optional[str] = None

class MaintenanceInterventionResponse(MaintenanceInterventionBase):
    id: int
    scheduled_maintenance_id: Optional[int] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    downtime_start: Optional[datetime] = None
    downtime_end: Optional[datetime] = None
    work_performed: Optional[str] = None
    issues_found: Optional[str] = None
    recommendations: Optional[str] = None
    validated_by: Optional[int] = None
    validated_at: Optional[datetime] = None
    validation_notes: Optional[str] = None
    labor_cost: Optional[int] = None
    parts_cost: Optional[int] = None
    total_cost: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    tasks: List[InterventionTaskResponse] = []
    
    class Config:
        from_attributes = True

# Schémas pour les statistiques
class MaintenanceStats(BaseModel):
    total_scheduled: int
    completed_this_month: int
    overdue: int
    in_progress: int
    by_type: dict
    by_priority: dict
    average_completion_time: float
    mttr: float
    mtbf: float

# Schémas pour les événements du calendrier
class CalendarEvent(BaseModel):
    id: str
    title: str
    start: datetime
    end: datetime
    allDay: bool = False
    backgroundColor: Optional[str] = None
    borderColor: Optional[str] = None
    textColor: Optional[str] = None
    extendedProps: Optional[dict] = None
