#!/usr/bin/env python3
"""
Script simple pour créer les tables manquantes et insérer des données
"""
import sys
import os
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, text

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def create_tables(engine):
    """Créer les tables manquantes"""
    print("🔧 Création des tables manquantes...")
    
    with engine.connect() as conn:
        # 1. Table maintenance_plans
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS maintenance_plans (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
                    maintenance_type VARCHAR(20) NOT NULL DEFAULT 'preventive',
                    frequency_days INTEGER NOT NULL,
                    estimated_duration INTEGER NOT NULL,
                    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                    is_active BOOLEAN NOT NULL DEFAULT true,
                    next_due_date TIMESTAMP,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """))
            conn.commit()
            print("✅ Table maintenance_plans créée")
        except Exception as e:
            print(f"⚠️  maintenance_plans: {e}")
        
        # 2. Table maintenance_tasks
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS maintenance_tasks (
                    id SERIAL PRIMARY KEY,
                    maintenance_plan_id INTEGER NOT NULL REFERENCES maintenance_plans(id) ON DELETE CASCADE,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    estimated_duration INTEGER NOT NULL,
                    required_skills JSON,
                    tools_required JSON,
                    safety_requirements JSON,
                    "order" INTEGER NOT NULL DEFAULT 1,
                    is_mandatory BOOLEAN NOT NULL DEFAULT true,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """))
            conn.commit()
            print("✅ Table maintenance_tasks créée")
        except Exception as e:
            print(f"⚠️  maintenance_tasks: {e}")
        
        # 3. Table intervention_tasks
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS intervention_tasks (
                    id SERIAL PRIMARY KEY,
                    intervention_id INTEGER NOT NULL REFERENCES maintenance_interventions(id) ON DELETE CASCADE,
                    maintenance_task_id INTEGER REFERENCES maintenance_tasks(id),
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    is_completed BOOLEAN NOT NULL DEFAULT false,
                    completion_notes TEXT,
                    completed_at TIMESTAMP,
                    "order" INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """))
            conn.commit()
            print("✅ Table intervention_tasks créée")
        except Exception as e:
            print(f"⚠️  intervention_tasks: {e}")
        
        # 4. Table maintenance_parts_used
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS maintenance_parts_used (
                    id SERIAL PRIMARY KEY,
                    intervention_id INTEGER NOT NULL REFERENCES maintenance_interventions(id) ON DELETE CASCADE,
                    part_id INTEGER NOT NULL,
                    quantity_used INTEGER NOT NULL,
                    unit_cost INTEGER,
                    total_cost INTEGER,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """))
            conn.commit()
            print("✅ Table maintenance_parts_used créée")
        except Exception as e:
            print(f"⚠️  maintenance_parts_used: {e}")

def add_missing_columns(engine):
    """Ajouter les colonnes manquantes aux tables existantes"""
    print("🔧 Ajout des colonnes manquantes...")
    
    with engine.connect() as conn:
        # Colonnes pour maintenance_interventions
        columns_to_add = [
            ("maintenance_type", "VARCHAR(20) NOT NULL DEFAULT 'corrective'"),
            ("priority", "VARCHAR(20) NOT NULL DEFAULT 'medium'"),
            ("scheduled_date", "TIMESTAMP"),
            ("actual_start_time", "TIMESTAMP"),
            ("actual_end_time", "TIMESTAMP"),
            ("downtime_start", "TIMESTAMP"),
            ("downtime_end", "TIMESTAMP"),
            ("work_performed", "TEXT"),
            ("issues_found", "TEXT"),
            ("recommendations", "TEXT"),
            ("validated_by", "INTEGER REFERENCES users(id)"),
            ("validated_at", "TIMESTAMP"),
            ("validation_notes", "TEXT"),
            ("labor_cost", "INTEGER"),
            ("parts_cost", "INTEGER"),
            ("total_cost", "INTEGER")
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                # Vérifier si la colonne existe
                result = conn.execute(text("""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='maintenance_interventions' AND column_name=:column_name
                """), {"column_name": column_name})
                
                if not result.fetchone():
                    conn.execute(text(f"""
                        ALTER TABLE maintenance_interventions ADD COLUMN {column_name} {column_def}
                    """))
                    conn.commit()
                    print(f"✅ Colonne {column_name} ajoutée à maintenance_interventions")
            except Exception as e:
                print(f"⚠️  Erreur pour {column_name}: {e}")
        
        # Colonnes pour scheduled_maintenances
        scheduled_columns = [
            ("maintenance_plan_id", "INTEGER REFERENCES maintenance_plans(id)"),
            ("estimated_start_time", "VARCHAR(8) NOT NULL DEFAULT '08:00:00'"),
            ("estimated_end_time", "VARCHAR(8) NOT NULL DEFAULT '10:00:00'"),
            ("priority", "VARCHAR(20) NOT NULL DEFAULT 'medium'"),
            ("notes", "TEXT")
        ]
        
        for column_name, column_def in scheduled_columns:
            try:
                # Vérifier si la colonne existe
                result = conn.execute(text("""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='scheduled_maintenances' AND column_name=:column_name
                """), {"column_name": column_name})
                
                if not result.fetchone():
                    conn.execute(text(f"""
                        ALTER TABLE scheduled_maintenances ADD COLUMN {column_name} {column_def}
                    """))
                    conn.commit()
                    print(f"✅ Colonne {column_name} ajoutée à scheduled_maintenances")
            except Exception as e:
                print(f"⚠️  Erreur pour {column_name}: {e}")

def insert_sample_data(engine):
    """Insérer des données d'exemple"""
    print("📊 Insertion des données d'exemple...")
    
    with engine.connect() as conn:
        # Récupérer les équipements existants
        result = conn.execute(text("SELECT id, name FROM equipment ORDER BY id LIMIT 3"))
        equipment_list = result.fetchall()
        
        if not equipment_list:
            print("❌ Aucun équipement trouvé")
            return
        
        # Récupérer les utilisateurs
        result = conn.execute(text("SELECT id FROM users WHERE role = 'technician' LIMIT 2"))
        technicians = result.fetchall()
        
        result = conn.execute(text("SELECT id FROM users WHERE role = 'supervisor' LIMIT 1"))
        supervisors = result.fetchall()
        
        print(f"🏭 {len(equipment_list)} équipements trouvés")
        print(f"👥 {len(technicians)} techniciens et {len(supervisors)} superviseurs trouvés")
        
        # 1. Créer des plans de maintenance
        plans_data = [
            {
                "name": "Maintenance préventive Robot",
                "description": "Maintenance mensuelle du robot de soudage",
                "equipment_id": equipment_list[0][0],
                "maintenance_type": "preventive",
                "frequency_days": 30,
                "estimated_duration": 120,
                "priority": "high",
                "next_due_date": datetime.now() + timedelta(days=5)
            },
            {
                "name": "Inspection Convoyeur",
                "description": "Inspection hebdomadaire du convoyeur",
                "equipment_id": equipment_list[1][0] if len(equipment_list) > 1 else equipment_list[0][0],
                "maintenance_type": "preventive",
                "frequency_days": 7,
                "estimated_duration": 45,
                "priority": "medium",
                "next_due_date": datetime.now() + timedelta(days=2)
            },
            {
                "name": "Maintenance Presse",
                "description": "Maintenance trimestrielle de la presse",
                "equipment_id": equipment_list[2][0] if len(equipment_list) > 2 else equipment_list[0][0],
                "maintenance_type": "preventive",
                "frequency_days": 90,
                "estimated_duration": 180,
                "priority": "critical",
                "next_due_date": datetime.now() + timedelta(days=15)
            }
        ]
        
        plan_ids = []
        for plan_data in plans_data:
            try:
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
            except Exception as e:
                print(f"⚠️  Erreur création plan: {e}")
        
        print(f"✅ {len(plan_ids)} plans de maintenance créés")
        
        # 2. Créer des tâches pour chaque plan
        if plan_ids:
            tasks_data = [
                {"maintenance_plan_id": plan_ids[0], "name": "Vérification huile", "description": "Contrôler les niveaux", "estimated_duration": 15, "order": 1},
                {"maintenance_plan_id": plan_ids[0], "name": "Test mouvements", "description": "Test des 6 axes", "estimated_duration": 30, "order": 2},
            ]
            
            if len(plan_ids) > 1:
                tasks_data.extend([
                    {"maintenance_plan_id": plan_ids[1], "name": "Inspection visuelle", "description": "Contrôle général", "estimated_duration": 10, "order": 1},
                    {"maintenance_plan_id": plan_ids[1], "name": "Lubrification", "description": "Lubrifier les roulements", "estimated_duration": 20, "order": 2},
                ])
            
            task_count = 0
            for task_data in tasks_data:
                try:
                    conn.execute(text("""
                        INSERT INTO maintenance_tasks (maintenance_plan_id, name, description, 
                                                     estimated_duration, "order", is_mandatory)
                        VALUES (:maintenance_plan_id, :name, :description, 
                                :estimated_duration, :order, true)
                    """), task_data)
                    task_count += 1
                except Exception as e:
                    print(f"⚠️  Erreur création tâche: {e}")
            
            conn.commit()
            print(f"✅ {task_count} tâches créées")
        
        # 3. Créer des maintenances planifiées
        if plan_ids and equipment_list:
            scheduled_data = []
            for i, plan_id in enumerate(plan_ids[:2]):  # Limiter à 2 pour éviter les erreurs
                scheduled_data.append({
                    "maintenance_plan_id": plan_id,
                    "equipment_id": equipment_list[i % len(equipment_list)][0],
                    "scheduled_date": datetime.now() + timedelta(days=2),
                    "estimated_start_time": "08:00:00",
                    "estimated_end_time": "10:00:00",
                    "assigned_technician_id": technicians[0][0] if technicians else None,
                    "status": "scheduled",
                    "priority": "medium",
                    "notes": "Maintenance planifiée"
                })
            
            for scheduled in scheduled_data:
                try:
                    conn.execute(text("""
                        INSERT INTO scheduled_maintenances (maintenance_plan_id, equipment_id, scheduled_date,
                                                          estimated_start_time, estimated_end_time, 
                                                          assigned_technician_id, status, priority, notes)
                        VALUES (:maintenance_plan_id, :equipment_id, :scheduled_date,
                                :estimated_start_time, :estimated_end_time,
                                :assigned_technician_id, :status, :priority, :notes)
                    """), scheduled)
                except Exception as e:
                    print(f"⚠️  Erreur création maintenance planifiée: {e}")
            
            conn.commit()
            print(f"✅ {len(scheduled_data)} maintenances planifiées créées")

def main():
    """Fonction principale"""
    print("🚀 Configuration simple de la base de données...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        # 1. Créer les tables manquantes
        create_tables(engine)
        
        # 2. Ajouter les colonnes manquantes
        add_missing_columns(engine)
        
        # 3. Insérer des données d'exemple
        insert_sample_data(engine)
        
        print("\n✅ Configuration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    main()
