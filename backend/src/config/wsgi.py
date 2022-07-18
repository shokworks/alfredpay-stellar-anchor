import os
import environ

from django.core.wsgi import get_wsgi_application
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
env_file = os.path.abspath(os.path.join(BASE_DIR, './etc/.env'))

try:
    os.path.exists(env_file)
    environ.Env.read_env(env_file)
except KeyError:
    raise ImproperlyConfigured(f"Problems with the {env_file} file")

LOCAL_MODE = env.bool("LOCAL_MODE", False)

if LOCAL_MODE:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
