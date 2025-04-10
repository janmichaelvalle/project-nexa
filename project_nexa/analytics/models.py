from django.contrib.auth.models import User
from django.db import models

# Add Rank model 
class Rank(models.Model):
    rank_id = models.AutoField(primary_key=True)  # Unique rank ID
    name = models.CharField(max_length=50, unique=True)  # Rank name

    def __str__(self):
        return self.name

class Character(models.Model):
    chara_id = models.AutoField(primary_key=True)  # Unique character ID
    name = models.CharField(max_length=50)  # Character name

    def __str__(self):
        return self.name
    
class Stage(models.Model):
    stage_id = models.AutoField(primary_key=True)  # Unique stage ID
    name = models.CharField(max_length=100)  # Stage name

    def __str__(self):
        return self.name
    
class Match(models.Model):
    battle_id = models.AutoField(primary_key=True)  # Auto-incrementing match ID
    battle_at = models.DateTimeField()  # Time of battle
    battle_type = models.IntegerField(default=2)  # Type of battle (ranked, casual, etc.)

    profile = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, null=True, blank=True) 
    character = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True, related_name="matches_as_character")

    opponent_name = models.CharField(max_length=100)  # Store opponent's name as a string
    opponent_character = models.CharField(max_length=50)  # Store opponent's character name

    rounds_won = models.IntegerField()
    rounds_lost = models.IntegerField()
    winner = models.BooleanField()  # True if profile won, False if lost

    class Meta:
        ordering = ['-battle_at']  # Orders matches by latest battle_at first

   
    def __str__(self):
        profile_name = self.profile.in_game_name if self.profile else "Unknown"
        character_name = self.character.name if self.character else "Unknown"
        return f"{profile_name} vs {self.opponent_name} ({character_name} vs {self.opponent_character}) - {'Win' if self.winner else 'Loss'}"