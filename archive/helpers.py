from django.db.models import Q

import math
from pytz.exceptions import NonExistentTimeError

from archive.models.log_models import WorldBossLogArchive, WorldBossLogItemDropArchive, WorldBossLogMonsterDropArchive, WorldBossLogRuneDropArchive, \
    WishLogArchive, WishLogItemDropArchive, WishLogMonsterDropArchive, WishLogRuneDropArchive, \
    DungeonArtifactDropArchive, DungeonItemDropArchive, DungeonLogArchive, DungeonMonsterDropArchive, DungeonMonsterPieceDropArchive, \
    DungeonRuneCraftDropArchive, DungeonRuneDropArchive, DungeonSecretDungeonDropArchive, \
    RiftDungeonItemDropArchive, RiftDungeonLogArchive, RiftDungeonMonsterDropArchive, RiftDungeonRuneCraftDropArchive, RiftDungeonRuneDropArchive, \
    RiftRaidLogArchive, RiftRaidItemDropArchive, RiftRaidMonsterDropArchive, RiftRaidRuneCraftDropArchive, \
    MagicBoxCraftArchive, MagicBoxCraftItemDropArchive, MagicBoxCraftRuneCraftDropArchive, MagicBoxCraftRuneDropArchive, \
    ShopRefreshLogArchive, ShopRefreshItemDropArchive, ShopRefreshMonsterDropArchive, ShopRefreshRuneDropArchive, \
    SummonLogArchive, CraftRuneLogArchive, FullLogArchive
from archive.models.report_models import WishReportArchive, LevelReportArchive, SummonReportArchive, \
    RuneCraftingReportArchive, MagicShopRefreshReportArchive, MagicBoxCraftingReportArchive
from data_log.models.log_models import WorldBossLog, WishLog, DungeonLog, RiftDungeonLog, RiftRaidLog, MagicBoxCraft, ShopRefreshLog, SummonLog, CraftRuneLog, FullLog
from data_log.models.report_models import WishReport, LevelReport, SummonReport, MagicShopRefreshReport, \
    RuneCraftingReport, MagicBoxCraftingReport


BATCH_SIZE = 5000

def _archive_log(date_to, options):
    log_model = options['log_model']
    archive_model = options['archive_model']
    filter_field = options['filter_field']
    is_dungeon = options.get('is_dungeon', False)

    # sub-tables
    item_submodel = options.get('item_submodel', None)
    monster_submodel = options.get('monster_submodel', None)
    monster_pieces_submodel = options.get('monster_pieces_submodel', None)
    rune_submodel = options.get('rune_submodel', None)
    rune_crafts_submodel = options.get('rune_crafts_submodel', None)
    artifact_submodel = options.get('artifact_submodel', None)
    secret_dungeon_submodel = options.get('secret_dungeon_submodel', None)

    select_related = ['summoner']
    if is_dungeon:
        select_related.append('level')

    prefetch_related = []
    if item_submodel:
        prefetch_related.append('items')
    if monster_submodel:
        prefetch_related.append('monsters')
    if monster_pieces_submodel:
        prefetch_related.append('monster_pieces')
    if rune_submodel:
        prefetch_related.append('runes')
    if rune_crafts_submodel:
        prefetch_related.append('rune_crafts')
    if artifact_submodel:
        prefetch_related.append('artifacts')
    if secret_dungeon_submodel:
        prefetch_related.append('secret_dungeons')

    q_log = Q(**{filter_field + '__lte': date_to})
    qs_log = log_model.objects.filter(q_log).select_related(*select_related)
    if prefetch_related:
        qs_log = qs_log.prefetch_related(*prefetch_related)
    
    qs_log_c = qs_log.count()
    batches = math.ceil(qs_log_c / BATCH_SIZE)
    print(f"[{log_model.__name__}] To archive: {str(batches)} batches, which equals {str(qs_log_c)}")
    for idb in range(batches):
        to_create_item_drop_archive = []
        to_create_monster_drop_archive = []
        to_create_monster_pieces_drop_archive = []
        to_create_rune_drop_archive = []
        to_create_rune_crafts_drop_archive = []
        to_create_artifact_drop_archive = []
        to_create_secret_dungeon_drop_archive = []
        ids_to_delete = []
        for log in qs_log[:BATCH_SIZE]:
            try:
                archive_log = archive_model.objects.create(**archive_model.archive_data(log))

                if item_submodel:
                    to_create_item_drop_archive += [item_submodel(
                        **item_submodel.archive_data(archive_log, item)
                    ) for item in log.items.all()]

                if monster_submodel:
                    to_create_monster_drop_archive += [monster_submodel(
                        **monster_submodel.archive_data(archive_log, monster)
                    ) for monster in log.monsters.all()]

                if monster_pieces_submodel:
                    to_create_monster_pieces_drop_archive += [monster_pieces_submodel(
                        **monster_pieces_submodel.archive_data(archive_log, item)
                    ) for item in log.monster_pieces.all()]

                if rune_submodel:
                    to_create_rune_drop_archive += [rune_submodel(
                        **rune_submodel.archive_data(archive_log, rune)
                    ) for rune in log.runes.all()]

                if rune_crafts_submodel:
                    to_create_rune_crafts_drop_archive += [rune_crafts_submodel(
                        **rune_crafts_submodel.archive_data(archive_log, item)
                    ) for item in log.rune_crafts.all()]

                if artifact_submodel:
                    to_create_artifact_drop_archive += [artifact_submodel(
                        **artifact_submodel.archive_data(archive_log, item)
                    ) for item in log.artifacts.all()]

                if secret_dungeon_submodel:
                    to_create_secret_dungeon_drop_archive += [secret_dungeon_submodel(
                        **secret_dungeon_submodel.archive_data(archive_log, item)
                    ) for item in log.secret_dungeons.all()]
            except NonExistentTimeError:
                pass

            ids_to_delete.append(log.id)
        
        log_model.objects.filter(pk__in=ids_to_delete).delete()
        _iter = min((idb + 1) * BATCH_SIZE, qs_log_c)
        print(f"[{archive_model.__name__}] {str(_iter)}/{str(qs_log_c)} ({str(round(_iter / qs_log_c * 100, 2))}%)")
        
        if item_submodel:
            item_submodel.objects.bulk_create(to_create_item_drop_archive, batch_size=BATCH_SIZE)
        if monster_submodel:
            monster_submodel.objects.bulk_create(to_create_monster_drop_archive, batch_size=BATCH_SIZE)
        if monster_pieces_submodel:
            monster_pieces_submodel.objects.bulk_create(to_create_monster_pieces_drop_archive, batch_size=BATCH_SIZE)
        if rune_submodel:
            rune_submodel.objects.bulk_create(to_create_rune_drop_archive, batch_size=BATCH_SIZE)
        if rune_crafts_submodel:
            rune_crafts_submodel.objects.bulk_create(to_create_rune_crafts_drop_archive, batch_size=BATCH_SIZE)
        if artifact_submodel:
            artifact_submodel.objects.bulk_create(to_create_artifact_drop_archive, batch_size=BATCH_SIZE)
        if secret_dungeon_submodel:
            secret_dungeon_submodel.objects.bulk_create(to_create_secret_dungeon_drop_archive, batch_size=BATCH_SIZE)


def archive_world_boss_logs(date_to):
    options = {
        'log_model': WorldBossLog,
        'archive_model': WorldBossLogArchive,
        'filter_field': 'timestamp',
        'is_dungeon': True,

        'item_submodel': WorldBossLogItemDropArchive,
        'monster_submodel': WorldBossLogMonsterDropArchive,
        'rune_submodel': WorldBossLogRuneDropArchive,
    }
    _archive_log(date_to, options)


def archive_wish_logs(date_to):
    options = {
        'log_model': WishLog,
        'archive_model': WishLogArchive,
        'filter_field': 'timestamp',

        'item_submodel': WishLogItemDropArchive,
        'monster_submodel': WishLogMonsterDropArchive,
        'rune_submodel': WishLogRuneDropArchive,
    }
    _archive_log(date_to, options)


def archive_dungeon_logs(date_to):
    options = {
        'log_model': DungeonLog,
        'archive_model': DungeonLogArchive,
        'filter_field': 'timestamp',
        'is_dungeon': True,

        'item_submodel': DungeonItemDropArchive,
        'monster_submodel': DungeonMonsterDropArchive,
        'monster_pieces_submodel': DungeonMonsterPieceDropArchive,
        'rune_submodel': DungeonRuneDropArchive,
        'rune_crafts_submodel': DungeonRuneCraftDropArchive,
        'artifact_submodel': DungeonArtifactDropArchive,
        'secret_dungeon_submodel': DungeonSecretDungeonDropArchive,
    }
    _archive_log(date_to, options)


def archive_rift_dungeon_logs(date_to):
    options = {
        'log_model': RiftDungeonLog,
        'archive_model': RiftDungeonLogArchive,
        'filter_field': 'timestamp',
        'is_dungeon': True,

        'item_submodel': RiftDungeonItemDropArchive,
        'monster_submodel': RiftDungeonMonsterDropArchive,
        'rune_submodel': RiftDungeonRuneDropArchive,
        'rune_crafts_submodel': RiftDungeonRuneCraftDropArchive,
    }
    _archive_log(date_to, options)


def archive_raid_dungeon_logs(date_to):
    options = {
        'log_model': RiftRaidLog,
        'archive_model': RiftRaidLogArchive,
        'filter_field': 'timestamp',
        'is_dungeon': True,

        'item_submodel': RiftRaidItemDropArchive,
        'monster_submodel': RiftRaidMonsterDropArchive,
        'rune_crafts_submodel': RiftRaidRuneCraftDropArchive,
    }
    _archive_log(date_to, options)


def archive_magic_box_craft_logs(date_to):
    options = {
        'log_model': MagicBoxCraft,
        'archive_model': MagicBoxCraftArchive,
        'filter_field': 'timestamp',

        'item_submodel': MagicBoxCraftItemDropArchive,
        'rune_submodel': MagicBoxCraftRuneDropArchive,
        'rune_crafts_submodel': MagicBoxCraftRuneCraftDropArchive,
    }
    _archive_log(date_to, options)


def archive_shop_refresh_logs(date_to):
    options = {
        'log_model': ShopRefreshLog,
        'archive_model': ShopRefreshLogArchive,
        'filter_field': 'timestamp',

        'item_submodel': ShopRefreshItemDropArchive,
        'rune_submodel': ShopRefreshRuneDropArchive,
        'monster_submodel': ShopRefreshMonsterDropArchive,
    }
    _archive_log(date_to, options)


def archive_summon_logs(date_to):
    options = {
        'log_model': SummonLog,
        'archive_model': SummonLogArchive,
        'filter_field': 'timestamp',
    }
    _archive_log(date_to, options)


def archive_craft_rune_logs(date_to):
    options = {
        'log_model': CraftRuneLog,
        'archive_model': CraftRuneLogArchive,
        'filter_field': 'timestamp',
    }
    _archive_log(date_to, options)


def archive_full_logs(date_to):
    options = {
        'log_model': FullLog,
        'archive_model': FullLogArchive,
        'filter_field': 'timestamp',
    }
    _archive_log(date_to, options)


def archive_reports(date_to):
    q_report = Q(generated_on__lte=date_to)

    report_archive_map = {
        WishReport: WishReportArchive,
        LevelReport: LevelReportArchive,
        SummonReport: SummonReportArchive,
        MagicShopRefreshReport: MagicShopRefreshReportArchive,
        MagicBoxCraftingReport: MagicBoxCraftingReportArchive,
        RuneCraftingReport: RuneCraftingReportArchive,
    }

    for report_model, archive_model in report_archive_map.items():
        qs_report = report_model.objects.filter(q_report).select_related('report_ptr')
        qs_report_c = qs_report.count()
        batches = math.ceil(qs_report_c / BATCH_SIZE)
        print(f"[{report_model.__name__}] To archive: {str(batches)} batches, which equals {str(qs_report_c)}")
        for idb in range(batches):
            ids_to_delete = []
            archive_to_create = []
            for report in qs_report[:BATCH_SIZE]:
                data = {
                    'content_type': report.content_type,
                    'generated_on': report.generated_on,
                    'start_timestamp': report.start_timestamp,
                    'end_timestamp': report.end_timestamp,
                    'log_count': report.log_count,
                    'unique_contributors': report.unique_contributors,
                    'report': report.report,
                    'generated_by_user': report.generated_by_user,
                }
                if report_model == LevelReport:
                    data['level_id'] = report.level_id
                elif report_model == SummonReport:
                    data['item_id'] = report.item_id
                elif report_model == MagicBoxCraftingReport:
                    data['box_type'] = report.box_type
                elif report_model == RuneCraftingReport:
                    data['craft_level'] = report.craft_level
                
                archive_to_create.append(archive_model(**data))
                ids_to_delete.append(report.id)
            
            archive_model.objects.bulk_create(archive_to_create, batch_size=BATCH_SIZE)
            report_model.objects.filter(pk__in=ids_to_delete).delete()
            _iter = min((idb + 1) * BATCH_SIZE, qs_report_c)
            print(f"[{archive_model.__name__}] {str(_iter)}/{str(qs_report_c)} ({str(round(_iter / qs_report_c * 100, 2))}%)")
