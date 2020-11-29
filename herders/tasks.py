from celery import shared_task, current_task, states
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins
from django.db import transaction
from django.db.models.signals import post_save

from .models import Summoner, MaterialStorage, MonsterShrineStorage, MonsterInstance, MonsterPiece, RuneInstance, RuneCraftInstance, BuildingInstance, ArtifactCraftInstance, ArtifactInstance
from .profile_parser import parse_sw_json
from .signals import update_profile_date


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
        current_task.update_state(state=states.STARTED, meta={'step': 'preprocessing'})

    # Import the new objects
    with transaction.atomic():
        if import_options['clear_profile']:
            RuneInstance.objects.filter(owner=summoner).delete()
            RuneCraftInstance.objects.filter(owner=summoner).delete()
            ArtifactInstance.objects.filter(owner=summoner).delete()
            ArtifactCraftInstance.objects.filter(owner=summoner).delete()
            MonsterInstance.objects.filter(owner=summoner).delete()
            MonsterPiece.objects.filter(owner=summoner).delete()

    results = parse_sw_json(data, summoner, import_options)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={'step': 'summoner'})

    # Disconnect summoner profile last update post-save signal to avoid mass spamming updates
    post_save.disconnect(update_profile_date, sender=MonsterInstance)
    post_save.disconnect(update_profile_date, sender=RuneInstance)
    post_save.disconnect(update_profile_date, sender=RuneCraftInstance)

    with transaction.atomic():
        # Update summoner and inventory
        if results['wizard_id']:
            summoner.com2us_id = results['wizard_id']
            summoner.save()

        # TODO: update Storage to new db 
        # summoner.storage.magic_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_magic_low', 0)
        # summoner.storage.magic_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_magic_mid', 0)
        # summoner.storage.magic_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_magic_high', 0)
        # summoner.storage.fire_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_fire_low', 0)
        # summoner.storage.fire_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_fire_mid', 0)
        # summoner.storage.fire_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_fire_high', 0)
        # summoner.storage.water_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_water_low', 0)
        # summoner.storage.water_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_water_mid', 0)
        # summoner.storage.water_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_water_high', 0)
        # summoner.storage.wind_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_wind_low', 0)
        # summoner.storage.wind_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_wind_mid', 0)
        # summoner.storage.wind_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_wind_high', 0)
        # summoner.storage.light_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_light_low', 0)
        # summoner.storage.light_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_light_mid', 0)
        # summoner.storage.light_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_light_high', 0)
        # summoner.storage.dark_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_dark_low', 0)
        # summoner.storage.dark_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_dark_mid', 0)
        # summoner.storage.dark_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_dark_high', 0)

        # summoner.storage.wood = results['inventory'].get('wood', 0)
        # summoner.storage.leather = results['inventory'].get('leather', 0)
        # summoner.storage.rock = results['inventory'].get('rock', 0)
        # summoner.storage.ore = results['inventory'].get('ore', 0)
        # summoner.storage.mithril = results['inventory'].get('mithril', 0)
        # summoner.storage.cloth = results['inventory'].get('cloth', 0)
        # summoner.storage.rune_piece = results['inventory'].get('rune_piece', 0)
        # summoner.storage.dust = results['inventory'].get('powder', 0)
        # summoner.storage.symbol_harmony = results['inventory'].get('symbol_harmony', 0)
        # summoner.storage.symbol_transcendance = results['inventory'].get('symbol_transcendance', 0)
        # summoner.storage.symbol_chaos = results['inventory'].get('symbol_chaos', 0)
        # summoner.storage.crystal_water = results['inventory'].get('crystal_water', 0)
        # summoner.storage.crystal_fire = results['inventory'].get('crystal_fire', 0)
        # summoner.storage.crystal_wind = results['inventory'].get('crystal_wind', 0)
        # summoner.storage.crystal_light = results['inventory'].get('crystal_light', 0)
        # summoner.storage.crystal_dark = results['inventory'].get('crystal_dark', 0)
        # summoner.storage.crystal_magic = results['inventory'].get('crystal_magic', 0)
        # summoner.storage.crystal_pure = results['inventory'].get('crystal_pure', 0)
        # summoner.storage.conversion_stone = results['inventory'].get('conversion_stone', 0)

        # summoner.storage.fire_angelmon = results['inventory'].get('fire_angelmon', 0)
        # summoner.storage.water_angelmon = results['inventory'].get('water_angelmon', 0)
        # summoner.storage.wind_angelmon = results['inventory'].get('wind_angelmon', 0)
        # summoner.storage.light_angelmon = results['inventory'].get('light_angelmon', 0)
        # summoner.storage.dark_angelmon = results['inventory'].get('dark_angelmon', 0)
        # summoner.storage.fire_king_angelmon = results['inventory'].get('fire_king_angelmon', 0)
        # summoner.storage.water_king_angelmon = results['inventory'].get('water_king_angelmon', 0)
        # summoner.storage.wind_king_angelmon = results['inventory'].get('wind_king_angelmon', 0)
        # summoner.storage.light_king_angelmon = results['inventory'].get('light_king_angelmon', 0)
        # summoner.storage.dark_king_angelmon = results['inventory'].get('dark_king_angelmon', 0)
        # summoner.storage.super_angelmon = results['inventory'].get('super_angelmon', 0)
        # summoner.storage.devilmon = results['inventory'].get('devilmon', 0)
        # summoner.storage.rainbowmon_2_20 = results['inventory'].get('rainbowmon_2_20', 0)
        # summoner.storage.rainbowmon_3_1 = results['inventory'].get('rainbowmon_3_1', 0)
        # summoner.storage.rainbowmon_3_25 = results['inventory'].get('rainbowmon_3_25', 0)
        # summoner.storage.rainbowmon_4_1 = results['inventory'].get('rainbowmon_4_1', 0)
        # summoner.storage.rainbowmon_4_30 = results['inventory'].get('rainbowmon_4_30', 0)
        # summoner.storage.rainbowmon_5_1 = results['inventory'].get('rainbowmon_5_1', 0)

        # summoner.storage.save()

        # Save imported buildings
        for bldg in results['buildings']:
            bldg.save()

        # Set missing buildings to level 0
        BuildingInstance.objects.filter(owner=summoner).exclude(pk__in=[bldg.pk for bldg in results['buildings']]).update(level=0)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={'step': 'monsters'})

    with transaction.atomic():
        # Save the imported monsters
        for mon in results['monsters']:
            mon.save()
            imported_monsters.append(mon.pk)

        # Update saved monster pieces
        for piece in results['monster_pieces']:
            piece.save()
            imported_pieces.append(piece.pk)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={'step': 'runes'})

    with transaction.atomic():
        # Save imported runes
        for rune in results['runes']:
            # Refresh the internal assigned_to_id field, as the monster didn't have a PK when the
            # relationship was previously set.
            rune.assigned_to = rune.assigned_to
            rune.save()
            imported_runes.append(rune.pk)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={'step': 'rta_builds'})

    with transaction.atomic():
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
                mon = MonsterInstance.objects.filter(owner=summoner).get(com2us_id=mon_id)
                runes = RuneInstance.objects.filter(owner=summoner, com2us_id__in=rune_ids)
                mon.rta_build.runes.set(runes, clear=True)
            except (MonsterInstance.MultipleObjectsReturned, MonsterInstance.DoesNotExist):
                # Continue with import in case monster was not imported or doesn't exist in user profile for some reason
                continue
            except ValidationError:
                slots = runes.values_list('slot', flat=True)
                mail_admins('Rune Build Validation Error', f'monster: {mon.id}\r\nrunes: {rune_ids}\r\nslots: {slots}')

                # Continue with import
                continue

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={'step': 'rune_crafts'})

    with transaction.atomic():
        # Save imported rune crafts
        for craft in results['rune_crafts']:
            craft.save()
            imported_crafts.append(craft.pk)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={'step': 'artifacts'})

    with transaction.atomic():
        # Save imported artifacts
        for artifact in results['artifacts']:
            # Refresh the internal assigned_to_id field, as the monster didn't have a PK when the
            # relationship was previously set.
            artifact.assigned_to = artifact.assigned_to
            artifact.save()
            imported_artifacts.append(artifact.pk)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={'step': 'artifact_crafts'})

    with transaction.atomic():
        # Save imported artifact crafts
        for craft in results['artifact_crafts']:
            craft.save()
            imported_artifact_crafts.append(craft.pk)

    with transaction.atomic():
        # Delete objects missing from import
        if import_options['delete_missing_monsters']:
            MonsterInstance.objects.filter(owner=summoner).exclude(pk__in=imported_monsters).delete()
            MonsterPiece.objects.filter(owner=summoner).exclude(pk__in=imported_pieces).delete()

        if import_options['delete_missing_runes']:
            RuneInstance.objects.filter(owner=summoner).exclude(pk__in=imported_runes).delete()
            RuneCraftInstance.objects.filter(owner=summoner).exclude(pk__in=imported_crafts).delete()
            ArtifactInstance.objects.filter(owner=summoner).exclude(pk__in=imported_artifacts).delete()
            ArtifactCraftInstance.objects.filter(owner=summoner).exclude(pk__in=imported_artifact_crafts).delete()
