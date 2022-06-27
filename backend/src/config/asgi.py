import os
import environ

from django.core.asgi import get_asgi_application
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
env_file = os.path.abspath(os.path.join(BASE_DIR, './etc/.env'))
print(f"wsgi env_file: {env_file}")

try:
    os.path.exists(env_file)
    environ.Env.read_env(env_file)
except KeyError:
    raise ImproperlyConfigured(f"Problems with the {env_file} file")

LOCAL_MODE = env.bool("LOCAL_MODE", False)
print(f"asgi LOCAL_MODE: {LOCAL_MODE}")

if LOCAL_MODE:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()
