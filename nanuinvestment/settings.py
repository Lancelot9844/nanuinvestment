import os
import socket
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = env_bool("DJANGO_DEBUG", True)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG=False.")
    local_secret_key_path = BASE_DIR / ".local_secret_key"
    if local_secret_key_path.exists():
        SECRET_KEY = local_secret_key_path.read_text(encoding="utf-8").strip()
    else:
        SECRET_KEY = get_random_secret_key()
        local_secret_key_path.write_text(SECRET_KEY, encoding="utf-8")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
if DEBUG:
    try:
        local_hostname = socket.gethostname()
        local_ipv4_addresses = socket.gethostbyname_ex(local_hostname)[2]
        ALLOWED_HOSTS = list(
            dict.fromkeys([*ALLOWED_HOSTS, local_hostname, *local_ipv4_addresses])
        )
    except OSError:
        # Local hostname discovery can fail when the machine is offline.
        pass

CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

AAKASHSMS_AUTH_TOKEN = os.environ.get("AAKASHSMS_AUTH_TOKEN", "").strip()
AAKASHSMS_API_URL = os.environ.get(
    "AAKASHSMS_API_URL",
    "https://sms.aakashsms.com/sms/v3/send",
).strip()
AAKASHSMS_TIMEOUT_SECONDS = int(os.environ.get("AAKASHSMS_TIMEOUT_SECONDS", "10"))
SMS_ENABLED = env_bool("SMS_ENABLED", bool(AAKASHSMS_AUTH_TOKEN))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'myapp.apps.MyappConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nanuinvestment.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nanuinvestment.wsgi.application'


DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    parsed_db_url = urlparse(DATABASE_URL)
    engine_map = {
        "postgres": "django.db.backends.postgresql",
        "postgresql": "django.db.backends.postgresql",
        "mysql": "django.db.backends.mysql",
        "mariadb": "django.db.backends.mysql",
        "sqlite": "django.db.backends.sqlite3",
    }
    db_engine = engine_map.get(parsed_db_url.scheme, parsed_db_url.scheme)
    db_name = unquote(parsed_db_url.path.lstrip("/"))
    if db_engine == "django.db.backends.sqlite3":
        db_name = db_name or str(BASE_DIR / "db.sqlite3")
    DATABASES = {
        "default": {
            "ENGINE": db_engine,
            "NAME": db_name,
            "USER": unquote(parsed_db_url.username or ""),
            "PASSWORD": unquote(parsed_db_url.password or ""),
            "HOST": parsed_db_url.hostname or "",
            "PORT": str(parsed_db_url.port or ""),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'templates',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SESSION_COOKIE_AGE = int(os.environ.get("DJANGO_SESSION_COOKIE_AGE", "7200"))
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", not DEBUG)
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", not DEBUG)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if env_bool("DJANGO_SECURE_PROXY_SSL_HEADER") else None

# SAMEORIGIN keeps admin receipt/PDF previews embeddable inside this site.
X_FRAME_OPTIONS = os.environ.get("DJANGO_X_FRAME_OPTIONS", "SAMEORIGIN")
