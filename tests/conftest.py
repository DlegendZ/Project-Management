import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.assignment import Assignment
from app.services.auth_service import AuthService

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def create_test_user(db: Session, username="testuser", email="test@example.com", password="Test1234", role=UserRole.user) -> User:
    hashed = AuthService.hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed, role=role)
    db.add(user)
    db.flush()
    return user


def create_test_admin(db: Session) -> User:
    return create_test_user(db, username="admin", email="admin@example.com", role=UserRole.admin)


def get_auth_headers(client: TestClient, email="test@example.com", password="Test1234") -> dict:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_user(db: Session) -> User:
    user = create_test_user(db)
    db.commit()
    return user


@pytest.fixture
def test_admin(db: Session) -> User:
    user = create_test_admin(db)
    db.commit()
    return user


@pytest.fixture
def user_headers(client: TestClient, test_user: User) -> dict:
    return get_auth_headers(client)


@pytest.fixture
def admin_headers(client: TestClient, test_admin: User) -> dict:
    return get_auth_headers(client, email="admin@example.com")


@pytest.fixture
def test_project(db: Session, test_user: User) -> Project:
    project = Project(name="Test Project", owner_id=test_user.id)
    db.add(project)
    db.flush()
    member = ProjectMember(project_id=project.id, user_id=test_user.id)
    db.add(member)
    db.commit()
    return project


@pytest.fixture
def test_task(db: Session, test_project: Project, test_user: User) -> Task:
    task = Task(
        title="Test Task",
        project_id=test_project.id,
        created_by=test_user.id,
        status=TaskStatus.todo,
        priority=TaskPriority.medium,
    )
    db.add(task)
    db.commit()
    return task
