def migrate(cr, version):
    if not version:
        return

    # Log data count for existing field (optional safety check)
    cr.execute("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = 'app_commission' AND column_name = 'fix_qty';
    """)
    result = cr.fetchone()
    if result and result[0] == 0:
        # Column doesn't exist or already removed
        return

    # Rename the column instead of dropping it immediately (safe approach)
    cr.execute("""
        ALTER TABLE app_commission
        RENAME COLUMN fix_qty TO old_fix_qty;
    """)
