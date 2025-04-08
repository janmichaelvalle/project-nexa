import requests
import sqlite3
from datetime import datetime, timedelta
import time
from django.core.management.base import BaseCommand

# Constants
DB_NAME = 'wavu_data.sqlite3'
TABLE_NAME = 'matches'
BASE_URL = 'https://wank.wavu.wiki/api/replays'

# Step 1: Create SQLite table if not exists
def setup_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            battle_id TEXT UNIQUE,
            battle_at INTEGER,
            battle_type INTEGER,
            game_version INTEGER,
            stage_id INTEGER,
            winner INTEGER,

            p1_name TEXT,
            p1_user_id INTEGER,
            p1_polaris_id TEXT,
            p1_chara_id INTEGER,
            p1_area_id INTEGER,
            p1_region_id INTEGER,
            p1_lang TEXT,
            p1_power INTEGER,
            p1_rank INTEGER,
            p1_rating_before INTEGER,
            p1_rating_change INTEGER,
            p1_rounds INTEGER,

            p2_name TEXT,
            p2_user_id INTEGER,
            p2_polaris_id TEXT,
            p2_chara_id INTEGER,
            p2_area_id INTEGER,
            p2_region_id INTEGER,
            p2_lang TEXT,
            p2_power INTEGER,
            p2_rank INTEGER,
            p2_rating_before INTEGER,
            p2_rating_change INTEGER,
            p2_rounds INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Step 2: Save match to SQLite
def save_matches(matches):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for match in matches:
        try:
            cur.execute(f'''
                INSERT OR IGNORE INTO {TABLE_NAME} (
                    battle_id, battle_at, battle_type, game_version, stage_id, winner,
                    p1_name, p1_user_id, p1_polaris_id, p1_chara_id, p1_area_id, p1_region_id, p1_lang, p1_power, p1_rank, p1_rating_before, p1_rating_change, p1_rounds,
                    p2_name, p2_user_id, p2_polaris_id, p2_chara_id, p2_area_id, p2_region_id, p2_lang, p2_power, p2_rank, p2_rating_before, p2_rating_change, p2_rounds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match.get("battle_id"),
                match.get("battle_at"),
                match.get("battle_type"),
                match.get("game_version"),
                match.get("stage_id"),
                match.get("winner"),

                match.get("p1_name"),
                match.get("p1_user_id"),
                match.get("p1_polaris_id"),
                match.get("p1_chara_id"),
                match.get("p1_area_id"),
                match.get("p1_region_id"),
                match.get("p1_lang"),
                match.get("p1_power"),
                match.get("p1_rank"),
                match.get("p1_rating_before"),
                match.get("p1_rating_change"),
                match.get("p1_rounds"),

                match.get("p2_name"),
                match.get("p2_user_id"),
                match.get("p2_polaris_id"),
                match.get("p2_chara_id"),
                match.get("p2_area_id"),
                match.get("p2_region_id"),
                match.get("p2_lang"),
                match.get("p2_power"),
                match.get("p2_rank"),
                match.get("p2_rating_before"),
                match.get("p2_rating_change"),
                match.get("p2_rounds")
            ))
        except Exception as e:
            print("Failed to insert match:", match.get("battle_id"), e)
    conn.commit()
    conn.close()

# Step 3: Pull data by timestamp
def fetch_matches_by_timestamp(cutoff_timestamp):
    before = int(time.time())  # Start from now
    while before > cutoff_timestamp:
        print(f"Fetching matches before {before} (cutoff {cutoff_timestamp})...")

        try:
            res = requests.get(BASE_URL, params={"before": before})
            res.raise_for_status()
            matches = res.json()
            print(f"→ Pulled {len(matches)} matches")
            save_matches(matches)
        except Exception as e:
            print(f"⚠️ Failed to fetch before {before}:", e)

        before -= 700  # Step back 700 seconds (~11.6 min of data)
        time.sleep(1)  # avoid rate limits

class Command(BaseCommand):
    help = 'Pull Wavu match data and store in SQLite'

    def handle(self, *args, **kwargs):
        setup_db()
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(f"SELECT MAX(battle_at) FROM {TABLE_NAME}")
        latest = cur.fetchone()[0] or int(datetime(2025, 4, 1).timestamp())
        conn.close()
        fetch_matches_by_timestamp(latest)
