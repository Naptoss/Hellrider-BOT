import sqlite3

def create_database():
    conm = sqlite3.connect('database/database.db')
    cursor = conm.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS farm_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        passport TEXT NOT NULL,
        farm_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conm.commit()
    conm.close()

create_database()

