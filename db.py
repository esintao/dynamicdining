import psycopg2
import os

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", 5432),
        database=os.environ.get("DB_NAME", "recipe_app"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "6452")
    )
    return conn