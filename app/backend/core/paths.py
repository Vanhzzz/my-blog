from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent

BACKEND_DIR = CORE_DIR.parent

APP_DIR = BACKEND_DIR.parent

PROJECT_DIR = APP_DIR.parent

FRONTEND_DIR = APP_DIR / "frontend"

TEMPLATES_DIR = FRONTEND_DIR / "templates"

STATIC_DIR = FRONTEND_DIR / "static"

# Project folders
LOGS_DIR = PROJECT_DIR / "logs"

SCRIPTS_DIR = PROJECT_DIR / "scripts"