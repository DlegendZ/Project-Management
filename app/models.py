from app.database import Base
from sqlalchemy import (
    Column, Integer, String,
    CheckConstraint, Boolean,
    func, TIMESTAMP, ForeignKey, Index, Date
)
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default='user')
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    #relationship
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner")
    tasks_users = relationship("TaskAssignments", back_populates="user", cascade="all, delete-orphan")
    token_blacklist = relationship("TokenBlacklist", back_populates="user", cascade="all, delete-orphan")

    #table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin')",
            name= "check_role"
        ),
        Index("ix_users_username", "username", unique=True),
        Index("ix_users_email", "email", unique=True),
    )

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    #relationship
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    #table constraints and indexes
    __table_args__ = (
        Index("ix_projects_owner_id", "owner_id"),
    )

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default='TODO')
    priority = Column(String, nullable=False, default='MEDIUM')
    due_date = Column(Date, nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    #relationship
    project = relationship("Project", back_populates="tasks")
    owner = relationship("User", back_populates="tasks")
    tasks_users = relationship("TaskAssignments", back_populates="task", cascade="all, delete-orphan")

    # table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "status IN ('TODO', 'IN_PROGRESS', 'DONE')",
            name= "check_status"
        ),
        CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH')",
            name= "check_priority"
        ),
        Index("ix_tasks_project_id", "project_id"),
        Index("ix_tasks_status", "status"),
        Index("ix_tasks_project_id_status", "project_id", "status"),
    )

class TaskAssignments(Base):
    __tablename__ = "task_assignments"
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    assigned_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # relationship
    task = relationship("Task", back_populates="tasks_users")
    user = relationship("User", back_populates="tasks_users")

    #table constraints and indexes
    __table_args__ = (
        Index("ix_tasks_assignment_user_id", "user_id"),
        Index("ix_tasks_assignment_task_id", "task_id"),
        Index("ix_tasks_assignment_task_id_user_id", "task_id", "user_id"),
    )

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    id = Column(Integer, primary_key=True)
    jti = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)

    #relationship
    user = relationship("User", back_populates="token_blacklist")