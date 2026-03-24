from pathlib import Path
import os
import importlib.util

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    import environ  # type: ignore
    env = environ.Env(DEBUG=(bool, False))
    environ.Env.read_env(BASE_DIR / ".env")
    get_env = lambda key, default=None: env(key, default=default)
    get_env_list = lambda key, default=None: env.list(key, default=default or [])
    get_env_bool = lambda key, default=False: env.bool(key, default=default)
    get_env_int = lambda key, default=0: env.int(key, default=default)
except Exception:
    get_env = lambda key, default=None: os.getenv(key, default)
    get_env_list = lambda key, default=None: [v.strip() for v in os.getenv(key, ",".join(default or [])).split(",") if v.strip()]
    get_env_bool = lambda key, default=False: os.getenv(key, str(default)).lower() in {"1", "true", "yes"}
    get_env_int = lambda key, default=0: int(os.getenv(key, default))

SECRET_KEY = get_env("SECRET_KEY", "dev-insecure-key")
DEBUG = get_env_bool("DEBUG", True)
ALLOWED_HOSTS = get_env_list("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions",
    "django.contrib.messages", "django.contrib.staticfiles", "rest_framework",
    "products", "orders", "blog", "contact",
]
if importlib.util.find_spec("corsheaders"):
    INSTALLED_APPS.append("corsheaders")
if importlib.util.find_spec("django_filters"):
    INSTALLED_APPS.append("django_filters")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if importlib.util.find_spec("corsheaders"):
    MIDDLEWARE.insert(2, "corsheaders.middleware.CorsMiddleware")

ROOT_URLCONF = "naqqash_tea.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "APP_DIRS": True, "OPTIONS": {"context_processors": ["django.template.context_processors.debug", "django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "naqqash_tea.wsgi.application"

try:
    import dj_database_url  # type: ignore
    DATABASES = {"default": dj_database_url.parse(get_env("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"))}
except Exception:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Baku"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = get_env_list("CORS_ALLOWED_ORIGINS", ["http://localhost:5173", "https://naqqashtea.com"])
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_FILTER_BACKENDS": (["django_filters.rest_framework.DjangoFilterBackend"] if importlib.util.find_spec("django_filters") else []) + ["rest_framework.filters.SearchFilter", "rest_framework.filters.OrderingFilter"],
}
STRIPE_SECRET_KEY = get_env("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = get_env("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = get_env("STRIPE_WEBHOOK_SECRET", "")
DEFAULT_FROM_EMAIL = get_env("DEFAULT_FROM_EMAIL", "hello@naqqashtea.com")
ADMIN_NOTIFICATION_EMAIL = get_env("ADMIN_NOTIFICATION_EMAIL", "hello@naqqashtea.com")

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = get_env("EMAIL_HOST", "")
    EMAIL_PORT = get_env_int("EMAIL_PORT", 587)
    EMAIL_HOST_USER = get_env("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = get_env("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = get_env_bool("EMAIL_USE_TLS", True)
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
