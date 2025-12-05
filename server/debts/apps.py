from django.apps import AppConfig

class DebtsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server.debts'

    def ready(self):
        from django.contrib.auth.models import User
        from django.db.utils import OperationalError

        try:
            if not User.objects.filter(username='alice').exists():
                User.objects.create_user(username='alice', password='alice123')
            if not User.objects.filter(username='bob').exists():
                User.objects.create_user(username='bob', password='bob123')
            if not User.objects.filter(username='charlie').exists():
                User.objects.create_user(username='charlie', password='charlie123')
        except OperationalError:
            pass