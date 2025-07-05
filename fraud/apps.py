from django.apps import AppConfig

class FraudConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fraud'

    def ready(self):
        # Import signal handlers
        import fraud.signals