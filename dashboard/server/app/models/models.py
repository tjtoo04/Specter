from typing import List

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, Table, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

user_projects = Table(
    "user_projects",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
)


class MagicLinkRequest(BaseModel):
    email: str


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    users: Mapped[List["UserModel"]] = relationship(
        secondary=user_projects, back_populates="projects"
    )


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

    projects: Mapped[List["Project"]] = relationship(
        secondary=user_projects, back_populates="users"
    )


class Configuration(Base):
    __tablename__ = "Configurations"
    id: Mapped[int] = mapped_column(primary_key=True)
    context: Mapped[str] = mapped_column(Text)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )

    user: Mapped["UserModel"] = relationship("UserModel")
    project: Mapped["Project"] = relationship("Project")
