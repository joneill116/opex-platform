import os
import time
import psycopg2
from psycopg2 import OperationalError

def run_migrations():
    """
    Connects to the database and applies all SQL migrations
    from the 'migrations' directory.
    """
    conn = None
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host="postgres-orchestration",
                port="5432"
            )
            print("✅ Database connection successful.")
            break
        except OperationalError as e:
            print(f"⏳ Database not ready yet, waiting... ({e})")
            retries -= 1
            time.sleep(5)
    
    if not conn:
        print("❌ Could not connect to the database after several retries. Exiting.")
        exit(1)

    try:
        with conn.cursor() as cur:
            migrations_dir = "migrations"
            if not os.path.exists(migrations_dir):
                print(f"No '{migrations_dir}' directory found. Skipping migrations.")
                return

            print("📂 Found migrations directory. Applying migrations...")
            for filename in sorted(os.listdir(migrations_dir)):
                if filename.endswith(".sql"):
                    filepath = os.path.join(migrations_dir, filename)
                    print(f"  -> Applying migration: {filename}")
                    with open(filepath, 'r') as f:
                        cur.execute(f.read())
            conn.commit()
        print("✅ All migrations applied successfully.")
    except Exception as e:
        print(f"❌ An error occurred during migration: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migrations()
