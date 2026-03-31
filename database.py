import sqlite3

def init_db():
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()
    # Create a table for reviews
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imdb_id TEXT NOT NULL,
            username TEXT NOT NULL,
            review_text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized!")