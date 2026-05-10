# Collaborative-Document-Platform
A collaborative document management platform with workspaces, role-based access, version history, tagging, threaded comments, and audit logs.

## Project overview
This project provides a REST API to manage:
- Users and workspaces with role-based membership
- Documents with versioning and tagging
- Threaded comments on documents
- Audit logging for document create/update events

## Key features
- Workspace membership with roles (admin/editor/viewer)
- Document versions automatically created on every save
- Tagging and tag-based filtering
- Threaded comments with parent/child structure
- Audit log records for key document events

## Requirements
- Python 3.11+ (recommended)
- PostgreSQL (optional; SQLite is used by default)

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:
	- `pip install -r requirements.txt`

## Environment variables
By default, the app uses SQLite. To use PostgreSQL, add a `.env` file in the project root:

```
USE_SUPABASE_DB=true
SUPABASE_DB_HOST=your-host
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=your-user
SUPABASE_DB_PASSWORD=your-password
SUPABASE_DB_PORT=5432
SUPABASE_DB_SSLMODE=require
SUPABASE_CONNECT_TIMEOUT=10
```

## Apply migrations
```
python manage.py makemigrations
python manage.py migrate
```

## Run the server
```
python manage.py runserver
```

## Postman collection
Import the Postman collection at the repository root:
- `Collaborative-Document-Platform.postman_collection.json`

## API endpoints

### Users
- `POST /api/users/` - Create a user
- `GET /api/users/{id}/` - Get user by ID

### Workspaces
- `POST /api/workspaces/` - Create workspace (owner added as admin)
- `GET /api/workspaces/{id}/` - Get workspace by ID (includes member_count)
- `POST /api/workspaces/{id}/members/` - Add workspace member
- `GET /api/workspaces/{id}/members/` - List workspace members
- `GET /api/workspaces/{id}/summary/` - Workspace summary (member/document/comment counts)

### Documents
- `POST /api/documents/` - Create a document (creates version 1)
- `PUT /api/documents/{id}/` - Update document (creates new version)
- `GET /api/documents/` - List documents with filters
	- Filters: `workspace`, `workspace__in`, `status`, `status__in`, `tag`, `q`, `updated_at__gte`, `updated_at__lte`
- `GET /api/documents/{id}/versions/` - List document versions
- `GET /api/documents/{id}/stats/` - Document stats (versions, comments, contributors)
- `POST /api/documents/{id}/tags/` - Add tags to document

### Comments
- `POST /api/comments/` - Create comment or reply
- `GET /api/comments/?document={id}` - List threaded comments by document

### Tags
- `POST /api/tags/` - Create tag

### Audit Logs
- `GET /api/audit-logs/` - List audit logs
	- Filters: `actor`, `date_from`, `date_to`
