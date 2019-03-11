from data_log import models
from .test_log_views import BaseLogTest


class ShopRefreshTests(BaseLogTest):
    fixtures = ['test_summon_monsters', 'test_game_items']

    def test_shop_refresh_new(self):
        self._do_log('GetBlackMarketList/shop_refresh_new.json')
        log = models.ShopRefreshLog.objects.first()
        self.assertEqual(log.slots_available, 12)

        self.assertEqual(log.shoprefreshrunedrop_set.count(), 7)
        self.assertEqual(log.shoprefreshrunedrop_set.first().cost, 36500)
        self.assertEqual(log.shoprefreshitemdrop_set.count(), 1)
        self.assertEqual(log.shoprefreshitemdrop_set.first().cost, 3900)
        self.assertEqual(log.shoprefreshmonsterdrop_set.count(), 4)
        self.assertEqual(log.shoprefreshmonsterdrop_set.first().cost, 2600)

    def test_shop_refresh_old(self):
        self._do_log('GetBlackMarketList/shop_refresh_old.json')
        log = models.ShopRefreshLog.objects.first()
        self.assertIsNone(log)
