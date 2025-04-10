from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('in_game_name', 'tekken_id', 'rank', 'user')
    search_fields = ('in_game_name', 'tekken_id', 'user__email')