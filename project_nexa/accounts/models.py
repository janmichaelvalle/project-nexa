from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # One account = One player
    in_game_name = models.CharField(max_length=100, unique=True)  # Tekken IGN
    tekken_id = models.CharField(max_length=50, unique=True)  # Tekken ID
    rank = models.ForeignKey('analytics.Rank', on_delete=models.SET_NULL, null=True, blank=True)  # Player Rank

    def __str__(self):
        return self.in_game_name