import os
import psycopg2
from db import get_db_connection

def clear_all_tables(cursor):
    """
    Safely empties all tables in the correct order and resets 
    their auto-incrementing SERIAL sequences back to 1.
    """
    print("🧹 Clearing existing data from all tables...")
    
    # List of all tables in your schema
    tables = [
        'member_of', 'Recipe_Tags', 'Reviews', 'Recipe_Ingredients', 'Stock',
        'Recipes', 'Tags', 'Ingredients', 'Household', 'Users'
    ]
    
    # JOINing them into a single string: "member_of, Recipe_Tags, ..."
    tables_str = ", ".join(tables)
    
    # RESTART IDENTITY resets SERIAL counters to 1
    # CASCADE ensures dependent rows are cleared smoothly without FK violations
    sql_command = f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE;"
    
    try:
        cursor.execute(sql_command)
        print("✅ Database is now completely empty and sequences are reset to 1!\n")
    except Exception as e:
        print(f"❌ Error while clearing tables: {e}")
        raise e

def import_csv_to_table(cursor, csv_filename, table_name):
    """
    Finds a CSV file in the project directory and streams it 
    into the designated PostgreSQL table using COPY.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, csv_filename)
    
    if not os.path.exists(csv_path):
        print(f"⚠️  Skipping '{table_name}': File '{csv_filename}' not found.")
        return

    print(f"⏳ Bulk-loading {csv_filename} into '{table_name}' table...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        sql_command = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
        try:
            cursor.copy_expert(sql_command, f)
            print(f"✅ Successfully populated '{table_name}'!")
        except Exception as e:
            print(f"❌ Error inserting into '{table_name}': {e}")
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
        print(f"⚠️  Could not reset sequence for {table_name}: {e}")

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("🚀 Starting full database refresh and import...\n")
        
        # --- PHASE 0: WIPE OUT EXISTING DATA ---
        clear_all_tables(cur)
        
        # --- PHASE 1: CORE / INDEPENDENT TABLES ---
        print("--- Loading core data ---")
        import_csv_to_table(cur, 'users.csv', 'Users')
        import_csv_to_table(cur, 'households.csv', 'Household')
        import_csv_to_table(cur, 'tags.csv', 'Tags')
        import_csv_to_table(cur, 'ingredients_cleaned.csv', 'Ingredients')
        
        # --- PHASE 2: DEPENDENT TABLES ---
        print("\n--- Loading dependent data ---")
        import_csv_to_table(cur, 'recipes.csv', 'Recipes')
        
        # --- PHASE 3: JUNCTION / RELATIONSHIP TABLES ---
        print("\n--- Loading relationship data ---")
        import_csv_to_table(cur, 'member_of.csv', 'member_of')
        import_csv_to_table(cur, 'recipe_tags.csv', 'Recipe_Tags')
        import_csv_to_table(cur, 'reviews.csv', 'Reviews')
        import_csv_to_table(cur, 'recipe_ingredients.csv', 'Recipe_Ingredients')
        import_csv_to_table(cur, 'stock.csv', 'Stock')
        
        # --- PHASE 4: SEQUENCE REPAIRS ---
        print("\n--- Aligning auto-incrementing sequences ---")
        fix_sequence(cur, 'Users', 'u_id')
        fix_sequence(cur, 'Household', 'h_id')
        fix_sequence(cur, 'Tags', 't_id')
        fix_sequence(cur, 'Ingredients', 'i_id')
        fix_sequence(cur, 'Recipes', 'r_id')
        fix_sequence(cur, 'Stock', 's_id')
        
        # Save all changes safely
        conn.commit()
        print("\n🎉 Excellent! All tables wiped, fresh data loaded, and sequences aligned.")
        
    except Exception as error:
        print(f"\n🚨 Critical error occurred. Rolling back all database modifications: {error}")
        conn.rollback()
        
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()