import os
import sys

# Set environment
os.environ.setdefault("FLASK_ENV", "production")

try:
    from app import create_app
    from app.infrastructure.database import db
except ImportError as e:
    print(f"Error importing app/db. Make sure you run this script from the backend directory: {e}")
    sys.exit(1)

def run_migration():
    app = create_app()
    with app.app_context():
        print("Connecting to database and creating missing tables...")
        # 1. Create missing tables using SQLAlchemy models (like PROMO_CODE, PACK, POST, etc.)
        db.create_all()
        print("✓ Missing tables created successfully.")

        # 2. Add missing columns to existing tables using raw SQL (with safety checks)
        print("Updating existing tables with new columns...")
        migration_statements = [
            # USER table
            'ALTER TABLE "USER" ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT \'{}\'::jsonb',
            
            # TICKET table
            'ALTER TABLE TICKET ADD COLUMN IF NOT EXISTS expiration_date TIMESTAMP',
            'ALTER TABLE TICKET ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP',
            'ALTER TABLE TICKET ADD COLUMN IF NOT EXISTS correlation_id VARCHAR(36)',
            
            # TRANSFER table
            'ALTER TABLE TRANSFER ADD COLUMN IF NOT EXISTS correlation_id VARCHAR(36)',
            'ALTER TABLE TRANSFER ADD COLUMN IF NOT EXISTS from_user_id INT',
            'ALTER TABLE TRANSFER ADD COLUMN IF NOT EXISTS to_user_id INT',
            'ALTER TABLE TRANSFER ADD COLUMN IF NOT EXISTS ticket_id INT',
            'ALTER TABLE TRANSFER ADD COLUMN IF NOT EXISTS id_payment INT',
            
            # TRADE_PROPOSAL table
            'ALTER TABLE TRADE_PROPOSAL ADD COLUMN IF NOT EXISTS offered_sticker_ids JSONB DEFAULT \'[]\'::jsonb',
            
            # sports_bet table
            'ALTER TABLE sports_bet ADD COLUMN IF NOT EXISTS stripe_intent_id VARCHAR(255)',
        ]

        for statement in migration_statements:
            try:
                db.session.execute(db.text(statement))
                db.session.commit()
                print(f"  Applied: {statement}")
            except Exception as ex:
                db.session.rollback()
                print(f"  Error or skipped statement: {statement} -> {ex}")

        # 3. Add foreign key constraints to TRANSFER if missing
        print("Checking/adding foreign keys to TRANSFER...")
        fk_statements = [
            'ALTER TABLE TRANSFER ADD CONSTRAINT fk_transfer_from FOREIGN KEY (from_user_id) REFERENCES "USER"(idUser) ON DELETE SET NULL',
            'ALTER TABLE TRANSFER ADD CONSTRAINT fk_transfer_to FOREIGN KEY (to_user_id) REFERENCES "USER"(idUser) ON DELETE SET NULL',
            'ALTER TABLE TRANSFER ADD CONSTRAINT fk_transfer_ticket FOREIGN KEY (ticket_id) REFERENCES TICKET(id_ticket) ON DELETE CASCADE',
            'ALTER TABLE TRANSFER ADD CONSTRAINT fk_transfer_payment FOREIGN KEY (id_payment) REFERENCES PAYMENT(id_payment) ON DELETE SET NULL',
        ]
        
        for fk in fk_statements:
            try:
                db.session.execute(db.text(fk))
                db.session.commit()
                print(f"  Applied FK: {fk}")
            except Exception:
                db.session.rollback()
                # If constraint already exists, it will fail, which is expected and safe
                print(f"  FK already exists or skipped: {fk}")

        # 4. Insert initial seed data for ROLE
        print("Seeding initial ROLE data...")
        try:
            db.session.execute(db.text("INSERT INTO ROLE (idRole, roleName) VALUES (1, 'Admin') ON CONFLICT (idRole) DO NOTHING"))
            db.session.execute(db.text("INSERT INTO ROLE (idRole, roleName) VALUES (2, 'Fan') ON CONFLICT (idRole) DO NOTHING"))
            db.session.commit()
            print("✓ Seeded ROLE data successfully.")
        except Exception as ex:
            db.session.rollback()
            print(f"  Failed to seed ROLE data: {ex}")

        # 5. Populate initial rarities (RARYTY_CAT) if they don't exist
        print("Checking rarity categories...")
        try:
            db.session.execute(db.text("INSERT INTO RARYTY_CAT (rarety_cat_id, name) VALUES (1, 'Common') ON CONFLICT (rarety_cat_id) DO NOTHING"))
            db.session.execute(db.text("INSERT INTO RARYTY_CAT (rarety_cat_id, name) VALUES (2, 'Epic') ON CONFLICT (rarety_cat_id) DO NOTHING"))
            db.session.execute(db.text("INSERT INTO RARYTY_CAT (rarety_cat_id, name) VALUES (3, 'Rare') ON CONFLICT (rarety_cat_id) DO NOTHING"))
            db.session.execute(db.text("INSERT INTO RARYTY_CAT (rarety_cat_id, name) VALUES (4, 'Legendary') ON CONFLICT (rarety_cat_id) DO NOTHING"))
            db.session.commit()
            print("✓ Seeded rarity categories successfully.")
        except Exception as ex:
            db.session.rollback()
            print(f"  Failed to seed rarity categories: {ex}")

        print("\nMigration completed successfully!")

if __name__ == "__main__":
    run_migration()
