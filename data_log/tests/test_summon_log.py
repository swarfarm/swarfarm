from bestiary.models import Monster, GameItem
from data_log import models
from .test_log_views import BaseLogTest


class SummonLogTests(BaseLogTest):
    fixtures = ['test_summon_monsters', 'test_game_items']

    def test_summon_1_with_unknown_scroll(self):
        self._do_log('SummonLog/scroll_unknown_qty1.json')

        self.assertEqual(models.SummonLog.objects.count(), 1)
        log = models.SummonLog.objects.first()
        self.assertEqual(log.item, GameItem.objects.get(category=GameItem.CATEGORY_SUMMON_SCROLL, com2us_id=1))
        self.assertEqual(log.monster, Monster.objects.get(com2us_id=13103))

    def test_summon_10_with_unknown_scroll(self):
        self._do_log('SummonLog/scroll_unknown_qty10.json')

        self.assertEqual(models.SummonLog.objects.count(), 10)
        for log in models.SummonLog.objects.all():
            self.assertEqual(log.item, GameItem.objects.get(category=GameItem.CATEGORY_SUMMON_SCROLL, com2us_id=1))
            self.assertEqual(log.monster, Monster.objects.get(com2us_id=13103))

    def test_summon_1_with_social_points(self):
        self._do_log('SummonLog/currency_social_qty1.json')

        self.assertEqual(models.SummonLog.objects.count(), 1)
        log = models.SummonLog.objects.first()
        self.assertEqual(log.item, GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, com2us_id=2))
        self.assertEqual(log.monster, Monster.objects.get(com2us_id=13103))

    def test_summon_10_with_social_points(self):
        self._do_log('SummonLog/currency_social_qty10.json')

        self.assertEqual(models.SummonLog.objects.count(), 10)
        for log in models.SummonLog.objects.all():
            self.assertEqual(log.item, GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, com2us_id=2))
            self.assertEqual(log.monster, Monster.objects.get(com2us_id=13103))

    def test_summon_with_mystical_scroll(self):
        self._do_log('SummonLog/scroll_mystical.json')

        self.assertEqual(models.SummonLog.objects.count(), 1)
        log = models.SummonLog.objects.first()
        self.assertEqual(log.item, GameItem.objects.get(category=GameItem.CATEGORY_SUMMON_SCROLL, com2us_id=2))
        self.assertEqual(log.monster, Monster.objects.get(com2us_id=14102))

    def test_summon_with_crystals(self):
        self._do_log('SummonLog/currency_crystals.json')

        self.assertEqual(models.SummonLog.objects.count(), 1)
        log = models.SummonLog.objects.first()
        self.assertEqual(log.item, GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, com2us_id=1))
        self.assertEqual(log.monster, Monster.objects.get(com2us_id=14102))

    def test_summon_with_exclusive_stones(self):
        self._do_log('SummonLog/scroll_exclusive.json')

        self.assertEqual(models.SummonLog.objects.count(), 1)
        log = models.SummonLog.objects.first()
        self.assertEqual(log.item, GameItem.objects.get(category=GameItem.CATEGORY_SUMMON_SCROLL, com2us_id=8))
        self.assertEqual(log.monster, Monster.objects.get(com2us_id=14102))
