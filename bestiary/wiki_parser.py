from wikitools import wiki, page
from herders.models import Monster, MonsterSkill, MonsterLeaderSkill


def compare_monster_data(monster):
    if monster.wikia_url:
        awakened_name = None

        if monster.is_awakened:
            unawakened_name = monster.awakens_from.name
            awakened_name = monster.name
        else:
            unawakened_name = monster.name
            if monster.can_awaken and monster.awakens_to:
                awakened_name = monster.awakens_to.name

        page_title = unawakened_name + ' (' + monster.get_element_display() + ')'
        if awakened_name:
            page_title += ' - ' + awakened_name

        wikisite = wiki.Wiki('http://summonerswar.wikia.com/api.php')

        monster_page = page.Page(wikisite, title=page_title)
        wikitext = monster_page.getWikiText().split('\n')

        parsed_monster = Monster()
        parsed_skills = [MonsterSkill()] * 4
        parsed_leader_skill = MonsterLeaderSkill()

        # Set up default values that can be assumed
        parsed_monster.crit_rate = 15
        parsed_monster.crit_damage = 50
        parsed_monster.accuracy = 0
        parsed_monster.resistance = 15
        parsed_leader_skill.area = MonsterLeaderSkill.AREA_GENERAL  # default value

        for line in wikitext:
            try:
                attribute, value = line.split('=', 1)
            except ValueError:
                # Not a valid stat line, skip it
                continue
            else:
                if attribute.startswith('|'):
                    attribute = attribute[1:].strip().lower()
                    value = value.strip()

                    # Parse each attribute line by line from the wiki text, picking and choosing depending on if the monster
                    # we passed in is awakened or not
                    if attribute == 'element':
                        parsed_monster.element = _parse_element(value)
                    if attribute == 'name' and not monster.is_awakened:
                        parsed_monster.name = value
                    elif attribute == 'awakened name' and monster.is_awakened:
                        parsed_monster.name = value
                    elif attribute == 'stars' and not monster.is_awakened:
                        parsed_monster.base_stars, parsed_monster.can_awaken, parsed_monster.is_awakened = _parse_stars(value)
                    elif attribute == 'awakened stars' and monster.is_awakened:
                        parsed_monster.base_stars, parsed_monster.can_awaken, parsed_monster.is_awakened = _parse_stars(value)
                    elif attribute == 'type':
                        parsed_monster.archetype = _parse_archetype(value)
                    elif 'essence' in attribute and not monster.is_awakened and monster.can_awaken and value:
                        if 'magic' in attribute and 'low' in attribute:
                            parsed_monster.awaken_mats_magic_low = int(value)
                        elif 'magic' in attribute and 'mid' in attribute:
                            parsed_monster.awaken_mats_magic_mid = int(value)
                        elif 'magic' in attribute and 'high' in attribute:
                            parsed_monster.awaken_mats_magic_high = int(value)
                        elif 'element' in attribute and 'low' in attribute:
                            # Use existing monster as source in case element wasn't parsed
                            if monster.element == Monster.ELEMENT_FIRE:
                                parsed_monster.awaken_mats_fire_low = int(value)
                            elif monster.element == Monster.ELEMENT_WATER:
                                parsed_monster.awaken_mats_water_low = int(value)
                            elif monster.element == Monster.ELEMENT_WIND:
                                parsed_monster.awaken_mats_wind_low = int(value)
                            elif monster.element == Monster.ELEMENT_DARK:
                                parsed_monster.awaken_mats_dark_low = int(value)
                            elif monster.element == Monster.ELEMENT_LIGHT:
                                parsed_monster.awaken_mats_light_low = int(value)
                        elif 'element' in attribute and 'mid' in attribute:
                            # Use existing monster as source in case element wasn't parsed
                            if monster.element == Monster.ELEMENT_FIRE:
                                parsed_monster.awaken_mats_fire_mid = int(value)
                            elif monster.element == Monster.ELEMENT_WATER:
                                parsed_monster.awaken_mats_water_mid = int(value)
                            elif monster.element == Monster.ELEMENT_WIND:
                                parsed_monster.awaken_mats_wind_mid = int(value)
                            elif monster.element == Monster.ELEMENT_DARK:
                                parsed_monster.awaken_mats_dark_mid = int(value)
                            elif monster.element == Monster.ELEMENT_LIGHT:
                                parsed_monster.awaken_mats_light_mid = int(value)
                        elif 'element' in attribute and 'high' in attribute:
                            # Use existing monster as source in case element wasn't parsed
                            if monster.element == Monster.ELEMENT_FIRE:
                                parsed_monster.awaken_mats_fire_high = int(value)
                            elif monster.element == Monster.ELEMENT_WATER:
                                parsed_monster.awaken_mats_water_high = int(value)
                            elif monster.element == Monster.ELEMENT_WIND:
                                parsed_monster.awaken_mats_wind_high = int(value)
                            elif monster.element == Monster.ELEMENT_DARK:
                                parsed_monster.awaken_mats_dark_high = int(value)
                            elif monster.element == Monster.ELEMENT_LIGHT:
                                parsed_monster.awaken_mats_light_high = int(value)
                    elif 'leader skill stat' in attribute:
                        parsed_leader_skill.attribute = _parse_stat(value)
                    elif 'leader skill attribute' in attribute:
                        if 'arena' in value:
                            parsed_leader_skill.area = MonsterLeaderSkill.AREA_ARENA
                        elif 'guild' in value:
                            parsed_leader_skill.area = MonsterLeaderSkill.AREA_GUILD
                        elif 'dungeon' in value:
                            parsed_leader_skill.area = MonsterLeaderSkill.AREA_DUNGEON
                        else:
                            element = _parse_element(value)

                            if element:
                                parsed_leader_skill.area = MonsterLeaderSkill.AREA_ELEMENT
                                parsed_leader_skill.attribute = element
                    elif 'leader skill value' in attribute:
                        parsed_leader_skill.amount = int(value.translate(None, "'"))
                    elif attribute == 'unawakened max hp' and not monster.is_awakened:
                        parsed_monster.base_hp = int(value.translate(None, "'"))
                    elif attribute == 'unawakened max atk' and not monster.is_awakened:
                        parsed_monster.base_attack = int(value.translate(None, "'"))
                    elif attribute == 'unawakened max def' and not monster.is_awakened:
                        parsed_monster.base_defense = int(value.translate(None, "'"))
                    elif attribute == 'unawakened spd' and not monster.is_awakened:
                        parsed_monster.speed = int(value.translate(None, "'"))
                    elif attribute == 'awakened spd' and monster.is_awakened:
                        parsed_monster.speed = int(value.translate(None, "'"))
                    elif attribute == 'awakened cri rate' and monster.is_awakened:
                        parsed_monster.crit_rate = int(value.translate(None, "'"))
                    elif attribute == 'awakened cri dmg' and monster.is_awakened:
                        parsed_monster.crit_damage = int(value.translate(None, "'"))
                    elif attribute == 'awakened res' and monster.is_awakened:
                        parsed_monster.resistance = int(value.translate(None, "'"))
                    elif attribute == 'awakened acc' and monster.is_awakened:
                        parsed_monster.accuracy = int(value.translate(None, "'"))

                else:
                    continue
        pass
    else:
        return None


def _parse_stars(star_text):
    # Figure out what type of monster it is based on star color
    base_stars = int(star_text[:1])
    status = star_text[1:]

    if status == 'P':
        # Purple stars
        can_awaken = True
        is_awakened = True
    elif status == 'G':
        # Gold stars
        can_awaken = True
        is_awakened = False
    else:
        # Silver stars
        can_awaken = False
        is_awakened = False

    return base_stars, can_awaken, is_awakened


def _parse_archetype(type_text):
    type_text = type_text.lower()

    if type_text == 'hp':
        return Monster.TYPE_HP
    elif type_text == 'attack':
        return Monster.TYPE_ATTACK
    elif type_text == 'support':
        return Monster.TYPE_SUPPORT
    elif type_text == 'defense':
        return Monster.TYPE_DEFENSE
    elif type_text == 'material':
        return Monster.TYPE_MATERIAL
    else:
        print 'ERROR: Unable to match archetype "' + type_text + '"'
        return None


def _parse_stat(stat_text):
    stat_text = stat_text.lower()

    if 'hp' in stat_text:
        return MonsterLeaderSkill.ATTRIBUTE_HP
    elif 'def' in stat_text:
        return MonsterLeaderSkill.ATTRIBUTE_DEF
    elif 'atk' in stat_text or 'attack' in stat_text:
        return MonsterLeaderSkill.ATTRIBUTE_ATK
    elif 'spd' in stat_text or 'speed' in stat_text:
        return MonsterLeaderSkill.ATTRIBUTE_SPD
    elif 'rate' in stat_text:
        return MonsterLeaderSkill.ATTRIBUTE_CRIT_RATE
    elif 'dmg' in stat_text or 'damage' in stat_text:
        return MonsterLeaderSkill.ATTRIBUTE_CRIT_DMG
    elif 'acc' in stat_text:
        return MonsterLeaderSkill.ATTRIBUTE_ACCURACY
    elif 'res' in stat_text:
        return MonsterLeaderSkill.ATTRIBUTE_RESIST
    else:
        print 'ERROR: Unable to match stat "' + stat_text + '"'
        return None

def _parse_element(element_text):
    element_text = element_text.lower()

    if 'fire' in element_text:
        return Monster.ELEMENT_FIRE
    if 'water' in element_text:
        return Monster.ELEMENT_WATER
    if 'wind' in element_text:
        return Monster.ELEMENT_WIND
    if 'dark' in element_text:
        return Monster.ELEMENT_DARK
    if 'light' in element_text:
        return Monster.ELEMENT_LIGHT
    else:
        print 'ERROR: Unable to match element "' + element_text + '"'
        return None