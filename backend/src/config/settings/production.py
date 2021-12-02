from .base import *


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False


DEBUG = False


DATABASES = config["DATABASES"]
<<<<<<< HEAD


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
=======
>>>>>>> 6d01b5c91b52143831b09596c6d4b63141490247
