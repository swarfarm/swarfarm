import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from data_log import views, models
from herders.models import Summoner


class BaseLogTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def _do_log(self, log_data_filename, *args, **kwargs):
        with open(f'data_log/tests/game_api_data/{log_data_filename}', 'r') as f:
            view = views.LogData.as_view({'post': 'create'})
            data = get_requested_keys(json.load(f))
            request = self.factory.post(
                reverse('data_log:log-upload-list'),
                data=data,
                format='json',
                **kwargs,
            )
            return view(request)


def get_requested_keys(log_data):
    # Sample data contains entire game API request/response, but log clients will trim data down
    # to the keys specified in `accepted_api_params`
    command = log_data['data']['request']['command']
    requested_data = views.accepted_api_params[command]

    trimmed_data = {
        'data': {
            'request': {},
            'response': {},
        }
    }

    for key in requested_data['request']:
        if key in log_data['data']['request']:
            trimmed_data['data']['request'][key] = log_data['data']['request'][key]

    for key in requested_data['response']:
        if key in log_data['data']['response']:
            trimmed_data['data']['response'][key] = log_data['data']['response'][key]

    return trimmed_data


class LogDataViewTests(BaseLogTest):
    # These tests assume SummonLog functionality is working too, and might fail for SummonLog related reasons
    fixtures = ['test_summon_monsters', 'test_game_items']

    def test_invalid_log_data(self):
        view = views.LogData.as_view({'post': 'create'})
        data = {'request': {}, 'response': {}}
        request = self.factory.post(
            reverse('data_log:log-upload-list'),
            data=data,
            format='json',
        )
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data.get('message'))
        self.assertTrue(response.data.get('reinit'))

    def test_log_data_validation(self):
        with open(f'data_log/tests/game_api_data/SummonLog/scroll_unknown_qty1.json', 'r') as f:
            data = get_requested_keys(json.load(f))

        del data['data']['request']['mode']  # Delete required key for test
        view = views.LogData.as_view({'post': 'create'})
        request = self.factory.post(
            reverse('data_log:log-upload-list'),
            data=data,
            format='json'
        )
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data.get('message'))
        self.assertTrue(response.data.get('reinit'))
        self.assertEqual(models.FullLog.objects.count(), 1)

    def test_non_accepted_api_command(self):
        view = views.LogData.as_view({'post': 'create'})
        data = {
            'data': {
                'request': {
                    'command': 'FakeApiCommand'
                },
                'response': {},
            }
        }
        request = self.factory.post(
            reverse('data_log:log-upload-list'),
            data=data,
            format='json',
        )
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data.get('message'))
        self.assertTrue(response.data.get('reinit'))

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
