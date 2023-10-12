from django.db.models import Q

import math
import json

from pathlib import Path

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


BATCH_SIZE = 25000
batch_sizes = [BATCH_SIZE * i / 100 for i in range(1, 101, 5)]

def _pack_log(options):
    Path('packs/').mkdir(exist_ok=True)
    log_model = options['log_model']
    archive_model = options['archive_model']
    filter_field = options['filter_field']
    is_dungeon = options.get('is_dungeon', False)
    skip_batch_to = options.get('skip_batch_to', 0)
	
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
	
    q_log = Q(**{filter_field + '__lt': "2023-01-01 00:00:00+00:00"})
    qs_log = log_model.objects.filter(q_log).select_related(*select_related)
    if prefetch_related:
        qs_log = qs_log.prefetch_related(*prefetch_related)
	
    qs_log_c = qs_log.count()
    batches = math.ceil(qs_log_c / BATCH_SIZE)
    print(f"[{log_model.__name__}] To pack: {str(batches - skip_batch_to)} batches, which equals {str(qs_log_c - skip_batch_to * BATCH_SIZE)}")
    for idb in range(batches):
        if idb < skip_batch_to: # .part#######. -> idb + 1
            print(f"[{archive_model.__name__}] Skipping batch {str(idb + 1)}")
            continue
        archives_to_pack = []
        for idl, log in enumerate(qs_log[BATCH_SIZE * idb:BATCH_SIZE * (idb + 1)]):
            archive_to_pack = archive_model.archive_data(log)
			
            if item_submodel:
                archive_to_pack["items"] = [item_submodel.archive_data(None, item) for item in log.items.all()]
			
            if monster_submodel:
                archive_to_pack["monsters"] = [monster_submodel.archive_data(None, monster) for monster in log.monsters.all()]

            if monster_pieces_submodel:
                archive_to_pack["monster_pieces"] = [monster_pieces_submodel.archive_data(None, item) for item in log.monster_pieces.all()]

            if rune_submodel:
                archive_to_pack["runes"] = [rune_submodel.archive_data(None, rune) for rune in log.runes.all()]

            if rune_crafts_submodel:
                archive_to_pack["rune_crafts"] = [rune_crafts_submodel.archive_data(None, item) for item in log.rune_crafts.all()]

            if artifact_submodel:
                archive_to_pack["artifacts"] = [artifact_submodel.archive_data(None, item) for item in log.artifacts.all()]

            if secret_dungeon_submodel:
                archive_to_pack["secret_dungeons"] = [secret_dungeon_submodel.archive_data(None, item) for item in log.secret_dungeons.all()]
				
            archives_to_pack.append(archive_to_pack)

            if idl in batch_sizes:
                print(f"\t[{archive_model.__name__}] {str(idl)}/{str(BATCH_SIZE)} ({str(round(idl / BATCH_SIZE * 100, 2))}%)")
		
        _iter = min((idb + 1) * BATCH_SIZE, qs_log_c)
        filename = f'packs/SWARFARM_Pack_Log_{archive_model.__name__}.part{str(idb + 1).rjust(6, "0")}.json'
        with open(filename, 'w+') as f:
            json.dump(archives_to_pack, f)
        print(f"[{archive_model.__name__}] {str(_iter)}/{str(qs_log_c)} ({str(round(_iter / qs_log_c * 100, 2))}%) -> {filename}")


def pack_world_boss_logs(skip_batch_to=0):
    options = {
        'log_model': WorldBossLog,
        'archive_model': WorldBossLogArchive,
        'filter_field': 'timestamp',
        'is_dungeon': True,

        'item_submodel': WorldBossLogItemDropArchive,
        'monster_submodel': WorldBossLogMonsterDropArchive,
        'rune_submodel': WorldBossLogRuneDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_wish_logs(skip_batch_to=0):
    options = {
        'log_model': WishLog,
        'archive_model': WishLogArchive,
        'filter_field': 'timestamp',

        'item_submodel': WishLogItemDropArchive,
        'monster_submodel': WishLogMonsterDropArchive,
        'rune_submodel': WishLogRuneDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_dungeon_logs(skip_batch_to=0):
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

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_rift_dungeon_logs(skip_batch_to=0):
    options = {
        'log_model': RiftDungeonLog,
        'archive_model': RiftDungeonLogArchive,
        'filter_field': 'timestamp',
        'is_dungeon': True,

        'item_submodel': RiftDungeonItemDropArchive,
        'monster_submodel': RiftDungeonMonsterDropArchive,
        'rune_submodel': RiftDungeonRuneDropArchive,
        'rune_crafts_submodel': RiftDungeonRuneCraftDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_raid_dungeon_logs(skip_batch_to=0):
    options = {
        'log_model': RiftRaidLog,
        'archive_model': RiftRaidLogArchive,
        'filter_field': 'timestamp',
        'is_dungeon': True,

        'item_submodel': RiftRaidItemDropArchive,
        'monster_submodel': RiftRaidMonsterDropArchive,
        'rune_crafts_submodel': RiftRaidRuneCraftDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_magic_box_craft_logs(skip_batch_to=0):
    options = {
        'log_model': MagicBoxCraft,
        'archive_model': MagicBoxCraftArchive,
        'filter_field': 'timestamp',

        'item_submodel': MagicBoxCraftItemDropArchive,
        'rune_submodel': MagicBoxCraftRuneDropArchive,
        'rune_crafts_submodel': MagicBoxCraftRuneCraftDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_shop_refresh_logs(skip_batch_to=0):
    options = {
        'log_model': ShopRefreshLog,
        'archive_model': ShopRefreshLogArchive,
        'filter_field': 'timestamp',

        'item_submodel': ShopRefreshItemDropArchive,
        'rune_submodel': ShopRefreshRuneDropArchive,
        'monster_submodel': ShopRefreshMonsterDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_summon_logs(skip_batch_to=0):
    options = {
        'log_model': SummonLog,
        'archive_model': SummonLogArchive,
        'filter_field': 'timestamp',

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_craft_rune_logs(skip_batch_to=0):
    options = {
        'log_model': CraftRuneLog,
        'archive_model': CraftRuneLogArchive,
        'filter_field': 'timestamp',

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_full_logs(skip_batch_to=0):
    options = {
        'log_model': FullLog,
        'archive_model': FullLogArchive,
        'filter_field': 'timestamp',

        'skip_batch_to': skip_batch_to,
    }
    _pack_log(options)


def pack_reports():
    Path('packs/').mkdir(exist_ok=True)
    q_report = Q(generated_on__lt="2023-01-01 00:00:00+00:00")

    report_pack_map = {
        WishReport: WishReportArchive,
        LevelReport: LevelReportArchive,
        SummonReport: SummonReportArchive,
        MagicShopRefreshReport: MagicShopRefreshReportArchive,
        MagicBoxCraftingReport: MagicBoxCraftingReportArchive,
        RuneCraftingReport: RuneCraftingReportArchive,
    }

    for report_model, archive_model in report_pack_map.items():
        qs_report = report_model.objects.filter(q_report).select_related('report_ptr')
        qs_report_c = qs_report.count()
        batches = math.ceil(qs_report_c / BATCH_SIZE)
        print(f"[{report_model.__name__}] To pack: {str(batches)} batches, which equals {str(qs_report_c)}")
        for idb in range(batches):
            reports_to_pack = []
            for report in qs_report[:BATCH_SIZE]:
                data = {
                    'content_type_id': report.content_type_id,
                    'generated_on': report.generated_on.strftime("%Y-%m-%d %H:%M:%S"),
                    'start_timestamp': report.start_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'end_timestamp': report.end_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
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
                
                reports_to_pack.append(data)
            
            filename = f'packs/SWARFARM_Pack_Report_{archive_model.__name__}.part{str(idb + 1).rjust(6, "0")}.json'
            with open(filename, 'w+') as f:
                json.dump(reports_to_pack, f)
            _iter = min((idb + 1) * BATCH_SIZE, qs_report_c)
            print(f"[{archive_model.__name__}] {str(_iter)}/{str(qs_report_c)} ({str(round(_iter / qs_report_c * 100, 2))}%) -> {filename}")
