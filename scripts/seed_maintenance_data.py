#!/usr/bin/env python3
"""
Script pour insérer des données complètes de maintenance dans la base de données
"""
import sys
import os
from datetime import date, datetime, timedelta
import random
from passlib.context import CryptContext

# Ajouter le répertoire parent au path pour importer les modules de l'app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.site import Site
from app.models.production_line import ProductionLine
from app.models.equipment import Equipment
from app.models.maintenance import (
    MaintenancePlan, MaintenanceTask, ScheduledMaintenance, 
    MaintenanceIntervention, InterventionTask,
    MaintenanceType, MaintenanceStatus, InterventionStatus, MaintenancePriority
)

# Configuration pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_users(db):
    """Créer des utilisateurs de test"""
    users_data = [
        {
            "username": "admin",
            "email": "admin@maintenance.com",
            "password_hash": hash_password("admin123"),
            "first_name": "Admin",
            "last_name": "System",
            "role": "admin",
            "is_active": True
        },
        {
            "username": "super1",
            "email": "supervisor1@maintenance.com",
            "password_hash": hash_password("super123"),
            "first_name": "Marie",
            "last_name": "Dubois",
            "role": "supervisor",
            "is_active": True
        },
        {
            "username": "tech1",
            "email": "tech1@maintenance.com",
            "password_hash": hash_password("tech123"),
            "first_name": "Pierre",
            "last_name": "Martin",
            "role": "technician",
            "is_active": True
        },
        {
            "username": "tech2",
            "email": "tech2@maintenance.com",
            "password_hash": hash_password("tech123"),
            "first_name": "Sophie",
            "last_name": "Bernard",
            "role": "technician",
            "is_active": True
        },
        {
            "username": "tech3",
            "email": "tech3@maintenance.com",
            "password_hash": hash_password("tech123"),
            "first_name": "Jean",
            "last_name": "Leroy",
            "role": "technician",
            "is_active": True
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        users.append(user)
    
    db.commit()
    return users

def create_sites_and_equipment(db):
    """Créer les sites, lignes de production et équipements"""
    # Sites
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
        }
    ]
    
    sites = []
    for site_data in sites_data:
        site = Site(**site_data)
        db.add(site)
        sites.append(site)
    
    db.commit()
    
    # Lignes de production
    production_lines_data = [
        {"name": "Ligne A - Assemblage", "site_id": sites[0].id, "description": "Ligne d'assemblage principal"},
        {"name": "Ligne B - Peinture", "site_id": sites[0].id, "description": "Ligne de peinture automatisée"},
        {"name": "Ligne C - Électronique", "site_id": sites[1].id, "description": "Assemblage composants électroniques"},
        {"name": "Ligne D - Test", "site_id": sites[1].id, "description": "Tests qualité et validation"}
    ]
    
    production_lines = []
    for line_data in production_lines_data:
        line = ProductionLine(**line_data)
        db.add(line)
        production_lines.append(line)
    
    db.commit()
    
    # Équipements
    equipment_data = [
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
            "criticality": "high"
        },
        {
            "name": "Convoyeur principal C1",
            "model": "FlexLink X85",
            "serial_number": "FL-X85-002",
            "manufacturer": "FlexLink",
            "purchase_date": date(2022, 6, 10),
            "installation_date": date(2022, 7, 1),
            "warranty_expiry": date(2025, 6, 10),
            "expected_lifespan": 15,
            "site_id": sites[0].id,
            "production_line_id": production_lines[0].id,
            "status": "active",
            "criticality": "medium"
        },
        {
            "name": "Station de peinture SP1",
            "model": "ABB IRB 5400",
            "serial_number": "ABB-5400-003",
            "manufacturer": "ABB",
            "purchase_date": date(2023, 3, 20),
            "installation_date": date(2023, 4, 15),
            "warranty_expiry": date(2026, 3, 20),
            "expected_lifespan": 12,
            "site_id": sites[0].id,
            "production_line_id": production_lines[1].id,
            "status": "active",
            "criticality": "high"
        },
        {
            "name": "Machine d'insertion SMT1",
            "model": "Panasonic NPM-D3",
            "serial_number": "PAN-NPM-004",
            "manufacturer": "Panasonic",
            "purchase_date": date(2022, 9, 5),
            "installation_date": date(2022, 10, 1),
            "warranty_expiry": date(2025, 9, 5),
            "expected_lifespan": 8,
            "site_id": sites[1].id,
            "production_line_id": production_lines[2].id,
            "status": "active",
            "criticality": "critical"
        },
        {
            "name": "Banc de test automatique BT1",
            "model": "Keysight E5071C",
            "serial_number": "KEY-E5071-005",
            "manufacturer": "Keysight",
            "purchase_date": date(2023, 5, 12),
            "installation_date": date(2023, 6, 1),
            "warranty_expiry": date(2026, 5, 12),
            "expected_lifespan": 10,
            "site_id": sites[1].id,
            "production_line_id": production_lines[3].id,
            "status": "maintenance",
            "criticality": "high"
        }
    ]
    
    equipment_list = []
    for equip_data in equipment_data:
        equipment = Equipment(**equip_data)
        db.add(equipment)
        equipment_list.append(equipment)
    
    db.commit()
    return sites, production_lines, equipment_list

def create_maintenance_plans(db, equipment_list):
    """Créer des plans de maintenance"""
    plans_data = [
        {
            "name": "Maintenance préventive Robot R1",
            "description": "Maintenance préventive mensuelle du robot de soudage",
            "equipment_id": equipment_list[0].id,
            "maintenance_type": MaintenanceType.PREVENTIVE,
            "frequency_days": 30,
            "estimated_duration": 120,
            "priority": MaintenancePriority.HIGH,
            "is_active": True,
            "next_due_date": datetime.now() + timedelta(days=5)
        },
        {
            "name": "Inspection convoyeur C1",
            "description": "Inspection hebdomadaire du convoyeur principal",
            "equipment_id": equipment_list[1].id,
            "maintenance_type": MaintenanceType.PREVENTIVE,
            "frequency_days": 7,
            "estimated_duration": 45,
            "priority": MaintenancePriority.MEDIUM,
            "is_active": True,
            "next_due_date": datetime.now() + timedelta(days=2)
        },
        {
            "name": "Maintenance station peinture",
            "description": "Maintenance préventive trimestrielle de la station de peinture",
            "equipment_id": equipment_list[2].id,
            "maintenance_type": MaintenanceType.PREVENTIVE,
            "frequency_days": 90,
            "estimated_duration": 180,
            "priority": MaintenancePriority.HIGH,
            "is_active": True,
            "next_due_date": datetime.now() + timedelta(days=15)
        },
        {
            "name": "Calibrage machine SMT",
            "description": "Calibrage mensuel de la machine d'insertion SMT",
            "equipment_id": equipment_list[3].id,
            "maintenance_type": MaintenanceType.PREDICTIVE,
            "frequency_days": 30,
            "estimated_duration": 90,
            "priority": MaintenancePriority.CRITICAL,
            "is_active": True,
            "next_due_date": datetime.now() + timedelta(days=8)
        },
        {
            "name": "Vérification banc de test",
            "description": "Vérification bi-mensuelle du banc de test",
            "equipment_id": equipment_list[4].id,
            "maintenance_type": MaintenanceType.PREVENTIVE,
            "frequency_days": 60,
            "estimated_duration": 75,
            "priority": MaintenancePriority.HIGH,
            "is_active": True,
            "next_due_date": datetime.now() + timedelta(days=12)
        }
    ]
    
    plans = []
    for plan_data in plans_data:
        plan = MaintenancePlan(**plan_data)
        db.add(plan)
        plans.append(plan)
    
    db.commit()
    return plans

def create_maintenance_tasks(db, plans):
    """Créer des tâches de maintenance pour chaque plan"""
    tasks_data = [
        # Tâches pour Robot R1
        [
            {"name": "Vérification des niveaux d'huile", "description": "Contrôler et compléter les niveaux d'huile hydraulique", "estimated_duration": 15, "order": 1, "is_mandatory": True},
            {"name": "Inspection des câbles", "description": "Vérifier l'état des câbles électriques et de données", "estimated_duration": 20, "order": 2, "is_mandatory": True},
            {"name": "Test des mouvements", "description": "Effectuer un test complet des 6 axes", "estimated_duration": 30, "order": 3, "is_mandatory": True},
            {"name": "Nettoyage général", "description": "Nettoyage complet du robot et de son environnement", "estimated_duration": 25, "order": 4, "is_mandatory": False},
            {"name": "Calibrage précision", "description": "Vérification et ajustement de la précision", "estimated_duration": 30, "order": 5, "is_mandatory": True}
        ],
        # Tâches pour Convoyeur C1
        [
            {"name": "Inspection visuelle", "description": "Contrôle visuel de l'état général du convoyeur", "estimated_duration": 10, "order": 1, "is_mandatory": True},
            {"name": "Vérification tension courroie", "description": "Contrôler et ajuster la tension de la courroie", "estimated_duration": 15, "order": 2, "is_mandatory": True},
            {"name": "Lubrification roulements", "description": "Lubrifier tous les points de graissage", "estimated_duration": 20, "order": 3, "is_mandatory": True}
        ],
        # Tâches pour Station peinture
        [
            {"name": "Nettoyage pistons", "description": "Nettoyage complet des pistons de peinture", "estimated_duration": 45, "order": 1, "is_mandatory": True},
            {"name": "Remplacement filtres", "description": "Changement des filtres à air et peinture", "estimated_duration": 30, "order": 2, "is_mandatory": True},
            {"name": "Test pression", "description": "Vérification des pressions de pulvérisation", "estimated_duration": 25, "order": 3, "is_mandatory": True},
            {"name": "Calibrage couleurs", "description": "Calibrage du système de mélange des couleurs", "estimated_duration": 40, "order": 4, "is_mandatory": True},
            {"name": "Test qualité", "description": "Test de qualité sur pièces d'essai", "estimated_duration": 40, "order": 5, "is_mandatory": True}
        ],
        # Tâches pour Machine SMT
        [
            {"name": "Calibrage caméras", "description": "Calibrage des caméras de vision", "estimated_duration": 30, "order": 1, "is_mandatory": True},
            {"name": "Vérification têtes", "description": "Contrôle de l'état des têtes de placement", "estimated_duration": 25, "order": 2, "is_mandatory": True},
            {"name": "Test précision", "description": "Test de précision de placement", "estimated_duration": 35, "order": 3, "is_mandatory": True}
        ],
        # Tâches pour Banc de test
        [
            {"name": "Calibrage instruments", "description": "Calibrage des instruments de mesure", "estimated_duration": 30, "order": 1, "is_mandatory": True},
            {"name": "Vérification connexions", "description": "Contrôle de toutes les connexions", "estimated_duration": 20, "order": 2, "is_mandatory": True},
            {"name": "Test étalons", "description": "Test avec étalons de référence", "estimated_duration": 25, "order": 3, "is_mandatory": True}
        ]
    ]

    all_tasks = []
    for i, plan in enumerate(plans):
        for task_data in tasks_data[i]:
            task = MaintenanceTask(
                maintenance_plan_id=plan.id,
                **task_data
            )
            db.add(task)
            all_tasks.append(task)

    db.commit()
    return all_tasks

def create_scheduled_maintenances(db, plans, users):
    """Créer des maintenances planifiées"""
    technicians = [u for u in users if u.role == "technician"]

    scheduled_maintenances = []

    # Créer des maintenances pour les 2 prochaines semaines
    for plan in plans:
        # Maintenance dans 2 jours
        scheduled_date = datetime.now() + timedelta(days=2)
        scheduled = ScheduledMaintenance(
            maintenance_plan_id=plan.id,
            equipment_id=plan.equipment_id,
            scheduled_date=scheduled_date,
            estimated_start_time="08:00:00",
            estimated_end_time="10:00:00",
            assigned_technician_id=random.choice(technicians).id,
            status=MaintenanceStatus.SCHEDULED,
            priority=plan.priority,
            notes=f"Maintenance planifiée pour {plan.name}"
        )
        db.add(scheduled)
        scheduled_maintenances.append(scheduled)

        # Maintenance dans 1 semaine
        scheduled_date = datetime.now() + timedelta(days=7)
        scheduled = ScheduledMaintenance(
            maintenance_plan_id=plan.id,
            equipment_id=plan.equipment_id,
            scheduled_date=scheduled_date,
            estimated_start_time="14:00:00",
            estimated_end_time="16:00:00",
            assigned_technician_id=random.choice(technicians).id,
            status=MaintenanceStatus.SCHEDULED,
            priority=plan.priority
        )
        db.add(scheduled)
        scheduled_maintenances.append(scheduled)

    db.commit()
    return scheduled_maintenances

def create_interventions(db, equipment_list, users):
    """Créer quelques interventions d'exemple"""
    technicians = [u for u in users if u.role == "technician"]
    supervisors = [u for u in users if u.role == "supervisor"]

    interventions_data = [
        {
            "equipment_id": equipment_list[0].id,
            "technician_id": technicians[0].id,
            "maintenance_type": MaintenanceType.CORRECTIVE,
            "status": InterventionStatus.COMPLETED,
            "priority": MaintenancePriority.HIGH,
            "scheduled_date": datetime.now() - timedelta(days=2),
            "actual_start_time": datetime.now() - timedelta(days=2, hours=2),
            "actual_end_time": datetime.now() - timedelta(days=2, hours=1),
            "description": "Réparation suite à dysfonctionnement du bras robotique",
            "work_performed": "Remplacement du moteur de l'axe 3, recalibrage complet",
            "issues_found": "Usure prématurée du moteur due à surcharge",
            "recommendations": "Réviser les paramètres de charge maximale",
            "validated_by": supervisors[0].id,
            "validated_at": datetime.now() - timedelta(days=1),
            "validation_notes": "Intervention conforme, robot opérationnel",
            "labor_cost": 15000,  # 150€ en centimes
            "parts_cost": 85000   # 850€ en centimes
        },
        {
            "equipment_id": equipment_list[1].id,
            "technician_id": technicians[1].id,
            "maintenance_type": MaintenanceType.PREVENTIVE,
            "status": InterventionStatus.IN_PROGRESS,
            "priority": MaintenancePriority.MEDIUM,
            "scheduled_date": datetime.now(),
            "actual_start_time": datetime.now() - timedelta(hours=1),
            "description": "Maintenance préventive hebdomadaire du convoyeur",
            "work_performed": "Inspection en cours, lubrification effectuée"
        },
        {
            "equipment_id": equipment_list[3].id,
            "technician_id": technicians[2].id,
            "maintenance_type": MaintenanceType.EMERGENCY,
            "status": InterventionStatus.ASSIGNED,
            "priority": MaintenancePriority.CRITICAL,
            "scheduled_date": datetime.now() + timedelta(hours=2),
            "description": "Panne critique - Machine SMT arrêtée",
            "issues_found": "Erreur de calibrage caméra, production arrêtée"
        }
    ]

    interventions = []
    for intervention_data in interventions_data:
        intervention = MaintenanceIntervention(**intervention_data)
        db.add(intervention)
        interventions.append(intervention)

    db.commit()
    return interventions

def main():
    """Fonction principale pour créer toutes les données"""
    db = SessionLocal()

    try:
        print("🌱 Création des données complètes de maintenance...")

        # Supprimer les données existantes
        print("🗑️  Suppression des données existantes...")
        db.query(InterventionTask).delete()
        db.query(MaintenanceIntervention).delete()
        db.query(ScheduledMaintenance).delete()
        db.query(MaintenanceTask).delete()
        db.query(MaintenancePlan).delete()
        db.query(Equipment).delete()
        db.query(ProductionLine).delete()
        db.query(Site).delete()
        db.query(User).delete()
        db.commit()

        # Créer les données
        print("👥 Création des utilisateurs...")
        users = create_users(db)
        print(f"✅ {len(users)} utilisateurs créés")

        print("🏭 Création des sites et équipements...")
        sites, production_lines, equipment_list = create_sites_and_equipment(db)
        print(f"✅ {len(sites)} sites, {len(production_lines)} lignes, {len(equipment_list)} équipements créés")

        print("📋 Création des plans de maintenance...")
        plans = create_maintenance_plans(db, equipment_list)
        print(f"✅ {len(plans)} plans de maintenance créés")

        print("✅ Création des tâches de maintenance...")
        tasks = create_maintenance_tasks(db, plans)
        print(f"✅ {len(tasks)} tâches créées")

        print("📅 Création des maintenances planifiées...")
        scheduled = create_scheduled_maintenances(db, plans, users)
        print(f"✅ {len(scheduled)} maintenances planifiées créées")

        print("🔧 Création des interventions...")
        interventions = create_interventions(db, equipment_list, users)
        print(f"✅ {len(interventions)} interventions créées")

        print("\n📊 Résumé des données créées:")
        print(f"   • Utilisateurs: {len(users)}")
        print(f"   • Sites: {len(sites)}")
        print(f"   • Lignes de production: {len(production_lines)}")
        print(f"   • Équipements: {len(equipment_list)}")
        print(f"   • Plans de maintenance: {len(plans)}")
        print(f"   • Tâches de maintenance: {len(tasks)}")
        print(f"   • Maintenances planifiées: {len(scheduled)}")
        print(f"   • Interventions: {len(interventions)}")

        print("\n🔑 Comptes de test créés:")
        print("   • admin / admin123 (Administrateur)")
        print("   • super1 / super123 (Superviseur)")
        print("   • tech1 / tech123 (Technicien)")
        print("   • tech2 / tech123 (Technicien)")
        print("   • tech3 / tech123 (Technicien)")

        print("\n🎉 Données de test créées avec succès!")

    except Exception as e:
        print(f"❌ Erreur lors de la création des données: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
