from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os

import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory to serve CSS
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# The Manifest is the "ID Card" of your Stremio Addon
MANIFEST = {
    "id": "org.socialreviews.example",
    "name": "Friend Reviews",
    "version": "0.0.1",
    "description": "See what your friends are saying about movies.",
    "logo": "https://via.placeholder.com/256x256?text=Friend+Reviews",
    "background": "https://via.placeholder.com/1200x800?text=Friend+Reviews",
    "resources": ["stream", "catalog"],
    "types": ["movie", "series"],
    "catalogs": [
        {
            "type": "movie",
            "id": "top_reviewed_movies",
            "name": "Top Reviewed Movies"
        }
    ],
    "behaviorHints": {
        "configurable": False,
        "p2p": False
    }
}

@app.get("/reviews/{imdb_id}")
async def get_reviews_page(imdb_id: str):
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, review_text FROM reviews WHERE imdb_id = ?", (imdb_id,))
    reviews = cursor.fetchall()
    conn.close()

    reviews_html = ""
    if reviews:
        for username, review_text in reviews:
            reviews_html += f"""
            <div class="review-card">
                <strong>@{username}</strong><br>
                <p class="review-text">{review_text}</p>
            </div>
            """
    else:
        reviews_html = '<p class="no-reviews">No reviews yet. Be the first to review this movie!</p>'

    template_path = os.path.join(os.path.dirname(__file__), "templates", "reviews.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    html_content = html_template.format(reviews_html=reviews_html)
    return HTMLResponse(content=html_content)

@app.get("/stream/{type}/{id}.json")
async def get_stream(type: str, id: str):
    print(f"DEBUG: /stream called with type={type}, id={id} at {datetime.now()}")
    
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, review_text FROM reviews WHERE imdb_id = ?", (id,))
    reviews = cursor.fetchall()
    conn.close()

    review_count = len(reviews)
    
    if review_count == 0:
        return {"streams": []}
    
    # Create a stream that opens the reviews page
    stream = {
        "name": "Friend Reviews",
        "title": f"⭐ {review_count} Friend Reviews",
        "externalUrl": f"http://localhost:8000/reviews/{id}",
        "behaviorHints": {
            "notWebReady": False,
            "proxyHeaders": {
                "request": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            }
        }
    }
    
    print(f"DEBUG: Returning stream for {id} with {review_count} reviews")
    return {"streams": [stream]}

@app.get("/catalog/movie/top_reviewed_movies.json")
async def get_catalog():
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()
    
    # Get movies with reviews, ordered by review count
    cursor.execute("""
        SELECT imdb_id, COUNT(*) as review_count 
        FROM reviews 
        GROUP BY imdb_id 
        ORDER BY review_count DESC 
        LIMIT 20
    """)
    movies = cursor.fetchall()
    conn.close()
    
    # Movie metadata mapping
    movie_data = {
        "tt1375666": {
            "name": "Inception",
            "poster": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg",
            "background": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg"
        }
        # Add more movies as needed
    }
    
    metas = []
    for imdb_id, count in movies:
        movie_info = movie_data.get(imdb_id, {
            "name": f"Movie {imdb_id}",
            "poster": "https://via.placeholder.com/342x513?text=Movie",
            "background": "https://via.placeholder.com/1200x800?text=Movie"
        })
        
        metas.append({
            "id": imdb_id,
            "type": "movie",
            "name": f"{movie_info['name']} ⭐ {count} Friend Reviews",
            "poster": movie_info["poster"],
            "background": movie_info["background"],
            "genres": ["Action", "Sci-Fi", "Thriller", "Friend Reviews"],
            "releaseInfo": "2010",
            "imdbRating": 8.8
        })
    
    return {
        "metas": metas
    }

@app.get("/meta/{type}/{id}.json")
async def get_meta(type: str, id: str):
    print(f"DEBUG: /meta called with type={type}, id={id} at {datetime.now()}")
    
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, review_text FROM reviews WHERE imdb_id = ?", (id,))
    reviews = cursor.fetchall()
    conn.close()

    review_count = len(reviews)
    review_text = ""
    
    if reviews:
        for row in reviews: 
            review_text += f"@{row[0]}: {row[1]}\n"
    
    print(f"DEBUG: Found {review_count} reviews for {id}")
    
    # Get movie name based on IMDB ID
    movie_names = {
        "tt1375666": "Inception",
        # Add more movies as needed
    }
    
    movie_name = movie_names.get(id, f"Movie {id}")
    
    response = {
        "meta": {
            "id": id,
            "type": type,
            "name": f"{movie_name} ⭐ {review_count} Friend Reviews",
            "genres": ["Action", "Sci-Fi", "Thriller", "Friend Reviews"],
            "description": f"🎬 FRIEND REVIEWS ({review_count})\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{review_text if review_text else 'No reviews yet'}\n\n👁️ View all reviews: http://localhost:8000/reviews/{id}",
            "releaseInfo": "2010",
            "imdbRating": 8.8,
            "runtime": "148 min",
            "poster": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg",
            "background": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg",
            "links": [
                {
                    "name": f"View {review_count} Friend Reviews",
                    "category": "Reviews",
                    "url": f"http://localhost:8000/reviews/{id}"
                }
            ]
        }
    }
    
    print(f"DEBUG: Response sent for {id}")
    return response

@app.get("/manifest.json")
async def get_manifest():
    return MANIFEST