import sqlite3

conn = sqlite3.connect('synergyai.db')
cursor = conn.cursor()

cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

if tables:
    cursor.execute('SELECT COUNT(*) FROM sessions')
    count = cursor.fetchone()[0]
    print(f'Sessions count: {count}')
    
    cursor.execute('SELECT id, created_at FROM sessions ORDER BY created_at DESC LIMIT 5')
    sessions = cursor.fetchall()
    print('Recent sessions:')
    for session in sessions:
        print(f'  - {session[0]}: {session[1]}')

conn.close()
