"""
Module: App configuration for the fraud detection component.
"""
from django.apps import AppConfig

class FraudConfig(AppConfig):
    """
    Configuration for the fraud app; connects signal handlers on startup.
    """
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'fraud'

    def ready(self) -> None:
        """
        Called when Django starts; imports signal handlers for fraud checks.
        """
        import fraud.signals