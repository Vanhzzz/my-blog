# MyBlog – Secure Personal Blog Platform

A security-focused personal blog platform built with FastAPI, Jinja2, SQLAlchemy ORM, Alembic, and TiDB Cloud.

The project was developed to practice backend development, authentication, session management, role-based access control, secure database interaction, and administrative blog management.

---

## Features

### Authentication & Authorization

- User registration and login
- Argon2 password hashing
- Role-based access control (`user` / `admin`)
- Protected admin routes
- Server-side authentication validation
- Account activation status support

### Session Security

The application uses server-side sessions instead of JWT authentication.

Authentication flow:

```text
User Login
    |
    v
Verify password with Argon2
    |
    v
Generate cryptographically secure random session token
    |
    +----------------------+
    |                      |
    v                      v
Browser Cookie         SHA-256(token)
raw token                   |
(HttpOnly)                  v
                        TiDB Cloud
                      sessions table

The raw session token is never stored in the database.

Session security includes:

Cryptographically secure opaque session tokens
SHA-256 session token hashing before database storage
HttpOnly cookies
Session expiration
Session revocation
User-agent and IP metadata
Server-side session validation

Blog Management

The admin area provides protected blog management functionality.

Implemented functionality includes:

Admin dashboard
Create blog posts
Automatic draft saving
Draft recovery
Continue editing saved drafts
Delete drafts
Draft / published-post separation
Post publishing workflow
Slug-based public URLs

Drafts are stored separately from published posts.

New Post
   |
   v
post_drafts
   |
   | autosave
   v
Draft remains recoverable
   |
   | Publish
   v
posts
   |
   +--> draft removed

When editing an existing published post, the public post remains unchanged while the administrator works on a separate draft.

Security Design
SQL Injection Mitigation

Database operations use SQLAlchemy ORM and parameterized queries rather than dynamically constructing SQL statements from user input.

Example:
user = (db.query(User).filter(User.username == username).first())
This keeps user input separated from the SQL query structure.

XSS Risk Reduction
Jinja2 template auto-escaping is used for server-rendered content to reduce the risk of reflected and stored XSS in normal template output.
User-controlled values are not intentionally rendered using unsafe raw HTML.

Role-Based Access Control
Administrative routes require authenticated users with the admin role.
Request
   |
   v
Session validation
   |
   v
Authenticated?
   |
   +-- No --> Reject
   |
   v
Role == admin?
   |
   +-- No --> 403 Forbidden
   |
   v
Admin resource
Authorization is enforced on the backend and does not rely solely on hiding UI elements.

Architecture
The application uses a separated frontend/backend structure.
Browser
   |
   | HTTP
   v
FastAPI
   |
   +----------------------------+
   |                            |
   v                            v
Jinja2 Templates           Backend Routes
                                |
                                v
                            Services
                                |
                                v
                         SQLAlchemy ORM
                                |
                                v
                           TiDB Cloud

Project structure:
.
├── webapp/
│   ├── backend/
│   │   ├── core/
│   │   ├── database/
│   │   ├── dependencies/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── alembic/
│   │   └── main.py
│   │
│   └── frontend/
│       ├── templates/
│       └── static/
│           ├── css/
│           ├── js/
│           └── images/
│
├── .env.example
├── .gitignore
├── alembic.ini
└── README.md

Database
The application uses TiDB Cloud as a MySQL-compatible relational database.
Main tables include:
users
sessions
posts
post_drafts
post_media
alembic_version

Users
Stores:
Username
Email
Argon2 password hash
Role
Account status
Timezone
Creation time

Sessions
Stores:
User ID
SHA-256 session token hash
Creation time
Expiration time
Revocation time
Last-seen metadata
User agent
IP address

Posts
Stores published blog content including:
Author
Title
Slug
Summary
Content
Category
Cover image URL
Status
Creation and update timestamps

Post Drafts
Drafts are stored independently from published posts.
This allows administrators to modify content without immediately changing the public version.

Post Media
Media metadata is separated from post content to support multiple uploaded assets per post or draft.

Database Migrations
Database schema changes are managed using Alembic.
Create a migration:
alembic revision --autogenerate -m "migration description"
Apply migrations:
alembic upgrade head
Check current revision:
alembic current

Technology Stack
Backend
Python
FastAPI
SQLAlchemy ORM
Alembic
PyMySQL
Pydantic Settings

Frontend
Jinja2
HTML
CSS
JavaScript

Security
Argon2
Opaque server-side sessions
SHA-256 session token hashing
Role-based access control

Database
TiDB Cloud
MySQL-compatible SQL

Environment Configuration
Create a .env file based on .env.example.
Example:
APP_NAME=MyBlog
APP_ENV=development

DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

SECRET_KEY=

SESSION_COOKIE_NAME=session
SESSION_HTTPS_ONLY=false

Never commit the real .env file.
The project .gitignore excludes environment secrets and virtual environments.

Installation
Clone the repository:
git clone <repository-url>
cd <repository-name>
Create a virtual environment:
python -m venv .venv

Activate it on Windows:
.\.venv\Scripts\Activate.ps1

Install dependencies:
pip install -r app/backend/requirements.txt

Configure the environment:
.env

Apply database migrations:
alembic upgrade head

Start the application:
uvicorn app.backend.main:app --reload

Open:
http://127.0.0.1:8000

Admin Workflow
Admin Login
    |
    v
Session Validation
    |
    v
RBAC Check
    |
    v
Admin Dashboard
    |
    +--> Posts
    |
    +--> Drafts
    |
    +--> Create Post
    |
    +--> Users

Draft creation uses automatic saving:
Admin types content
      |
      | debounce
      v
POST /admin/posts/autosave
      |
      v
Create draft
      |
      v
Return draft_id
      |
      v
Subsequent changes
      |
      v
PUT /admin/posts/drafts/{draft_id}/autosave
This allows unfinished content to be recovered after the administrator leaves or closes the editor.

Security Notes
Sensitive information is never committed to the repository.
Excluded information includes:
.env
Database credentials
SECRET_KEY
Raw session tokens

The application also avoids logging sensitive authentication information such as:
Plaintext passwords
Password hashes
Raw session cookies
Database passwords
Secret keys

Current Development Status
Implemented:
Authentication
Registration
Login / logout
Argon2 password hashing
Server-side session management
Session expiration and revocation
Role-based admin protection
TiDB Cloud integration
SQLAlchemy ORM
Alembic migrations
Admin dashboard
Automatic post drafts
Draft recovery
Draft deletion
Post publishing workflow

Some additional security and administration features are still under development.

Purpose
This project was developed as a hands-on backend and web security project to strengthen practical understanding of:
Web authentication
Session management
Authorization
Secure password storage
Database security
SQL Injection mitigation
XSS risk reduction
Secure administrative workflows
Web application architecture

Author
Personal security and backend development project.