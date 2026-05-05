# MongoDB Migration Guide

## Overview
This codebase has been migrated from PostgreSQL to MongoDB Cloud using Motor (async driver) and Beanie (ODM).

## What Changed

### 1. Database Layer
- **Before**: SQLAlchemy ORM with PostgreSQL
- **After**: Motor + Beanie ODM with MongoDB

### 2. Models (26 files converted)
All models in `app/models/` have been converted:
- Removed: `sqlalchemy.Column`, `ForeignKey`, `relationship`, `Base` inheritance
- Added: `beanie.Document` inheritance, Pydantic `Field()`, MongoDB indexes

Example conversion:
```python
# Before (SQLAlchemy)
class Visitor(Base):
    __tablename__ = "visitors"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100))
    platform_id = Column(UUID, ForeignKey("platforms.id"))

# After (Beanie)
class Visitor(Document):
    name: Optional[str] = Field(max_length=100, default=None)
    platform_id: PydanticObjectId = Field(...)
    
    class Settings:
        name = "visitors"
        indexes = [
            [("platform_id", 1)],
        ]
```

### 3. Database Configuration
- **File**: `app/core/database.py`
- Uses `AsyncIOMotorClient` for async MongoDB connections
- Initializes Beanie with all 26 document models
- Provides `get_db()` dependency for FastAPI

### 4. Infrastructure
- **docker-compose.yml**: Replaced PostgreSQL with MongoDB container
- **Removed**: `alembic/` directory (no longer needed)
- **Environment**: Changed from `DATABASE_URL` to `MONGODB_URL` and `MONGODB_DB_NAME`

## Setup Instructions

### Option A: Local Development with Docker
```bash
# Start MongoDB and Redis
docker-compose up -d mongodb redis

# The app will connect to:
# MONGODB_URL=mongodb://mongoadmin:mongopassword@localhost:27017/tgo_api?authSource=admin
```

### Option B: MongoDB Atlas (Cloud)
1. Create a free cluster at https://cloud.mongodb.com
2. Get your connection string (mongodb+srv://...)
3. Update `.env`:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/tgo_api?retryWrites=true&w=majority
MONGODB_DB_NAME=tgo_api
```

### Install Dependencies
```bash
poetry install
```

### Run the Application
```bash
poetry run uvicorn app.main:app --reload
```

## Migration Status

### ✅ Completed
- [x] All 26 models converted to Beanie Documents
- [x] Database configuration updated
- [x] Docker Compose updated for MongoDB
- [x] Alembic removed
- [x] Dependencies updated (motor, beanie, pymongo)
- [x] Core services (`visitor_service.py`, `visitor_notifications.py`) converted
- [x] Environment configuration updated

### ⚠️ Requires Attention
The following files still contain SQLAlchemy code and need manual review/conversion:

**API Endpoints (22 files):**
- `app/api/v1/endpoints/visitors.py` (16 endpoints with Session dependencies)
- `app/api/v1/endpoints/staff.py`
- `app/api/v1/endpoints/channels.py`
- And 19 more...

**Services (12 files):**
- `app/services/chat_service.py`
- `app/services/session_service.py`
- `app/services/transfer_service.py`
- And 9 more...

**Tasks (6 files):**
- `app/tasks/sync_ai_providers.py`
- `app/tasks/close_timeout_sessions.py`
- And 4 more...

## Next Steps for Full Migration

1. **Convert Service Layer**: Update remaining service files to use Beanie async operations
   - Replace `db.query(Model).filter()` with `Model.find()`
   - Replace `db.add(obj); db.commit()` with `await obj.insert()`
   - Replace `db.delete(obj)` with `await obj.delete()`

2. **Convert API Endpoints**: Update endpoint functions
   - Remove `db: Session = Depends(get_db)` parameters
   - Call updated async service methods
   - Use `await` for all database operations

3. **Convert Background Tasks**: Update Celery/cron tasks
   - Initialize Beanie in task context
   - Use async database operations

4. **Testing**: Thoroughly test all functionality
   - Unit tests for services
   - Integration tests for API endpoints
   - Load testing for MongoDB performance

## Common Patterns

### Querying
```python
# Find one
visitor = await Visitor.find_one(Visitor.id == visitor_id)

# Find many with filter
visitors = await Visitor.find(Visitor.project_id == project_id).to_list()

# Count
count = await Visitor.find(Visitor.project_id == project_id).count()
```

### Creating
```python
visitor = Visitor(name="John", project_id=project_id)
await visitor.insert()
```

### Updating
```python
visitor = await Visitor.find_one(Visitor.id == visitor_id)
visitor.name = "Jane"
await visitor.save()
```

### Deleting
```python
# Soft delete (if supported)
visitor.deleted_at = datetime.utcnow()
await visitor.save()

# Hard delete
await visitor.delete()
```

## Support
For issues or questions about the migration, please refer to:
- [Beanie Documentation](https://beanie-odm.dev/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
