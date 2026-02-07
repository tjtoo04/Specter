import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from propelauth_fastapi import init_auth, User

auth = init_auth(os.getenv("PROPEL_AUTH_URL"), os.getenv("PROPEL_AUTH"))

mode = os.getenv("VITE_APP_MODE")
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

@app.get("/")
def read_root():
    return {"message": "Welcome to the Specter Backend API HAHA"}


@app.get("/api/status")
def get_status():
    print(url)
    print("pls")
    return {"status": "Specter Backend Online", "version": "0.1.0"}


@app.get("/api/config")
def get_config():
    return {
        "model": "llama3",
        "context": "You are a helpful Specter agent.",
        "temperature": 0.7,
    }


@app.get("/api/whoami")
async def root(current_user: User = Depends(auth.require_user)):
    return {"user_id": f"{current_user.user_id}"}
