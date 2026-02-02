# eletronLab/signals.py
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Coment

CACHE_KEY = "coment_assuntos_distintos_v3"

@receiver(post_save, sender=Coment)
def limpa_cache_assuntos_save(sender, instance, **kwargs):
    cache.delete(CACHE_KEY)

@receiver(post_delete, sender=Coment)
def limpa_cache_assuntos_delete(sender, instance, **kwargs):
    cache.delete(CACHE_KEY)
