from data_log import models
from .test_log_views import BaseLogTest


class WishTests(BaseLogTest):
    fixtures = ['test_wish_monster', 'test_game_items']

    def test_wish_log(self):
        self._do_log('DoRandomWishItem/wish_mana.json')
        log = models.WishLog.objects.first()
        self.assertEqual(log.wish_id, 2)
        self.assertEqual(log.wish_sequence, 2)
        self.assertTrue(log.crystal_used)

    def test_wish_currency_drop(self):
        self._do_log('DoRandomWishItem/wish_mana.json')
        log = models.WishLog.objects.last()
        self.assertEqual(log.wishlogitemdrop_set.count(), 1)

    def test_wish_rune_drop(self):
        self._do_log('DoRandomWishItem/wish_rune.json')
        log = models.WishLog.objects.last()
        self.assertEqual(log.wishlogrunedrop_set.count(), 1)

    def test_wish_monster_drop(self):
        self._do_log('DoRandomWishItem/wish_monster.json')
        log = models.WishLog.objects.last()
        self.assertEqual(log.wishlogmonsterdrop_set.count(), 1)
