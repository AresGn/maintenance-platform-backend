#!/usr/bin/env python3
"""
Script pour ajouter la colonne status et insérer des données d'exemple
"""
import sys
import os
from sqlalchemy import create_engine, text

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def add_status_and_data(engine):
    """Ajouter la colonne status et des données d'exemple"""
    print("🔧 Ajout de la colonne status...")
    
    with engine.connect() as conn:
        # Ajouter la colonne status
        try:
            conn.execute(text("""
                ALTER TABLE scheduled_maintenances 
                ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'scheduled'
            """))
            conn.commit()
            print("✅ Colonne status ajoutée")
        except Exception as e:
            print(f"⚠️  Colonne status: {e}")
        
        # Ajouter des données d'exemple
        print("📝 Ajout de données d'exemple...")
        
        # Récupérer les IDs nécessaires
        result = conn.execute(text("SELECT id FROM equipment LIMIT 3"))
        equipment_ids = [row[0] for row in result.fetchall()]
        
        result = conn.execute(text("SELECT id FROM maintenance_plans LIMIT 3"))
        plan_ids = [row[0] for row in result.fetchall()]
        
        result = conn.execute(text("SELECT id FROM users WHERE role = 'technician' LIMIT 1"))
        technician_result = result.fetchone()
        technician_id = technician_result[0] if technician_result else None
        
        if equipment_ids and plan_ids:
            # Supprimer les données existantes pour éviter les doublons
            conn.execute(text("DELETE FROM scheduled_maintenances"))
            conn.commit()
            
            # Ajouter des maintenances planifiées
            sample_data = [
                {
                    'maintenance_plan_id': plan_ids[0],
                    'equipment_id': equipment_ids[0],
                    'scheduled_date': '2025-07-02 08:00:00',
                    'estimated_start_time': '08:00:00',
                    'estimated_end_time': '10:00:00',
                    'assigned_technician_id': technician_id,
                    'status': 'scheduled',
                    'priority': 'medium',
                    'notes': 'Maintenance préventive planifiée',
                    'title': 'Maintenance Robot',
                    'description': 'Maintenance préventive du robot de soudage',
                    'frequency_type': 'monthly',
                    'frequency_value': 1,
                    'next_due_date': '2025-08-02 08:00:00',
                    'estimated_duration': 120,
                    'is_active': True
                },
                {
                    'maintenance_plan_id': plan_ids[1] if len(plan_ids) > 1 else plan_ids[0],
                    'equipment_id': equipment_ids[1] if len(equipment_ids) > 1 else equipment_ids[0],
                    'scheduled_date': '2025-07-05 14:00:00',
                    'estimated_start_time': '14:00:00',
                    'estimated_end_time': '16:00:00',
                    'assigned_technician_id': technician_id,
                    'status': 'scheduled',
                    'priority': 'high',
                    'notes': 'Inspection trimestrielle',
                    'title': 'Inspection Convoyeur',
                    'description': 'Inspection trimestrielle du convoyeur',
                    'frequency_type': 'quarterly',
                    'frequency_value': 1,
                    'next_due_date': '2025-10-05 14:00:00',
                    'estimated_duration': 90,
                    'is_active': True
                },
                {
                    'maintenance_plan_id': plan_ids[2] if len(plan_ids) > 2 else plan_ids[0],
                    'equipment_id': equipment_ids[2] if len(equipment_ids) > 2 else equipment_ids[0],
                    'scheduled_date': '2025-07-08 09:00:00',
                    'estimated_start_time': '09:00:00',
                    'estimated_end_time': '11:00:00',
                    'assigned_technician_id': technician_id,
                    'status': 'scheduled',
                    'priority': 'low',
                    'notes': 'Maintenance corrective',
                    'title': 'Maintenance Presse',
                    'description': 'Maintenance corrective de la presse',
                    'frequency_type': 'weekly',
                    'frequency_value': 2,
                    'next_due_date': '2025-07-22 09:00:00',
                    'estimated_duration': 60,
                    'is_active': True
                },
                # Ajouter plus de maintenances pour le calendrier
                {
                    'maintenance_plan_id': plan_ids[0],
                    'equipment_id': equipment_ids[0],
                    'scheduled_date': '2025-07-10 10:00:00',
                    'estimated_start_time': '10:00:00',
                    'estimated_end_time': '12:00:00',
                    'assigned_technician_id': technician_id,
                    'status': 'scheduled',
                    'priority': 'medium',
                    'notes': 'Maintenance hebdomadaire',
                    'title': 'Maintenance Robot',
                    'description': 'Maintenance hebdomadaire du robot',
                    'frequency_type': 'weekly',
                    'frequency_value': 1,
                    'next_due_date': '2025-07-17 10:00:00',
                    'estimated_duration': 120,
                    'is_active': True
                },
                {
                    'maintenance_plan_id': plan_ids[1] if len(plan_ids) > 1 else plan_ids[0],
                    'equipment_id': equipment_ids[1] if len(equipment_ids) > 1 else equipment_ids[0],
                    'scheduled_date': '2025-07-15 15:00:00',
                    'estimated_start_time': '15:00:00',
                    'estimated_end_time': '17:00:00',
                    'assigned_technician_id': technician_id,
                    'status': 'in_progress',
                    'priority': 'critical',
                    'notes': 'Maintenance urgente',
                    'title': 'Réparation Convoyeur',
                    'description': 'Réparation urgente du convoyeur',
                    'frequency_type': 'monthly',
                    'frequency_value': 1,
                    'next_due_date': '2025-08-15 15:00:00',
                    'estimated_duration': 120,
                    'is_active': True
                }
            ]
            
            for data in sample_data:
                try:
                    conn.execute(text("""
                        INSERT INTO scheduled_maintenances 
                        (maintenance_plan_id, equipment_id, scheduled_date, 
                         estimated_start_time, estimated_end_time, assigned_technician_id, 
                         status, priority, notes, title, description, frequency_type,
                         frequency_value, next_due_date, estimated_duration, is_active)
                        VALUES 
                        (:maintenance_plan_id, :equipment_id, :scheduled_date,
                         :estimated_start_time, :estimated_end_time, :assigned_technician_id,
                         :status, :priority, :notes, :title, :description, :frequency_type,
                         :frequency_value, :next_due_date, :estimated_duration, :is_active)
                    """), data)
                except Exception as e:
                    print(f"   ⚠️  Erreur insertion: {e}")
            
            conn.commit()
            
            # Vérifier le nouveau count
            result = conn.execute(text("SELECT COUNT(*) FROM scheduled_maintenances"))
            new_count = result.scalar()
            print(f"   ✅ {new_count} maintenances planifiées ajoutées")
        
        print("\n📊 Données finales:")
        result = conn.execute(text("""
            SELECT sm.title, sm.scheduled_date, sm.status, sm.priority, e.name as equipment_name
            FROM scheduled_maintenances sm
            LEFT JOIN equipment e ON sm.equipment_id = e.id
            ORDER BY sm.scheduled_date
        """))
        
        maintenances = result.fetchall()
        for maintenance in maintenances:
            print(f"   • {maintenance[0]} - {maintenance[1]} - {maintenance[2]} ({maintenance[3]}) - {maintenance[4]}")

def main():
    """Fonction principale"""
    print("🚀 Ajout de la colonne status et données d'exemple...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        add_status_and_data(engine)
        
        print("\n✅ Configuration terminée avec succès!")
        print("\n🔄 Redémarrez le serveur backend pour appliquer les changements.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    main()
