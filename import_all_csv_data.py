import os
import psycopg2
from db import get_db_connection

def clear_all_tables(cursor):
    """
    Safely empties all tables in the correct order and resets 
    their auto-incrementing SERIAL sequences back to 1.
    """
    print("🧹 Clearing existing data from all tables...")
    
    # Updated to reflect the lowercased table realities in PostgreSQL
    tables = [
        'member_of', 'recipe_tags', 'reviews', 'recipe_ingredients', 'stock',
        'recipes', 'tags', 'ingredients', 'household', 'users'
    ]
    
    tables_str = ", ".join(tables)
    sql_command = f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE;"
    
    try:
        cursor.execute(sql_command)
        print("Database is now completely empty and sequences are reset to 1!\n")
    except Exception as e:
        print(f"Error while clearing tables: {e}")
        raise e

def import_csv_to_table(cursor, csv_filename, table_name):
    """
    Finds a CSV file in the project directory and streams it 
    into the designated PostgreSQL table using COPY.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, 'value_files', csv_filename)
    
    if not os.path.exists(csv_path):
        print(f"Skipping '{table_name}': File '{csv_filename}' not found.")
        return

    print(f"Bulk-loading {csv_filename} into '{table_name}' table...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        sql_command = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
        try:
            cursor.copy_expert(sql_command, f)
            print(f"Successfully populated '{table_name}'!")
        except Exception as e:
            print(f"Error inserting into '{table_name}': {e}")
            raise e

def fix_sequence(cursor, table_name, pk_column):
    """
    Fast-forwards the background SERIAL sequence counter to match the 
    highest imported ID. This protects live app inserts from colliding.
    """
    try:
        sql_command = f"""
            SELECT setval(
                pg_get_serial_sequence('{table_name}', '{pk_column}'), 
                COALESCE(MAX({pk_column}), 1)
            ) FROM {table_name};
        """
        cursor.execute(sql_command)
        print(f"  -> Reset sequence for '{table_name}.{pk_column}'")
    except Exception as e:
        print(f"Could not reset sequence for {table_name}: {e}")

def create_database_indexes(cursor):
    """
    Applies search indexing across critical relational target tables.
    Table names are written clean without double quotes so PostgreSQL finds its lowercased identifiers.
    """
    print("Creating computational search tree performance indexes...")
    
    indexes = [
        # 1. Faster recipe title search filter calculations (mapped to r_name)
        "CREATE INDEX IF NOT EXISTS idx_recipes_r_name ON recipes(r_name);",
        
        # 2. Optimized primary foreign key parameters for recipe ingredient linking rows
        "CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_r_id ON recipe_ingredients(r_id);",
        "CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_i_id ON recipe_ingredients(i_id);",
        
        # 3. Fast lookup composite index evaluating pantry matching groups by household 
        "CREATE INDEX IF NOT EXISTS idx_stock_household_lookup ON stock(h_id, i_id);",
        
        # 4. Multi-variable lookups sorting recipe collections with filtering tags
        "CREATE INDEX IF NOT EXISTS idx_recipe_tags_lookup ON recipe_tags(r_id, t_id);"
    ]
    
    for query in indexes:
        try:
            cursor.execute(query)
        except Exception as e:
            print(f"Failed to compile operational index: {e}")
            raise e
    print("Performance indexes compiled and optimized across target datasets!")

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("Starting full database refresh and import...\n")
        
        # --- PHASE 0: WIPE OUT EXISTING DATA ---
        clear_all_tables(cur)
        
        # --- PHASE 1: CORE / INDEPENDENT TABLES ---
        print("--- Loading core data ---")
        import_csv_to_table(cur, 'users.csv', 'users')
        import_csv_to_table(cur, 'households.csv', 'household')
        import_csv_to_table(cur, 'tags.csv', 'tags')
        import_csv_to_table(cur, 'ingredients_cleaned.csv', 'ingredients')
        
        # --- PHASE 2: DEPENDENT TABLES ---
        print("\n--- Loading dependent data ---")
        import_csv_to_table(cur, 'recipes.csv', 'recipes')
        
        # --- PHASE 3: JUNCTION / RELATIONSHIP TABLES ---
        print("\n--- Loading relationship data ---")
        import_csv_to_table(cur, 'member_of.csv', 'member_of')
        import_csv_to_table(cur, 'recipe_tags.csv', 'recipe_tags')
        import_csv_to_table(cur, 'reviews.csv', 'reviews')
        import_csv_to_table(cur, 'recipe_ingredients.csv', 'recipe_ingredients')
        import_csv_to_table(cur, 'stock.csv', 'stock')
        
        # --- PHASE 4: SEQUENCE REPAIRS ---
        print("\n--- Aligning auto-incrementing sequences ---")
        fix_sequence(cur, 'users', 'u_id')
        fix_sequence(cur, 'household', 'h_id')
        fix_sequence(cur, 'tags', 't_id')
        fix_sequence(cur, 'ingredients', 'i_id')
        fix_sequence(cur, 'recipe_ingredients', 'ri_id')
        fix_sequence(cur, 'recipes', 'r_id')
        fix_sequence(cur, 'stock', 's_id')
        
        # --- PHASE 5: EXECUTE SEARCH PERFORMANCE INDEXES ---
        print("\n--- Building performance layers ---")
        create_database_indexes(cur)
        
        # Save all changes safely
        conn.commit()
        print("\nExcellent! All tables wiped, fresh data loaded, sequences aligned, and search indexes built.")
        
    except Exception as error:
        print(f"\nCritical error occurred. Rolling back all database modifications: {error}")
        conn.rollback()
        
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()