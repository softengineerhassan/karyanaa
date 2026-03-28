-- MANUAL SQL MIGRATION FOR VENUE OPERATING HOURS
-- 1. Create the day of week enum
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'day_of_week_enum') THEN
        CREATE TYPE day_of_week_enum AS ENUM (
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
        );
    END IF;
END $$;

-- 2. Create the venue_operating_hours table
CREATE TABLE IF NOT EXISTS venue_operating_hours (
    id UUID PRIMARY KEY,
    venue_id UUID NOT NULL,
    day_of_week day_of_week_enum NOT NULL,
    is_open BOOLEAN DEFAULT TRUE NOT NULL,
    open_time TIME,
    close_time TIME,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE,
    UNIQUE (venue_id, day_of_week)
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS ix_venue_operating_hours_venue_id ON venue_operating_hours(venue_id);
