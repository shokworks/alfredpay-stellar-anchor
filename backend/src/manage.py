#!/usr/bin/env python
import os
import sys
import environ

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
env_file = os.path.abspath(os.path.join(BASE_DIR, './src/etc/.env'))
try:
    os.path.exists(env_file)
    environ.Env.read_env(env_file)
except KeyError:
    raise ImproperlyConfigured(f"Problems with the {env_file} file")

LOCAL_MODE = env.bool("LOCAL_MODE", True)


def main():
    """Run administrative tasks."""
    if LOCAL_MODE:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
