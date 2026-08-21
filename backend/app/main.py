from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings

from app.routers import auth, shows, seasons, episodes, artwork, health, publish, catalog

app = FastAPI(title="Peblo TV Mini API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local storage for serving artwork in dev
import os
os.makedirs(settings.storage_local_path, exist_ok=True)
app.mount("/storage", StaticFiles(directory=settings.storage_local_path), name="storage")

app.include_router(auth.router)
app.include_router(shows.router)
app.include_router(seasons.router)
app.include_router(episodes.router)
app.include_router(artwork.router)
app.include_router(health.router)
app.include_router(publish.router)
app.include_router(catalog.router)

@app.get("/")
def read_root():
    return {"message": "Peblo TV Mini API is running"}
