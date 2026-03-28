-- MANUAL SQL MIGRATION FOR PERKS TABLE
-- 1. Create the perk type enum
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'perk_type_enum') THEN
        CREATE TYPE perk_type_enum AS ENUM ('always', 'conditional');
    END IF;
END $$;

-- 2. Add new columns
ALTER TABLE perks ADD COLUMN IF NOT EXISTS perk_type perk_type_enum DEFAULT 'always';
ALTER TABLE perks ADD COLUMN IF NOT EXISTS start_date DATE;
ALTER TABLE perks ADD COLUMN IF NOT EXISTS end_date DATE;
ALTER TABLE perks ADD COLUMN IF NOT EXISTS valid_days TEXT[];
ALTER TABLE perks ADD COLUMN IF NOT EXISTS start_time TIME;
ALTER TABLE perks ADD COLUMN IF NOT EXISTS end_time TIME;

-- 3. Migrate existing data
-- Map 'condition' boolean to 'perk_type' enum
-- If condition was TRUE, it's now 'conditional'. If FALSE, it's 'always'.
UPDATE perks 
SET perk_type = CASE 
    WHEN condition = TRUE THEN 'conditional'::perk_type_enum 
    ELSE 'always'::perk_type_enum 
END;

-- 4. Drop legacy column
ALTER TABLE perks DROP COLUMN IF EXISTS condition;
