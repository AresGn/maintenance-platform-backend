#!/usr/bin/env python3
"""
Script pour ajouter plus de données de maintenance réalistes
"""
import sys
import os
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, text

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def add_more_data(engine):
    """Ajouter plus de données réalistes"""
    print("📊 Ajout de données supplémentaires...")
    
    with engine.connect() as conn:
        # Récupérer les IDs existants
        result = conn.execute(text("SELECT id, name FROM equipment ORDER BY id"))
        equipment_list = result.fetchall()
        
        result = conn.execute(text("SELECT id FROM users WHERE role = 'technician'"))
        technicians = result.fetchall()
        
        result = conn.execute(text("SELECT id FROM users WHERE role = 'supervisor'"))
        supervisors = result.fetchall()
        
        result = conn.execute(text("SELECT id FROM maintenance_plans"))
        plans = result.fetchall()
        
        print(f"🏭 {len(equipment_list)} équipements disponibles")
        print(f"👥 {len(technicians)} techniciens, {len(supervisors)} superviseurs")
        print(f"📋 {len(plans)} plans de maintenance existants")
        
        # 1. Ajouter des maintenances planifiées pour les prochaines semaines
        if plans and equipment_list and technicians:
            scheduled_maintenances = []
            
            # Créer des maintenances pour les 4 prochaines semaines
            for week in range(1, 5):
                for day in range(0, 7, 2):  # Tous les 2 jours
                    date = datetime.now() + timedelta(weeks=week, days=day)
                    
                    # Choisir un plan et équipement aléatoire
                    plan_id = random.choice(plans)[0]
                    equipment_id = random.choice(equipment_list)[0]
                    technician_id = random.choice(technicians)[0]
                    
                    # Heures aléatoires
                    start_hour = random.choice([8, 9, 10, 14, 15])
                    duration = random.choice([1, 2, 3])  # 1-3 heures
                    
                    scheduled_maintenances.append({
                        "maintenance_plan_id": plan_id,
                        "equipment_id": equipment_id,
                        "scheduled_date": date,
                        "estimated_start_time": f"{start_hour:02d}:00:00",
                        "estimated_end_time": f"{start_hour + duration:02d}:00:00",
                        "assigned_technician_id": technician_id,
                        "status": "scheduled",
                        "priority": random.choice(["low", "medium", "high"]),
                        "notes": f"Maintenance planifiée - Semaine {week}"
                    })
            
            # Insérer les maintenances planifiées
            for maintenance in scheduled_maintenances:
                try:
                    conn.execute(text("""
                        INSERT INTO scheduled_maintenances (maintenance_plan_id, equipment_id, 
                                                          assigned_technician_id, status, priority, notes,
                                                          estimated_start_time, estimated_end_time)
                        VALUES (:maintenance_plan_id, :equipment_id, 
                                :assigned_technician_id, :status, :priority, :notes,
                                :estimated_start_time, :estimated_end_time)
                    """), {
                        "maintenance_plan_id": maintenance["maintenance_plan_id"],
                        "equipment_id": maintenance["equipment_id"],
                        "assigned_technician_id": maintenance["assigned_technician_id"],
                        "status": maintenance["status"],
                        "priority": maintenance["priority"],
                        "notes": maintenance["notes"],
                        "estimated_start_time": maintenance["estimated_start_time"],
                        "estimated_end_time": maintenance["estimated_end_time"]
                    })
                except Exception as e:
                    print(f"⚠️  Erreur maintenance planifiée: {e}")
            
            conn.commit()
            print(f"✅ {len(scheduled_maintenances)} maintenances planifiées ajoutées")
        
        # 2. Ajouter des interventions avec différents statuts
        if equipment_list and technicians:
            interventions = []
            
            # Interventions terminées (historique)
            for i in range(5):
                days_ago = random.randint(1, 30)
                start_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(1, 8))
                end_time = start_time + timedelta(hours=random.randint(1, 4))
                
                interventions.append({
                    "equipment_id": random.choice(equipment_list)[0],
                    "technician_id": random.choice(technicians)[0],
                    "maintenance_type": random.choice(["preventive", "corrective", "predictive"]),
                    "status": "completed",
                    "priority": random.choice(["low", "medium", "high"]),
                    "scheduled_date": start_time - timedelta(hours=1),
                    "actual_start_time": start_time,
                    "actual_end_time": end_time,
                    "description": f"Intervention de maintenance {random.choice(['preventive', 'corrective'])}",
                    "work_performed": f"Travaux effectues: {random.choice(['Remplacement piece', 'Nettoyage complet', 'Calibrage', 'Lubrification'])}",
                    "issues_found": random.choice([None, "Usure normale", "Probleme mineur detecte", "Aucun probleme"]),
                    "recommendations": random.choice([None, "Surveiller evolution", "Prevoir remplacement", "RAS"]),
                    "validated_by": supervisors[0][0] if supervisors else None,
                    "validated_at": end_time + timedelta(hours=random.randint(1, 24)),
                    "validation_notes": "Intervention validee",
                    "labor_cost": random.randint(5000, 20000),  # 50-200€
                    "parts_cost": random.randint(0, 50000)      # 0-500€
                })
            
            # Interventions en cours
            for i in range(2):
                start_time = datetime.now() - timedelta(hours=random.randint(1, 6))
                
                interventions.append({
                    "equipment_id": random.choice(equipment_list)[0],
                    "technician_id": random.choice(technicians)[0],
                    "maintenance_type": random.choice(["corrective", "emergency"]),
                    "status": "in_progress",
                    "priority": random.choice(["medium", "high", "critical"]),
                    "scheduled_date": start_time - timedelta(hours=1),
                    "actual_start_time": start_time,
                    "description": f"Intervention {random.choice(['corrective', 'urgence'])} en cours",
                    "work_performed": "Diagnostic en cours..."
                })
            
            # Interventions assignées (à venir)
            for i in range(3):
                scheduled_time = datetime.now() + timedelta(hours=random.randint(1, 48))
                
                interventions.append({
                    "equipment_id": random.choice(equipment_list)[0],
                    "technician_id": random.choice(technicians)[0],
                    "maintenance_type": random.choice(["preventive", "corrective"]),
                    "status": "assigned",
                    "priority": random.choice(["low", "medium", "high"]),
                    "scheduled_date": scheduled_time,
                    "description": f"Intervention planifiée - {random.choice(['Maintenance preventive', 'Reparation programmee'])}"
                })
            
            # Insérer les interventions
            for intervention in interventions:
                try:
                    conn.execute(text("""
                        INSERT INTO maintenance_interventions (
                            equipment_id, technician_id, maintenance_type, status, priority,
                            scheduled_date, actual_start_time, actual_end_time, description,
                            work_performed, issues_found, recommendations, validated_by,
                            validated_at, validation_notes, labor_cost, parts_cost
                        ) VALUES (
                            :equipment_id, :technician_id, :maintenance_type, :status, :priority,
                            :scheduled_date, :actual_start_time, :actual_end_time, :description,
                            :work_performed, :issues_found, :recommendations, :validated_by,
                            :validated_at, :validation_notes, :labor_cost, :parts_cost
                        )
                    """), intervention)
                except Exception as e:
                    print(f"⚠️  Erreur intervention: {e}")
            
            conn.commit()
            print(f"✅ {len(interventions)} interventions ajoutées")
        
        # 3. Vérifier les données finales
        result = conn.execute(text("SELECT COUNT(*) FROM maintenance_plans"))
        plans_count = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM maintenance_tasks"))
        tasks_count = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM scheduled_maintenances"))
        scheduled_count = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM maintenance_interventions"))
        interventions_count = result.scalar()
        
        print(f"\n📊 Données finales:")
        print(f"   • Plans de maintenance: {plans_count}")
        print(f"   • Tâches: {tasks_count}")
        print(f"   • Maintenances planifiées: {scheduled_count}")
        print(f"   • Interventions: {interventions_count}")

def main():
    """Fonction principale"""
    print("🚀 Ajout de données supplémentaires...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        add_more_data(engine)
        
        print("\n✅ Données supplémentaires ajoutées avec succès!")
        print("\n🎯 Vous pouvez maintenant tester l'interface frontend avec des données réalistes!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    main()
