def migrate(cr, version):
    if not version:
        return

    # Step 1: Add the new `fix_rate` column if not already present
    cr.execute("""
        ALTER TABLE app_commission
        ADD COLUMN IF NOT EXISTS fix_rate FLOAT;
    """)

    # Step 2: Copy old values from `old_fix_qty` (renamed in pre-migration)
    cr.execute("""
        UPDATE app_commission
        SET fix_rate = old_fix_qty
        WHERE old_fix_qty IS NOT NULL;
    """)

    # Optional: Drop the old column after migration
    cr.execute("""
        ALTER TABLE app_commission
        DROP COLUMN IF EXISTS old_fix_qty;
    """)
