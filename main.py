from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

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