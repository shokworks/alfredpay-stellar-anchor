import os
import environ
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


SETTINGS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '../'))

"""
    SETTINGS_DIR: /home/Josean/Scripts/Django/stellar-anchor/backend/src/config
    BASE_DIR: /home/Josean/Scripts/Django/stellar-anchor/backend/src
"""

env = environ.Env()
env_file = os.path.abspath(os.path.join(BASE_DIR, 'etc/.env'))


try:
    os.path.exists(env_file)
    environ.Env.read_env(env_file)
except KeyError:
    raise ImproperlyConfigured(f"Problems with the {env_file} file")

SECRET_KEY = env("SECRET_KEY")

MULT_ASSET_ADDITIONAL_SIGNING_SEED = env(
    "MULT_ASSET_ADDITIONAL_SIGNING_SEED", default=None
)

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "[::1]", "0.0.0.0"]
)

BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'core.polaris',
    'core.testing',
]

THIRD_APPS = [
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'polaris.middleware.TimezoneMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# SEP24 Allow Custom Templates
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

local_mode = env.bool("LOCAL_MODE", default=False)

# Redirect HTTP to HTTPS if not in local mode
SECURE_SSL_REDIRECT = not local_mode
if SECURE_SSL_REDIRECT:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SETTINGS_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/La_Paz'
# TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ("en", _("English")),
]


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


FORM_RENDERER = "django.forms.renderers.TemplatesSetting"


# The absolute path to the directory where collectstatic will collect static files for deployment.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "server/collectstatic")
# URL to use when referring to static files located in STATIC_ROOT.
# Example: "/static/" or "http://static.example.com/"
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "server/media")
# if settings.DEBUG is True.
MEDIA_URL = '/media/'


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",

    ],
    "DEFAULT_PERMISSION_CLASSES": [
        # "rest_framework.permissions.IsAuthenticated",
        # "rest_framework.permissions.IsAdminUser"
    ],
    "DEFAULT_PAGINATION_CLASS":
        "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework.renderers.TemplateHTMLRenderer",
    ],
    "PAGE_SIZE": 10,
}

CORS_ORIGIN_ALLOW_ALL = True

LOGGING = {
    "version": 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    "loggers": {
        "testing": {
            "level": "DEBUG",
            "handlers": [
                "console", "testing_info", "testing_debug",
            ]
        },
        "polaris": {
            "level": "DEBUG",
            "handlers": [
                "console", "polaris",
            ]
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "polaris": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "./etc/log/polaris.log",
            "formatter": "simple"
        },
        "testing_info": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "./etc/log/testing_info.log",
            "formatter": "simple"
        },
        "testing_debug": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "./etc/log/testing_debug.log",
            "formatter": "simple"
        },
    },
}
