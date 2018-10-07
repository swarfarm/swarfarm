from django.apps import AppConfig


class HerdersConfig(AppConfig):
    name = 'herders'
    verbose_name = 'SWARFARM'

    def ready(self):
        import herders.signals #noqa
