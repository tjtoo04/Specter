import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .database import Base, engine
from .routes import configurations, users, projects, auth, reports


mode = os.getenv("VITE_APP_MODE")
url = (
    os.getenv("VITE_FRONTEND_URL_DEV")
    if mode == "dev"
    else os.getenv("VITE_FRONTEND_URL_PROD")
)

if url is None:
    raise RuntimeError("FRONTEND URL not set")


app = FastAPI()

# Allow React (port 5173) to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Specter Backend API HAHA"}


@app.get("/api/status")
def get_status():
    return {"status": "Specter Backend Online", "version": "0.1.0"}


app.include_router(configurations.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(auth.router)
app.include_router(reports.router)
