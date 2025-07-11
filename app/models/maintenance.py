# Modèles pour la maintenance
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from .base import BaseModel

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

class MaintenancePlan(BaseModel):
    __tablename__ = "maintenance_plans"
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False, default=MaintenanceType.PREVENTIVE)
    frequency_days = Column(Integer, nullable=False)  # fréquence en jours
    estimated_duration = Column(Integer, nullable=False)  # durée estimée en minutes
    priority = Column(SQLEnum(MaintenancePriority), nullable=False, default=MaintenancePriority.MEDIUM)
    is_active = Column(Boolean, default=True, nullable=False)
    next_due_date = Column(DateTime, nullable=True)
    
    # Relations
    equipment = relationship("Equipment", back_populates="maintenance_plans")
    tasks = relationship("MaintenanceTask", back_populates="maintenance_plan", cascade="all, delete-orphan")
    scheduled_maintenances = relationship("ScheduledMaintenance", back_populates="maintenance_plan")
    
    def __repr__(self):
        return f"<MaintenancePlan(id={self.id}, name='{self.name}', equipment_id={self.equipment_id})>"

class MaintenanceTask(BaseModel):
    __tablename__ = "maintenance_tasks"
    
    maintenance_plan_id = Column(Integer, ForeignKey("maintenance_plans.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    estimated_duration = Column(Integer, nullable=False)  # en minutes
    required_skills = Column(JSON, nullable=True)  # liste des compétences requises
    tools_required = Column(JSON, nullable=True)  # liste des outils requis
    safety_requirements = Column(JSON, nullable=True)  # exigences de sécurité
    order = Column(Integer, nullable=False, default=1)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    
    # Relations
    maintenance_plan = relationship("MaintenancePlan", back_populates="tasks")
    intervention_tasks = relationship("InterventionTask", back_populates="maintenance_task")
    
    def __repr__(self):
        return f"<MaintenanceTask(id={self.id}, name='{self.name}', plan_id={self.maintenance_plan_id})>"

class ScheduledMaintenance(BaseModel):
    __tablename__ = "scheduled_maintenances"
    
    maintenance_plan_id = Column(Integer, ForeignKey("maintenance_plans.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    estimated_start_time = Column(String(8), nullable=False)  # Format HH:MM:SS
    estimated_end_time = Column(String(8), nullable=False)    # Format HH:MM:SS
    assigned_technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.SCHEDULED)
    priority = Column(SQLEnum(MaintenancePriority), nullable=False, default=MaintenancePriority.MEDIUM)
    notes = Column(Text, nullable=True)
    
    # Relations
    maintenance_plan = relationship("MaintenancePlan", back_populates="scheduled_maintenances")
    equipment = relationship("Equipment", back_populates="scheduled_maintenances")
    assigned_technician = relationship("User", foreign_keys=[assigned_technician_id])
    interventions = relationship("MaintenanceIntervention", back_populates="scheduled_maintenance")
    
    def __repr__(self):
        return f"<ScheduledMaintenance(id={self.id}, equipment_id={self.equipment_id}, date={self.scheduled_date})>"

class MaintenanceIntervention(BaseModel):
    __tablename__ = "maintenance_interventions"
    
    scheduled_maintenance_id = Column(Integer, ForeignKey("scheduled_maintenances.id"), nullable=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False)
    status = Column(SQLEnum(InterventionStatus), nullable=False, default=InterventionStatus.PENDING)
    priority = Column(SQLEnum(MaintenancePriority), nullable=False, default=MaintenancePriority.MEDIUM)
    
    # Dates et durées
    scheduled_date = Column(DateTime, nullable=True)
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    downtime_start = Column(DateTime, nullable=True)
    downtime_end = Column(DateTime, nullable=True)
    
    # Détails de l'intervention
    description = Column(Text, nullable=False)
    work_performed = Column(Text, nullable=True)
    issues_found = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Validation
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    validation_notes = Column(Text, nullable=True)
    
    # Coûts
    labor_cost = Column(Integer, nullable=True)  # en centimes d'euro
    parts_cost = Column(Integer, nullable=True)  # en centimes d'euro
    total_cost = Column(Integer, nullable=True)  # en centimes d'euro
    
    # Relations
    scheduled_maintenance = relationship("ScheduledMaintenance", back_populates="interventions")
    equipment = relationship("Equipment", back_populates="interventions")
    technician = relationship("User", foreign_keys=[technician_id])
    validator = relationship("User", foreign_keys=[validated_by])
    tasks = relationship("InterventionTask", back_populates="intervention", cascade="all, delete-orphan")
    parts_used = relationship("MaintenancePartUsed", back_populates="intervention", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MaintenanceIntervention(id={self.id}, equipment_id={self.equipment_id}, status='{self.status}')>"

class InterventionTask(BaseModel):
    __tablename__ = "intervention_tasks"
    
    intervention_id = Column(Integer, ForeignKey("maintenance_interventions.id"), nullable=False)
    maintenance_task_id = Column(Integer, ForeignKey("maintenance_tasks.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    completion_notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    order = Column(Integer, nullable=False, default=1)
    
    # Relations
    intervention = relationship("MaintenanceIntervention", back_populates="tasks")
    maintenance_task = relationship("MaintenanceTask", back_populates="intervention_tasks")
    
    def __repr__(self):
        return f"<InterventionTask(id={self.id}, name='{self.name}', completed={self.is_completed})>"

class MaintenancePartUsed(BaseModel):
    __tablename__ = "maintenance_parts_used"
    
    intervention_id = Column(Integer, ForeignKey("maintenance_interventions.id"), nullable=False)
    part_id = Column(Integer, nullable=False)  # Référence vers une table de pièces (à créer plus tard)
    quantity_used = Column(Integer, nullable=False)
    unit_cost = Column(Integer, nullable=True)  # en centimes d'euro
    total_cost = Column(Integer, nullable=True)  # en centimes d'euro
    
    # Relations
    intervention = relationship("MaintenanceIntervention", back_populates="parts_used")
    
    def __repr__(self):
        return f"<MaintenancePartUsed(id={self.id}, part_id={self.part_id}, quantity={self.quantity_used})>"
