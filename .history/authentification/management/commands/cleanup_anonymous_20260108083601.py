from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Supprime les utilisateurs anonymes inactifs depuis plus de 24h"

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(hours=24)
        users = User.objects.filter(
            username__startswith="anonymous_",
            last_login__lt=cutoff
        )
        count = users.count()
        users.delete()
        self.stdout.write(self.style.SUCCESS(f"{count} utilisateurs anonymes supprimés."))