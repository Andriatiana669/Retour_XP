# marches/signals.py
import logging
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import MarcheDetaille

logger = logging.getLogger('marches')

@receiver(pre_save, sender=MarcheDetaille)
def log_marche_errors(sender, instance, **kwargs):
    try:
        # on force la validation pour capturer l’erreur
        instance.full_clean()
    except Exception as e:
        logger.exception("Erreur lors de la validation du MarcheDetaille : %s", e)