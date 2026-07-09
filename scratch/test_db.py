import os
import sys
import traceback

# Append parent dir to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    import database as db
    print("Connecting to database...")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("\n--- Testing Tables ---")
    tables = ['users', 'income', 'expenses', 'budgets']
    for table in tables:
        try:
            db.execute_sql(cursor, f"SELECT COUNT(*) FROM {table}")
            row = cursor.fetchone()
            print(f"Table '{table}': {row[0]} records found.")
        except Exception as te:
            print(f"Table '{table}' error: {te}")
            
    print("\n--- Listing Users ---")
    try:
        db.execute_sql(cursor, "SELECT id, username FROM users LIMIT 10")
        rows = cursor.fetchall()
        for r in rows:
            print(f"User ID: {r[0]}, Username: {r[1]}")
    except Exception as ue:
        print(f"Error querying users: {ue}")
        
    conn.close()
    print("\nDatabase test completed successfully!")
except Exception as e:
    print("\nDatabase test failed!")
    traceback.print_exc()
