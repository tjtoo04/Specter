import os
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from propelauth_fastapi import User, init_auth
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import Base, engine, get_db
from .models.models import Project, User
from .schemas.Project import ProjectCreate, ProjectResponse, ProjectUpdate

PROPEL_AUTH_URL = os.getenv("PROPEL_AUTH_URL")
PROPEL_AUTH_API_KEY = os.getenv("PROPEL_AUTH")

# Ensure they aren't None before passing to init_auth
if PROPEL_AUTH_URL is None or PROPEL_AUTH_API_KEY is None:
    raise RuntimeError("Missing PropelAuth environment variables!")

auth = init_auth(PROPEL_AUTH_URL, PROPEL_AUTH_API_KEY)

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


@app.get("/api/config")
def get_config():
    return {
        "model": "llama3",
        "context": "You are a helpful Specter agent.",
        "temperature": 0.7,
    }


@app.get("/api/whoami")
async def root(
    current_user: User = Depends(auth.require_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == current_user.user_id))
    db_user = result.scalars().first()

    if not db_user:
        db_user = User(
            id=current_user.user_id,
            username=current_user.email,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    return {
        "user_id": db_user.id,
        "username": db_user.username,
        "internal_db": "synced",
    }


@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"detail": "User deleted successfully"}


@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == current_user.user_id))
    db_user = result.scalars().first()

    if not db_user:
        db_user = User(id=current_user.user_id, username=current_user.email)
        db.add(db_user)

    new_project = Project(title=project_data.title)
    new_project.users.append(db_user)

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project


@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_my_projects(
    current_user: User = Depends(auth.require_user), db: AsyncSession = Depends(get_db)
):
    query = select(Project).join(Project.users).where(User.id == current_user.user_id)
    result = await db.execute(query)
    return result.scalars().all()


@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Project)
        .join(Project.users)
        .where(Project.id == project_id, User.id == current_user.user_id)
    )
    result = await db.execute(query)
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    if project_data.title:
        project.title = project_data.title

    await db.commit()
    await db.refresh(project)
    return project


@app.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Project)
        .join(Project.users)
        .where(Project.id == project_id, User.id == current_user.user_id)
    )
    result = await db.execute(query)
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted"}
