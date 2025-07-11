#!/usr/bin/env python3
"""
Script pour vérifier la structure de la base de données Neon
"""
import sys
import os
from sqlalchemy import create_engine, text, inspect

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def check_database_structure():
    """Vérifier la structure de la base de données"""
    print("🔍 Vérification de la structure de la base de données Neon...")
    
    try:
        # Créer la connexion
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        
        # Lister toutes les tables
        tables = inspector.get_table_names()
        print(f"\n📊 Tables existantes ({len(tables)}):")
        for table in sorted(tables):
            print(f"   • {table}")
        
        # Vérifier les tables spécifiques
        expected_tables = [
            'users', 'sites', 'production_lines', 'equipment',
            'maintenance_plans', 'maintenance_tasks', 'scheduled_maintenances',
            'maintenance_interventions', 'intervention_tasks', 'maintenance_parts_used'
        ]
        
        print(f"\n✅ Tables attendues:")
        missing_tables = []
        for table in expected_tables:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (manquante)")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️  Tables manquantes: {', '.join(missing_tables)}")
        else:
            print(f"\n🎉 Toutes les tables attendues sont présentes!")
        
        # Vérifier quelques tables importantes en détail
        important_tables = ['users', 'equipment', 'maintenance_plans']
        for table_name in important_tables:
            if table_name in tables:
                print(f"\n📋 Structure de la table '{table_name}':")
                columns = inspector.get_columns(table_name)
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    default = f" DEFAULT {col['default']}" if col['default'] else ""
                    print(f"   • {col['name']}: {col['type']} {nullable}{default}")
        
        # Vérifier s'il y a des données
        print(f"\n📊 Nombre d'enregistrements par table:")
        with engine.connect() as conn:
            for table in sorted(tables):
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"   • {table}: {count} enregistrements")
                except Exception as e:
                    print(f"   • {table}: Erreur - {e}")
        
        return tables, missing_tables
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return [], []

def check_sample_data():
    """Vérifier les données d'exemple"""
    print(f"\n🔍 Vérification des données d'exemple...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Vérifier les utilisateurs
            result = conn.execute(text("SELECT username, role FROM users ORDER BY role, username"))
            users = result.fetchall()
            if users:
                print(f"\n👥 Utilisateurs existants:")
                for user in users:
                    print(f"   • {user[0]} ({user[1]})")
            else:
                print(f"\n👥 Aucun utilisateur trouvé")
            
            # Vérifier les équipements
            result = conn.execute(text("SELECT name, status, criticality FROM equipment ORDER BY name"))
            equipment = result.fetchall()
            if equipment:
                print(f"\n🏭 Équipements existants:")
                for eq in equipment:
                    print(f"   • {eq[0]} - {eq[1]} ({eq[2]})")
            else:
                print(f"\n🏭 Aucun équipement trouvé")
            
            # Vérifier les plans de maintenance si la table existe
            try:
                result = conn.execute(text("SELECT name, maintenance_type, frequency_days FROM maintenance_plans ORDER BY name"))
                plans = result.fetchall()
                if plans:
                    print(f"\n📋 Plans de maintenance existants:")
                    for plan in plans:
                        print(f"   • {plan[0]} - {plan[1]} (tous les {plan[2]} jours)")
                else:
                    print(f"\n📋 Aucun plan de maintenance trouvé")
            except:
                print(f"\n📋 Table maintenance_plans non trouvée")
                
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des données: {e}")

if __name__ == "__main__":
    tables, missing = check_database_structure()
    check_sample_data()
    
    print(f"\n📝 Résumé:")
    print(f"   • Tables trouvées: {len(tables)}")
    print(f"   • Tables manquantes: {len(missing)}")
    
    if missing:
        print(f"\n🔧 Actions recommandées:")
        print(f"   1. Créer les tables manquantes avec Alembic")
        print(f"   2. Exécuter le script de données d'exemple")
    else:
        print(f"\n✅ Base de données prête à utiliser!")
