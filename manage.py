#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# ---- START DEBUG ----
# print(f"DEBUG: Python Executable: {sys.executable}")
# print(f"DEBUG: Python Version: {sys.version}")
# print("DEBUG: sys.path:")
# for p in sys.path:
#     print(f"  {p}")
# ---- END DEBUG ----

from dotenv import load_dotenv


def main():
    """Run administrative tasks."""
    load_dotenv()  # Load .env file before accessing settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'questify_backend.settings')
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
