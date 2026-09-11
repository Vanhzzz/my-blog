# MyBlog – Secure Personal Blog Platform

MyBlog is a security-focused personal blog platform built with FastAPI, Jinja2, SQLAlchemy ORM, Alembic, and TiDB Cloud.

The project was developed as a hands-on backend and web security project to practice authentication, session management, role-based access control, secure database interaction, and protected administrative workflows.

---

## Overview

The application follows a separated frontend/backend architecture:

```text
Browser
   |
   | HTTP Request
   v
FastAPI Application
   |
   +-------------------------+
   |                         |
   v                         v
Jinja2 Templates        Backend Routes
                             |
                             v
                          Services
                             |
                             v
                      SQLAlchemy ORM
                             |
                             v
                        TiDB Cloud
```

The backend handles authentication, authorization, session validation, database operations, and administrative functionality.

The frontend uses server-side rendered Jinja2 templates together with HTML, CSS, and JavaScript.

---

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy ORM
- Alembic
- PyMySQL
- Pydantic Settings

### Frontend

- Jinja2
- HTML
- CSS
- JavaScript

### Database

- TiDB Cloud
- MySQL-compatible SQL

### Security

- Argon2 password hashing
- Cryptographically secure opaque session tokens
- SHA-256 session token hashing
- HttpOnly session cookies
- Server-side session validation
- Session expiration
- Session revocation
- Role-based access control

---

## Project Structure

```text
.
├── app/
│   ├── backend/
│   │   ├── alembic/
│   │   │   └── versions/
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── paths.py
│   │   │   ├── security.py
│   │   │   ├── templates.py
│   │   │   └── time.py
│   │   │
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── session.py
│   │   │
│   │   ├── dependencies/
│   │   │   ├── admin.py
│   │   │   └── auth.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   ├── post.py
│   │   │   ├── post_draft.py
│   │   │   └── post_media.py
│   │   │
│   │   ├── routes/
│   │   │   ├── home.py
│   │   │   ├── about.py
│   │   │   ├── auth.py
│   │   │   ├── blog.py
│   │   │   └── admin.py
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── session_service.py
│   │   │   └── post_draft_service.py
│   │   │
│   │   ├── requirements.txt
│   │   └── main.py
│   │
│   └── frontend/
│       ├── templates/
│       │   ├── admin/
│       │   ├── auth/
│       │   ├── blog/
│       │   ├── about.html
│       │   ├── base.html
│       │   └── home.html
│       │
│       └── static/
│           ├── css/
│           ├── js/
│           └── images/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── README.md
└── test_db.py
```

---

## Authentication

The application supports user registration, login, and logout.

Passwords are never stored in plaintext.

User passwords are hashed using Argon2 before being stored in TiDB Cloud.

```text
Password
   |
   v
Argon2
   |
   v
Password Hash
   |
   v
users.password_hash
```

During login, the submitted password is verified against the stored Argon2 hash.

The public registration flow always creates normal users with:

```text
role = user
```

Administrative privileges are not accepted from public registration input.

---

## Server-Side Session Management

The application uses server-side sessions instead of JWT authentication.

After successful authentication:

```text
Login
   |
   v
Verify password with Argon2
   |
   v
Generate random opaque session token
   |
   +-------------------------+
   |                         |
   v                         v
Browser Cookie          SHA-256(token)
Raw Token                    |
HttpOnly                     v
                         TiDB Cloud
                      sessions.token_hash
```

The raw session token is only sent to the browser.

The database stores only the SHA-256 hash of the session token.

This means the original session token is not stored directly in the database.

---

## Session Validation

For authenticated requests:

```text
Browser Request
      |
      v
Read Session Cookie
      |
      v
SHA-256(raw token)
      |
      v
Lookup sessions.token_hash
      |
      v
Check session expiration
      |
      v
Check session revocation
      |
      v
Resolve session.user_id
      |
      v
Load User
      |
      v
Check account status
      |
      v
current_user
```

If the session is missing, expired, revoked, or associated with an inactive account, authentication fails.

---

## Session Expiration

Session lifetime depends on the user role.

Current configuration:

```text
Normal User
→ 7 days

Admin
→ 12 hours
```

Session expiration is stored server-side in TiDB Cloud.

The browser cookie also receives a corresponding expiration period.

---

## Session Revocation

Logout revokes the server-side session before deleting the browser cookie.

```text
POST /logout
      |
      v
Read raw session token
      |
      v
SHA-256(token)
      |
      v
Find session
      |
      v
Set revoked_at
      |
      v
Delete browser cookie
```

This prevents a revoked session token from being reused.

---

## Role-Based Access Control

The application currently supports:

```text
user
admin
```

Administrative routes use server-side authorization checks.

```text
Request
   |
   v
Session Validation
   |
   v
Authenticated?
   |
   +---- No ----> Reject
   |
   v
Role == admin?
   |
   +---- No ----> 403 Forbidden
   |
   v
Allow Admin Resource
```

Authorization is enforced by the backend and does not depend only on hiding links or buttons in the frontend.

---

## SQL Injection Mitigation

Database operations use SQLAlchemy ORM and parameterized queries.

Example:

```python
user = (
    db.query(User)
    .filter(User.username == username)
    .first()
)
```

User input is passed as query parameters rather than concatenated directly into SQL query strings.

This reduces the risk of SQL Injection caused by unsafe dynamic SQL construction.

---

## XSS Risk Reduction

Server-rendered pages use Jinja2 templates.

Jinja2 auto-escaping is used for normal template variables, reducing the risk of reflected and stored XSS when displaying user-controlled values.

Unsafe raw HTML rendering is not intentionally used for normal user input.

Additional Markdown/content sanitization is not currently claimed as implemented.

---

## Admin Dashboard

Administrative functionality is protected by authentication and role-based authorization.

The dashboard retrieves real data directly from TiDB Cloud.

Dashboard statistics include:

```text
Total Posts
Published Posts
Draft Posts
Total Users
```

No hard-coded statistics are used for these values.

Recent posts are also retrieved from the database.

---

## Draft Management

Draft content is stored separately from published posts.

```text
posts
→ published/main blog content

post_drafts
→ unfinished or edited content
```

This separation allows an administrator to work on a draft without immediately changing the public article.

---

## Automatic Draft Saving

The post editor automatically saves changes after the administrator stops typing for a short period.

The first autosave creates a new draft:

```text
Admin types content
      |
      v
JavaScript debounce
      |
      v
POST /admin/posts/autosave
      |
      v
INSERT post_drafts
      |
      v
Return draft_id
```

The browser then keeps the returned draft ID.

Subsequent autosaves update the existing draft:

```text
PUT /admin/posts/drafts/{draft_id}/autosave
      |
      v
UPDATE post_drafts
```

This prevents every autosave operation from creating a new draft.

---

## Draft Recovery

After the first autosave, the editor URL changes from:

```text
/admin/posts/create
```

to:

```text
/admin/posts/drafts/{draft_id}/edit
```

If the administrator leaves the page after an autosave, the draft remains stored in TiDB Cloud.

The draft can later be reopened and editing can continue.

---

## Draft Deletion

Administrators can delete unfinished drafts.

The endpoint uses the HTTP DELETE method:

```text
DELETE /admin/posts/drafts/{draft_id}
```

A successful deletion returns:

```text
204 No Content
```

The backend verifies that the authenticated administrator owns the draft before allowing deletion.

---

## Publishing Workflow

For a new article:

```text
post_drafts
      |
      | Publish
      v
Validate draft
      |
      v
INSERT posts
      |
      v
DELETE post_drafts
```

The published article becomes the main post and the temporary draft is removed.

---

## Editing Published Posts

The architecture also supports creating an editable draft from an existing published post.

```text
Published Post
      |
      v
Copy content
      |
      v
post_drafts
      |
      v
Administrator edits draft
```

The public post remains unchanged while the draft is being edited.

When the updated draft is published:

```text
post_drafts
      |
      v
UPDATE posts
      |
      v
DELETE post_drafts
```

This prevents partially edited content from immediately affecting the public article.

---

## Post URLs

Public blog posts use human-readable slug-based URLs.

Example:

```text
/blog/understanding-sql-injection
```

rather than exposing database IDs in public blog URLs.

The `posts.slug` column has a unique constraint.

---

## Database

The application uses TiDB Cloud as a MySQL-compatible relational database.

The current database schema includes:

```text
users
sessions
posts
post_drafts
post_media
alembic_version
```

---

## Users Table

The `users` table stores:

```text
id
username
email
password_hash
role
is_active
timezone
created_at
```

Passwords are stored only as Argon2 hashes.

User timezone information is stored separately from timestamps.

---

## Sessions Table

The `sessions` table stores:

```text
id
user_id
token_hash
created_at
expires_at
last_seen_at
revoked_at
user_agent
ip_address
```

The raw session token is not stored in this table.

---

## Posts Table

The `posts` table stores:

```text
id
author_id
title
slug
summary
content
category
cover_image_url
status
created_at
updated_at
```

Published content is separated from temporary drafts.

---

## Post Drafts Table

The `post_drafts` table stores temporary editing state.

Fields include:

```text
id
post_id
author_id
title
slug
summary
content
category
cover_image_url
created_at
updated_at
```

A `NULL` `post_id` represents a new post that has never been published.

A draft with a `post_id` represents an edited version of an existing published post.

---

## Post Media Table

The database includes a `post_media` model for tracking media metadata associated with posts and drafts.

It contains fields such as:

```text
id
draft_id
post_id
uploaded_by
blob_url
blob_pathname
media_type
created_at
```

The database stores media metadata and URLs rather than binary image data.

Cloud media upload integration is still under development.

---

## Time Handling

Application timestamps are normalized to UTC before storage.

A shared time helper is used:

```python
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    ).replace(
        tzinfo=None
    )
```

TiDB/MySQL `DATETIME` does not preserve timezone information directly, so timestamps are consistently treated as UTC.

A separate timezone field is available on user accounts.

---

## Database Migrations

Database schema changes are managed with Alembic.

Current migrations include the initial tables and later schema additions such as post drafts, post media, and user timezone support.

Create a migration:

```bash
alembic revision --autogenerate -m "migration description"
```

Apply migrations:

```bash
alembic upgrade head
```

Check the current database revision:

```bash
alembic current
```

---

## Environment Configuration

Application configuration is loaded using Pydantic Settings.

Create a local `.env` file based on:

```text
.env.example
```

Example:

```env
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
```

The real `.env` file must never be committed to Git.

---

## Secret Management

Sensitive configuration is excluded from version control through `.gitignore`.

Examples of sensitive information that must not be committed:

```text
Database password
SECRET_KEY
.env
Raw session tokens
Authentication cookies
```

The repository contains `.env.example` only as a configuration template.

---

## Local Installation

Clone the repository:

```bash
git clone https://github.com/Vanhzzz/my-blog.git
```

Enter the project:

```bash
cd my-blog
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r app/backend/requirements.txt
```

Create and configure:

```text
.env
```

Apply database migrations:

```bash
alembic upgrade head
```

Run the application:

```bash
uvicorn app.backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

## Current Development Status

Implemented:

- FastAPI backend
- Jinja2 server-side rendering
- SQLAlchemy ORM
- TiDB Cloud integration
- Alembic database migrations
- User registration
- User login
- User logout
- Argon2 password hashing
- Opaque session tokens
- SHA-256 session token hashing
- HttpOnly session cookies
- Session expiration
- Session revocation
- Server-side session validation
- Role-based access control
- Protected admin routes
- Admin dashboard
- Automatic draft saving
- Draft recovery
- Draft continuation
- Draft deletion
- Separation between drafts and published posts
- Post publishing workflow
- Slug-based blog URLs
- UTC timestamp handling

Database support prepared for:

- Post media metadata
- User timezone storage

Still under development:

- Full media upload integration
- Complete Markdown preview/rendering workflow
- Extended user administration
- Additional application security controls

---

## Security Scope

The project currently demonstrates practical implementation of:

- Secure password storage
- Authentication
- Server-side session management
- Session revocation
- Authorization
- Role-based access control
- SQL Injection mitigation
- Jinja2 auto-escaping
- Secret management
- Protected administrative workflows

Features that are not yet implemented are not presented as completed security controls.

---

## Purpose

This project was created to strengthen practical knowledge of backend development and web application security, particularly:

- Authentication design
- Session security
- Authorization
- Secure password handling
- Relational database security
- SQL Injection mitigation
- XSS risk reduction
- Administrative access control
- Secure application architecture
- Database migration management

---

## Author

Hoàng Việt Anh

Security & Backend Development
