# Modèle Site
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class Site(BaseModel):
    __tablename__ = "sites"
    
    name = Column(String(100), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Relations
    production_lines = relationship("ProductionLine", back_populates="site", cascade="all, delete-orphan")
    equipment = relationship("Equipment", back_populates="site")
    
    def __repr__(self):
        return f"<Site(id={self.id}, name='{self.name}', location='{self.location}')>"
