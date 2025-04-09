from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('in_game_name', 'polaris_id', 'rank', 'user')
    search_fields = ('in_game_name', 'polaris_id', 'user__email')