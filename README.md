Setup & Run Locally
1. Clone the repo

git clone <your-repo-url>

3. Create and activate virtual environment
   
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

5. Install dependencies
   
cd backend
pip install -r requirements.txt

Database Setup
You have two options — PostgreSQL (recommended for production) or SQLite (quick local setup, no installation needed).

Option A — PostgreSQL
Install PostgreSQL
Mac:

brew install postgresql
Ubuntu/Linux:

sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
Windows: Download and install from https://www.postgresql.org/download/windows

Create a database
psql -U postgres
Inside the psql shell:

CREATE DATABASE bank;
CREATE USER bloguser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE bank TO bloguser;
\q
Set environment variables
Create a .env file inside backend/:

DATABASE_URL=postgresql://bloguser:yourpassword@localhost:5432/blogdb
SECRET_KEY=your_secret_key
Option B — SQLite (no installation needed)
SQLite is built into Python — no setup required. Just change the DATABASE_URL in your .env:

DATABASE_URL=sqlite:///./bank.db
SECRET_KEY=your_secret_key
And update database.py to add the SQLite connect argument:

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Note: SQLite is great for local development but not recommended for production.

4. Run the backend
cd backend
uvicorn main:app --reload
