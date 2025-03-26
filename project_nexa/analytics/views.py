from django.shortcuts import render
from .models import Match
from datetime import timedelta
from django.db.models import Count, Sum

def index(request):
    # Get all matches and separate last 100 matches
    all_match_data = list(Match.objects.order_by('-battle_at'))
    last_100_matches = all_match_data[:100]
    print(last_100_matches)

    # Manually add 8 hours to battle_at timestamp for all matches
    for match in all_match_data:
        match.battle_at = match.battle_at + timedelta(hours=8)

    # Compute win/loss per character
    matchup_stats = Match.objects.filter(battle_at__in=[m.battle_at for m in last_100_matches]) \
        .values('opponent_character') \
        .annotate(
            total_matches=Count('battle_id'),
            wins=Sum('winner')  # Assuming 'winner' is stored as True for wins
        ).order_by('-total_matches')
    print(matchup_stats)

    # Compute win rate
    for matchup in matchup_stats:
        matchup['win_rate'] = (matchup['wins'] / matchup['total_matches']) * 100 if matchup['total_matches'] > 0 else 0

    # Sort by lowest win rate to highlight weaknesses
    matchup_weaknesses = sorted(matchup_stats, key=lambda x: x['win_rate'])

    return render(request, 'analytics/match_list.html', {
        'all_match_data': all_match_data,
        'last_100_matches': last_100_matches,
        'matchup_weaknesses': matchup_weaknesses
    })