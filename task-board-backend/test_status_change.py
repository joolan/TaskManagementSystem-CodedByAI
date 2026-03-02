import sqlite3
import os
import time

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'task_board.db')

print(f"Testing task status change in database: {db_path}")
print("=" * 60)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current message count
cursor.execute("SELECT COUNT(*) FROM messages WHERE message_type='task_message';")
original_count = cursor.fetchone()[0]
print(f"Original task_message count: {original_count}")

# Check current task 1 status
cursor.execute("SELECT status_id FROM tasks WHERE id = 1;")
current_status_id = cursor.fetchone()[0]
cursor.execute("SELECT name FROM statuses WHERE id = ?;", (current_status_id,))
current_status_name = cursor.fetchone()[0]
print(f"Current task 1 status: {current_status_name} (ID: {current_status_id})")

# Determine new status (toggle between completed and in progress)
if current_status_id == 3:  # Currently completed
    new_status_id = 2  # Change to in progress
    new_status_name = "进行中"
else:  # Currently not completed
    new_status_id = 3  # Change to completed
    new_status_name = "已完成"

print(f"Changing task 1 status to: {new_status_name} (ID: {new_status_id})")

# Update task status
cursor.execute("UPDATE tasks SET status_id = ? WHERE id = 1;", (new_status_id,))
conn.commit()
print("✓ Task status updated")

# Simulate the notification logic manually to test
# This is what the backend code should do
old_status_name = current_status_name

# Check if we need to send notification
if (old_status_name != "已完成" and new_status_name == "已完成") or \
   (old_status_name == "已完成" and new_status_name != "已完成"):
    print("✓ Status change triggers notification condition")
    
    # Get task title
    cursor.execute("SELECT title FROM tasks WHERE id = 1;")
    task_title = cursor.fetchone()[0]
    
    # Get current user ID (using admin user)
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1;")
    admin_id = cursor.fetchone()[0]
    
    # Create message
    content = f"任务「{task_title}」的状态已从「{old_status_name}」变更为「{new_status_name}」"
    cursor.execute("""
    INSERT INTO messages (message_type, title, content, task_id, created_by, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'task_message',
        '任务消息',
        content,
        1,
        admin_id,
        time.strftime('%Y-%m-%d %H:%M:%S')
    ))
    message_id = cursor.lastrowid
    conn.commit()
    print(f"✓ Created message with ID: {message_id}")
    print(f"  Content: {content}")
    
    # Get all task followers
    cursor.execute("""
    SELECT user_id FROM task_follows WHERE task_id = 1
    """)
    followers = cursor.fetchall()
    print(f"Found {len(followers)} followers for task 1")
    
    # Create user messages for followers
    for follower in followers:
        user_id = follower[0]
        cursor.execute("""
        INSERT INTO user_messages (user_id, message_id)
        VALUES (?, ?)
        """, (user_id, message_id))
    if followers:
        conn.commit()
        print(f"✓ Created user messages for {len(followers)} followers")
else:
    print("✗ Status change does not trigger notification condition")

# Check new message count
cursor.execute("SELECT COUNT(*) FROM messages WHERE message_type='task_message';")
new_count = cursor.fetchone()[0]
print(f"New task_message count: {new_count}")
print(f"Messages created: {new_count - original_count}")

# Show the latest message
cursor.execute("""
SELECT id, title, content, created_at
FROM messages 
WHERE message_type = 'task_message'
ORDER BY created_at DESC
LIMIT 1
""")
latest_message = cursor.fetchone()
if latest_message:
    print("\nLatest task_message:")
    print(f"ID: {latest_message[0]}")
    print(f"Title: {latest_message[1]}")
    print(f"Content: {latest_message[2]}")
    print(f"Created at: {latest_message[3]}")

# Restore original status (optional)
# cursor.execute("UPDATE tasks SET status_id = ? WHERE id = 1;", (current_status_id,))
# conn.commit()
# print(f"✓ Restored task 1 status to: {current_status_name}")

conn.close()
print("=" * 60)
print("Status change test completed")
