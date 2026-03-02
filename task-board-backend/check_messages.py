import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'task_board.db')

print(f"Checking messages in database: {db_path}")
print("=" * 60)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if messages table exists
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages';")
    if cursor.fetchone():
        print("✓ Messages table exists")
        
        # Check if there are any messages
        cursor.execute("SELECT COUNT(*) FROM messages;")
        message_count = cursor.fetchone()[0]
        print(f"✓ Total messages: {message_count}")
        
        # Check task_message type messages
        cursor.execute("SELECT COUNT(*) FROM messages WHERE message_type='task_message';")
        task_message_count = cursor.fetchone()[0]
        print(f"✓ Task message type messages: {task_message_count}")
        
        # Get all task_message type messages
        cursor.execute("""
        SELECT m.id, m.title, m.content, m.message_type, m.task_id, m.created_by, m.created_at, 
               u.name as creator_name
        FROM messages m
        LEFT JOIN users u ON m.created_by = u.id
        WHERE m.message_type = 'task_message'
        ORDER BY m.created_at DESC
        """)
        
        messages = cursor.fetchall()
        if messages:
            print("\nTask message details:")
            print("-" * 80)
            for msg in messages:
                print(f"ID: {msg[0]}")
                print(f"Title: {msg[1]}")
                print(f"Content: {msg[2]}")
                print(f"Type: {msg[3]}")
                print(f"Task ID: {msg[4]}")
                print(f"Created by: {msg[6]} (ID: {msg[5]})")
                print(f"Created at: {msg[7]}")
                print("-" * 80)
        else:
            print("\nNo task_message type messages found")
            
        # Check user_messages table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_messages';")
        if cursor.fetchone():
            print("\n✓ User messages table exists")
            cursor.execute("SELECT COUNT(*) FROM user_messages;")
            user_message_count = cursor.fetchone()[0]
            print(f"✓ Total user messages: {user_message_count}")
        else:
            print("\n✗ User messages table does not exist")
            
    else:
        print("✗ Messages table does not exist")
        
except Exception as e:
    print(f"Error checking database: {e}")
finally:
    conn.close()

print("=" * 60)
print("Message check completed")
