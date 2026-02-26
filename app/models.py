from app.database import Base
from sqlalchemy import (
    Column, Integer, String,
    CheckConstraint, Boolean,
    func, TIMESTAMP, ForeignKey, Index, Date, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default='user')
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner", foreign_keys="Task.created_by")
    task_assignments = relationship("TaskAssignment", back_populates="user", cascade="all, delete-orphan", foreign_keys="TaskAssignment.user_id")
    assignments_made = relationship("TaskAssignment", back_populates="assigner", foreign_keys="TaskAssignment.assigned_by")
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    token_blacklist = relationship("TokenBlacklist", back_populates="user", cascade="all, delete-orphan")

    # table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin')",
            name="check_role"
        ),
        Index("ix_users_username", "username", unique=True),
        Index("ix_users_email", "email", unique=True),
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_archived = Column(Boolean, nullable=False, default=False)                          # SRD §3.3
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # relationships
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")

    # table constraints and indexes
    __table_args__ = (
        Index("ix_projects_owner_id", "owner_id"),
        Index("ix_projects_is_archived", "is_archived"),
    )


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    joined_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

    # table constraints and indexes
    __table_args__ = (
        Index("ix_project_members_project_id", "project_id"),
        Index("ix_project_members_user_id", "user_id"),
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(15), nullable=False, default='todo')       # SRD: todo | in_progress | done
    priority = Column(String(10), nullable=False, default='medium')   # SRD: low | medium | high
    due_date = Column(Date, nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # relationships
    project = relationship("Project", back_populates="tasks")
    owner = relationship("User", back_populates="tasks", foreign_keys="users.id")
    task_assignments = relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan")

    # table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "status IN ('todo', 'in_progress', 'done')",
            name="check_status"
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="check_priority"
        ),
        Index("ix_tasks_project_id", "project_id"),
        Index("ix_tasks_status", "status"),
        Index("ix_tasks_priority", "priority"),
        Index("ix_tasks_project_id_status", "project_id", "status"),
        Index("ix_tasks_created_by", "created_by"),
    )


class TaskAssignment(Base):
    __tablename__ = "task_assignments"

    id = Column(Integer, primary_key=True)                                                       # SRD §3.5: dedicated PK
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    assigned_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)    # SRD §3.5
    assigned_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # relationships
    task = relationship("Task", back_populates="task_assignments")
    user = relationship("User", back_populates="task_assignments", foreign_keys="users.id")
    assigner = relationship("User", back_populates="assignments_made", foreign_keys="users.id")

    # table constraints and indexes
    __table_args__ = (
        UniqueConstraint("task_id", "user_id", name="uq_task_assignment_task_user"),  # SRD §3.5
        Index("ix_task_assignments_user_id", "user_id"),
        Index("ix_task_assignments_task_id", "task_id"),
        Index("ix_task_assignments_task_id_user_id", "task_id", "user_id"),
        Index("ix_task_assignments_assigned_by", "assigned_by"),
    )