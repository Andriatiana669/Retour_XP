from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def cleanup_anonymous():
    """
    Tâche exécutée par APScheduler.
    """
    cutoff = timezone.now() - timedelta(hours=24)
    qs = User.objects.filter(
        username__startswith="anonymous_",
        last_login__lt=cutoff
    )
    deleted, _ = qs.delete()
    return deleted