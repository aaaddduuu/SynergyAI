import sqlite3
from datetime import datetime

def clean_duplicate_sessions():
    conn = sqlite3.connect('data/workspace.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, data, created_at FROM sessions ORDER BY created_at DESC')
    sessions = cursor.fetchall()

    print(f'Total sessions: {len(sessions)}')

    if len(sessions) <= 1:
        print('No duplicates found.')
        return

    print('\nSessions:')
    for i, (session_id, data, created_at) in enumerate(sessions[:10]):
        print(f'{i+1}. {session_id} - {created_at}')

    print(f'\nKeeping the most recent session: {sessions[0][0]}')
    print(f'Deleting {len(sessions) - 1} older sessions...')

    for session_id, _, _ in sessions[1:]:
        cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        print(f'Deleted: {session_id}')

    conn.commit()

    cursor.execute('SELECT COUNT(*) FROM sessions')
    remaining = cursor.fetchone()[0]
    print(f'\nRemaining sessions: {remaining}')

    conn.close()
    print('Cleanup complete!')

if __name__ == '__main__':
    clean_duplicate_sessions()
