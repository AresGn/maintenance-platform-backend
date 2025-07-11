# Modèle Production Line
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class ProductionLine(BaseModel):
    __tablename__ = "production_lines"
    
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relations
    site = relationship("Site", back_populates="production_lines")
    equipment = relationship("Equipment", back_populates="production_line")
    
    def __repr__(self):
        return f"<ProductionLine(id={self.id}, name='{self.name}', site_id={self.site_id})>"
