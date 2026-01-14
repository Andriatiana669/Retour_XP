# marches/signals.py
import logging
from django.db.models.signals import pre_save, pre_delete, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import MarcheDetaille
 

logger = logging.getLogger('marches')

@receiver(pre_save, sender=MarcheDetaille)
def log_marche_errors(sender, instance, **kwargs):
    try:
        # on force la validation pour capturer l’erreur
        instance.full_clean()
    except Exception as e:
        logger.exception("Erreur lors de la validation du MarcheDetaille : %s", e)


@receiver(post_delete, sender=MarcheDetaille)
def renum_matricules_apres_suppression(sender, instance, **kwargs):
    """
    Après suppression d'un MarcheDetaille, on renumérote MD_01, MD_02…
    pour le même marché global.
    """
    mg = instance.marche_global
    qs = MarcheDetaille.objects.filter(marche_global=mg).order_by('id')
    total = qs.count()
    # largeur du numéro (01, 001, 0001…)
    width = len(str(total)) if total > 99 else (3 if total > 9 else 2)

    with transaction.atomic():
        for idx, md in enumerate(qs, start=1):
            new_mat = f"MD_{str(idx).zfill(width)}"
            if md.matricule != new_mat:
                md.matricule = new_mat
                md.save(update_fields=['matricule'])

        # on remet à jour le compteur du global
        mg.nombre_projet = qs.count()
        mg.save(update_fields=['nombre_projet'])
