import math
import json
import glob
from datetime import timedelta

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


BATCH_SIZE = 10000

def _unpack_log(options):
    archive_model = options['archive_model']
	
    # sub-tables
    item_submodel = options.get('item_submodel', None)
    monster_submodel = options.get('monster_submodel', None)
    monster_pieces_submodel = options.get('monster_pieces_submodel', None)
    rune_submodel = options.get('rune_submodel', None)
    rune_crafts_submodel = options.get('rune_crafts_submodel', None)
    artifact_submodel = options.get('artifact_submodel', None)
    secret_dungeon_submodel = options.get('secret_dungeon_submodel', None)
    skip_batch_to = options.get('skip_batch_to', 1)

    files_to_unpack = glob.glob(f'**/SWARFARM_Pack_Log_{archive_model.__name__}.part*.json', recursive=True)
    files_to_unpack.sort()
    files_to_unpack_c = len(files_to_unpack)
    results = 0
    print(f"[{archive_model.__name__}] Found {str(files_to_unpack_c)} parts to unpack")

    for file_to_unpack in files_to_unpack:
        filename_rev = file_to_unpack[::-1]
        part_txt = filename_rev.find('trap')
        extension = filename_rev.find('.')
        part_number = filename_rev[extension + 1:part_txt][::-1]
        part_number = int(part_number)
        if part_number < skip_batch_to: # .part#######. -> part_number
            print(f"[{archive_model.__name__}] Skipping batch {str(part_number)}")
            continue
        print(f"\tUnpacking part #{str(part_number)} ;)")
        with open(file_to_unpack, 'r') as f:
            records_to_unpack = json.load(f)
        
        records_to_unpack_c = len(records_to_unpack)
        results += records_to_unpack_c

        batch_sizes = [math.ceil(records_to_unpack_c * i / 100) for i in range(1, 101, 5)]
        # prep
        items, items_data = [], []
        monsters, monsters_data = [], []
        monster_pieces, monster_pieces_data = [], []
        runes, runes_data = [], []
        rune_crafts, rune_crafts_data = [], []
        artifacts, artifacts_data = [], []
        secret_dungeons, secret_dungeons_data = [], []
        #

        for idl, archive_record in enumerate(records_to_unpack):
            items_data = archive_record.pop('items', [])
            monsters_data = archive_record.pop('monsters', [])
            monster_pieces_data = archive_record.pop('monster_pieces', [])
            runes_data = archive_record.pop('runes', [])
            rune_crafts_data = archive_record.pop('rune_crafts', [])
            artifacts_data = archive_record.pop('artifacts', [])
            secret_dungeons_data = archive_record.pop('secret_dungeons', [])
            
            if 'timestamp' in archive_record and archive_record['timestamp'] and not archive_record['timestamp'].endswith('+00:00'):
                archive_record['timestamp'] += '+00:00'
            if 'clear_time' in archive_record and archive_record['clear_time']:
                archive_record['clear_time'] = timedelta(seconds=archive_record['clear_time'])
            try:
                archive_obj = archive_model.objects.create(**archive_record)
            except:
                continue
            for item in items_data:
                item['log'] = archive_obj
                items.append(item_submodel(**item))
            for monster in monsters_data:
                monster['log'] = archive_obj
                monsters.append(monster_submodel(**monster))
            for monster_piece in monster_pieces_data:
                monster_piece['log'] = archive_obj
                monster_pieces.append(monster_pieces_submodel(**monster_piece))
            for rune in runes_data:
                rune['log'] = archive_obj
                runes.append(rune_submodel(**rune))
            for rune_craft in rune_crafts_data:
                rune_craft['log'] = archive_obj
                rune_crafts.append(rune_crafts_submodel(**rune_craft))
            for artifact in artifacts_data:
                artifact['log'] = archive_obj
                artifacts.append(artifact_submodel(**artifact))
            for secret_dungeon in secret_dungeons_data:
                secret_dungeon['log'] = archive_obj
                secret_dungeons.append(secret_dungeon_submodel(**secret_dungeon))
            
            if idl in batch_sizes:
                print(f"\t\t[{archive_model.__name__}] {str(idl)}/{str(records_to_unpack_c)} ({str(round(idl / records_to_unpack_c * 100, 2))}%)")
		
        if item_submodel and items:
            item_submodel.objects.bulk_create(items, batch_size=BATCH_SIZE)
        if monster_submodel and monsters:
            monster_submodel.objects.bulk_create(monsters, batch_size=BATCH_SIZE)
        if monster_pieces_submodel and items:
            monster_pieces_submodel.objects.bulk_create(monster_pieces, batch_size=BATCH_SIZE)
        if rune_submodel and items:
            rune_submodel.objects.bulk_create(runes, batch_size=BATCH_SIZE)
        if rune_crafts_submodel and items:
            rune_crafts_submodel.objects.bulk_create(rune_crafts, batch_size=BATCH_SIZE)
        if artifact_submodel and items:
            artifact_submodel.objects.bulk_create(artifacts, batch_size=BATCH_SIZE)
        if secret_dungeon_submodel and items:
            secret_dungeon_submodel.objects.bulk_create(secret_dungeons, batch_size=BATCH_SIZE)
        
    print(f"[{archive_model.__name__}] Done unpacking {str(files_to_unpack_c)} parts, which resulted in adding {str(results)} records")


def unpack_world_boss_logs(skip_batch_to=1):
    options = {
        'archive_model': WorldBossLogArchive,

        'item_submodel': WorldBossLogItemDropArchive,
        'monster_submodel': WorldBossLogMonsterDropArchive,
        'rune_submodel': WorldBossLogRuneDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_wish_logs(skip_batch_to=1):
    options = {
        'archive_model': WishLogArchive,

        'item_submodel': WishLogItemDropArchive,
        'monster_submodel': WishLogMonsterDropArchive,
        'rune_submodel': WishLogRuneDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_dungeon_logs(skip_batch_to=1):
    options = {
        'archive_model': DungeonLogArchive,

        'item_submodel': DungeonItemDropArchive,
        'monster_submodel': DungeonMonsterDropArchive,
        'monster_pieces_submodel': DungeonMonsterPieceDropArchive,
        'rune_submodel': DungeonRuneDropArchive,
        'rune_crafts_submodel': DungeonRuneCraftDropArchive,
        'artifact_submodel': DungeonArtifactDropArchive,
        'secret_dungeon_submodel': DungeonSecretDungeonDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_rift_dungeon_logs(skip_batch_to=1):
    options = {
        'archive_model': RiftDungeonLogArchive,

        'item_submodel': RiftDungeonItemDropArchive,
        'monster_submodel': RiftDungeonMonsterDropArchive,
        'rune_submodel': RiftDungeonRuneDropArchive,
        'rune_crafts_submodel': RiftDungeonRuneCraftDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_raid_dungeon_logs(skip_batch_to=1):
    options = {
        'archive_model': RiftRaidLogArchive,

        'item_submodel': RiftRaidItemDropArchive,
        'monster_submodel': RiftRaidMonsterDropArchive,
        'rune_crafts_submodel': RiftRaidRuneCraftDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_magic_box_craft_logs(skip_batch_to=1):
    options = {
        'archive_model': MagicBoxCraftArchive,

        'item_submodel': MagicBoxCraftItemDropArchive,
        'rune_submodel': MagicBoxCraftRuneDropArchive,
        'rune_crafts_submodel': MagicBoxCraftRuneCraftDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_shop_refresh_logs(skip_batch_to=1):
    options = {
        'archive_model': ShopRefreshLogArchive,

        'item_submodel': ShopRefreshItemDropArchive,
        'rune_submodel': ShopRefreshRuneDropArchive,
        'monster_submodel': ShopRefreshMonsterDropArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_summon_logs(skip_batch_to=1):
    options = {
        'archive_model': SummonLogArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_craft_rune_logs(skip_batch_to=1):
    options = {
        'archive_model': CraftRuneLogArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_full_logs(skip_batch_to=1):
    options = {
        'archive_model': FullLogArchive,

        'skip_batch_to': skip_batch_to,
    }
    _unpack_log(options)


def unpack_reports():
    archive_report_models = [
        WishReportArchive,
        LevelReportArchive,
        SummonReportArchive,
        MagicShopRefreshReportArchive,
        MagicBoxCraftingReportArchive,
        RuneCraftingReportArchive,
    ]

    for archive_model in archive_report_models:
        files_to_unpack = glob.glob(f'**/SWARFARM_Pack_Report_{archive_model.__name__}.part*.json', recursive=True)
        files_to_unpack_c = len(files_to_unpack)
        results = 0
        print(f"[{archive_model.__name__}] Found {str(files_to_unpack_c)} parts to unpack")

        for file_to_unpack in files_to_unpack:
            filename_rev = file_to_unpack[::-1]
            part_txt = filename_rev.find('trap')
            extension = filename_rev.find('.')
            part_number = filename_rev[extension + 1:part_txt][::-1]
            part_number = int(part_number)
            print(f"\tUnpacking part #{str(part_number)} ;)")
            with open(file_to_unpack, 'r') as f:
                records_to_unpack = json.load(f)
            
            records_to_unpack_c = len(records_to_unpack)
            results += records_to_unpack_c

            batch_sizes = [math.ceil(records_to_unpack_c * i / 100) for i in range(1, 101, 5)]
            records_to_create = []
            for idl, archive_record in enumerate(records_to_unpack):
                archive_record['start_timestamp'] += '+00:00'
                archive_record['end_timestamp'] += '+00:00'
                archive_record['generated_on'] += '+00:00'
                records_to_create.append(archive_model(**archive_record))
                if idl in batch_sizes:
                    print(f"\t\t[{archive_model.__name__}] {str(idl)}/{str(records_to_unpack_c)} ({str(round(idl / records_to_unpack_c * 100, 2))}%)")\
            
            archive_model.objects.bulk_create(records_to_create, batch_size=BATCH_SIZE)

        print(f"[{archive_model.__name__}] Done unpacking {str(files_to_unpack_c)} parts, which resulted in adding {str(results)} records")
