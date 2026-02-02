# eletronLab/apps.py
from django.apps import AppConfig

class EletronLabConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eletronLab'

    def ready(self):
        from . import signals  # noqa
