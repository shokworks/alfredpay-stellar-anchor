import os
import json
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open('etc/config.json', encoding='utf-8-sig') as config_file:
    """Get the config json file and save inside config variable"""
    config = json.load(config_file)


def get_config_set(setting, config=config):
    """Get config setting or fail with ImproperlyConfigured"""
    try:
        return config[setting]
    except KeyError:
        raise ImproperlyConfigured(f"Set the {setting} setting")


SECRET_KEY = get_config_set("SECRET_KEY")

ALLOWED_HOSTS = get_config_set("ALLOWED_HOSTS")


BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'core.testing'
]

THIRD_APPS = [
    'corsheaders',
    'rest_framework',
    'polaris',
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Polaris Environment Variables.
POLARIS_STELLAR_NETWORK_PASSPHRASE = get_config_set("STELLAR_NETWORK_PASSPHRASE")
POLARIS_HORIZON_URI = get_config_set("HORIZON_URI")
POLARIS_HOST_URL = get_config_set("HOST_URL")
POLARIS_LOCAL_MODE = get_config_set("LOCAL_MODE")
POLARIS_ACTIVE_SEPS = get_config_set("ACTIVE_SEPS")
POLARIS_SEP10_HOME_DOMAINS = get_config_set("SEP10_HOME_DOMAINS")
POLARIS_SERVER_JWT_KEY = get_config_set("SEP10_JWT_KEY")
POLARIS_SIGNING_KEY = get_config_set("SEP10_SERVER_KEY")
POLARIS_SIGNING_SEED = get_config_set("SEP10_SERVER_SEED")
POLARIS_CLIENT_KEY = get_config_set("SEP10_CLIENT_KEY")
POLARIS_CLIENT_SEED = get_config_set("SEP10_CLIENT_SEED")
POLARIS_SEP10_CLIENT_ATTRIBUTION_REQUIRED = (get_config_set("SEP10_CLIENT_A_REQ") == True)


FORM_RENDERER = "django.forms.renderers.TemplatesSetting"


ROOT_URLCONF = 'config.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# CORS_ALLOWED_ORIGINS = get_config_set("CORS_ALLOWED_ORIGINS")
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False
# CORS_ORIGIN_WHITELIST = get_config_set("CORS_ALLOWED_ORIGINS")


STATIC_ROOT = os.path.join(BASE_DIR, 'collectstatic')
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_URL = '/static/'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIAFILES_DIRS = [os.path.join(BASE_DIR, 'media')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root')


REST_FRAMEWORK = {
   'DEFAULT_AUTHENTICATION_CLASSES': [
    ],
   'DEFAULT_PERMISSION_CLASSES': [
    ],
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
