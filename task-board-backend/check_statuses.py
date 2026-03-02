import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'task_board.db')

print(f"Checking statuses in database: {db_path}")
print("=" * 60)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if statuses table exists
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='statuses';")
    if cursor.fetchone():
        print("✓ Statuses table exists")
        
        # Get all statuses
        cursor.execute("SELECT id, name, color FROM statuses ORDER BY id;")
        statuses = cursor.fetchall()
        
        if statuses:
            print("\nStatus details:")
            print("-" * 60)
            for status in statuses:
                print(f"ID: {status[0]}")
                print(f"Name: '{status[1]}'")
                print(f"Color: {status[2]}")
                print("-" * 60)
        else:
            print("\nNo statuses found")
            
        # Check task 1 current status
        cursor.execute("SELECT status_id FROM tasks WHERE id = 1;")
        task1_status = cursor.fetchone()
        if task1_status:
            status_id = task1_status[0]
            cursor.execute("SELECT name FROM statuses WHERE id = ?;", (status_id,))
            status_name = cursor.fetchone()
            if status_name:
                print(f"\n✓ Task 1 current status: {status_name[0]} (ID: {status_id})")
            else:
                print(f"\n✗ Task 1 status ID {status_id} not found")
        else:
            print("\n✗ Task 1 not found")
            
    else:
        print("✗ Statuses table does not exist")
        
except Exception as e:
    print(f"Error checking database: {e}")
finally:
    conn.close()

print("=" * 60)
print("Status check completed")
