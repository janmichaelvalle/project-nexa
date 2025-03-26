from django.core.management.base import BaseCommand
from analytics.models import Stage

class Command(BaseCommand):
    help = 'Populate the database with Tekken 8 stages'

    def handle(self, *args, **kwargs):
        stages = [
            'Arena_Underground', 'Arena', 'Celebration on the Seine', 'Coliseum of Fate',
            'Descent into Subconscious', 'Elegant Palace', 'Fallen Destiny', 'Genmaji Temple',
            'Into the Stratosphere', 'Midnight Siege', 'Ortiz Farm', 'Phoenix Gate', 'Rebel Hangar',
            'Sanctum', 'Seaside Resort', 'Secluded Training Ground', 'Urban Square',
            'Urban Square_Evening', 'Yakushima'
        ]

        for stage_name in stages:
            Stage.objects.get_or_create(name=stage_name)

        self.stdout.write(self.style.SUCCESS('Tekken 8 stages populated successfully.'))