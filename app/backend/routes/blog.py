from fastapi import APIRouter, Depends, HTTPException, Request

from ..core.templates import templates
from ..dependencies.auth import get_current_user
from ..models.user import User


router = APIRouter(
    prefix="/blog",
    tags=["Blog"]
)


POSTS = [
    {
        "slug": "my-journey-into-web-security",
        "title": "My Journey into Web Security",
        "summary": (
            "How I started learning web security "
            "and what I have learned so far."
        ),
        "category": "Web Security",
        "date": "September 7, 2026",
        "read_time": "5 min read",
        "content": """
My interest in web security started when I began looking
beyond how websites are built and started asking how they
could fail.

I began with basic web technologies, HTTP, authentication,
sessions and common vulnerabilities. Over time, I started
practicing with intentionally vulnerable applications and
documenting what I learned.

This blog is where I keep those notes, experiments and
lessons from my journey.
        """
    },

    {
        "slug": "understanding-sql-injection",
        "title": "Understanding SQL Injection",
        "summary": (
            "Notes about SQL injection, vulnerable queries "
            "and how applications should prevent them."
        ),
        "category": "Web Security",
        "date": "September 5, 2026",
        "read_time": "7 min read",
        "content": """
SQL injection occurs when untrusted input is included in
database queries without proper parameterization.

Understanding how an application constructs SQL queries
helps explain why the vulnerability occurs and how it
should be prevented.
        """
    },

    {
        "slug": "building-my-blog-with-fastapi",
        "title": "Building My Blog with FastAPI",
        "summary": (
            "A personal project built with FastAPI, "
            "Jinja2 and MySQL."
        ),
        "category": "Development",
        "date": "September 3, 2026",
        "read_time": "6 min read",
        "content": """
I built this blog as a personal project to practice backend
development and document the things I learn.

The application uses FastAPI for the backend and Jinja2
for server-side rendering. MySQL will be used to store
users, sessions and blog posts.
        """
    },

    {
        "slug": "learning-java-backend-development",
        "title": "Learning Java Backend Development",
        "summary": (
            "Things I learned while exploring Java "
            "and backend development."
        ),
        "category": "Development",
        "date": "August 30, 2026",
        "read_time": "4 min read",
        "content": """
Java is one of the technologies I am currently exploring
for backend development.

My goal is to better understand application architecture,
object-oriented programming and how production backend
systems are structured.
        """
    },

    {
        "slug": "how-i-organize-my-learning-notes",
        "title": "How I Organize My Learning Notes",
        "summary": (
            "A simple approach I use to organize "
            "technical knowledge and research."
        ),
        "category": "Learning Notes",
        "date": "August 27, 2026",
        "read_time": "3 min read",
        "content": """
Keeping notes helps me understand technical topics more
deeply instead of simply reading and forgetting them.

I usually separate concepts, experiments, errors and
important lessons so I can review them later.
        """
    },

    {
        "slug": "my-current-security-learning-roadmap",
        "title": "My Current Security Learning Roadmap",
        "summary": (
            "The topics and skills I am currently "
            "focusing on in cybersecurity."
        ),
        "category": "Learning Notes",
        "date": "August 24, 2026",
        "read_time": "5 min read",
        "content": """
My current learning roadmap focuses on web security,
networking, operating systems and backend development.

I want to understand both how vulnerabilities happen and
how applications can be designed more securely.
        """
    }
]


@router.get("")
async def blog_list(
    request: Request,
    current_user: User | None = Depends(get_current_user)
):
    return templates.TemplateResponse(
        request=request,
        name="blog/index.html",
        context={
            "title": "Blog",
            "posts": POSTS,
            "current_user": current_user
        }
    )


@router.get("/{slug}")
async def blog_detail(
    slug: str,
    request: Request,
    current_user: User | None = Depends(get_current_user)
):

    post = next(
        (post for post in POSTS if post["slug"] == slug),
        None
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="blog/detail.html",
        context={
            "title": post["title"],
            "post": post,
            "current_user": current_user
        }
    )