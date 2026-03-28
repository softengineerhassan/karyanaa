-- MANUAL SQL MIGRATION FOR DYNAMIC PRICING RULES
-- 1. Create the pricing rule type enum
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pricing_rule_type_enum') THEN
        CREATE TYPE pricing_rule_type_enum AS ENUM ('peak_hours', 'weekend', 'seasonal', 'last_minute');
    END IF;
END $$;

-- 2. Add deposit_amount to existing pricing table
ALTER TABLE pricing ADD COLUMN IF NOT EXISTS deposit_amount FLOAT;

-- 3. Create the pricing_rules table
CREATE TABLE IF NOT EXISTS pricing_rules (
    id UUID PRIMARY KEY,
    pricing_id UUID NOT NULL,
    rule_type pricing_rule_type_enum NOT NULL,
    price_adjustment_percent INTEGER NOT NULL,
    start_time TIME,
    end_time TIME,
    start_date DATE,
    end_date DATE,
    active_days TEXT[],
    hours_before_booking INTEGER,
    applies_to_resources UUID[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (pricing_id) REFERENCES pricing(id) ON DELETE CASCADE
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS ix_pricing_rules_pricing_id ON pricing_rules(pricing_id);
CREATE INDEX IF NOT EXISTS ix_pricing_rules_rule_type ON pricing_rules(rule_type);
