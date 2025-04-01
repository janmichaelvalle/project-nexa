from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
import pytz
from analytics.models import Match, Player, Character

class Command(BaseCommand):
    help = "Scrapes match data from Wavu Wank and stores it in the database"

    def handle(self, *args, **kwargs):
        Match.objects.all().delete()
        URL = "https://wank.wavu.wiki/player/4BDhN4Yhg82y?char=lili&limit=5000"
        response = requests.get(URL)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to retrieve data"))
            return

        soup = BeautifulSoup(response.text, "html.parser")
        game_list_div = soup.find("div", class_="game-list")
        if not game_list_div:
            self.stdout.write(self.style.ERROR("Game list not found!"))
            return

        match_table = game_list_div.find("table")
        if not match_table:
            self.stdout.write(self.style.ERROR("Match table not found inside game list!"))
            return

        match_rows = match_table.find_all("tr")  # Find all match rows

        matches = []
        for row in match_rows:
            columns = row.find_all("td")
            if len(columns) < 5:
                continue  # Skip if not enough columns

            match_date_raw = columns[0].find("time").text.strip()
            try:
                match_date = datetime.strptime(match_date_raw, "%d %b %y %H:%M")
                ph_tz = pytz.timezone("Asia/Manila")
                utc_tz = pytz.utc
                match_date = ph_tz.localize(match_date)
                match_date = match_date.astimezone(utc_tz)
            except ValueError as e:
                print(f"Error parsing datetime: {match_date_raw} - {e}")
                continue  # Skip this match if the date is invalid

            p1_name = columns[1].find("a").text.strip()
            p1_character_name = columns[1].find("span", class_="char").text.strip()
            result = columns[2].text.strip()
            p2_character_name = columns[3].find("span", class_="char").text.strip()
            p2_name = columns[3].find("a").text.strip()

            # Fetch or create players
            player, _ = Player.objects.get_or_create(in_game_name=p1_name, defaults={'polaris_id': p1_name})

            # Fetch or create characters
            character, _ = Character.objects.get_or_create(name=p1_character_name)

            # Parse result (e.g., "3-2" -> rounds won)
            p1_rounds, p2_rounds = map(int, result.split("-"))
            rounds_won = p1_rounds
            rounds_lost = p2_rounds
            winner = True if p1_rounds > p2_rounds else False

            print(f"Creating match: {match_date}, {p1_name} ({p1_character_name}) - {rounds_won}-{rounds_lost}")

            matches.append(
                Match(
                    battle_at=match_date,
                    battle_type=2,
                    player=player,
                    character=character,
                    opponent_name=p2_name,
                    opponent_character=p2_character_name,
                    rounds_won=rounds_won,
                    rounds_lost=rounds_lost,
                    winner=winner,
                )
            )

        if matches:
            Match.objects.bulk_create(matches)
            self.stdout.write(self.style.SUCCESS(f"{len(matches)} matches saved to the database!"))
        else:
            self.stdout.write(self.style.WARNING("No valid matches were found."))