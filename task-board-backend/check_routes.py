import main

print('Backend server imported successfully')
print('Routes:')
for route in main.app.routes:
    print(f'  {route.path}')