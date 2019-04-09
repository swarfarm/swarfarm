from rest_framework import serializers

from . import models


class LogEntrySeralizer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'timestamp',
            'server',
        ]

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context')
        if context.get('private'):
            # Add private user identifying data to log
            self.Meta.fields

        super().__init__(*args, **kwargs)




class ItemDropSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'item',
            'quantity',
        )


class DungeonLogItemDropSerializer(ItemDropSerializer):
    class Meta(ItemDropSerializer.Meta):
        model = models.DungeonItemDrop

class DungeonLogSerializer(LogEntrySeralizer):
    class Meta(LogEntrySeralizer.Meta):
        model = models.DungeonLog