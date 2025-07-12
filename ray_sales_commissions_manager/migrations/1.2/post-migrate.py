def migrate(cr, version):
    if not version:
        return

    cr.execute("""
        ALTER TABLE app_commission
        ADD COLUMN IF NOT EXISTS fix_rate FLOAT;
    """)


    cr.execute("""
        UPDATE app_commission
        SET fix_rate = old_fix_qty
        WHERE old_fix_qty IS NOT NULL;
    """)

    cr.execute("""
        ALTER TABLE app_commission
        DROP COLUMN IF EXISTS old_fix_qty;
    """)
