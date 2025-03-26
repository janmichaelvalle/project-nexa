from django.core.management.base import BaseCommand
from analytics.models import Character

class Command(BaseCommand):
    help = 'Populate the database with Tekken 8 characters'

    def handle(self, *args, **kwargs):
        characters = [
            'Alisa Bosconovitch', 'Asuka Kazama', 'Azucena', 'Bryan Fury', 'Claudio Serafino',
            'Devil Jin', 'Dragunov', 'Eddy Gordo', 'Feng Wei', 'Hwoarang', 'Jack-8', 'Jin Kazama',
            'Jun Kazama', 'Kazuya Mishima', 'King', 'Kuma', 'Lars Alexandersson', 'Lee Chaolan',
            'Leo Kliesen', 'Leroy Smith', 'Lidia Sobieska', 'Ling Xiaoyu', 'Marshall Law',
            'Nina Williams', 'Panda', 'Paul Phoenix', 'Raven', 'Reina', 'Shaheen', 'Steve Fox',
            'Victor Chevalier', 'Yoshimitsu', 'Zafina', 'Heihachi Mishima', 'Clive Rosfield'
        ]

        for character_name in characters:
            Character.objects.get_or_create(name=character_name)

        self.stdout.write(self.style.SUCCESS('Tekken 8 characters populated successfully.'))