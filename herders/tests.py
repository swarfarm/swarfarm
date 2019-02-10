import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TransactionTestCase

# Create your tests here.
from herders.models import Summoner
from herders.tasks import com2us_data_import


class DataImportTest(TransactionTestCase):
    fixtures = ['bestiary_data.json']

    def setUp(self):
        self.user = User(
            username='test',
            email='test@test.test',
        )
        self.user.save()
        self.summoner = Summoner.objects.create(user=self.user)

    def test_import_profile(self):
        import_options = {
            'clear_profile': False,
            'default_priority': None,
            'lock_monsters': False,
            'minimum_stars': 1,
            'ignore_silver': False,
            'ignore_material': False,
            'except_with_runes': True,
            'except_light_and_dark': True,
            'except_fusion_ingredient': True,
            'delete_missing_monsters': True,
            'delete_missing_runes': True,
            'ignore_validation_errors': False,
        }
        with open(os.path.join(settings.BASE_DIR, 'herders', 'test_files', 'sw.json'), encoding="utf8") as f:
            data = f.read()
            data = json.loads(data)
        com2us_data_import(data, self.summoner.pk, import_options)
