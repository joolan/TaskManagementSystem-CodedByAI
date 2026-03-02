from db import get_db, Permission

db = next(get_db())
permissions = db.query(Permission).all()

print('ID\tName\tCode\tDescription')
for perm in permissions:
    print(f'{perm.id}\t{perm.name}\t{perm.code}\t{perm.description}')
