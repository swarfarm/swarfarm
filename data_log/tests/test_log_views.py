import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

from data_log import views, models
from herders.models import Summoner


class BaseLogTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def _do_log(self, log_data_filename, *args, **kwargs):
        with open(f'data_log/tests/game_api_responses/{log_data_filename}', 'r') as f:
            view = views.LogData.as_view({'post': 'create'})
            data = json.load(f)
            request = self.factory.post(
                reverse('data_log:log-upload-list'),
                data=data,
                format='json',
                **kwargs,
            )
            view(request)


class LogDataViewTests(BaseLogTest):
    # These tests assume SummonLog functionality is working too, and might fail for SummonLog related reasons
    fixtures = ['test_summon_monsters', 'test_game_items']

    def test_anonymous_log(self):
        self._do_log('SummonLog/scroll_unknown_qty1.json')

        # Verify created log does not have any user account associated
        log = models.SummonLog.objects.first()
        self.assertIsNone(log.summoner)
        self.assertEqual(log.wizard_id, 123)

    def test_wizard_id_log(self):
        u = User.objects.create(username='t')
        Summoner.objects.create(user=u, com2us_id=123)

        self._do_log('SummonLog/scroll_unknown_qty1.json')

        # Verify created log found user account based on wizard_id
        log = models.SummonLog.objects.first()
        self.assertEqual(log.summoner, u.summoner)
        self.assertEqual(log.wizard_id, 123)

    def test_authenticated_log(self):
        u = User.objects.create(username='t')
        Summoner.objects.create(user=u)
        token = Token.objects.create(user=u)

        self._do_log('SummonLog/scroll_unknown_qty1.json', HTTP_AUTHORIZATION=f'Token {token.key}')

        # Verify created log found user without any com2us_id stored on Summoner instance
        log = models.SummonLog.objects.first()
        self.assertEqual(log.summoner, u.summoner)
        self.assertEqual(log.wizard_id, 123)
