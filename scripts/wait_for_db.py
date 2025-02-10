import time
import psycopg2
from src.core.config import settings

def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=settings.DATABASE_URL.split("://")[1].split(":")[0],
                password=settings.DATABASE_URL.split(":")[2].split("@")[0],
                host=settings.DATABASE_URL.split("@")[1].split(":")[0],
            )
            conn.close()
            break
        except psycopg2.OperationalError:
            print("Waiting for database...")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_db() 