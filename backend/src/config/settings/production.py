from .base import *


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False

DEBUG = env.bool("LOCAL_MODE", False)
print("modo production")


try:
    DATABASES = {
        'default': {
            'ENGINE': env("DB_ENGINE_PROD"),
            'NAME': env("DB_NAME_PROD"),
            'USER': env("DB_USER_PROD"),
            'PASSWORD': env("DB_PASSWORD_PROD"),
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
