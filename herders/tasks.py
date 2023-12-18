from celery import shared_task, current_task, states
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins
from django.db import IntegrityError
from django.db.models.signals import post_save, m2m_changed

from .models import RuneBuild, Summoner, MaterialStorage, MonsterShrineStorage, MonsterInstance, MonsterPiece, \
    RuneInstance, RuneCraftInstance, ArtifactCraftInstance, ArtifactInstance, LevelSkillInstance
from .profile_parser import parse_sw_json
from .signals import update_profile_date, validate_rune_build_runes, validate_rune_build_artifacts, update_rune_build_stats

from bestiary.models import GameItem, Monster


@shared_task
def com2us_data_import(data, user_id, import_options):
    summoner = Summoner.objects.get(pk=user_id)
    imported_monsters = []
    imported_runes = []
    imported_crafts = []
    imported_artifacts = []
    imported_artifact_crafts = []
    imported_pieces = []

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={
                                  'step': 'preprocessing'})

    # Import the new objects
    if import_options['clear_profile']:
        RuneInstance.objects.filter(owner=summoner).delete()
        RuneCraftInstance.objects.filter(owner=summoner).delete()
        ArtifactInstance.objects.filter(owner=summoner).delete()
        ArtifactCraftInstance.objects.filter(owner=summoner).delete()
        MonsterInstance.objects.filter(owner=summoner).delete()
        MonsterPiece.objects.filter(owner=summoner).delete()
        MaterialStorage.objects.filter(owner=summoner).delete()
        MonsterShrineStorage.objects.filter(owner=summoner).delete()

    results = parse_sw_json(data, summoner, import_options)

    if not current_task.request.called_directly:
        current_task.update_state(
            state=states.STARTED, meta={'step': 'summoner'})

    # Disconnect summoner profile last update post-save signal to avoid mass spamming updates
    post_save.disconnect(update_profile_date, sender=MonsterInstance)
    post_save.disconnect(update_profile_date, sender=MonsterPiece)
    post_save.disconnect(update_profile_date, sender=RuneInstance)
    post_save.disconnect(update_profile_date, sender=RuneCraftInstance)
    post_save.disconnect(update_profile_date, sender=ArtifactInstance)
    post_save.disconnect(update_profile_date, sender=ArtifactCraftInstance)
    post_save.disconnect(update_profile_date, sender=MaterialStorage)
    post_save.disconnect(update_profile_date, sender=MonsterShrineStorage)
    post_save.disconnect(update_profile_date, sender=LevelSkillInstance)
    # Disconnect Rune Build m2m-changed signal to avoid mass spamming updates
    # We'll update it explicitly
    m2m_changed.disconnect(validate_rune_build_runes, sender=RuneBuild.runes.through)
    m2m_changed.disconnect(validate_rune_build_artifacts, sender=RuneBuild.artifacts.through)
    m2m_changed.disconnect(update_rune_build_stats, sender=RuneBuild.runes.through)
    m2m_changed.disconnect(update_rune_build_stats, sender=RuneBuild.artifacts.through)

    # Update summoner and inventory
    if results['wizard_id']:
        summoner.com2us_id = results['wizard_id']
        summoner.server = results['server_id']
        summoner.save()

    # inventory bulk update or create
    # firstly, delete all Summoner MaterialStorage records, if GameItem points to `UNKNOWN ITEM`
    MaterialStorage.objects.select_related('item').filter(owner=summoner).exclude(item__category__in=dict(GameItem.CATEGORY_CHOICES).keys()).delete()
    all_inv_items = {gi.com2us_id: gi for gi in GameItem.objects.filter(category__in=dict(GameItem.CATEGORY_CHOICES).keys())}  # to handle some `UNKNOWN ITEM` records
    summoner_inv_items = {ms.item.com2us_id: ms for ms in MaterialStorage.objects.select_related(
        'item').filter(owner=summoner)}
    summoner_new_inv_items = []
    summoner_old_inv_items = []
    summoner_inv_items_pks = []
    for key, val in results['inventory'].items():
        if key not in all_inv_items:
            continue  # GameItem doesn't exist
        if key in summoner_inv_items:
            summoner_inv_items_pks.append(summoner_inv_items[key].pk)
            if summoner_inv_items[key].quantity != val:
                summoner_old_inv_items.append(summoner_inv_items[key])
                summoner_old_inv_items[-1].quantity = val
        else:
            summoner_new_inv_items.append(MaterialStorage(
                owner=summoner,
                item=all_inv_items[key],
                quantity=val)
            )

    # inventory, remove old records if not existing in JSON anymore
    MaterialStorage.objects.filter(owner=summoner).exclude(pk__in=summoner_inv_items_pks).delete()
    MaterialStorage.objects.bulk_create(summoner_new_inv_items)
    MaterialStorage.objects.bulk_update(
        summoner_old_inv_items, ['quantity'])

    # parse Monster Shrine Storage only when it's presented in JSON file
    if isinstance(data.get('unit_storage_list'), list):
        # monster shrine bulk update or create
        all_monsters = {m.com2us_id: m for m in Monster.objects.all()}
        summoner_mon_shrine = {mss.item.com2us_id: mss for mss in MonsterShrineStorage.objects.select_related(
            'item').filter(owner=summoner)}
        summoner_new_mon_shrine = []
        summoner_old_mon_shrine = []
        summoner_mon_shrine_pks = []
        for key, val in results['monster_shrine'].items():
            if key not in all_monsters:
                continue  # Monster doesn't exist
            if key in summoner_mon_shrine:
                summoner_mon_shrine_pks.append(summoner_mon_shrine[key].pk)
                if summoner_mon_shrine[key].quantity != val:
                    summoner_old_mon_shrine.append(summoner_mon_shrine[key])
                    summoner_old_mon_shrine[-1].quantity = val
            else:
                summoner_new_mon_shrine.append(MonsterShrineStorage(
                    owner=summoner,
                    item=all_monsters[key],
                    quantity=val)
                )

        # monster shrine, remove old records if not existing in JSON anymore
        MonsterShrineStorage.objects.filter(owner=summoner).exclude(pk__in=summoner_mon_shrine_pks).delete()
        MonsterShrineStorage.objects.bulk_create(summoner_new_mon_shrine)
        MonsterShrineStorage.objects.bulk_update(summoner_old_mon_shrine, ['quantity'])

    # Save imported summoner skills
    for lvl_skill in results['level_skills'].values():
        if lvl_skill['new']:
            lvl_skill['obj'].save()
    # Set missing level_skills to level 0
    LevelSkillInstance.objects.filter(owner=summoner).exclude(
        pk__in=results['level_skills'].keys()).update(level=0)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={'step': 'runes'})

    # Save imported runes
    if results['runes']['to_create']:
        RuneInstance.objects.bulk_create(results['runes']['to_create'].values(), batch_size=1000)
    if results['runes']['to_update']:
        RuneInstance.objects.bulk_update(results['runes']['to_create'].values(), batch_size=1000, fields=[
            'type', 'marked_for_sale', 'notes', 'stars', 'level', 'slot', 'quality', 
            'original_quality', 'ancient', 'value', 'main_stat', 'main_stat_value', 
            'innate_stat', 'innate_stat_value', 'substats', 'substat_values', 
            'substats_enchanted', 'substats_grind_value', 'has_hp', 'has_atk', 
            'has_def', 'has_crit_rate', 'has_crit_dmg', 'has_speed', 'has_resist', 
            'has_accuracy', 'efficiency', 'max_efficiency', 'substat_upgrades_remaining', 
            'has_grind', 'has_gem',
        ])
    imported_runes = list(results['runes']['to_create'].keys()) + list(results['runes']['to_update'].keys())

    if not current_task.request.called_directly:
        current_task.update_state(
            state=states.STARTED, meta={'step': 'artifacts'})

    # Save imported artifacts
    if results['artifacts']['to_create']:
        ArtifactInstance.objects.bulk_create(results['artifacts']['to_create'].values(), batch_size=1000)
    if results['artifacts']['to_update']:
        ArtifactInstance.objects.bulk_update(results['artifacts']['to_create'].values(), batch_size=1000, fields=[
            'level', 'original_quality', 'main_stat', 'main_stat_value', 'effects', 'effects_value', 
            'effects_upgrade_count', 'effects_reroll_count', 'efficiency', 'max_efficiency',
        ])
    imported_artifacts = list(results['artifacts']['to_create'].keys()) + list(results['artifacts']['to_update'].keys())

    if not current_task.request.called_directly:
        current_task.update_state(
            state=states.STARTED, meta={'step': 'monsters'})

    # Refresh owner runes and artifacts to decrease query hits 
    owner_runes = {r['com2us_id']: r['id'] for r in RuneInstance.objects.values('id', 'com2us_id').filter(owner=summoner)}
    owner_artifacts = {r['com2us_id']: r['id'] for r in ArtifactInstance.objects.values('id', 'com2us_id').filter(owner=summoner)}

    # Save the imported monsters
    for mon in results['monsters'].values():
        mon['obj'].save()
        mon_runes = [owner_runes.get(c2us_id, None) for c2us_id in mon['runes'] if owner_runes.get(c2us_id, None)]
        mon_artifacts = [owner_artifacts.get(c2us_id, None) for c2us_id in mon['artifacts'] if owner_artifacts.get(c2us_id, None)]
        if mon['is_new']:
            if mon_runes:
                mon['obj'].default_build.runes.add(*mon_runes,)
            if mon_artifacts:
                mon['obj'].default_build.artifacts.add(*mon_artifacts)
            
        else:
            mon['obj'].default_build.runes.set(mon_runes, clear=True)
            mon['obj'].default_build.artifacts.set(mon_artifacts, clear=True)
            mon['obj'].rta_build.runes.clear()
            mon['obj'].rta_build.artifacts.clear()
            mon['obj'].rta_build.clear_cache_properties()
            mon['obj'].rta_build.update_stats()
            mon['obj'].rta_build.save()

        mon['obj'].default_build.clear_cache_properties()
        mon['obj'].default_build.update_stats()
        mon['obj'].default_build.save()
        imported_monsters.append(mon['obj'].pk)

    # Update saved monster pieces
    for piece in results['monster_pieces']:
        if piece['new']:
            try:
                piece['obj'].save()
            except IntegrityError:
                pass

        imported_pieces.append(piece['obj'].pk)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={
                                  'step': 'rune_crafts'})

    # Save imported rune crafts
    for craft in results['rune_crafts'].values():
        if craft['new']:
            craft['obj'].save()
        imported_crafts.append(craft['obj'].pk)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={
                                  'step': 'artifact_crafts'})

    # Save imported artifact crafts
    for craft in results['artifact_crafts'].values():
        if craft['new']:
            craft['obj'].save()
        imported_artifact_crafts.append(craft['obj'].pk)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={
                                  'step': 'rta_builds'})

    # Set RTA rune builds assignments
    # Group by assignee first
    assignments = {}
    for assignment in results['rta_assignments']:
        mon_com2us_id = assignment['occupied_id']
        if mon_com2us_id not in assignments:
            assignments[mon_com2us_id] = []
        assignments[mon_com2us_id].append(assignment['rune_id'])

    for mon_id, rune_ids in assignments.items():
        try:
            mon = results['monsters'].get(mon_id, None)
            if not mon:
                continue
            mon_runes = [owner_runes.get(c2us_id, None) for c2us_id in rune_ids if owner_runes.get(c2us_id, None)]
            if not mon_runes:
                continue
            if mon['is_new']:
                mon['obj'].rta_build.runes.add(*mon_runes)
            else:
                mon['obj'].rta_build.runes.set(mon_runes, clear=True)
            mon['obj'].rta_build.clear_cache_properties()
            mon['obj'].rta_build.update_stats()
            mon['obj'].rta_build.save()
        except ValidationError:
            mail_admins('Rune Build Validation Error',
                        f'monster: {mon.id}\r\nrunes: {rune_ids}')
            # Continue with import

    # Set RTA artifact builds assignments
    assignments = {}
    for assignment in results['rta_assignments_artifacts']:
        mon_com2us_id = assignment['occupied_id']
        if mon_com2us_id not in assignments:
            assignments[mon_com2us_id] = []
        assignments[mon_com2us_id].append(assignment['artifact_id'])

    for mon_id, artifact_ids in assignments.items():
        try:
            mon = results['monsters'].get(mon_id, None)
            if not mon:
                continue
            mon_artifacts = [owner_artifacts.get(c2us_id, None) for c2us_id in artifact_ids if owner_artifacts.get(c2us_id, None)]
            if not mon_artifacts:
                continue
            if mon['is_new']:
                mon['obj'].rta_build.artifacts.add(*mon_artifacts)
            else:
                mon['obj'].rta_build.artifacts.set(mon_artifacts, clear=True)
            mon['obj'].rta_build.clear_cache_properties()
            mon['obj'].rta_build.update_stats()
            mon['obj'].rta_build.save()
        except ValidationError:
            mail_admins('Artifaact Build Validation Error',
                        f'monster: {mon.id}\r\artifacts: {artifact_ids}')
            # Continue with import
            continue

    # Delete objects missing from import
    if import_options['delete_missing_monsters']:
        MonsterInstance.objects.filter(owner=summoner).exclude(
            pk__in=imported_monsters).delete()
        MonsterPiece.objects.filter(owner=summoner).exclude(
            pk__in=imported_pieces).delete()

    if import_options['delete_missing_runes']:
        RuneInstance.objects.filter(owner=summoner).exclude(
            com2us_id__in=imported_runes).delete()
        RuneCraftInstance.objects.filter(owner=summoner).exclude(
            pk__in=imported_crafts).delete()
        ArtifactInstance.objects.filter(owner=summoner).exclude(
            com2us_id__in=imported_artifacts).delete()
        ArtifactCraftInstance.objects.filter(owner=summoner).exclude(
            pk__in=imported_artifact_crafts).delete()


@shared_task
def swex_sync_monster_shrine(data, user_id):
    summoner = Summoner.objects.get(pk=user_id)

    all_monsters = {m.com2us_id: m for m in Monster.objects.all()}
    summoner_mon_shrine = {mss.item.com2us_id: mss for mss in MonsterShrineStorage.objects.select_related(
        'item').filter(owner=summoner)}
    summoner_new_mon_shrine = []
    summoner_old_mon_shrine = []
    summoner_mon_shrine_pks = []
    data_shrine_keys = []
    for mon in data['unit_storage_list']:
        key = mon['unit_master_id']
        data_shrine_keys.append(key)
        if key not in all_monsters:
            continue  # Monster doesn't exist
        if key in summoner_mon_shrine:
            summoner_mon_shrine_pks.append(summoner_mon_shrine[key].pk)
            if summoner_mon_shrine[key].quantity != mon['quantity']:
                summoner_old_mon_shrine.append(summoner_mon_shrine[key])
                summoner_old_mon_shrine[-1].quantity = mon['quantity']
        else:
            summoner_new_mon_shrine.append(MonsterShrineStorage(
                owner=summoner,
                item=all_monsters[key],
                quantity=mon['quantity'])
            )

    # monster shrine, remove old records if not existing anymore
    MonsterShrineStorage.objects.filter(owner=summoner).exclude(pk__in=summoner_mon_shrine_pks).delete()
    MonsterShrineStorage.objects.bulk_create(summoner_new_mon_shrine)
    MonsterShrineStorage.objects.bulk_update(
        summoner_old_mon_shrine, ['quantity'])


@shared_task
def update_rune_builds_for_summoner(summoner_pk):
    summoner = Summoner.objects.get(pk=summoner_pk)
    for rune_build in RuneBuild.objects.filter(owner=summoner):
        rune_build.clear_cache_properties()
        rune_build.update_stats()
        rune_build.save()
