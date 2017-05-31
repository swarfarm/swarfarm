from datetime import timedelta
import os
import os.path

from drf_ujson.renderers import UJSONRenderer

from django.conf import settings

from .serializers import *

EXPORT_FOLDER = 'log_data'


def export_scenarios():
    queryset = RunLog.objects.filter(dungeon__type=Dungeon.TYPE_SCENARIO, timestamp__isnull=False)
    _do_export('scenarios', queryset, RunLogSerializer)


def export_rune_dungeons():
    queryset = RunLog.objects.filter(dungeon__type=Dungeon.TYPE_RUNE_DUNGEON)
    _do_export('rune_dungeons', queryset, RunLogSerializer)


def export_elemental_dungeons():
    queryset = RunLog.objects.filter(dungeon__type=Dungeon.TYPE_ESSENCE_DUNGEON)
    _do_export('elemental_dungeons', queryset, RunLogSerializer)


def export_other_dungeons():
    queryset = RunLog.objects.filter(dungeon__type=Dungeon.TYPE_OTHER_DUNGEON)
    _do_export('other_dungeons', queryset, RunLogSerializer)


def export_summons():
    queryset = SummonLog.objects.all()
    _do_export('summons', queryset, SummonLogSerializer)


def export_rift_dungeons():
    queryset = RiftDungeonLog.objects.all()
    _do_export('rift_dungeons', queryset, RiftDungeonLogSerializer)


def export_world_boss():
    queryset = WorldBossLog.objects.all()
    _do_export('world_boss', queryset, WorldBossLogSerializer)


def export_rune_crafts():
    queryset = RuneCraftLog.objects.all()
    _do_export('rune_crafts', queryset, RuneCraftLogSerializer)


def export_shop_refresh():
    queryset = ShopRefreshLog.objects.all()
    _do_export('magic_shop', queryset, ShopRefreshLogSerializer)


def export_wishes():
    queryset = WishLog.objects.all()
    _do_export('wish', queryset, WishLogSerializer)


def export_all():
    exports = [
        export_scenarios,
        export_rune_dungeons,
        export_elemental_dungeons,
        export_other_dungeons,
        export_summons,
        export_rift_dungeons,
        export_world_boss,
        export_rune_crafts,
        export_shop_refresh,
        export_wishes,
    ]

    for export in exports:
        try:
            print('Exporting {}'.format(export.__name__))
            export()
        except Exception as e:
            print('Error exporting {}: {}'.format(export.__name__, e))


def _do_export(category_name, queryset, serializer):
    # Filter out already exported data according to the export manager
    export_info, _ = ExportManager.objects.get_or_create(export_category=category_name)
    time_format = '%Y-%m-%d_%H.%M.%S'

    # Filter out all rows that have already been exported
    queryset = queryset.filter(pk__gt=export_info.last_row).order_by('pk')

    while queryset.count():
        # Limit to 1 week at a time
        first_record = queryset.filter(pk__gt=export_info.last_row).first()
        logs_to_export = queryset.filter(
            pk__gt=export_info.last_row,
            timestamp__lte=first_record.timestamp + timedelta(weeks=1)
        )

        last_record = logs_to_export.last()

        # Set up the folder if necessary
        filename = os.path.join(
            settings.BASE_DIR,
            EXPORT_FOLDER,
            category_name,
            '{}_{}_to_{}.json'.format(
                category_name,
                first_record.timestamp.strftime(time_format),
                last_record.timestamp.strftime(time_format),
            )
        )

        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        serialized = serializer(logs_to_export, many=True)
        rendered = UJSONRenderer().render(serialized.data)

        with open(filename, 'wb') as outfile:
            outfile.write(rendered)

        export_info.last_row = last_record.pk
        export_info.save()

        # Update queryset to filter out just-exported entries
        queryset = queryset.filter(pk__gt=export_info.last_row)
