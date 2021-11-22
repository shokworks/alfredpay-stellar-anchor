from .base import *


DEBUG = True


DATABASES = config["DATABASES"]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'myapp': {
            'handlers': ['console'],
            'propogate': True,
            'LEVEL': 'DEBUG'
        },
        'polaris': {
            'handlers': ['console'],
            'propagate': True,
            'LEVEL': 'INFO'
        },
    }
}
