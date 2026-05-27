import os
import psycopg2
from db import get_db_connection

def import_csv_to_table(cursor, csv_filename, table_name):
    """
    Finds a CSV file in the project directory and streams it 
    into the designated PostgreSQL table using COPY.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, csv_filename)
    
    # Gracefully skip if a specific CSV file hasn't been created yet
    if not os.path.exists(csv_path):
        print(f"⚠️  Skipping '{table_name}': File '{csv_filename}' not found.")
        return

    print(f"⏳ Bulk-loading {csv_filename} into '{table_name}' table...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        # WITH CSV HEADER ignores the first line containing the column names
        sql_command = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
        try:
            cursor.copy_expert(sql_command, f)
            print(f"✅ Successfully populated '{table_name}'!")
        except Exception as e:
            print(f"❌ Error inserting into '{table_name}': {e}")
            raise e  # Force a transaction rollback to prevent messy data states

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("🚀 Starting full database import...\n")
        
        # --- PHASE 1: CORE / INDEPENDENT TABLES ---
        # These tables don't rely on foreign keys from other tables.
        import_csv_to_table(cur, 'users.csv', 'Users')
        import_csv_to_table(cur, 'households.csv', 'Household')
        import_csv_to_table(cur, 'tags.csv', 'Tags')
        import_csv_to_table(cur, 'ingredients_cleaned.csv', 'Ingredients')
        
        print("\n--- Core tables loaded. Moving to relationship tables ---\n")
        
        # --- PHASE 2: DEPENDENT TABLES ---
        # Recipes relies on a writer_id from the Users table.
        import_csv_to_table(cur, 'recipes.csv', 'Recipes')
        
        # --- PHASE 3: JUNCTION / RELATIONSHIP TABLES ---
        # These multi-way link tables depend heavily on the IDs created above.
        import_csv_to_table(cur, 'member_of.csv', 'member_of')
        import_csv_to_table(cur, 'recipe_tags.csv', 'Recipe_Tags')
        import_csv_to_table(cur, 'reviews.csv', 'Reviews')
        import_csv_to_table(cur, 'recipe_ingredients.csv', 'Recipe_Ingredients')
        import_csv_to_table(cur, 'stock.csv', 'Stock')
        
        # Save changes if everything went through without an exception
        conn.commit()
        print("\n🎉 Excellent! All tables have been successfully populated with your CSV data.")
        
    except Exception as error:
        print(f"\n🚨 Critical error occurred. Rolling back all database modifications: {error}")
        conn.rollback()
        
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()