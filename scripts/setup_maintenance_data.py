#!/usr/bin/env python3
"""
Script pour créer les tables manquantes et insérer des données de maintenance réalistes
"""
import sys
import os
from datetime import datetime, timedelta, date
import random
from sqlalchemy import create_engine, text

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def execute_sql_file(engine, file_path):
    """Exécuter un fichier SQL"""
    print(f"📄 Exécution du fichier SQL: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        sql_content = file.read()
    
    with engine.connect() as conn:
        # Exécuter le SQL par blocs (séparés par des points-virgules)
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                try:
                    conn.execute(text(statement))
                    conn.commit()
                except Exception as e:
                    print(f"⚠️  Erreur lors de l'exécution: {e}")
                    print(f"Statement: {statement[:100]}...")

def insert_maintenance_data(engine):
    """Insérer des données de maintenance réalistes"""
    print("📊 Insertion des données de maintenance...")
    
    with engine.connect() as conn:
        # Récupérer les équipements existants
        result = conn.execute(text("SELECT id, name FROM equipment ORDER BY id"))
        equipment_list = result.fetchall()
        
        if not equipment_list:
            print("❌ Aucun équipement trouvé. Veuillez d'abord créer des équipements.")
            return
        
        print(f"🏭 {len(equipment_list)} équipements trouvés")
        
        # Récupérer les utilisateurs techniciens
        result = conn.execute(text("SELECT id, first_name, last_name FROM users WHERE role = 'technician'"))
        technicians = result.fetchall()
        
        result = conn.execute(text("SELECT id, first_name, last_name FROM users WHERE role = 'supervisor'"))
        supervisors = result.fetchall()
        
        print(f"👥 {len(technicians)} techniciens et {len(supervisors)} superviseurs trouvés")
        
        # 1. Créer des plans de maintenance
        maintenance_plans_data = [
            {
                "name": "Maintenance préventive Robot de soudage",
                "description": "Maintenance préventive mensuelle du robot de soudage",
                "equipment_id": equipment_list[0][0],
                "maintenance_type": "preventive",
                "frequency_days": 30,
                "estimated_duration": 120,
                "priority": "high",
                "next_due_date": datetime.now() + timedelta(days=5)
            },
            {
                "name": "Inspection Convoyeur principal",
                "description": "Inspection hebdomadaire du convoyeur principal",
                "equipment_id": equipment_list[1][0],
                "maintenance_type": "preventive", 
                "frequency_days": 7,
                "estimated_duration": 45,
                "priority": "medium",
                "next_due_date": datetime.now() + timedelta(days=2)
            },
            {
                "name": "Maintenance Presse hydraulique",
                "description": "Maintenance trimestrielle de la presse hydraulique",
                "equipment_id": equipment_list[2][0],
                "maintenance_type": "preventive",
                "frequency_days": 90,
                "estimated_duration": 180,
                "priority": "critical",
                "next_due_date": datetime.now() + timedelta(days=15)
            }
        ]
        
        plan_ids = []
        for plan_data in maintenance_plans_data:
            result = conn.execute(text("""
                INSERT INTO maintenance_plans (name, description, equipment_id, maintenance_type, 
                                             frequency_days, estimated_duration, priority, next_due_date)
                VALUES (:name, :description, :equipment_id, :maintenance_type, 
                        :frequency_days, :estimated_duration, :priority, :next_due_date)
                RETURNING id
            """), plan_data)
            plan_id = result.fetchone()[0]
            plan_ids.append(plan_id)
            conn.commit()
        
        print(f"✅ {len(plan_ids)} plans de maintenance créés")
        
        # 2. Créer des tâches pour chaque plan
        tasks_data = [
            # Tâches pour Robot de soudage
            [
                {"name": "Vérification des niveaux d'huile", "description": "Contrôler et compléter les niveaux d'huile hydraulique", "estimated_duration": 15, "order": 1},
                {"name": "Inspection des câbles", "description": "Vérifier l'état des câbles électriques et de données", "estimated_duration": 20, "order": 2},
                {"name": "Test des mouvements", "description": "Effectuer un test complet des 6 axes", "estimated_duration": 30, "order": 3},
                {"name": "Nettoyage général", "description": "Nettoyage complet du robot", "estimated_duration": 25, "order": 4, "is_mandatory": False},
                {"name": "Calibrage précision", "description": "Vérification et ajustement de la précision", "estimated_duration": 30, "order": 5}
            ],
            # Tâches pour Convoyeur
            [
                {"name": "Inspection visuelle", "description": "Contrôle visuel de l'état général", "estimated_duration": 10, "order": 1},
                {"name": "Vérification tension courroie", "description": "Contrôler et ajuster la tension", "estimated_duration": 15, "order": 2},
                {"name": "Lubrification roulements", "description": "Lubrifier tous les points de graissage", "estimated_duration": 20, "order": 3}
            ],
            # Tâches pour Presse hydraulique
            [
                {"name": "Contrôle pression hydraulique", "description": "Vérifier les pressions de fonctionnement", "estimated_duration": 30, "order": 1},
                {"name": "Inspection joints", "description": "Contrôler l'état des joints d'étanchéité", "estimated_duration": 45, "order": 2},
                {"name": "Test sécurités", "description": "Test de tous les systèmes de sécurité", "estimated_duration": 60, "order": 3},
                {"name": "Remplacement filtres", "description": "Changement des filtres hydrauliques", "estimated_duration": 45, "order": 4}
            ]
        ]
        
        task_count = 0
        for i, plan_id in enumerate(plan_ids):
            for task_data in tasks_data[i]:
                task_data["maintenance_plan_id"] = plan_id
                task_data.setdefault("is_mandatory", True)
                
                conn.execute(text("""
                    INSERT INTO maintenance_tasks (maintenance_plan_id, name, description, 
                                                 estimated_duration, "order", is_mandatory)
                    VALUES (:maintenance_plan_id, :name, :description, 
                            :estimated_duration, :order, :is_mandatory)
                """), task_data)
                task_count += 1
        
        conn.commit()
        print(f"✅ {task_count} tâches de maintenance créées")
        
        # 3. Créer des maintenances planifiées
        scheduled_data = []
        for plan_id in plan_ids:
            # Maintenance dans 2 jours
            scheduled_data.append({
                "maintenance_plan_id": plan_id,
                "equipment_id": equipment_list[plan_ids.index(plan_id)][0],
                "scheduled_date": datetime.now() + timedelta(days=2),
                "estimated_start_time": "08:00:00",
                "estimated_end_time": "10:00:00",
                "assigned_technician_id": random.choice(technicians)[0] if technicians else None,
                "status": "scheduled",
                "priority": "medium",
                "notes": f"Maintenance planifiée"
            })
            
            # Maintenance dans 1 semaine
            scheduled_data.append({
                "maintenance_plan_id": plan_id,
                "equipment_id": equipment_list[plan_ids.index(plan_id)][0],
                "scheduled_date": datetime.now() + timedelta(days=7),
                "estimated_start_time": "14:00:00",
                "estimated_end_time": "16:00:00",
                "assigned_technician_id": random.choice(technicians)[0] if technicians else None,
                "status": "scheduled",
                "priority": "medium"
            })
        
        for scheduled in scheduled_data:
            conn.execute(text("""
                INSERT INTO scheduled_maintenances (maintenance_plan_id, equipment_id, scheduled_date,
                                                  estimated_start_time, estimated_end_time, 
                                                  assigned_technician_id, status, priority, notes)
                VALUES (:maintenance_plan_id, :equipment_id, :scheduled_date,
                        :estimated_start_time, :estimated_end_time,
                        :assigned_technician_id, :status, :priority, :notes)
            """), scheduled)
        
        conn.commit()
        print(f"✅ {len(scheduled_data)} maintenances planifiées créées")
        
        # 4. Créer quelques interventions d'exemple
        interventions_data = [
            {
                "equipment_id": equipment_list[0][0],
                "technician_id": technicians[0][0] if technicians else 1,
                "maintenance_type": "corrective",
                "status": "completed",
                "priority": "high",
                "scheduled_date": datetime.now() - timedelta(days=2),
                "actual_start_time": datetime.now() - timedelta(days=2, hours=2),
                "actual_end_time": datetime.now() - timedelta(days=2, hours=1),
                "description": "Réparation suite à dysfonctionnement du robot",
                "work_performed": "Remplacement du moteur de l'axe 3, recalibrage complet",
                "issues_found": "Usure prématurée du moteur due à surcharge",
                "recommendations": "Réviser les paramètres de charge maximale",
                "validated_by": supervisors[0][0] if supervisors else None,
                "validated_at": datetime.now() - timedelta(days=1),
                "validation_notes": "Intervention conforme, robot opérationnel",
                "labor_cost": 15000,  # 150€
                "parts_cost": 85000   # 850€
            },
            {
                "equipment_id": equipment_list[1][0],
                "technician_id": technicians[1][0] if len(technicians) > 1 else technicians[0][0],
                "maintenance_type": "preventive",
                "status": "in_progress",
                "priority": "medium",
                "scheduled_date": datetime.now(),
                "actual_start_time": datetime.now() - timedelta(hours=1),
                "description": "Maintenance préventive hebdomadaire du convoyeur",
                "work_performed": "Inspection en cours, lubrification effectuée"
            }
        ]
        
        intervention_ids = []
        for intervention_data in interventions_data:
            result = conn.execute(text("""
                INSERT INTO maintenance_interventions (equipment_id, technician_id, maintenance_type,
                                                     status, priority, scheduled_date, actual_start_time,
                                                     actual_end_time, description, work_performed,
                                                     issues_found, recommendations, validated_by,
                                                     validated_at, validation_notes, labor_cost, parts_cost)
                VALUES (:equipment_id, :technician_id, :maintenance_type, :status, :priority,
                        :scheduled_date, :actual_start_time, :actual_end_time, :description,
                        :work_performed, :issues_found, :recommendations, :validated_by,
                        :validated_at, :validation_notes, :labor_cost, :parts_cost)
                RETURNING id
            """), intervention_data)
            intervention_id = result.fetchone()[0]
            intervention_ids.append(intervention_id)
        
        conn.commit()
        print(f"✅ {len(intervention_ids)} interventions créées")
        
        print("\n🎉 Données de maintenance créées avec succès!")
        print(f"   • Plans de maintenance: {len(plan_ids)}")
        print(f"   • Tâches: {task_count}")
        print(f"   • Maintenances planifiées: {len(scheduled_data)}")
        print(f"   • Interventions: {len(intervention_ids)}")

def main():
    """Fonction principale"""
    print("🚀 Configuration de la base de données de maintenance...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        # 1. Créer les tables manquantes
        sql_file_path = os.path.join(os.path.dirname(__file__), "create_missing_tables.sql")
        execute_sql_file(engine, sql_file_path)
        
        # 2. Insérer les données de test
        insert_maintenance_data(engine)
        
        print("\n✅ Configuration terminée avec succès!")
        print("\n🔑 Comptes de test disponibles:")
        print("   • admin / admin123 (Administrateur)")
        print("   • super1 / super123 (Superviseur)")
        print("   • tech1 / tech123 (Technicien)")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    main()
