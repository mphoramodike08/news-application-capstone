#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys



def main() -> None:
    """Run administrative tasks for the Django project."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_project.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
