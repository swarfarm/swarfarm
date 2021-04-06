from django.core.management.base import BaseCommand
from django.core import serializers

from bestiary.models.dungeons import Level
from data_log import models
import json


class Command(BaseCommand):
    help = 'Create Data Log Report fixtures'

    def _get_latest_report(self, model, field):
        if not hasattr(model, field):
            raise ValueError(f"Model {model} doesn't have {field} field.")
        
        qs_ids = []
        attr_list = []

        for report in model.objects.order_by('-generated_on').iterator(chunk_size=100):
            attr = getattr(report, field)
            if attr in attr_list:
                break
            attr_list.append(attr)
            qs_ids.append(report.pk)

        qs = model.objects.filter(pk__in=qs_ids)
        return qs

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO('Creating fixtures for Data Log Reports...'))
        JSONSerializer = serializers.get_serializer("json")
        j = JSONSerializer()

        fields_models_mapper = {
            'level': models.LevelReport, 
            'item': models.SummonReport, 
            'box_type': models.MagicBoxCraftingReport, 
            'craft_level': models.RuneCraftingReport
        }
        models_to_serialize_normally = [
            models.MagicShopRefreshReport, 
            models.WishReport, 
        ]
        data = []
        pks = []

        for field, model in fields_models_mapper.items():
            self.stdout.write(self.style.WARNING(model.__name__))
            qs = self._get_latest_report(model, field)
            serialized_data = json.loads(j.serialize(qs))
            pks += [d['pk'] for d in serialized_data]
            data += serialized_data

        for model in models_to_serialize_normally:
            self.stdout.write(self.style.WARNING(model.__name__))
            serialized_data = json.loads(j.serialize(model.objects.order_by('-generated_on')[:1]))
            pks += [d['pk'] for d in serialized_data]
            data += serialized_data
        
        self.stdout.write(self.style.WARNING(models.Report.__name__))
        reports = json.loads(j.serialize(models.Report.objects.order_by('-generated_on')[:100]))

        self.stdout.write(self.style.HTTP_INFO("Finishing special reports..."))
        reports += json.loads(j.serialize(models.Report.objects.filter(pk__in=pks)))

        data = reports + data

        self.stdout.write(self.style.HTTP_INFO('Saving fixtures to file'))
        with open("fixture_reports.json", "w+") as f:
            json.dump(data, f)

        self.stdout.write(self.style.SUCCESS('Done!'))
