import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

mode = os.getenv("VITE_FRONTEND_URL_DEV")
url = (
    os.getenv("VITE_FRONTEND_URL_DEV")
    if mode == "dev"
    else os.getenv("VITE_FRONTEND_URL_PROD")
)


app = FastAPI()

# Allow React (port 5173) to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
def get_status():
    return {"status": "Specter Backend Online", "version": "0.1.0"}


@app.get("/api/config")
def get_config():
    return {
        "model": "llama3",
        "context": "You are a helpful Specter agent.",
        "temperature": 0.7,
    }
