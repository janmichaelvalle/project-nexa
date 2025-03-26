from django.core.management.base import BaseCommand
from analytics.models import Rank

class Command(BaseCommand):
    help = 'Populate the database with Tekken 8 ranks'

    def handle(self, *args, **kwargs):
        ranks = [
            'Beginner', '1st dan', '2nd dan', 'Fighter', 'Strategist', 'Combatant',
            'Brawler', 'Ranger', 'Cavalry', 'Warrior', 'Assailant', 'Dominator',
            'Vanquisher', 'Destroyer', 'Eliminator', 'Garyu', 'Shinryu', 'Tenryu',
            'Mighty Ruler', 'Flame Ruler', 'Battle Ruler', 'Fujin', 'Raijin', 'Kishin',
            'Bushin', 'Tekken King', 'Tekken Emperor', 'Tekken God', 'Tekken God Supreme',
            'God of Destruction', 'Tekken Lord', 'Tekken Lord Supreme', 'Lord of Destruction'
        ]

        for rank_name in ranks:
            Rank.objects.get_or_create(name=rank_name)

        self.stdout.write(self.style.SUCCESS('Tekken 8 ranks populated successfully.'))