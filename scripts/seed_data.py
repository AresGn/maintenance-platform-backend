#!/usr/bin/env python3
"""
Script pour insérer des données d'exemple dans la base de données
"""
import sys
import os
from datetime import date, datetime, timedelta

# Ajouter le répertoire parent au path pour importer les modules de l'app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.site import Site
from app.models.production_line import ProductionLine
from app.models.equipment import Equipment

def create_sample_data():
    """Créer des données d'exemple"""
    db = SessionLocal()
    
    try:
        print("🌱 Insertion des données d'exemple...")
        
        # Vérifier si des données existent déjà
        if db.query(Site).count() > 0:
            print("⚠️  Des données existent déjà. Suppression en cours...")
            # Supprimer les données existantes dans l'ordre inverse des dépendances
            db.query(Equipment).delete()
            db.query(ProductionLine).delete()
            db.query(Site).delete()
            db.commit()
        
        # Créer les sites
        sites_data = [
            {
                "name": "Usine de Lyon",
                "location": "Lyon, France",
                "description": "Site principal de production automobile"
            },
            {
                "name": "Usine de Marseille",
                "location": "Marseille, France", 
                "description": "Site de production de composants électroniques"
            },
            {
                "name": "Centre de Distribution Paris",
                "location": "Paris, France",
                "description": "Centre logistique et de distribution"
            }
        ]
        
        sites = []
        for site_data in sites_data:
            site = Site(**site_data)
            db.add(site)
            sites.append(site)
        
        db.commit()
        print(f"✅ {len(sites)} sites créés")
        
        # Créer les lignes de production
        production_lines_data = [
            # Usine de Lyon
            {"site_id": sites[0].id, "name": "Ligne d'assemblage A", "description": "Assemblage des moteurs"},
            {"site_id": sites[0].id, "name": "Ligne d'assemblage B", "description": "Assemblage des châssis"},
            {"site_id": sites[0].id, "name": "Ligne de peinture", "description": "Peinture et finition"},
            
            # Usine de Marseille
            {"site_id": sites[1].id, "name": "Ligne PCB", "description": "Production de circuits imprimés"},
            {"site_id": sites[1].id, "name": "Ligne de test", "description": "Tests et contrôle qualité"},
            
            # Centre de Distribution Paris
            {"site_id": sites[2].id, "name": "Zone de tri", "description": "Tri et préparation des commandes"},
            {"site_id": sites[2].id, "name": "Zone d'expédition", "description": "Emballage et expédition"}
        ]
        
        production_lines = []
        for line_data in production_lines_data:
            line = ProductionLine(**line_data)
            db.add(line)
            production_lines.append(line)
        
        db.commit()
        print(f"✅ {len(production_lines)} lignes de production créées")
        
        # Créer les équipements
        equipment_data = [
            # Équipements Lyon - Ligne A
            {
                "name": "Robot de soudage R1",
                "model": "KUKA KR 6 R900",
                "serial_number": "KR6-001-2023",
                "manufacturer": "KUKA",
                "purchase_date": date(2023, 1, 15),
                "installation_date": date(2023, 2, 1),
                "warranty_expiry": date(2026, 1, 15),
                "expected_lifespan": 10,
                "site_id": sites[0].id,
                "production_line_id": production_lines[0].id,
                "status": "active",
                "criticality": "high",
                "specifications": {"payload": "6kg", "reach": "900mm", "precision": "±0.03mm"}
            },
            {
                "name": "Convoyeur principal",
                "model": "CONV-2000",
                "serial_number": "CONV-001-2023",
                "manufacturer": "FlexLink",
                "purchase_date": date(2023, 1, 20),
                "installation_date": date(2023, 2, 5),
                "warranty_expiry": date(2025, 1, 20),
                "expected_lifespan": 15,
                "site_id": sites[0].id,
                "production_line_id": production_lines[0].id,
                "status": "active",
                "criticality": "medium",
                "specifications": {"length": "20m", "speed": "0.5m/s", "load_capacity": "50kg/m"}
            },
            
            # Équipements Lyon - Ligne B
            {
                "name": "Presse hydraulique P1",
                "model": "SCHULER PH-500",
                "serial_number": "SCH-PH-001",
                "manufacturer": "SCHULER",
                "purchase_date": date(2022, 6, 10),
                "installation_date": date(2022, 7, 1),
                "warranty_expiry": date(2025, 6, 10),
                "expected_lifespan": 20,
                "site_id": sites[0].id,
                "production_line_id": production_lines[1].id,
                "status": "maintenance",
                "criticality": "critical",
                "specifications": {"force": "500T", "stroke": "300mm", "speed": "10mm/s"}
            },
            
            # Équipements Marseille
            {
                "name": "Machine d'insertion SMD",
                "model": "YAMAHA YSM20R",
                "serial_number": "YAM-SMD-001",
                "manufacturer": "YAMAHA",
                "purchase_date": date(2023, 3, 1),
                "installation_date": date(2023, 3, 15),
                "warranty_expiry": date(2026, 3, 1),
                "expected_lifespan": 12,
                "site_id": sites[1].id,
                "production_line_id": production_lines[3].id,
                "status": "active",
                "criticality": "high",
                "specifications": {"placement_rate": "45000cph", "accuracy": "±25μm", "component_range": "0201-55mm"}
            },
            {
                "name": "Four de refusion",
                "model": "REHM VISION X",
                "serial_number": "REHM-VX-001",
                "manufacturer": "REHM",
                "purchase_date": date(2023, 3, 5),
                "installation_date": date(2023, 3, 20),
                "warranty_expiry": date(2026, 3, 5),
                "expected_lifespan": 15,
                "site_id": sites[1].id,
                "production_line_id": production_lines[3].id,
                "status": "broken",
                "criticality": "critical",
                "specifications": {"zones": "10", "max_temp": "350°C", "belt_width": "350mm"}
            },
            
            # Équipements Paris
            {
                "name": "Système de tri automatique",
                "model": "DEMATIC SortCap",
                "serial_number": "DEM-SC-001",
                "manufacturer": "DEMATIC",
                "purchase_date": date(2022, 11, 1),
                "installation_date": date(2022, 12, 1),
                "warranty_expiry": date(2025, 11, 1),
                "expected_lifespan": 12,
                "site_id": sites[2].id,
                "production_line_id": production_lines[5].id,
                "status": "active",
                "criticality": "high",
                "specifications": {"capacity": "15000items/h", "accuracy": "99.9%", "dimensions": "50x30x5m"}
            }
        ]
        
        equipment_list = []
        for equip_data in equipment_data:
            equipment = Equipment(**equip_data)
            db.add(equipment)
            equipment_list.append(equipment)
        
        db.commit()
        print(f"✅ {len(equipment_list)} équipements créés")
        
        print("\n📊 Résumé des données créées:")
        print(f"   • Sites: {len(sites)}")
        print(f"   • Lignes de production: {len(production_lines)}")
        print(f"   • Équipements: {len(equipment_list)}")
        
        # Afficher les statistiques par statut
        status_counts = {}
        for equipment in equipment_list:
            status_counts[equipment.status] = status_counts.get(equipment.status, 0) + 1
        
        print(f"\n📈 Répartition par statut:")
        for status, count in status_counts.items():
            print(f"   • {status}: {count}")
        
        print("\n🎉 Données d'exemple créées avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
