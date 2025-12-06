from django.apps import AppConfig


class BingoAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bingo_app'
    
    def ready(self):
        # Importar señales para que se registren
        import bingo_app.signals