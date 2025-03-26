from django.core.management.base import BaseCommand
from analytics.models import Player, Rank
import random

class Command(BaseCommand):
    
    help = 'Populate the database with dummy players'

    def handle(self, *args, **kwargs):
        Player.objects.all().delete() 

        players = [
            {'in_game_name': 'Mikagi', 'polaris_id': '4BDhN4Yhg82y'},
            {'in_game_name': 'clintskiii', 'polaris_id': '4i554h5BmTMJ'}
        ]

        ranks = list(Rank.objects.all())

        for player in players:
            rank = random.choice(ranks) if ranks else None
            Player.objects.create(
                in_game_name=player['in_game_name'],
                polaris_id=player['polaris_id'],
                rank=rank
            )

        self.stdout.write(self.style.SUCCESS('Dummy players populated successfully.'))