from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

import sqlite3

@app.get("/meta/{type}/{id}.json")
async def get_meta(type: str, id: str):
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, review_text FROM reviews WHERE imdb_id = ?", (id,))
    reviews = cursor.fetchall()
    conn.close()

    if rows: 
        # Format reviews into a string
        review_string = "\n\n--- FRIEND REVIEWS ---\n\n"
        for row in rows: 
            review_string += f"@{row[0]}: '{row[1]}'\n\n"
        else: 
            review_string = "\n\n--- FRIEND REVIEWS ---\n\nNo reviews yet. Be the first to review this movie!\n\n"
        return {
            "meta": {
                "id": id,
                "description": f"Official Synopsis here.\n\n{review_string}"
            }
        }

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_methods=["*"],
    allow_headers=["*"],
)

# The Manifest is the "ID Card" of your Stremio Addon
MANIFEST = {
    "id": "org.socialreviews.example",
    "name": "Friend Reviews",
    "version": "0.0.1",
    "description": "See what your friends are saying about movies.",
    "resources": ["meta"], # This tells Stremio we provide extra info
    "types": ["movie", "series"],
    "catalogs": []
}

@app.get("/manifest.json")
async def get_manifest():
    return MANIFEST

# A placeholder for where the reviews will go later
@app.get("/meta/{type}/{id}.json")
async def get_meta(type: str, id: str):
    return {
        "meta": {
            "id": id,
            "description": "Friend Review: 'This was a great movie!' - @UserA"
        }
    }