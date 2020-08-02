from django.core.exceptions import ValidationError
from django.test import TestCase

from bestiary import models


class Artifact(models.Artifact):
    class Meta:
        abstract = True

    @classmethod
    def stub(cls, **kwargs):
        defaults = {
            'slot': models.Artifact.SLOT_ELEMENTAL,
            'quality': models.Artifact.QUALITY_NORMAL,
            'original_quality': models.Artifact.QUALITY_NORMAL,
            'level': 0,
            'main_stat': models.Artifact.STAT_HP_PCT,
            'effects': [],
            'effects_values': [],
            'substats_enchanted': [],
            'substats_grind_value': [],
        }

        defaults.update(kwargs)

        defaults['main_stat_value'] = models.Artifact.MAIN_STAT_VALUES[defaults['main_stat']][defaults['level']]

        artifact = cls(**defaults)

        return artifact
