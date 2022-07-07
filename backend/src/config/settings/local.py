from .base import *


DEBUG = env.bool("LOCAL_MODE", False)
print("modo local")

# Ensure SEP-24 session cookies have the secure flag (only Production)
SESSION_COOKIE_SECURE = False


try:
    DATABASES = {
        'default': {
            'ENGINE': env("DB_ENGINE_LOCAL"),
            'NAME': env("DB_NAME_LOCAL"),
            'USER': env("DB_USER_LOCAL"),
            'PASSWORD': env("DB_PASSWORD_LOCAL"),
            'HOST': env("DB_HOST"),
            'PORT': env("DB_PORT"),
        }
    }
except:
    print(f"Problems with the DATABASES file")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'testing_db.sqlite3',
        }
    }
