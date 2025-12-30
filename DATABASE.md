# PostgreSQL Database Setup

This application now uses PostgreSQL for persistent data storage instead of in-memory dictionaries.

## 🐘 PostgreSQL Configuration

### Database Connection
- **Host:** localhost
- **Port:** 5432
- **Database:** schooldb
- **User:** school
- **Password:** school123

### Environment Variable
You can customize the connection using:
```bash
export DATABASE_URL="postgresql://user:password@host:port/dbname"
```

## 🚀 Quick Start

### 1. Start PostgreSQL (Docker)
```bash
docker run -d \
  --name school-postgres \
  -e POSTGRES_PASSWORD=school123 \
  -e POSTGRES_USER=school \
  -e POSTGRES_DB=schooldb \
  -p 5432:5432 \
  postgres:16-alpine
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
cd src
python migrate.py
```

### 4. Run Application
```bash
cd src
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Database Schema

### Activities Table
```sql
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(1000),
    schedule VARCHAR(200),
    max_participants INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Participants Table
```sql
CREATE TABLE participants (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Useful Commands

### Check PostgreSQL Status
```bash
docker ps | grep school-postgres
```

### Stop PostgreSQL
```bash
docker stop school-postgres
```

### Remove PostgreSQL Container
```bash
docker rm school-postgres
```

### Connect to PostgreSQL CLI
```bash
docker exec -it school-postgres psql -U school -d schooldb
```

### View Tables
```sql
\dt
```

### Query Activities
```sql
SELECT * FROM activities;
```

### Query Participants
```sql
SELECT a.name, p.email 
FROM activities a 
JOIN participants p ON a.id = p.activity_id;
```

## ✅ Benefits of PostgreSQL

- **Persistence:** Data survives server restarts
- **Concurrency:** Multiple users can safely access data simultaneously
- **Capacity Check:** Prevents overbooking activities
- **Data Integrity:** Foreign keys ensure referential integrity
- **Scalability:** Ready for production deployment

## 🎓 Migration from In-Memory

The migration script (`migrate.py`) automatically:
1. Creates database tables
2. Imports all existing activities
3. Preserves participant enrollments

All API endpoints remain unchanged - the app works exactly as before, but with persistent storage!
