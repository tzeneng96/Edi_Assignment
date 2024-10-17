from django.apps import AppConfig


class EmployeeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employee_app'

    def ready(self):
        from django.core.management import call_command
        from django.db.utils import OperationalError
        import time

        # Wait for the database to be ready
        while True:
            try:
                call_command('seed_data')
                break
            except OperationalError:
                time.sleep(1)  # Wait for the database to be available