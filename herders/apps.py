from django.apps import AppConfig


class HerdersConfig(AppConfig):
    name = 'herders'
    verbose_name = 'Everything SWARFARM pretty much'

    def ready(self):
        import herders.signals
