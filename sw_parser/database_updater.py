from herders.models import Monster
from .data_mapping import monster_id_map


def update_monster_com2us_ids():
    # Reverse the monster/id dict so monster names are the keys
    id_monster_map = {v: k for k, v in monster_id_map.items()}

    for mon in Monster.objects.filter(is_awakened=False):
        if mon.name in id_monster_map:
            print str(mon) + ' - ' + str(id_monster_map[mon.name])
            mon.com2us_id = id_monster_map[mon.name]
            mon.save(skip_url_gen=True)

            if mon.awakens_to:
                mon.awakens_to.com2us_id = id_monster_map[mon.name]
                mon.awakens_to.save(skip_url_gen=True)
