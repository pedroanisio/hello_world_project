from sqlalchemy import create_engine, text
from src.core.config import settings
import re

def create_database():
    # Extract database name from URL
    db_name = re.search(r"/([^/]+)$", settings.DATABASE_URL).group(1)
    base_url = settings.DATABASE_URL.rsplit('/', 1)[0]
    
    # Connect to default postgres database
    engine = create_engine(f"{base_url}/postgres")
    
    conn = engine.connect()
    conn.execute(text("commit"))
    
    try:
        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        print(f"Database {db_name} created successfully")
    except Exception as e:
        print(f"Database creation failed (maybe it already exists): {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database() 