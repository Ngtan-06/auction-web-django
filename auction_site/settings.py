import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = ["*"]  # chỉnh khi deploy

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("SUPABASE_DB_HOST"),
        "PORT": os.getenv("SUPABASE_DB_PORT", 5432),
        "NAME": os.getenv("SUPABASE_DB_NAME"),
        "USER": os.getenv("SUPABASE_DB_USER"),
        "PASSWORD": os.getenv("SUPABASE_DB_PASSWORD"),
        "OPTIONS": {"sslmode": "require"},
    }
}

# Static files (for Render)
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = 'auctions.User'

# Fetch variables
DATABASE_URL = os.getenv("DATABASE_URL")

connection = psycopg2.connect(DATABASE_URL)