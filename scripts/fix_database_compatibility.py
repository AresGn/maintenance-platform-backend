#!/usr/bin/env python3
"""
Script pour corriger la compatibilité entre les modèles et la base de données
"""
import sys
import os
from sqlalchemy import create_engine, text

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def fix_database_compatibility(engine):
    """Corriger les problèmes de compatibilité"""
    print("🔧 Correction de la compatibilité base de données...")
    
    with engine.connect() as conn:
        # 1. Corriger les valeurs d'enum dans maintenance_plans
        print("📝 Correction des valeurs d'enum...")
        
        try:
            # Mettre à jour les valeurs en minuscules vers majuscules
            conn.execute(text("""
                UPDATE maintenance_plans 
                SET maintenance_type = UPPER(maintenance_type),
                    priority = UPPER(priority)
                WHERE maintenance_type IN ('preventive', 'corrective', 'predictive', 'emergency')
                   OR priority IN ('low', 'medium', 'high', 'critical')
            """))
            conn.commit()
            print("✅ Valeurs d'enum corrigées dans maintenance_plans")
        except Exception as e:
            print(f"⚠️  Erreur enum maintenance_plans: {e}")
        
        # 2. Corriger les valeurs dans scheduled_maintenances
        try:
            conn.execute(text("""
                UPDATE scheduled_maintenances 
                SET status = UPPER(status),
                    priority = UPPER(priority)
                WHERE status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'overdue')
                   OR priority IN ('low', 'medium', 'high', 'critical')
            """))
            conn.commit()
            print("✅ Valeurs d'enum corrigées dans scheduled_maintenances")
        except Exception as e:
            print(f"⚠️  Erreur enum scheduled_maintenances: {e}")
        
        # 3. Corriger les valeurs dans maintenance_interventions
        try:
            conn.execute(text("""
                UPDATE maintenance_interventions 
                SET maintenance_type = UPPER(maintenance_type),
                    priority = UPPER(priority),
                    status = UPPER(status)
                WHERE maintenance_type IN ('preventive', 'corrective', 'predictive', 'emergency')
                   OR priority IN ('low', 'medium', 'high', 'critical')
                   OR status IN ('pending', 'assigned', 'in_progress', 'completed', 'validated', 'rejected')
            """))
            conn.commit()
            print("✅ Valeurs d'enum corrigées dans maintenance_interventions")
        except Exception as e:
            print(f"⚠️  Erreur enum maintenance_interventions: {e}")
        
        # 4. Vérifier et corriger la structure de scheduled_maintenances
        print("🔍 Vérification de la structure de scheduled_maintenances...")
        
        # Vérifier les colonnes existantes
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'scheduled_maintenances'
        """))
        existing_columns = [row[0] for row in result.fetchall()]
        print(f"Colonnes existantes: {existing_columns}")
        
        # Ajouter scheduled_date si elle n'existe pas
        if 'scheduled_date' not in existing_columns:
            try:
                conn.execute(text("""
                    ALTER TABLE scheduled_maintenances 
                    ADD COLUMN scheduled_date TIMESTAMP
                """))
                conn.commit()
                print("✅ Colonne scheduled_date ajoutée")
            except Exception as e:
                print(f"⚠️  Erreur scheduled_date: {e}")
        
        # 5. Insérer des données de test simples
        print("📊 Insertion de données de test simples...")
        
        # Supprimer les données existantes pour éviter les conflits
        try:
            conn.execute(text("DELETE FROM scheduled_maintenances"))
            conn.commit()
            print("✅ Données existantes supprimées")
        except Exception as e:
            print(f"⚠️  Erreur suppression: {e}")
        
        # Récupérer les IDs nécessaires
        result = conn.execute(text("SELECT id FROM equipment LIMIT 3"))
        equipment_ids = [row[0] for row in result.fetchall()]
        
        result = conn.execute(text("SELECT id FROM maintenance_plans LIMIT 3"))
        plan_ids = [row[0] for row in result.fetchall()]
        
        result = conn.execute(text("SELECT id FROM users WHERE role = 'technician' LIMIT 1"))
        technician_result = result.fetchone()
        technician_id = technician_result[0] if technician_result else None
        
        if equipment_ids and plan_ids:
            # Insérer des maintenances simples
            simple_data = [
                {
                    'maintenance_plan_id': plan_ids[0],
                    'equipment_id': equipment_ids[0],
                    'scheduled_date': '2025-07-02 08:00:00',
                    'estimated_start_time': '08:00:00',
                    'estimated_end_time': '10:00:00',
                    'assigned_technician_id': technician_id,
                    'status': 'SCHEDULED',
                    'priority': 'MEDIUM',
                    'notes': 'Maintenance préventive'
                },
                {
                    'maintenance_plan_id': plan_ids[1] if len(plan_ids) > 1 else plan_ids[0],
                    'equipment_id': equipment_ids[1] if len(equipment_ids) > 1 else equipment_ids[0],
                    'scheduled_date': '2025-07-05 14:00:00',
                    'estimated_start_time': '14:00:00',
                    'estimated_end_time': '16:00:00',
                    'assigned_technician_id': technician_id,
                    'status': 'SCHEDULED',
                    'priority': 'HIGH',
                    'notes': 'Inspection trimestrielle'
                },
                {
                    'maintenance_plan_id': plan_ids[2] if len(plan_ids) > 2 else plan_ids[0],
                    'equipment_id': equipment_ids[2] if len(equipment_ids) > 2 else equipment_ids[0],
                    'scheduled_date': '2025-07-08 09:00:00',
                    'estimated_start_time': '09:00:00',
                    'estimated_end_time': '11:00:00',
                    'assigned_technician_id': technician_id,
                    'status': 'IN_PROGRESS',
                    'priority': 'CRITICAL',
                    'notes': 'Maintenance corrective'
                }
            ]
            
            for data in simple_data:
                try:
                    conn.execute(text("""
                        INSERT INTO scheduled_maintenances 
                        (maintenance_plan_id, equipment_id, scheduled_date, 
                         estimated_start_time, estimated_end_time, assigned_technician_id, 
                         status, priority, notes)
                        VALUES 
                        (:maintenance_plan_id, :equipment_id, :scheduled_date,
                         :estimated_start_time, :estimated_end_time, :assigned_technician_id,
                         :status, :priority, :notes)
                    """), data)
                except Exception as e:
                    print(f"⚠️  Erreur insertion: {e}")
            
            conn.commit()
            
            # Vérifier les données finales
            result = conn.execute(text("SELECT COUNT(*) FROM scheduled_maintenances"))
            count = result.scalar()
            print(f"✅ {count} maintenances planifiées insérées")
        
        # 6. Vérifier les données finales
        print("\n📊 Vérification finale des données:")
        
        # Plans de maintenance
        result = conn.execute(text("""
            SELECT name, maintenance_type, priority 
            FROM maintenance_plans 
            LIMIT 3
        """))
        plans = result.fetchall()
        print("Plans de maintenance:")
        for plan in plans:
            print(f"   • {plan[0]} - {plan[1]} ({plan[2]})")
        
        # Maintenances planifiées
        result = conn.execute(text("""
            SELECT sm.scheduled_date, sm.status, sm.priority, e.name as equipment_name
            FROM scheduled_maintenances sm
            LEFT JOIN equipment e ON sm.equipment_id = e.id
            ORDER BY sm.scheduled_date
        """))
        maintenances = result.fetchall()
        print("Maintenances planifiées:")
        for maintenance in maintenances:
            print(f"   • {maintenance[0]} - {maintenance[1]} ({maintenance[2]}) - {maintenance[3]}")

def main():
    """Fonction principale"""
    print("🚀 Correction de la compatibilité base de données...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        fix_database_compatibility(engine)
        
        print("\n✅ Correction terminée avec succès!")
        print("\n🔄 Redémarrez le serveur backend pour appliquer les changements.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    main()
