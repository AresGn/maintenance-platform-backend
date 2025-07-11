#!/usr/bin/env python3
"""
Script pour forcer la correction des valeurs d'enum
"""
import sys
import os
from sqlalchemy import create_engine, text

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def force_fix_enums(engine):
    """Forcer la correction des valeurs d'enum"""
    print("🔧 Correction forcée des valeurs d'enum...")
    
    with engine.connect() as conn:
        # 1. Vérifier et corriger maintenance_plans
        print("📝 Correction de maintenance_plans...")
        
        # Vérifier les valeurs actuelles
        result = conn.execute(text("SELECT DISTINCT maintenance_type FROM maintenance_plans"))
        types = [row[0] for row in result.fetchall()]
        print(f"Types actuels: {types}")
        
        result = conn.execute(text("SELECT DISTINCT priority FROM maintenance_plans"))
        priorities = [row[0] for row in result.fetchall()]
        print(f"Priorités actuelles: {priorities}")
        
        # Corriger les valeurs
        corrections = [
            ("UPDATE maintenance_plans SET maintenance_type = 'PREVENTIVE' WHERE maintenance_type = 'preventive'"),
            ("UPDATE maintenance_plans SET maintenance_type = 'CORRECTIVE' WHERE maintenance_type = 'corrective'"),
            ("UPDATE maintenance_plans SET maintenance_type = 'PREDICTIVE' WHERE maintenance_type = 'predictive'"),
            ("UPDATE maintenance_plans SET maintenance_type = 'EMERGENCY' WHERE maintenance_type = 'emergency'"),
            ("UPDATE maintenance_plans SET priority = 'LOW' WHERE priority = 'low'"),
            ("UPDATE maintenance_plans SET priority = 'MEDIUM' WHERE priority = 'medium'"),
            ("UPDATE maintenance_plans SET priority = 'HIGH' WHERE priority = 'high'"),
            ("UPDATE maintenance_plans SET priority = 'CRITICAL' WHERE priority = 'critical'"),
        ]
        
        for correction in corrections:
            try:
                result = conn.execute(text(correction))
                if result.rowcount > 0:
                    print(f"✅ {result.rowcount} lignes mises à jour: {correction}")
                conn.commit()
            except Exception as e:
                print(f"⚠️  Erreur: {e}")
        
        # 2. Vérifier et corriger scheduled_maintenances
        print("\n📝 Correction de scheduled_maintenances...")
        
        # Vérifier les valeurs actuelles
        result = conn.execute(text("SELECT DISTINCT status FROM scheduled_maintenances"))
        statuses = [row[0] for row in result.fetchall()]
        print(f"Statuts actuels: {statuses}")
        
        result = conn.execute(text("SELECT DISTINCT priority FROM scheduled_maintenances"))
        priorities = [row[0] for row in result.fetchall()]
        print(f"Priorités actuelles: {priorities}")
        
        # Corriger les valeurs
        corrections = [
            ("UPDATE scheduled_maintenances SET status = 'SCHEDULED' WHERE status = 'scheduled'"),
            ("UPDATE scheduled_maintenances SET status = 'IN_PROGRESS' WHERE status = 'in_progress'"),
            ("UPDATE scheduled_maintenances SET status = 'COMPLETED' WHERE status = 'completed'"),
            ("UPDATE scheduled_maintenances SET status = 'CANCELLED' WHERE status = 'cancelled'"),
            ("UPDATE scheduled_maintenances SET status = 'OVERDUE' WHERE status = 'overdue'"),
            ("UPDATE scheduled_maintenances SET priority = 'LOW' WHERE priority = 'low'"),
            ("UPDATE scheduled_maintenances SET priority = 'MEDIUM' WHERE priority = 'medium'"),
            ("UPDATE scheduled_maintenances SET priority = 'HIGH' WHERE priority = 'high'"),
            ("UPDATE scheduled_maintenances SET priority = 'CRITICAL' WHERE priority = 'critical'"),
        ]
        
        for correction in corrections:
            try:
                result = conn.execute(text(correction))
                if result.rowcount > 0:
                    print(f"✅ {result.rowcount} lignes mises à jour: {correction}")
                conn.commit()
            except Exception as e:
                print(f"⚠️  Erreur: {e}")
        
        # 3. Vérifier et corriger maintenance_interventions
        print("\n📝 Correction de maintenance_interventions...")
        
        # Vérifier les valeurs actuelles
        result = conn.execute(text("SELECT DISTINCT maintenance_type FROM maintenance_interventions"))
        types = [row[0] for row in result.fetchall()]
        print(f"Types actuels: {types}")
        
        result = conn.execute(text("SELECT DISTINCT status FROM maintenance_interventions"))
        statuses = [row[0] for row in result.fetchall()]
        print(f"Statuts actuels: {statuses}")
        
        result = conn.execute(text("SELECT DISTINCT priority FROM maintenance_interventions"))
        priorities = [row[0] for row in result.fetchall()]
        print(f"Priorités actuelles: {priorities}")
        
        # Corriger les valeurs
        corrections = [
            ("UPDATE maintenance_interventions SET maintenance_type = 'PREVENTIVE' WHERE maintenance_type = 'preventive'"),
            ("UPDATE maintenance_interventions SET maintenance_type = 'CORRECTIVE' WHERE maintenance_type = 'corrective'"),
            ("UPDATE maintenance_interventions SET maintenance_type = 'PREDICTIVE' WHERE maintenance_type = 'predictive'"),
            ("UPDATE maintenance_interventions SET maintenance_type = 'EMERGENCY' WHERE maintenance_type = 'emergency'"),
            ("UPDATE maintenance_interventions SET status = 'PENDING' WHERE status = 'pending'"),
            ("UPDATE maintenance_interventions SET status = 'ASSIGNED' WHERE status = 'assigned'"),
            ("UPDATE maintenance_interventions SET status = 'IN_PROGRESS' WHERE status = 'in_progress'"),
            ("UPDATE maintenance_interventions SET status = 'COMPLETED' WHERE status = 'completed'"),
            ("UPDATE maintenance_interventions SET status = 'VALIDATED' WHERE status = 'validated'"),
            ("UPDATE maintenance_interventions SET status = 'REJECTED' WHERE status = 'rejected'"),
            ("UPDATE maintenance_interventions SET priority = 'LOW' WHERE priority = 'low'"),
            ("UPDATE maintenance_interventions SET priority = 'MEDIUM' WHERE priority = 'medium'"),
            ("UPDATE maintenance_interventions SET priority = 'HIGH' WHERE priority = 'high'"),
            ("UPDATE maintenance_interventions SET priority = 'CRITICAL' WHERE priority = 'critical'"),
        ]
        
        for correction in corrections:
            try:
                result = conn.execute(text(correction))
                if result.rowcount > 0:
                    print(f"✅ {result.rowcount} lignes mises à jour: {correction}")
                conn.commit()
            except Exception as e:
                print(f"⚠️  Erreur: {e}")
        
        # 4. Vérification finale
        print("\n📊 Vérification finale...")
        
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
            SELECT title, status, priority 
            FROM scheduled_maintenances 
            LIMIT 3
        """))
        maintenances = result.fetchall()
        print("Maintenances planifiées:")
        for maintenance in maintenances:
            print(f"   • {maintenance[0]} - {maintenance[1]} ({maintenance[2]})")

def main():
    """Fonction principale"""
    print("🚀 Correction forcée des valeurs d'enum...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        force_fix_enums(engine)
        
        print("\n✅ Correction forcée terminée!")
        print("\n🔄 Redémarrez le serveur backend.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    main()
