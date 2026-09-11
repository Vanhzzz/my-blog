from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi import Depends
from .dependencies.auth import require_login
from .models.user import User

from .core.paths import STATIC_DIR
from .routes import home, blog, about, auth, admin

app = FastAPI(
    title="My Blog",
    version="1.0.0"
)

# Static files
app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static"
)

# Routes
app.include_router(home.router)
app.include_router(blog.router)
app.include_router(about.router)
app.include_router(auth.router)
app.include_router(admin.router)