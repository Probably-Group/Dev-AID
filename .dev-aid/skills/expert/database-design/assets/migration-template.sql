-- =============================================================================
-- Migration: [NNN]_[short_description].sql
-- Description: [What this migration does and why]
-- Author: [Name]
-- Date: [YYYY-MM-DD]
-- Depends on: [Previous migration number, e.g. 005]
-- =============================================================================

-- =============================================================================
-- UP MIGRATION
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Schema Changes
-- ---------------------------------------------------------------------------

-- Create new table (with safety check)
CREATE TABLE IF NOT EXISTS [table_name] (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    [column_name] [TYPE] NOT NULL,
    [column_name] [TYPE] CHECK ([constraint]),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add column to existing table
ALTER TABLE [existing_table]
    ADD COLUMN IF NOT EXISTS [column_name] [TYPE];

-- Add constraint (after data is clean)
-- ALTER TABLE [table_name]
--     ADD CONSTRAINT [constraint_name] CHECK ([expression]);

-- ---------------------------------------------------------------------------
-- 2. Indexes
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_[table]_[columns]
    ON [table_name] ([column1], [column2]);

-- Partial index for common filter
-- CREATE INDEX IF NOT EXISTS idx_[table]_[column]_active
--     ON [table_name] ([column]) WHERE deleted_at IS NULL;

-- ---------------------------------------------------------------------------
-- 3. Data Migration (if needed)
-- ---------------------------------------------------------------------------

-- Backfill new column with default/computed values
-- UPDATE [table_name]
--     SET [new_column] = [expression]
--     WHERE [new_column] IS NULL;

-- Make column NOT NULL after backfill
-- ALTER TABLE [table_name]
--     ALTER COLUMN [column_name] SET NOT NULL;

-- ---------------------------------------------------------------------------
-- 4. Triggers / Functions (if needed)
-- ---------------------------------------------------------------------------

-- Auto-update updated_at timestamp
-- CREATE OR REPLACE FUNCTION update_updated_at()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.updated_at = NOW();
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER [table]_updated_at
--     BEFORE UPDATE ON [table_name]
--     FOR EACH ROW EXECUTE FUNCTION update_updated_at();

COMMIT;

-- =============================================================================
-- DOWN MIGRATION (Revert)
-- =============================================================================

-- BEGIN;
--
-- DROP TRIGGER IF EXISTS [table]_updated_at ON [table_name];
-- DROP FUNCTION IF EXISTS update_updated_at();
-- DROP INDEX IF EXISTS idx_[table]_[columns];
-- ALTER TABLE [existing_table] DROP COLUMN IF EXISTS [column_name];
-- DROP TABLE IF EXISTS [table_name];
--
-- COMMIT;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Verify table exists and has expected columns
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = '[table_name]'
-- ORDER BY ordinal_position;

-- Verify indexes exist
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename = '[table_name]';

-- Verify row count after data migration
-- SELECT COUNT(*) FROM [table_name] WHERE [new_column] IS NOT NULL;
