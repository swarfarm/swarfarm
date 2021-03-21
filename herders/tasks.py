from celery import shared_task, current_task, states
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins
from django.db import transaction, IntegrityError
from django.db.models.signals import post_save

from .models import Summoner, MaterialStorage, MonsterShrineStorage, MonsterInstance, MonsterPiece, RuneInstance, RuneCraftInstance, BuildingInstance, ArtifactCraftInstance, ArtifactInstance
from .profile_parser import parse_sw_json
from .signals import update_profile_date

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
    with transaction.atomic():
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
    post_save.disconnect(update_profile_date, sender=BuildingInstance)

    with transaction.atomic():
        # Update summoner and inventory
        if results['wizard_id']:
            summoner.com2us_id = results['wizard_id']
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

        # Save imported buildings
        for bldg in results['buildings'].values():
            if bldg['new']:
                bldg['obj'].save()

        # Set missing buildings to level 0
        BuildingInstance.objects.filter(owner=summoner).exclude(
            pk__in=results['buildings'].keys()).update(level=0)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={'step': 'runes'})

    with transaction.atomic():
        # Save imported runes
        for rune in results['runes'].values():
            rune.save()
            imported_runes.append(rune.pk)

    if not current_task.request.called_directly:
        current_task.update_state(
            state=states.STARTED, meta={'step': 'artifacts'})

    with transaction.atomic():
        # Save imported artifacts
        for artifact in results['artifacts'].values():
            artifact.save()
            imported_artifacts.append(artifact.pk)

    if not current_task.request.called_directly:
        current_task.update_state(
            state=states.STARTED, meta={'step': 'monsters'})

    with transaction.atomic():
        # Save the imported monsters
        for mon in results['monsters'].values():
            mon['obj'].save()
            mon['obj'].default_build.runes.set(mon['runes'], clear=True)
            mon['obj'].default_build.artifacts.set(mon['artifacts'], clear=True)
            mon['obj'].rta_build.runes.clear()
            mon['obj'].rta_build.artifacts.clear()
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

    with transaction.atomic():
        # Save imported rune crafts
        for craft in results['rune_crafts'].values():
            if craft['new']:
                craft['obj'].save()
            imported_crafts.append(craft['obj'].pk)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={
                                  'step': 'artifact_crafts'})

    with transaction.atomic():
        # Save imported artifact crafts
        for craft in results['artifact_crafts'].values():
            if craft['new']:
                craft['obj'].save()
            imported_artifact_crafts.append(craft['obj'].pk)

    if not current_task.request.called_directly:
        current_task.update_state(state=states.STARTED, meta={
                                  'step': 'rta_builds'})

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
                mon = MonsterInstance.objects.filter(
                    owner=summoner).get(com2us_id=mon_id)
                runes = RuneInstance.objects.filter(
                    owner=summoner, com2us_id__in=rune_ids)
                mon.rta_build.runes.set(runes, clear=True)
            except (MonsterInstance.MultipleObjectsReturned, MonsterInstance.DoesNotExist):
                # Continue with import in case monster was not imported or doesn't exist in user profile for some reason
                continue
            except ValidationError:
                slots = runes.values_list('slot', flat=True)
                mail_admins('Rune Build Validation Error',
                            f'monster: {mon.id}\r\nrunes: {rune_ids}\r\nslots: {slots}')

                # Continue with import
                continue

        # Set RTA artofact builds assignments
        assignments = {}
        for assignment in results['rta_assignments_artifacts']:
            mon_com2us_id = assignment['occupied_id']
            if mon_com2us_id not in assignments:
                assignments[mon_com2us_id] = []
            assignments[mon_com2us_id].append(assignment['artifact_id'])
        for mon_id, artifact_ids in assignments.items():
            try:
                mon = MonsterInstance.objects.filter(
                    owner=summoner).get(com2us_id=mon_id)
                artifacts = ArtifactInstance.objects.filter(
                    owner=summoner, com2us_id__in=artifact_ids)
                mon.rta_build.artifacts.set(artifacts, clear=True)
            except (MonsterInstance.MultipleObjectsReturned, MonsterInstance.DoesNotExist):
                # Continue with import in case monster was not imported or doesn't exist in user profile for some reason
                continue
            except ValidationError:
                slots = artifacts.values_list('slot', flat=True)
                mail_admins('Artifaact Build Validation Error',
                            f'monster: {mon.id}\r\artifacts: {artifact_ids}\r\nslots: {slots}')

                # Continue with import
                continue


    with transaction.atomic():
        # Delete objects missing from import
        if import_options['delete_missing_monsters']:
            MonsterInstance.objects.filter(owner=summoner).exclude(
                pk__in=imported_monsters).delete()
            MonsterPiece.objects.filter(owner=summoner).exclude(
                pk__in=imported_pieces).delete()

        if import_options['delete_missing_runes']:
            RuneInstance.objects.filter(owner=summoner).exclude(
                pk__in=imported_runes).delete()
            RuneCraftInstance.objects.filter(owner=summoner).exclude(
                pk__in=imported_crafts).delete()
            ArtifactInstance.objects.filter(owner=summoner).exclude(
                pk__in=imported_artifacts).delete()
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
