import sqlite3

conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()

cursor.execute('SELECT id, name, code, description FROM permissions')
permissions = cursor.fetchall()

print('ID\tName\tCode\tDescription')
for perm in permissions:
    print(f'{perm[0]}\t{perm[1]}\t{perm[2]}\t{perm[3]}')

conn.close()
