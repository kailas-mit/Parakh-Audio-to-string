from django.apps import AppConfig


class App1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app1'

    # def ready(self):
    #     from django.utils.translation import gettext_lazy as _

    #     # Define language options here
    #     LANGUAGES = (
    #         ('en-us', _('English')),
    #         ('hi', _('Hindi'))
    #     )
