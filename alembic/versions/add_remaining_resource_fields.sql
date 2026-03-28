-- Manual SQL to add remaining resource fields if they don't exist

-- Add resource_type if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='resources' AND column_name='resource_type') THEN
        ALTER TABLE resources ADD COLUMN resource_type VARCHAR(50);
        UPDATE resources SET resource_type = 'table' WHERE resource_type IS NULL;
        ALTER TABLE resources ALTER COLUMN resource_type SET NOT NULL;
    END IF;
END $$;

-- Add resource_name if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='resources' AND column_name='resource_name') THEN
        ALTER TABLE resources ADD COLUMN resource_name VARCHAR(150);
        UPDATE resources SET resource_name = COALESCE(name_en, 'Resource') WHERE resource_name IS NULL;
        ALTER TABLE resources ALTER COLUMN resource_name SET NOT NULL;
    END IF;
END $$;

-- Add price_per_hour if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='resources' AND column_name='price_per_hour') THEN
        ALTER TABLE resources ADD COLUMN price_per_hour DOUBLE PRECISION;
        UPDATE resources SET price_per_hour = COALESCE(base_price, 0) WHERE price_per_hour IS NULL;
        ALTER TABLE resources ALTER COLUMN price_per_hour SET NOT NULL;
    END IF;
END $$;

-- Add min_booking_hours if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='resources' AND column_name='min_booking_hours') THEN
        ALTER TABLE resources ADD COLUMN min_booking_hours INTEGER DEFAULT 1;
        UPDATE resources SET min_booking_hours = 1 WHERE min_booking_hours IS NULL;
        ALTER TABLE resources ALTER COLUMN min_booking_hours SET NOT NULL;
    END IF;
END $$;

-- Add max_booking_hours if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='resources' AND column_name='max_booking_hours') THEN
        ALTER TABLE resources ADD COLUMN max_booking_hours INTEGER DEFAULT 24;
        UPDATE resources SET max_booking_hours = 24 WHERE max_booking_hours IS NULL;
        ALTER TABLE resources ALTER COLUMN max_booking_hours SET NOT NULL;
    END IF;
END $$;

-- Add location_within_venue if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='resources' AND column_name='location_within_venue') THEN
        ALTER TABLE resources ADD COLUMN location_within_venue VARCHAR(255);
    END IF;
END $$;

-- Add amenities if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='resources' AND column_name='amenities') THEN
        ALTER TABLE resources ADD COLUMN amenities JSON;
    END IF;
END $$;

-- Add description if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='resources' AND column_name='description') THEN
        ALTER TABLE resources ADD COLUMN description TEXT;
    END IF;
END $$;

-- Add is_available_for_booking if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='resources' AND column_name='is_available_for_booking') THEN
        ALTER TABLE resources ADD COLUMN is_available_for_booking BOOLEAN DEFAULT TRUE;
        UPDATE resources SET is_available_for_booking = TRUE WHERE is_available_for_booking IS NULL;
        ALTER TABLE resources ALTER COLUMN is_available_for_booking SET NOT NULL;
    END IF;
END $$;

-- Make legacy fields nullable
ALTER TABLE resources ALTER COLUMN name_en DROP NOT NULL;
ALTER TABLE resources ALTER COLUMN name_ar DROP NOT NULL;
ALTER TABLE resources ALTER COLUMN name_fr DROP NOT NULL;
ALTER TABLE resources ALTER COLUMN base_price DROP NOT NULL;
ALTER TABLE resources ALTER COLUMN price_unit DROP NOT NULL;

-- Add indexes if they don't exist
CREATE INDEX IF NOT EXISTS ix_resources_resource_type ON resources(resource_type);
CREATE INDEX IF NOT EXISTS ix_resources_venue_id_resource_name ON resources(venue_id, resource_name);

-- Success message
SELECT 'Resource fields migration completed successfully!' as status;
