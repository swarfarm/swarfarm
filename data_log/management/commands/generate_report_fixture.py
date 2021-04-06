from django.core.management.base import BaseCommand
from django.core import serializers

from data_log import models
import json


class Command(BaseCommand):
    help = 'Create Data Log Report fixtures'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO('Creating fixtures for Data Log Reports...'))
        JSONSerializer = serializers.get_serializer("json")
        j = JSONSerializer()
        data = []
        models_to_serialize = [
            models.LevelReport, 
            models.SummonReport, 
            models.MagicShopRefreshReport, 
            models.MagicBoxCraftingReport, 
            models.WishReport, 
            models.RuneCraftingReport
        ]

        for model in models_to_serialize:
            self.stdout.write(self.style.WARNING(model.__name__))
            data += json.loads(j.serialize(model.objects.order_by('-generated_on')[:100]))
        
        self.stdout.write(self.style.WARNING(models.Report.__name__))
        data += json.loads(j.serialize(models.Report.objects.order_by('-generated_on')[:1000]))

        with open("fixture_reports.json", "w+") as f:
            json.dump(data, f)

        self.stdout.write(self.style.SUCCESS('Done!'))
