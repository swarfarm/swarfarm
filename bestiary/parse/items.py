from bestiary.models import GameItem
from bestiary.parse import game_data


def craft_materials():
    for master_id, raw in game_data.tables.CRAFT_MATERIALS.items():
        defaults = {
            'name': game_data.strings.CRAFT_MATERIAL_NAMES.get(master_id, raw['name']),
            'icon': 'craftstuff_icon_{0:04d}_{1:02d}_{2:02d}.png'.format(*raw['thumbnail']),
            'description': game_data.strings.CRAFT_MATERIAL_DESCRIPTIONS.get(master_id, ''),
            'sell_value': raw['sell info']
        }

        GameItem.objects.update_or_create(
            category=GameItem.CATEGORY_CRAFT_STUFF,
            com2us_id=master_id,
            defaults=defaults,
        )
