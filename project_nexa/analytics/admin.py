from django.contrib import admin
from .models import Rank, Player, Character, Stage, Match

class MatchAdmin(admin.ModelAdmin):
    list_display = ('battle_at', 'player', 'character', 'opponent_name', 'rounds_won', 'rounds_lost', 'winner')
    ordering = ['-battle_at']  # Ensures newest matches show first

# Register your models here.
admin.site.register(Rank)
admin.site.register(Player)
admin.site.register(Character)
admin.site.register(Stage)
admin.site.register(Match, MatchAdmin)  # Fixed casing
