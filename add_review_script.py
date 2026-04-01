import sqlite3

def add_manual_review():
    imdb_id = input("Enter the IMDb ID of the movie (e.g., tt0111161): ")
    username = input("Enter the reviewer's username: ")
    review_text = input("Enter the review text: ")

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    try: 
        cursor.execute("INSERT INTO reviews (imdb_id, username, review_text) VALUES (?, ?, ?)", 
                       (imdb_id, username, review_text))
        conn.commit()
        print("Review added successfully!")
    except Exception as e:
        print(f"Error adding review: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_manual_review()