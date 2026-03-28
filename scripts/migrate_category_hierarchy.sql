-- ============================================================================
-- CATEGORY HIERARCHY MIGRATION
-- Purpose: Add subcategory_id to venues table
-- Hierarchy: Category → Subcategory → Venue
-- ============================================================================

-- ============================================================================
-- STEP 1: ADD SUBCATEGORY_ID COLUMN (NULLABLE)
-- ============================================================================
-- Description: Add new column as nullable to avoid data loss
-- Safe to run: YES (additive change only)
-- ============================================================================

ALTER TABLE omnia.venues 
ADD COLUMN subcategory_id UUID NULL;

-- Verification:
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'omnia' 
  AND table_name = 'venues' 
  AND column_name = 'subcategory_id';
-- Expected: subcategory_id | uuid | YES


-- ============================================================================
-- STEP 2: ADD FOREIGN KEY CONSTRAINT
-- ============================================================================
-- Description: Ensure referential integrity with subcategories table
-- Safe to run: YES (uses RESTRICT to prevent orphaned records)
-- ============================================================================

ALTER TABLE omnia.venues
ADD CONSTRAINT fk_venues_subcategory
FOREIGN KEY (subcategory_id) 
REFERENCES omnia.subcategories(id)
ON DELETE RESTRICT;

-- Verification:
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'omnia'
  AND table_name = 'venues'
  AND constraint_name = 'fk_venues_subcategory';
-- Expected: fk_venues_subcategory | FOREIGN KEY


-- ============================================================================
-- STEP 3: ADD INDEX FOR PERFORMANCE
-- ============================================================================
-- Description: Index on subcategory_id for faster queries
-- Safe to run: YES (performance optimization)
-- ============================================================================

CREATE INDEX idx_venues_subcategory_id 
ON omnia.venues(subcategory_id);

-- Verification:
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'omnia'
  AND tablename = 'venues'
  AND indexname = 'idx_venues_subcategory_id';
-- Expected: idx_venues_subcategory_id | CREATE INDEX...


-- ============================================================================
-- STEP 4: DATA BACKFILL STRATEGY
-- ============================================================================
-- Description: Populate subcategory_id for existing venues
-- IMPORTANT: Choose ONE strategy based on your data
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STRATEGY A: Manual Mapping (Recommended if subcategories are well-defined)
-- ----------------------------------------------------------------------------
-- Example: Assign venues to specific subcategories based on business logic
-- 
-- UPDATE omnia.venues 
-- SET subcategory_id = 'uuid-of-subcategory'
-- WHERE category_id = 'uuid-of-category' 
--   AND <additional_business_logic>;


-- ----------------------------------------------------------------------------
-- STRATEGY B: Create Default Subcategory per Category
-- ----------------------------------------------------------------------------
-- Description: Auto-create "General" subcategory for each category
-- Use this if you want to preserve existing structure

DO $$
DECLARE
    cat RECORD;
    new_subcat_id UUID;
BEGIN
    FOR cat IN SELECT id, name_en, name_ar, name_fr FROM omnia.categories
    LOOP
        -- Create default subcategory
        INSERT INTO omnia.subcategories (
            id, 
            category_id, 
            name_en, 
            name_ar, 
            name_fr,
            description,
            created_at,
            updated_at
        ) VALUES (
            gen_random_uuid(),
            cat.id,
            'General ' || cat.name_en,
            'عام ' || cat.name_ar,
            'Général ' || cat.name_fr,
            'Default subcategory',
            NOW(),
            NOW()
        ) RETURNING id INTO new_subcat_id;
        
        -- Assign all venues in this category to the new subcategory
        UPDATE omnia.venues
        SET subcategory_id = new_subcat_id
        WHERE category_id = cat.id
          AND subcategory_id IS NULL;
    END LOOP;
END $$;

-- Verification after backfill:
SELECT 
    COUNT(*) as total_venues,
    COUNT(subcategory_id) as venues_with_subcategory,
    COUNT(*) - COUNT(subcategory_id) as venues_without_subcategory
FROM omnia.venues;
-- Expected: venues_without_subcategory = 0 (if backfill complete)


-- ----------------------------------------------------------------------------
-- STRATEGY C: Leave Nullable (Manual Assignment Later)
-- ----------------------------------------------------------------------------
-- Description: Skip backfill, assign subcategories manually via admin UI
-- No SQL needed - subcategory_id remains NULL until manually set


-- ============================================================================
-- STEP 5: MAKE CATEGORY_ID NULLABLE (OPTIONAL)
-- ============================================================================
-- Description: Allow category_id to be null for pure subcategory hierarchy
-- Safe to run: AFTER backfill complete and verified
-- WARNING: Only run if you want to fully migrate to subcategory-only model
-- ============================================================================

-- ALTER TABLE omnia.venues 
-- ALTER COLUMN category_id DROP NOT NULL;

-- Verification:
-- SELECT column_name, is_nullable
-- FROM information_schema.columns
-- WHERE table_schema = 'omnia' 
--   AND table_name = 'venues' 
--   AND column_name = 'category_id';
-- Expected: category_id | YES


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check schema changes
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'omnia' 
  AND table_name = 'venues' 
  AND column_name IN ('category_id', 'subcategory_id')
ORDER BY column_name;

-- Check constraints
SELECT 
    constraint_name, 
    constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'omnia'
  AND table_name = 'venues'
  AND constraint_name LIKE '%subcategory%';

-- Check indexes
SELECT 
    indexname, 
    indexdef
FROM pg_indexes
WHERE schemaname = 'omnia'
  AND tablename = 'venues'
  AND indexname LIKE '%subcategory%';

-- Data integrity check
SELECT 
    v.id,
    v.name_en,
    v.category_id,
    v.subcategory_id,
    c.name_en as category_name,
    sc.name_en as subcategory_name
FROM omnia.venues v
LEFT JOIN omnia.categories c ON v.category_id = c.id
LEFT JOIN omnia.subcategories sc ON v.subcategory_id = sc.id
WHERE v.subcategory_id IS NULL
LIMIT 10;

-- Check for orphaned references
SELECT COUNT(*)
FROM omnia.venues v
LEFT JOIN omnia.subcategories sc ON v.subcategory_id = sc.id
WHERE v.subcategory_id IS NOT NULL 
  AND sc.id IS NULL;
-- Expected: 0


-- ============================================================================
-- ROLLBACK PROCEDURE
-- ============================================================================
-- Description: Emergency revert if issues occur
-- WARNING: This will remove all subcategory assignments
-- ============================================================================

-- Step 1: Remove index
DROP INDEX IF EXISTS omnia.idx_venues_subcategory_id;

-- Step 2: Remove FK constraint
ALTER TABLE omnia.venues
DROP CONSTRAINT IF EXISTS fk_venues_subcategory;

-- Step 3: Remove column
ALTER TABLE omnia.venues
DROP COLUMN IF EXISTS subcategory_id;

-- Step 4: Restore category_id NOT NULL (if it was changed)
-- ALTER TABLE omnia.venues
-- ALTER COLUMN category_id SET NOT NULL;

-- Verification after rollback:
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'omnia' 
  AND table_name = 'venues' 
  AND column_name = 'subcategory_id';
-- Expected: 0 rows


-- ============================================================================
-- EXECUTION CHECKLIST
-- ============================================================================
-- [ ] 1. Backup database
-- [ ] 2. Run STEP 1: Add column
-- [ ] 3. Run STEP 2: Add FK constraint
-- [ ] 4. Run STEP 3: Add index
-- [ ] 5. Verify schema changes
-- [ ] 6. Deploy updated SQLAlchemy models
-- [ ] 7. Run STEP 4: Backfill data (choose strategy)
-- [ ] 8. Verify data integrity
-- [ ] 9. (Optional) Run STEP 5: Make category_id nullable
-- [ ] 10. Monitor application logs
-- [ ] 11. Final verification
-- ============================================================================
