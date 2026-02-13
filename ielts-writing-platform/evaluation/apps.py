"""Evaluation app configuration."""

from django.apps import AppConfig


class EvaluationConfig(AppConfig):
    """Configuration for evaluation app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evaluation'
