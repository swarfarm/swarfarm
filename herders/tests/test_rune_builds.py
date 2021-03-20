from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from bestiary.models import Monster
from herders import models

User = get_user_model()


class RuneBuildModelTests(TestCase):
    fixtures = ['test_summon_monsters']

    def setUp(self):
        # Create a user
        self.user = User.objects.create(username='testuser')
        self.summoner = models.Summoner.objects.create(user=self.user)

        # Create a monster instance
        self.monster = models.MonsterInstance.objects.create(
            owner=self.summoner,
            monster=Monster.objects.get(com2us_id=14102),
            stars=6,
            level=40,
        )
        self.rune_build = self.monster.default_build
        self.rta_build = self.monster.rta_build

    def test_stats_update_when_adding_rune(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            type=models.RuneInstance.TYPE_ENERGY,
            slot=1,
            main_stat=models.RuneInstance.STAT_ATK,
            stars=1,
            level=0,
            quality=models.RuneInstance.QUALITY_MAGIC,
            innate_stat=models.RuneInstance.STAT_HP,
            innate_stat_value=4,
            substats=[models.RuneInstance.STAT_DEF],
            substat_values=[4],
            substats_enchanted=[False],
            substats_grind_value=[3],
        )
        self.rune_build.assign_rune(rune)

        self.assertEqual(self.rune_build.attack, 3)
        self.assertEqual(self.rune_build.hp, 4)
        self.assertEqual(self.rune_build.defense, 7)

    def test_stats_update_when_adding_artifact(self):
        artifact = models.ArtifactInstance.objects.create(
            owner=self.summoner,
            slot=models.ArtifactInstance.SLOT_ARCHETYPE,
            archetype=self.monster.monster.archetype,
            main_stat=models.ArtifactInstance.STAT_ATK,
            original_quality=models.ArtifactInstance.QUALITY_NORMAL,
            quality=models.ArtifactInstance.QUALITY_NORMAL,
            level=0
        )
        self.rune_build.assign_artifact(artifact)

        self.assertEqual(self.rune_build.attack, 10)

    def test_rune_assigned_to_updates_when_assigned_to_build(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            type=models.RuneInstance.TYPE_ENERGY,
            slot=1,
            main_stat=models.RuneInstance.STAT_ATK,
            stars=1,
            level=0,
            quality=models.RuneInstance.QUALITY_NORMAL,
        )
        self.rune_build.assign_rune(rune)

        rune.refresh_from_db()
        self.assertEqual(rune.assigned_to, self.monster)

    def test_artifact_assigned_to_updates_when_assigned_to_build(self):
        artifact = models.ArtifactInstance.objects.create(
            owner=self.summoner,
            slot=models.ArtifactInstance.SLOT_ARCHETYPE,
            archetype=self.monster.monster.archetype,
            main_stat=models.ArtifactInstance.STAT_ATK,
            original_quality=models.ArtifactInstance.QUALITY_NORMAL,
            quality=models.ArtifactInstance.QUALITY_NORMAL,
            level=0
        )
        self.rune_build.assign_artifact(artifact)

        artifact.refresh_from_db()
        self.assertEqual(artifact.assigned_to, self.monster)

    def test_add_rune_occupied_slot_raise_error(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            type=models.RuneInstance.TYPE_ENERGY,
            slot=1,
            main_stat=models.RuneInstance.STAT_ATK,
            stars=1,
            level=0,
            quality=models.RuneInstance.QUALITY_NORMAL,
        )
        self.rune_build.runes.add(rune)

        rune2 = models.RuneInstance.objects.create(
            owner=self.summoner,
            type=models.RuneInstance.TYPE_FATAL,
            slot=1,
            main_stat=models.RuneInstance.STAT_ATK,
            stars=1,
            level=0,
            quality=models.RuneInstance.QUALITY_NORMAL,
        )
        with self.assertRaises(ValidationError) as cm:
            self.rune_build.runes.add(rune2)

    def test_add_artifact_occupied_slot_raise_error(self):
        artifact = models.ArtifactInstance.objects.create(
            owner=self.summoner,
            slot=models.ArtifactInstance.SLOT_ARCHETYPE,
            archetype=self.monster.monster.archetype,
            main_stat=models.ArtifactInstance.STAT_ATK,
            original_quality=models.ArtifactInstance.QUALITY_NORMAL,
            quality=models.ArtifactInstance.QUALITY_NORMAL,
            level=0
        )
        self.rune_build.artifacts.add(artifact)

        artifact2 = models.ArtifactInstance.objects.create(
            owner=self.summoner,
            slot=models.ArtifactInstance.SLOT_ARCHETYPE,
            archetype=self.monster.monster.archetype,
            main_stat=models.ArtifactInstance.STAT_DEF,
            original_quality=models.ArtifactInstance.QUALITY_NORMAL,
            quality=models.ArtifactInstance.QUALITY_NORMAL,
            level=0
        )
        with self.assertRaises(ValidationError) as cm:
            self.rune_build.artifacts.add(artifact2)

    def test_assign_rune_occupied_slot_unassigns_other(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            type=models.RuneInstance.TYPE_ENERGY,
            slot=1,
            main_stat=models.RuneInstance.STAT_ATK,
            stars=1,
            level=0,
            quality=models.RuneInstance.QUALITY_NORMAL,
        )
        self.rune_build.assign_rune(rune)
        rune.refresh_from_db()
        self.assertEqual(rune.assigned_to, self.monster)

        rune2 = models.RuneInstance.objects.create(
            owner=self.summoner,
            type=models.RuneInstance.TYPE_FATAL,
            slot=1,
            main_stat=models.RuneInstance.STAT_ATK,
            stars=1,
            level=0,
            quality=models.RuneInstance.QUALITY_NORMAL,
        )
        self.rune_build.assign_rune(rune2)
        rune.refresh_from_db()
        rune2.refresh_from_db()
        self.assertIsNone(rune.assigned_to)
        self.assertEqual(rune2.assigned_to, self.monster)

    def test_assign_artifact_occupied_slot_unassigns_other(self):
        artifact = models.ArtifactInstance.objects.create(
            owner=self.summoner,
            slot=models.ArtifactInstance.SLOT_ARCHETYPE,
            archetype=self.monster.monster.archetype,
            main_stat=models.ArtifactInstance.STAT_ATK,
            original_quality=models.ArtifactInstance.QUALITY_NORMAL,
            quality=models.ArtifactInstance.QUALITY_NORMAL,
            level=0
        )
        self.rune_build.assign_artifact(artifact)
        artifact.refresh_from_db()
        self.assertEqual(artifact.assigned_to, self.monster)

        artifact2 = models.ArtifactInstance.objects.create(
            owner=self.summoner,
            slot=models.ArtifactInstance.SLOT_ARCHETYPE,
            archetype=self.monster.monster.archetype,
            main_stat=models.ArtifactInstance.STAT_DEF,
            original_quality=models.ArtifactInstance.QUALITY_NORMAL,
            quality=models.ArtifactInstance.QUALITY_NORMAL,
            level=0
        )
        self.rune_build.assign_artifact(artifact2)
        artifact.refresh_from_db()
        artifact2.refresh_from_db()
        self.assertIsNone(artifact.assigned_to)
        self.assertEqual(artifact2.assigned_to, self.monster)


    def test_assign_artifact_default_build_check_rta_build(self):
        artifact = models.ArtifactInstance.objects.create(
            owner=self.summoner,
            slot=models.ArtifactInstance.SLOT_ARCHETYPE,
            archetype=self.monster.monster.archetype,
            main_stat=models.ArtifactInstance.STAT_ATK,
            original_quality=models.ArtifactInstance.QUALITY_NORMAL,
            quality=models.ArtifactInstance.QUALITY_NORMAL,
            level=0
        )
        self.rune_build.assign_artifact(artifact)
        artifact.refresh_from_db()
        self.assertEqual(artifact.assigned_to, self.monster)
        self.assertEqual(artifact.rta_assigned_to, None)
