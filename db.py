import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="recipe_app",
        user="postgres",
        password="6452"
    )
    return conn