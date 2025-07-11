#!/usr/bin/env python3
"""
Script pour corriger la structure de la table scheduled_maintenances
"""
import sys
import os
from sqlalchemy import create_engine, text

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def check_and_fix_table(engine):
    """Vérifier et corriger la structure de la table scheduled_maintenances"""
    print("🔍 Vérification de la table scheduled_maintenances...")
    
    with engine.connect() as conn:
        # Vérifier la structure actuelle
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'scheduled_maintenances'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print(f"\n📋 Colonnes actuelles de scheduled_maintenances:")
        existing_columns = []
        for col in columns:
            existing_columns.append(col[0])
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            print(f"   • {col[0]}: {col[1]} {nullable}{default}")
        
        # Colonnes requises
        required_columns = {
            'scheduled_date': 'TIMESTAMP',
            'maintenance_plan_id': 'INTEGER REFERENCES maintenance_plans(id)',
            'estimated_start_time': 'VARCHAR(8) NOT NULL DEFAULT \'08:00:00\'',
            'estimated_end_time': 'VARCHAR(8) NOT NULL DEFAULT \'10:00:00\'',
            'priority': 'VARCHAR(20) NOT NULL DEFAULT \'medium\'',
            'notes': 'TEXT'
        }
        
        print(f"\n🔧 Ajout des colonnes manquantes...")
        
        # Ajouter les colonnes manquantes
        for column_name, column_def in required_columns.items():
            if column_name not in existing_columns:
                try:
                    print(f"   ➕ Ajout de la colonne {column_name}...")
                    conn.execute(text(f"""
                        ALTER TABLE scheduled_maintenances 
                        ADD COLUMN {column_name} {column_def}
                    """))
                    conn.commit()
                    print(f"   ✅ Colonne {column_name} ajoutée")
                except Exception as e:
                    print(f"   ⚠️  Erreur pour {column_name}: {e}")
            else:
                print(f"   ✅ Colonne {column_name} existe déjà")
        
        # Vérifier s'il y a des données dans la table
        result = conn.execute(text("SELECT COUNT(*) FROM scheduled_maintenances"))
        count = result.scalar()
        print(f"\n📊 Nombre d'enregistrements: {count}")
        
        # Si la table est vide, ajouter quelques données d'exemple
        if count == 0:
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
                # Ajouter quelques maintenances planifiées
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
                        'notes': 'Maintenance préventive planifiée'
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
                        'notes': 'Inspection trimestrielle'
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
                        'notes': 'Maintenance corrective'
                    }
                ]
                
                for data in sample_data:
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
                        print(f"   ⚠️  Erreur insertion: {e}")
                
                conn.commit()
                
                # Vérifier le nouveau count
                result = conn.execute(text("SELECT COUNT(*) FROM scheduled_maintenances"))
                new_count = result.scalar()
                print(f"   ✅ {new_count} maintenances planifiées ajoutées")
        
        # Vérifier la structure finale
        print(f"\n📋 Structure finale de scheduled_maintenances:")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'scheduled_maintenances'
            ORDER BY ordinal_position
        """))
        
        final_columns = result.fetchall()
        for col in final_columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            print(f"   • {col[0]}: {col[1]} {nullable}")

def main():
    """Fonction principale"""
    print("🚀 Correction de la table scheduled_maintenances...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        check_and_fix_table(engine)
        
        print("\n✅ Table scheduled_maintenances corrigée avec succès!")
        print("\n🔄 Redémarrez le serveur backend pour appliquer les changements.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    main()
