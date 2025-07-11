# Modèle Equipment
from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Equipment(BaseModel):
    __tablename__ = "equipment"
    
    name = Column(String(100), nullable=False)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), unique=True, nullable=True)
    manufacturer = Column(String(100), nullable=True)
    purchase_date = Column(Date, nullable=True)
    installation_date = Column(Date, nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    expected_lifespan = Column(Integer, nullable=True)  # en années
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    production_line_id = Column(Integer, ForeignKey("production_lines.id"), nullable=True)
    status = Column(String(20), nullable=False, default='active')  # active, inactive, maintenance, broken
    criticality = Column(String(10), nullable=False, default='medium')  # low, medium, high, critical
    specifications = Column(JSON, nullable=True)
    
    # Relations
    site = relationship("Site", back_populates="equipment")
    production_line = relationship("ProductionLine", back_populates="equipment")
    maintenance_plans = relationship("MaintenancePlan", back_populates="equipment")
    scheduled_maintenances = relationship("ScheduledMaintenance", back_populates="equipment")
    interventions = relationship("MaintenanceIntervention", back_populates="equipment")
    
    def __repr__(self):
        return f"<Equipment(id={self.id}, name='{self.name}', status='{self.status}', criticality='{self.criticality}')>"
    
    @property
    def status_display(self):
        """Retourne le statut en français pour l'affichage"""
        status_map = {
            'active': 'Actif',
            'inactive': 'Inactif',
            'maintenance': 'En maintenance',
            'broken': 'En panne'
        }
        return status_map.get(self.status, self.status)
    
    @property
    def criticality_display(self):
        """Retourne la criticité en français pour l'affichage"""
        criticality_map = {
            'low': 'Faible',
            'medium': 'Moyenne',
            'high': 'Élevée',
            'critical': 'Critique'
        }
        return criticality_map.get(self.criticality, self.criticality)
