## Setup & Run Locally

### 1. Clone the repo

```bash
git clone <your-repo-url>
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## Database Setup

You have two options — **PostgreSQL** (recommended for production) or **SQLite** (quick local setup, no installation needed).

---

### Option A — PostgreSQL

#### Install PostgreSQL

**Mac:**
```bash
brew install postgresql
```

**Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows

#### Create a database

```bash
psql -U postgres
```

Inside the psql shell:
```sql
CREATE DATABASE bankdb;
CREATE USER bloguser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE bankdb TO bloguser;
\q
```

#### Set environment variables

Create a `.env` file inside `backend/`:

```
DATABASE_URL=postgresql://bloguser:yourpassword@localhost:5432/bankdb
SECRET_KEY=your_secret_key
```

---

### Option B — SQLite (no installation needed)

SQLite is built into Python — no setup required. Just change the `DATABASE_URL` in your `.env`:

```
DATABASE_URL=sqlite:///./blog.db
SECRET_KEY=your_secret_key
```

And update `database.py` to add the SQLite connect argument:

```python
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

> Note: SQLite is great for local development but not recommended for production.

---

### 4. Run the backend

```bash
cd backend
uvicorn main:app --reload
```