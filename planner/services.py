from bestiary.models import LeaderSkill, Dungeon
from . import models


def make_composite(owner, name, pks):
    """
    This method combines several teams into a single optimization plan.  Leader skills from individual teams are
    collapsed into the combined unit requirements.  SPD leaders are handled in a non-standard way because SPD tuning
    must account for integer-level rounding that only occurs after the effects of towers, sets, and leaders are
    considered.
    """
    composite = models.OptimizeTeam.objects.create(
        owner=owner,
        name=name,
    )
    teams = models.OptimizeTeam.objects.filter(
        pk__in=pks
    ).prefetch_related(
        'monsters'  # don't prefetch
    )

    # track monster stats for min/max aggregation
    mons = {}
    # an "empty" base to union with local sets
    tunes = models.SpeedTune.objects.none()

    for team in teams:
        # extract leader skill
        leader_skill = None
        try:
            leader_skill = team.monsters.get(leader=True).monster.monster.leader_skill
        except models.OptimizeMonster.DoesNotExist:
            pass
        # clear leader skill (set to None) if there is an area mismatch
        # LeaderSkill.area:  AREA_GENERAL, AREA_DUNGEON, AREA_ELEMENT, AREA_ARENA, AREA_GUILD
        # Dungeon.category:  CATEGORY_SCENARIO, CATEGORY_RUNE_DUNGEON, CATEGORY_ESSENCE_DUNGEON, CATEGORY_OTHER_DUNGEON,
        #                    CATEGORY_RAID, CATEGORY_HALL_OF_HEROES
        if leader_skill is not None and leader_skill.area == LeaderSkill.AREA_DUNGEON:
            if team.dungeon.dungeon.category not in [
                Dungeon.CATEGORY_RUNE_DUNGEON, Dungeon.CATEGORY_ESSENCE_DUNGEON, Dungeon.CATEGORY_RAID,
                Dungeon.CATEGORY_HALL_OF_HEROES,
            ]:
                leader_skill = None
        # make sure dungeon is arena
        if leader_skill is not None and leader_skill.area == LeaderSkill.AREA_ARENA:
            leader_skill = None
        # make sure dungeon is guild
        if leader_skill is not None and leader_skill.area == LeaderSkill.AREA_GUILD:
            leader_skill = None
        # Composite stats from all teams, adjusting for leader skill
        for stat in team.monsters.all():
            # TODO: need to store SPD leadership along side tune in this cache
            tunes = tunes.union(stat.slower_than_by.all())
            apply_skill = leader_skill
            # disable if there is an element mismatch
            if leader_skill is not None and leader_skill.element is not None and leader_skill.element != stat.monster.monster.element:
                apply_skill = None
            # the stats to which the leader skill applies
            if apply_skill is not None:
                skill_map = {
                    # TODO: figure out how to properly handle rounding issues when towers, sets, and leaders are considered
                    LeaderSkill.ATTRIBUTE_SPD: ['min_spd'],
                    LeaderSkill.ATTRIBUTE_HP: ['min_hp'],
                    LeaderSkill.ATTRIBUTE_DEF: ['min_def'],
                    LeaderSkill.ATTRIBUTE_ATK: [],
                    LeaderSkill.ATTRIBUTE_CRIT_DMG: [],
                    LeaderSkill.ATTRIBUTE_CRIT_RATE: ['min_crate', 'max_crate'],
                    LeaderSkill.ATTRIBUTE_ACCURACY: ['min_acc'],
                    LeaderSkill.ATTRIBUTE_RESIST: ['min_res'],
                }
                for field in skill_map[apply_skill.attribute]:
                    if getattr(stat, field) is not None:
                        setattr(stat, field, getattr(stat, field) - apply_skill.amount)
            if stat.monster_id not in mons:
                # create first entry
                mons[stat.monster_id] = stat
                stat.pk = None  # new object
                stat.team = composite  # update team
                stat.leader = False  # make sure there are no leaders
                # no need to compare since the values are the same
                continue
            else:
                # update existing stat
                monster = mons[stat.monster_id]
                skill_operation = {
                    'min_spd': max,
                    'min_hp': max,
                    'min_def': max,
                    'min_ehp': max,
                    'min_res': max,
                    'min_acc': max,
                    'min_crate': max,
                    'max_crate': min,
                }
                # update stat
                for field, operation in skill_operation.items():
                    if getattr(stat, field) is None:
                        continue  # no need to update
                    elif getattr(monster, field) is None:
                        # replace with stat (even if None)
                        setattr(monster, field, getattr(stat, field))
                    else:
                        # select stricter constraint
                        setattr(monster, field, operation(getattr(monster, field), getattr(stat, field)))
    for monster in mons.values():
        monster.save()
    for tune in tunes:
        # TODO: Incorporate leaders into speed tuning rules
        """
        Leaders affect the relative speed of units.  Assume unit F needs to be faster than unit S in the presence of a
        +20% SPD leader.  If F has a base speed of 120 and S has a base speed of 90, F will gain +6 net SPD from the
        leader.  As a result, F could be 6 slower than S during final tuning and still faster on the team.
        
        We need to do a similar accounting for ATB boosters.  The difference in speed used for ATB boost calculations
        applies after both units have been SPD boosted.  A 25% difference between F & S after the Leader boost is 
        really -- where B(F) means the base speed of F:
         
            (1-ATB) * (F + B(F) * Leader) < (S + B(S) * Leader) 
            
        The base speeds and Leader are already known so we can simplify the formula to something like:
        
            (1-ATB) * F < S + Leader * [B(S) - (1-ATB) * B(F)]
            
        This collapses to:
        
            (1-ATB) * F < S + Constant
            
        ... or (since ATB is also known and can be incorporated into the constant)
        
             F < S / (1-ATB) + Constant
        
        The generated tuning rules need to support this (often non-integer) complexity.
        """
        tune.pk = None  # force PK update
        tune.faster_than = mons[tune.faster_than.monster_id]
        tune.slower_than = mons[tune.slower_than.monster_id]
        # tune.leader = leader SPD %
        tune.save()
    composite.save()
    return composite


def eliminate_redundant_constraints_mon(monster):
    tunes = set([t for t in monster.slower_than_by.all()])
    while tunes:
        left = tunes.pop()
        for right in tunes:
            if left.slower_than_id != right.slower_than_id:
                continue
            if right.type == models.SpeedTune.SPD_ANY_AMOUNT:
                # ANY is the most general so we can toss it in favor of any other relationship
                right.delete()
                continue
            elif left.type == models.SpeedTune.SPD_ANY_AMOUNT:
                # ANY is the most general so we can toss it in favor of any other relationship
                left.delete()
                break  # no more comparisons make sense if we remove left
            if left.type != right.type:
                continue
            if right.amount > left.amount:
                # parent is less constraining than implied constraint
                right.delete()
                continue
            elif left.amount > right.amount:
                left.delete()
                break  # no more comparisons make sense if we remove left


def eliminate_redundant_constraints(team):
    analyzed = {}
    monsters = set([m for m in team.monsters.all()])
    # make sure the first "progress" check clears
    for monster in monsters:
        eliminate_redundant_constraints_mon(monster)

    count = len(monsters) + 1
    while monsters:
        # make sure we make progress on each pass
        if len(monsters) == count:
            raise Exception("Cyclic Constraint Detected")
        count = len(monsters)

        processed = set()
        for stat in monsters:
            # if all of the parents aren't present, delay and retry
            delay = False
            for parent in stat.slower_than_by.all():
                if parent.slower_than_id not in analyzed:
                    delay = True
                    break
            if delay:
                continue
            processed.add(stat)

            ####### DUPLICATE LOGIC ########
            # create tracking object
            current = analyzed[stat.id] = []
            for parent in stat.slower_than_by.all():
                # Infer relationship from Parent and Grandparent
                # Parent + Grand = Integrated
                #    ANY +     * = ANY
                #      * +   ANY = ANY
                #    MIN +   MIN = MIN <<
                #    MIN +  FLAT = ANY
                #    MIN +     % = ANY
                #   FLAT +   MIN = ANY
                #   FLAT +  FLAT = FLAT (a + b)
                #   FLAT +     % = ANY
                #      % +   MIN = ANY
                #      % +  FLAT = ANY
                #      % +     % = %    1 - (1-a)*(1-b)
                for grand in analyzed[parent.slower_than_id]:
                    amount = None
                    if parent.type == grand.type == models.SpeedTune.SPD_AS_LITTLE_AS_POSSIBLE:
                        # MIN + MIN
                        type = models.SpeedTune.SPD_AS_LITTLE_AS_POSSIBLE
                    elif parent.type == grand.type == models.SpeedTune.SPD_WITHIN_FLAT:
                        type = models.SpeedTune.SPD_WITHIN_FLAT
                        amount = parent.amount + grand.amount
                    elif parent.type == grand.type == models.SpeedTune.SPD_WITHIN_PERCENT:
                        type = models.SpeedTune.SPD_WITHIN_PERCENT
                        amount = 1 - (1-parent.amount) * (1-grand.amount)
                    else:
                        type = models.SpeedTune.SPD_ANY_AMOUNT
                    # Create the implied constraint
                    implied_constraint = models.SpeedTune(
                        slower_than=grand.slower_than,
                        faster_than=stat,
                        type=type,
                        amount=amount,
                    )
                    implied_constraint.depends_on = parent
                    current.append(implied_constraint)
            # remove redundant constraints
            redundant = []
            for parent in stat.slower_than_by.all():
                for implied in current:
                    if parent.slower_than_id != implied.slower_than_id:
                        continue
                    if parent.faster_than_id != implied.faster_than_id:
                        continue
                    if parent.type == models.SpeedTune.SPD_ANY_AMOUNT:
                        # can always toss an ANY in favor of an implied relationship
                        redundant.append(parent)
                        continue
                    if parent.type != implied.type:
                        continue
                    if parent.amount > implied.amount:
                        # parent is less constraining than implied constraint
                        redundant.append(parent)
                        continue
            for parent in stat.slower_than_by.all():
                if parent not in redundant:
                    current.append(parent)
            for constraint in redundant:
                constraint.delete()
            ####### END DUPLICATE LOGIC ########

        monsters = monsters - processed
