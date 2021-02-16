from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User

from herders.models import ArtifactInstance, RuneInstance, MonsterInstance, Summoner

import os
import json
import copy
import time
import random
import string

class Command(BaseCommand):
    help = 'Creates `accounts_quantity` accounts with propagated data from first Summoner.'
    MIN, MAX = 1, 1000000000

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            '-a',
            '--accounts_quantity',
            type=int,
            default=100,
            help='Number of accounts to create',
        )

    def _rand(self, target, iter_target):
        rand = random.randint(self.MIN, self.MAX)
        while rand in target or rand in iter_target:
            rand = random.randint(self.MIN, self.MAX)
        return rand

    def handle(self, *args, **kwargs):
        # TODO: Add whole `herders` copy, not only Monsters, Runes & Artifacts
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR('Command used outside DEBUG Mode'))
            return

        # timestamp, so there's no problem with dupe account logins
        ACC_LOGIN = f'propagated_$ID$_{int(time.time())}'
        # some sort of PASSWD generator, we won't use it anyway
        PASSWD = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(24))

        monster_fields = [
            'pk', 'owner_id', 'monster_id', 'com2us_id', 'created', 'stars', 'level', 'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level',
            'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes', 'custom_name',
            'rune_hp', 'rune_attack', 'rune_defense', 'rune_speed', 'rune_crit_rate', 'rune_crit_damage', 'rune_resistance', 'rune_accuracy',
            'avg_rune_efficiency', 'artifact_hp', 'artifact_attack', 'artifact_defense',
        ]
        rune_fields = [
            'type', 'owner_id', 'com2us_id', 'assigned_to_id', 'marked_for_sale', 'notes', 'main_stat', 'main_stat_value',
            'substat_1', 'substat_1_value', 'substat_1_craft', 'substat_2', 'substat_2_value', 'substat_2_craft',
            'substat_3', 'substat_3_value', 'substat_3_craft', 'substat_4', 'substat_4_value', 'substat_4_craft',
            'innate_stat', 'innate_stat_value', 'stars', 'level', 'slot', 'quality', 'original_quality', 'ancient', 'value', 
            'substats', 'substat_values', 'substats_enchanted', 'substats_grind_value', 'has_hp', 'has_atk', 'has_def',
            'has_crit_rate', 'has_crit_dmg', 'has_speed', 'has_resist', 'has_accuracy', 'efficiency', 'max_efficiency',
            'substat_upgrades_remaining', 'has_grind', 'has_gem',
        ]
        artifact_fields = [
            'owner_id', 'com2us_id', 'assigned_to_id', 'level', 'original_quality', 'main_stat', 'main_stat_value',
            'effects', 'effects_value', 'effects_upgrade_count', 'effects_reroll_count', 'efficiency', 'max_efficiency',
            'slot', 'element', 'archetype', 'quality'
        ]

        start = time.time()
        acc_quantity = kwargs['accounts_quantity']
        self.stdout.write(self.style.SUCCESS(f'Starting data duplication process for {acc_quantity} account(s)!'))

        summoner = Summoner.objects.first()
        if not summoner:
            self.stdout.write(self.style.ERROR("No Summoner records in database, can't duplicate empty data"))
            return

        monsters = MonsterInstance.objects.filter(owner=summoner).values(*monster_fields)
        runes = RuneInstance.objects.filter(owner=summoner).values(*rune_fields)
        artifacts = ArtifactInstance.objects.filter(owner=summoner).values(*artifact_fields)

        self.stdout.write(self.style.SUCCESS(f'Duplicating per account:'))
        self.stdout.write(self.style.WARNING(f'- Monsters: {len(monsters)}'))
        self.stdout.write(self.style.WARNING(f'- Runes: {len(runes)}'))
        self.stdout.write(self.style.WARNING(f'- Artifacts: {len(artifacts)}'))

        ids = {
            'wizards': [summoner.com2us_id],
            'monsters': list(set(MonsterInstance.objects.all().values_list('com2us_id', flat=True))),
            'runes': list(set(RuneInstance.objects.all().values_list('com2us_id', flat=True))),
            'artifacts': list(set(ArtifactInstance.objects.all().values_list('com2us_id', flat=True))),
        }
        monster_pks = {m.pop('pk'): m['com2us_id'] for m in monsters}

        for iter in range(acc_quantity):
            iter_ids = {
                'monsters': {},
                'runes': {},
                'artifacts': {},
            }
            iter_objs = {
                'monsters': [],
                'runes': [],
                'artifacts': [],
            }
            login = ACC_LOGIN.replace('$ID$', str(iter))
            iter_start = time.time()
            with transaction.atomic():
                user = User.objects.create_user(login, login + '@gmail.com', PASSWD)

                wizard_id = self._rand(ids['wizards'], [])
                ids['wizards'].append(wizard_id)
                summoner = Summoner.objects.create(user=user, com2us_id=wizard_id)

                for mon in monsters:
                    mon_obj = MonsterInstance(**mon)
                    mon_id = self._rand(ids['monsters'], iter_ids['monsters'].values())
                    iter_ids['monsters'][mon_obj.com2us_id] = mon_id
                    mon_obj.com2us_id = mon_id
                    mon_obj.owner = summoner
                    iter_objs['monsters'].append(mon_obj)

                iter_mons = {m.com2us_id: m for m in MonsterInstance.objects.bulk_create(iter_objs['monsters'])}

                for rune in runes:
                    rune_obj = RuneInstance(**rune)
                    rune_id = self._rand(ids['runes'], iter_ids['runes'].values())
                    iter_ids['runes'][rune_obj.com2us_id] = rune_id
                    rune_obj.com2us_id = rune_id
                    rune_obj.owner = summoner
                    rune_obj.assigned_to = iter_mons[iter_ids['monsters'][monster_pks[rune['assigned_to_id']]]] if rune['assigned_to_id'] else None
                    iter_objs['runes'].append(rune_obj)

                for artifact in artifacts:
                    artifact_obj = ArtifactInstance(**artifact)
                    artifact_id = self._rand(ids['artifacts'], iter_ids['artifacts'].values())
                    iter_ids['artifacts'][artifact_obj.com2us_id] = artifact_id
                    artifact_obj.com2us_id = artifact_id
                    artifact_obj.owner = summoner
                    artifact_obj.assigned_to = iter_mons[iter_ids['monsters'][monster_pks[artifact['assigned_to_id']]]] if artifact['assigned_to_id'] else None
                    iter_objs['artifacts'].append(artifact_obj)

                RuneInstance.objects.bulk_create(iter_objs['runes'])
                ArtifactInstance.objects.bulk_create(iter_objs['artifacts'])

                for k, v in ids.items():
                    if k not in iter_ids.keys():
                        continue
                    v += iter_ids[k].values()
                    if len(v) != len(set(v)):
                        raise ValueError(f"Some duplicates in {k}.")
                
                self.stdout.write(self.style.WARNING(f"[{iter + 1}] This iteration took {round(time.time() - iter_start, 2)} seconds ({round(time.time() - start, 2)} in total)!"))
                
        self.stdout.write(self.style.SUCCESS('Done creating accounts and duplicating data.'))