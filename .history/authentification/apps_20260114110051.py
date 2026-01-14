from django.apps import AppConfig

class AuthentificationConfig(AppConfig):
    name = 'authentification'

    def ready(self):
        # évite double exécution en dev (runserver + reload)
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore
        from django_apscheduler.models import DjangoJobExecution
        from authentification.tasks import cleanup_anonymous
        import atexit

        scheduler = BackgroundScheduler(timezone='Indian/Antananarivo')
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        # une seule instance de la tâche
        scheduler.add_job(
            cleanup_anonymous,
            trigger='cron',
            hour=3,            # 03:00 du matin
            minute=0,
            id='cleanup_anonymous',
            max_instances=1,
            replace_existing=True,
            coalesce=True
        )

        scheduler.start()
        atexit.register(lambda: scheduler.shutdown(wait=False))