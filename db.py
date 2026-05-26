import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def query(query, params=None, one=False):
    """Executes a SQL query and returns the results as a list of dictionaries."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params)
    result = cur.fetchone() if one else cur.fetchall()
    cur.close()
    conn.close()
    return result

def execute(query, params=None):
    """Executes a SQL command that modifies the database (INSERT, UPDATE, DELETE)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    cur.close()
    conn.close()
