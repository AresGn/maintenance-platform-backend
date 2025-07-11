-- Script pour créer les tables de maintenance manquantes
-- À exécuter sur la base de données Neon

-- Table des plans de maintenance
CREATE TABLE IF NOT EXISTS maintenance_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    maintenance_type VARCHAR(20) NOT NULL DEFAULT 'preventive',
    frequency_days INTEGER NOT NULL,
    estimated_duration INTEGER NOT NULL, -- en minutes
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    is_active BOOLEAN NOT NULL DEFAULT true,
    next_due_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Table des tâches de maintenance
CREATE TABLE IF NOT EXISTS maintenance_tasks (
    id SERIAL PRIMARY KEY,
    maintenance_plan_id INTEGER NOT NULL REFERENCES maintenance_plans(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    estimated_duration INTEGER NOT NULL, -- en minutes
    required_skills JSON,
    tools_required JSON,
    safety_requirements JSON,
    "order" INTEGER NOT NULL DEFAULT 1,
    is_mandatory BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Table des tâches d'intervention
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
);

-- Table des pièces utilisées dans les interventions
CREATE TABLE IF NOT EXISTS maintenance_parts_used (
    id SERIAL PRIMARY KEY,
    intervention_id INTEGER NOT NULL REFERENCES maintenance_interventions(id) ON DELETE CASCADE,
    part_id INTEGER NOT NULL, -- Référence vers une table de pièces
    quantity_used INTEGER NOT NULL,
    unit_cost INTEGER, -- en centimes d'euro
    total_cost INTEGER, -- en centimes d'euro
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Ajouter des colonnes manquantes à la table maintenance_interventions si nécessaire
DO $$ 
BEGIN
    -- Vérifier et ajouter les colonnes manquantes
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='maintenance_type') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN maintenance_type VARCHAR(20) NOT NULL DEFAULT 'corrective';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='priority') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='scheduled_date') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN scheduled_date TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='actual_start_time') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN actual_start_time TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='actual_end_time') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN actual_end_time TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='downtime_start') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN downtime_start TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='downtime_end') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN downtime_end TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='work_performed') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN work_performed TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='issues_found') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN issues_found TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='recommendations') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN recommendations TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='validated_by') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN validated_by INTEGER REFERENCES users(id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='validated_at') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN validated_at TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='validation_notes') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN validation_notes TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='labor_cost') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN labor_cost INTEGER; -- en centimes
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='parts_cost') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN parts_cost INTEGER; -- en centimes
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='maintenance_interventions' AND column_name='total_cost') THEN
        ALTER TABLE maintenance_interventions ADD COLUMN total_cost INTEGER; -- en centimes
    END IF;
END $$;

-- Ajouter des colonnes manquantes à la table scheduled_maintenances si nécessaire
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='scheduled_maintenances' AND column_name='maintenance_plan_id') THEN
        ALTER TABLE scheduled_maintenances ADD COLUMN maintenance_plan_id INTEGER REFERENCES maintenance_plans(id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='scheduled_maintenances' AND column_name='estimated_start_time') THEN
        ALTER TABLE scheduled_maintenances ADD COLUMN estimated_start_time VARCHAR(8) NOT NULL DEFAULT '08:00:00';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='scheduled_maintenances' AND column_name='estimated_end_time') THEN
        ALTER TABLE scheduled_maintenances ADD COLUMN estimated_end_time VARCHAR(8) NOT NULL DEFAULT '10:00:00';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='scheduled_maintenances' AND column_name='priority') THEN
        ALTER TABLE scheduled_maintenances ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='scheduled_maintenances' AND column_name='notes') THEN
        ALTER TABLE scheduled_maintenances ADD COLUMN notes TEXT;
    END IF;
END $$;

-- Créer des index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_maintenance_plans_equipment_id ON maintenance_plans(equipment_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_plans_active ON maintenance_plans(is_active);
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_plan_id ON maintenance_tasks(maintenance_plan_id);
CREATE INDEX IF NOT EXISTS idx_intervention_tasks_intervention_id ON intervention_tasks(intervention_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_maintenances_date ON scheduled_maintenances(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_maintenance_interventions_equipment_id ON maintenance_interventions(equipment_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_interventions_status ON maintenance_interventions(status);

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour mettre à jour automatiquement updated_at
DROP TRIGGER IF EXISTS update_maintenance_plans_updated_at ON maintenance_plans;
CREATE TRIGGER update_maintenance_plans_updated_at BEFORE UPDATE ON maintenance_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_maintenance_tasks_updated_at ON maintenance_tasks;
CREATE TRIGGER update_maintenance_tasks_updated_at BEFORE UPDATE ON maintenance_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_intervention_tasks_updated_at ON intervention_tasks;
CREATE TRIGGER update_intervention_tasks_updated_at BEFORE UPDATE ON intervention_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_maintenance_parts_used_updated_at ON maintenance_parts_used;
CREATE TRIGGER update_maintenance_parts_used_updated_at BEFORE UPDATE ON maintenance_parts_used FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
