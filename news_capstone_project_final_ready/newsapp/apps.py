"""Application configuration for the news app."""

from django.apps import AppConfig

class NewsappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "newsapp"
