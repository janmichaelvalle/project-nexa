from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from django.utils.dateparse import parse_datetime
from analytics.models import Match, Player, Character

class Command(BaseCommand):
    help = "Scrapes match data from Wavu Wank and stores it in the database"

    def handle(self, *args, **kwargs):
        URL = "https://wank.wavu.wiki/player/4BDhN4Yhg82y?char=lili&limit=5000"
        response = requests.get(URL)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to retrieve data"))
            return

        soup = BeautifulSoup(response.text, "html.parser")
        match_table = soup.find("table")  # Find the table with matches
        if not match_table:
            self.stdout.write(self.style.ERROR("Match table not found!"))
            return

        match_rows = match_table.find_all("tr")  # Find all match rows

        matches = []
        for row in match_rows:
            columns = row.find_all("td")
            if len(columns) < 5:
                continue  # Skip if not enough columns

            match_date = columns[0].find("time").text.strip()
            match_date = parse_datetime(match_date)

            p1_name = columns[1].find("a").text.strip()
            p1_character_name = columns[1].find("span", class_="char").text.strip()
            result = columns[2].text.strip()
            p2_character_name = columns[3].find("span", class_="char").text.strip()
            p2_name = columns[3].find("a").text.strip()

            # Fetch or create players
            player, _ = Player.objects.get_or_create(in_game_name=p1_name, polaris_id=p1_name)

            # Fetch or create characters
            character, _ = Character.objects.get_or_create(name=p1_character_name)

            # Parse result (e.g., "3-2" -> rounds won)
            p1_rounds, p2_rounds = map(int, result.split("-"))
            rounds_won = p1_rounds
            rounds_lost = p2_rounds
            winner = True if p1_rounds > p2_rounds else False

            matches.append(
                Match(
                    battle_at=match_date,
                    battle_type=2,
                    player=player,
                    character=character,
                    rounds_won=rounds_won,
                    rounds_lost=rounds_lost,
                    winner=winner,
                )
            )

        Match.objects.bulk_create(matches)
        self.stdout.write(self.style.SUCCESS(f"{len(matches)} matches saved to the database!"))