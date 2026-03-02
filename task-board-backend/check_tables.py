import sqlite3

conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()

# 获取所有表
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
tables = cursor.fetchall()

print('Tables in database:')
for table in tables:
    print(table[0])

conn.close()
