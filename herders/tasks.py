from celery import shared_task, current_task, states
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins
from django.db import transaction
from django.db.models.signals import post_save

from .models import Summoner, MaterialStorage, MonsterShrineStorage, MonsterInstance, MonsterPiece, RuneInstance, RuneCraftInstance, BuildingInstance, ArtifactCraftInstance, ArtifactInstance
from .profile_parser import parse_sw_json
from .signals import update_profile_date

from bestiary.models import GameItem


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

        # bulk update or create
        all_inv_items = {gi.com2us_id: gi for gi in GameItem.objects.all()}
        summoner_inv_items = {ms.item_id: ms for ms in MaterialStorage.objects.filter(owner=summoner)}
        summoner_new_inv_items = []
        summoner_old_inv_items = []
        for key, val in results['inventory'].items():
            if key in summoner_inv_items:
                summoner_old_inv_items.append(summoner_inv_items[key])
                summoner_old_inv_items[-1].quantity = val
            else:
                summoner_new_inv_items.append(MaterialStorage(
                    owner=summoner, 
                    item=all_inv_items[key], 
                    quantity=val)
                )
        MaterialStorage.objects.bulk_create(summoner_new_inv_items)
        MaterialStorage.objects.bulk_update(summoner_old_inv_items, ['quantity'])

        # TODO: add summoner MonsterShrineStorage records

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
