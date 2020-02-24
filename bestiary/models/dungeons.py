from django.db import models
from django.utils.text import slugify

from . import base
from .monsters import Monster


class Dungeon(models.Model):
    CATEGORY_SCENARIO = 0
    CATEGORY_CAIROS = 1
    CATEGORY_TOA = 2
    CATEGORY_RIFT_OF_WORLDS_RAID = 3
    CATEGORY_RIFT_OF_WORLDS_BEASTS = 4
    CATEGORY_HALL_OF_HEROES = 5
    CATEGORY_ARENA = 6
    CATEGORY_GUILD = 7
    CATEGORY_SECRET = 8
    CATEGORY_WORLD_BOSS = 9
    CATEGORY_DIMENSIONAL_HOLE = 10
    CATEGORY_OTHER = 99

    CATEGORY_CHOICES = (
        (CATEGORY_SCENARIO, 'Scenario'),
        (CATEGORY_CAIROS, 'Cairos Dungeon'),
        (CATEGORY_TOA, 'Tower of Ascension'),
        (CATEGORY_RIFT_OF_WORLDS_RAID, 'Rift Raid'),
        (CATEGORY_RIFT_OF_WORLDS_BEASTS, 'Rift Beast'),
        (CATEGORY_HALL_OF_HEROES, 'Hall of Heroes'),
        (CATEGORY_ARENA, 'Arena'),
        (CATEGORY_GUILD, 'Guild Content'),
        (CATEGORY_SECRET, 'Secret Dungeon'),
        (CATEGORY_WORLD_BOSS, 'World Boss'),
        (CATEGORY_DIMENSIONAL_HOLE, 'Dimensional Hole'),
        (CATEGORY_OTHER, 'Other'),
    )

    com2us_id = models.IntegerField()
    enabled = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    category = models.IntegerField(choices=CATEGORY_CHOICES, blank=True, null=True)
    icon = models.CharField(max_length=100, default='', blank=True)

    class Meta:
        ordering = ['category', 'com2us_id']
        unique_together = ('com2us_id', 'category')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Dungeon, self).save(*args, **kwargs)


class SecretDungeon(Dungeon):
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)


class LevelDifficultyManager(models.Manager):
    # Provide easy methods to access scenario difficulties
    def normal(self):
        return self.get_queryset().filter(difficulty=self.model.DIFFICULTY_NORMAL)

    def hard(self):
        return self.get_queryset().filter(difficulty=self.model.DIFFICULTY_HARD)

    def hell(self):
        return self.get_queryset().filter(difficulty=self.model.DIFFICULTY_HELL)


class Level(models.Model):
    DIFFICULTY_NORMAL = 1
    DIFFICULTY_HARD = 2
    DIFFICULTY_HELL = 3
    DIFFICULTY_CHOICES = (
        (DIFFICULTY_NORMAL, 'Normal'),
        (DIFFICULTY_HARD, 'Hard'),
        (DIFFICULTY_HELL, 'Hell'),
    )

    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE)
    floor = models.IntegerField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, blank=True, null=True)
    energy_cost = models.IntegerField(blank=True, null=True, help_text='Energy cost to start a run')
    xp = models.IntegerField(blank=True, null=True, help_text='XP gained by fully clearing the level')
    frontline_slots = models.IntegerField(default=5)
    backline_slots = models.IntegerField(blank=True, null=True, help_text='Leave null for normal dungeons')
    total_slots = models.IntegerField(default=5, help_text='Maximum monsters combined front/backline.')

    objects = LevelDifficultyManager()

    class Meta:
        unique_together = (
            'dungeon',
            'floor',
            'difficulty',
        )
        ordering = (
            'dungeon',
            'difficulty',
            'floor',
        )

    def __str__(self):
        difficulty = self.get_difficulty_display() if self.difficulty else ''
        if self.dungeon.category == Dungeon.CATEGORY_RIFT_OF_WORLDS_RAID:
            level_char = 'R'
        else:
            level_char = 'B'

        return f'{self.dungeon.name} {difficulty} {level_char}{self.floor}'


class Wave(base.Orderable):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    class Meta(base.Orderable.Meta):
        pass


class Enemy(base.Orderable, base.Stars):
    wave = models.ForeignKey(Wave, on_delete=models.CASCADE)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    com2us_id = models.IntegerField()

    boss = models.BooleanField(default=False)
    stars = models.IntegerField(choices=base.Stars.STAR_CHOICES)
    level = models.IntegerField()

    hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    speed = models.IntegerField()
    resist = models.IntegerField()
    accuracy_bonus = models.IntegerField()
    crit_bonus = models.IntegerField()
    crit_damage_reduction = models.IntegerField()

    class Meta(base.Orderable.Meta):
        pass
