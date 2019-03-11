from data_log import models
from .test_log_views import BaseLogTest


class CraftRuneTests(BaseLogTest):
    def test_low_rune_craft(self):
        self._do_log('BuyShopItem/craft_rune_low.json')
        log = models.CraftRuneLog.objects.first()
        self.assertEqual(log.craft_level, models.CraftRuneLog.CRAFT_LOW)

    def test_mid_rune_craft(self):
        self._do_log('BuyShopItem/craft_rune_mid.json')
        log = models.CraftRuneLog.objects.first()
        self.assertEqual(log.craft_level, models.CraftRuneLog.CRAFT_MID)

    def test_high_rune_craft(self):
        self._do_log('BuyShopItem/craft_rune_high.json')
        log = models.CraftRuneLog.objects.first()
        self.assertEqual(log.craft_level, models.CraftRuneLog.CRAFT_HIGH)
