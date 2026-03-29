# Synopsis-AI

## Backend

### Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Migrations (Alembic)

All commands must be run from the `backend/` directory with the venv active.

**Generate a new migration after changing models:**
```bash
alembic -c app/database/alembic.ini revision --autogenerate -m "describe your change"
```
**Similar to prisma generate**
```bash
alembic -c app/database/alembic.ini upgrade head
```

> If the migration touches the `embedding` column, manually add `import pgvector.sqlalchemy` to the generated file in `app/database/alembic/versions/`.

**Apply all pending migrations:**
```bash
alembic -c app/database/alembic.ini upgrade head
```

**Rollback one migration:**
```bash
alembic -c app/database/alembic.ini downgrade -1
```

**Check current migration state:**
```bash
alembic -c app/database/alembic.ini current
```

**View migration history:**
```bash
alembic -c app/database/alembic.ini history
```

### Run Dev Server

```bash
uvicorn app.main:app --reload
```
