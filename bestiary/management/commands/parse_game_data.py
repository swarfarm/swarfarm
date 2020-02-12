from django.core.management.base import BaseCommand

from bestiary import parse


class Command(BaseCommand):
    help = 'Parse all bestiary data from game files'

    def handle(self, *args, **kwargs):
        self.stdout.write('Processing static files...')
        parse.static.decrypt_images()
        parse.static.crop_images()

        self.stdout.write('Parsing skill data...')
        parse.skills()

        self.stdout.write('Parsing homunculus skill data...')
        parse.homonculus_skills()

        self.stdout.write('Parsing monster data...')
        parse.monsters()

        self.stdout.write('Setting monster awaken/transformation relationships...')
        parse.monster_relationships()

        self.stdout.write('Parsing monster crafting data...')
        parse.monster_crafting()

        self.stdout.write(self.style.SUCCESS('Done!'))
