"""
FastAPI CORS + static-file server for production deployment.
Serves the frontend and ensures correct CORS headers for the agent API.

Usage:
    pip install fastapi uvicorn
    python gateway.py

Then open http://localhost:5173
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

app = FastAPI(title="Slurm Agent Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5173)
