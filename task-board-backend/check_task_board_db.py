import sqlite3

conn = sqlite3.connect('task_board.db')
cursor = conn.cursor()

# 获取所有表
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
tables = cursor.fetchall()

print('Tables in task_board.db:')
for table in tables:
    print(table[0])

# 检查permissions表是否存在
cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type=\"table\" AND name=\"permissions\";')
if cursor.fetchone()[0] > 0:
    print('\nPermissions table exists, showing contents:')
    cursor.execute('SELECT id, name, code, description FROM permissions')
    permissions = cursor.fetchall()
    print('ID\tName\tCode\tDescription')
    for perm in permissions:
        print(f'{perm[0]}\t{perm[1]}\t{perm[2]}\t{perm[3]}')
else:
    print('\nPermissions table does not exist')

conn.close()
