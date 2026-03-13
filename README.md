# TrelloLite

A full-stack project management app inspired by Trello. Organize work into projects, manage tasks on a Kanban board, assign members, and track progress.

**Stack:** FastAPI · PostgreSQL · React 19 · TypeScript · Vite · Tailwind CSS

---

## Features

- 🔐 JWT authentication (access + refresh tokens)
- 📋 Kanban board with drag-and-drop task management
- 👥 Project members & task assignments
- 🗂️ Archive/restore projects
- 🔍 Search & filter tasks by priority, assignee, and more
- 🛡️ Admin panel for user management (activate / deactivate / delete)
- 🌙 Dark-themed UI

---

## Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Python | 3.12 |
| PostgreSQL | 13+ |
| Node.js | 18+ |
| npm | 7+ |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/trello-lite.git
cd trello-lite
```

---

### 2. Set up the database

Create a PostgreSQL database:

```sql
CREATE DATABASE trello_lite;
CREATE USER admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE trello_lite TO admin;
```

---

### 3. Configure the backend

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# PostgreSQL connection string
DATABASE_URL=postgresql://admin:your_password@localhost:5432/trello_lite

# Generate a secret key by running: python app/secret_key_generator.py
SECRET_KEY=your-super-secret-key-minimum-32-characters-long

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12

# Allow requests from the frontend dev server
CORS_ORIGINS=http://localhost:5173

APP_ENV=development
LOG_LEVEL=INFO
```

> **Tip — generate a secure SECRET_KEY:**
> ```bash
> python app/secret_key_generator.py
> ```

---

### 4. Install backend dependencies

It is recommended to use a virtual environment:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

### 5. Run database migrations

```bash
alembic upgrade head
```

---

### 6. Start the backend server

```bash
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**

Interactive API docs (Swagger UI): **http://localhost:8000/docs**

---

### 7. Configure the frontend

```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

---

### 8. Install frontend dependencies

```bash
npm install
```

---

### 9. Start the frontend dev server

```bash
npm run dev
```

The app will be available at **http://localhost:5173**

---

## Project Structure

```
trello-lite/
├── app/                        # FastAPI backend
│   ├── main.py                 # App entry point & router registration
│   ├── config.py               # Settings (loaded from .env)
│   ├── database.py             # SQLAlchemy engine & session
│   ├── dependencies.py         # Auth dependency injection
│   ├── exceptions.py           # Global exception handlers
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── repositories/           # Database access layer
│   ├── services/               # Business logic layer
│   └── routers/                # API route handlers
│
├── migrations/                 # Alembic migration scripts
│   └── versions/
│       └── 0001_initial_schema.py
│
├── tests/                      # Pytest test suite
│
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── api/                # Axios API client modules
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page-level components
│   │   ├── store/              # Zustand auth store
│   │   └── types/              # TypeScript type definitions
│   ├── public/
│   ├── index.html
│   └── package.json
│
├── .env.example                # Backend environment template
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Available Scripts

### Backend

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --reload` | Start development server |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic revision --autogenerate -m "msg"` | Create a new migration |
| `alembic downgrade -1` | Roll back the last migration |
| `pytest` | Run the full test suite |
| `pytest --cov=app` | Run tests with coverage report |
| `python app/secret_key_generator.py` | Generate a secure SECRET_KEY |

### Frontend

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server |
| `npm run build` | Type-check and build for production |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint |

---

## Environment Variables Reference

### Backend (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | — | JWT signing secret (min. 32 chars) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ❌ | `7` | Refresh token lifetime |
| `BCRYPT_ROUNDS` | ❌ | `12` | Password hashing cost factor |
| `CORS_ORIGINS` | ❌ | `*` | Allowed CORS origins (comma-separated) |
| `APP_ENV` | ❌ | `development` | `development` or `production` |
| `LOG_LEVEL` | ❌ | `INFO` | Logging verbosity |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | ✅ | — | Backend API base URL |

---

## First-Time Setup Notes

- The **first registered user** is automatically assigned the `admin` role.
- Subsequent users are assigned the `user` role by default.
- Admins can manage all users from the **Admin** panel in the sidebar.

---

## API Documentation

Once the backend is running, full interactive docs are available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Running Tests

```bash
# From the project root (with venv activated)
pytest

# With coverage
pytest --cov=app --cov-report=term-missing
```

The test suite requires an 80% minimum code coverage.
