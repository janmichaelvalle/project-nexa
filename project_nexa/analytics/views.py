from django.shortcuts import render
from .models import Match
from django.db.models import Count, Sum, IntegerField
from django.db.models.functions import Cast

def index(request):
    # Get all matches sorted by battle_at
    all_match_data = list(Match.objects.order_by('-battle_at'))
    last_100_matches = Match.objects.order_by('-battle_at')[:100]

    # Function to compute win rate per character from a queryset
    def compute_win_rate(queryset):
        stats = queryset.values('opponent_character') \
            .annotate(
                total_matches=Count('battle_id'),
                wins=Sum(Cast('winner', IntegerField()))
            )
        for stat in stats:
            stat['win_rate'] = (stat['wins'] / stat['total_matches']) * 100 if stat['total_matches'] > 0 else 0
        return {s['opponent_character']: s for s in stats}

    # Compute win rate for last 100 matches
    matchup_weaknesses = compute_win_rate(last_100_matches).values()
    matchup_weaknesses = sorted(matchup_weaknesses, key=lambda x: x['win_rate'])

    # Find the last 20 matches per opponent character
    character_match_history = {}
    for match in all_match_data:
        char = match.opponent_character
        if char not in character_match_history:
            character_match_history[char] = []
        character_match_history[char].append(match)

    # Compare last 10 vs. previous 10 matches for each character
    matchup_trends = []
    for char, matches in character_match_history.items():
        if len(matches) < 10:
            continue  # Skip if there are not enough matches

        last_20 = matches[:20]  # Get last 20 matches for this character
        recent_10 = last_20[:10]  # Most recent 10 matches
        previous_10 = last_20[10:20]  # Previous 10 matches

        recent_win_rates = compute_win_rate(Match.objects.filter(battle_at__in=[m.battle_at for m in recent_10]))
        previous_win_rates = compute_win_rate(Match.objects.filter(battle_at__in=[m.battle_at for m in previous_10]))

        recent = recent_win_rates.get(char, {'win_rate': 0})
        previous = previous_win_rates.get(char, {'win_rate': 0})

        improvement = recent['win_rate'] - previous['win_rate']

        matchup_trends.append({
            'opponent_character': char,
            'previous_win_rate': previous['win_rate'],
            'recent_win_rate': recent['win_rate'],
            'improvement': improvement
        })

    # Sort trends by improvement (from worst to best)
    matchup_trends = sorted(matchup_trends, key=lambda x: x['improvement'])

    return render(request, 'analytics/match_list.html', {
        'all_match_data': all_match_data,
        'matchup_weaknesses': matchup_weaknesses,
        'matchup_trends': matchup_trends,
    })