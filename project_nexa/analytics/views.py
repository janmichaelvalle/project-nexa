import sqlite3
import os
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Match
from django.db.models import Count, Sum, IntegerField, Q
from django.db.models.functions import Cast
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from accounts.models import Profile
from analytics.models import Match, Character
from collections import defaultdict
from django.utils.timezone import localtime

def index(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'profile'):
        return render(request, 'analytics/match_list.html', {
            'error': 'No profile found or user not logged in.'
        })
    
    user_profile = request.user.profile

    return render(request, 'analytics/match_list.html', {
        'user_profile': user_profile
    })

@login_required
def regenerate_matches(request):
    user = request.user
    profile = user.profile
    tekken_id = profile.tekken_id

    # Delete old matches
    Match.objects.filter(profile=profile).delete()

    # Pull new data from wavu_data.sqlite3
    db_path = os.path.join(settings.BASE_DIR, 'wavu_data.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT battle_at, p1_polaris_id, p1_name, p1_chara_id, p1_rounds, 
               p2_polaris_id, p2_name, p2_chara_id, p2_rounds, winner
        FROM matches
        WHERE p1_polaris_id = ? OR p2_polaris_id = ?
        ORDER BY battle_at DESC
    """, (tekken_id, tekken_id))

    match_rows = cursor.fetchall()
    match_objects = []

    for row in match_rows:
        battle_at, p1_pid, p1_name, p1_chara_id, p1_rounds, p2_pid, p2_name, p2_chara_id, p2_rounds, winner = row
        battle_at = datetime.fromtimestamp(battle_at)
        is_p1 = tekken_id == p1_pid
        user_rounds = p1_rounds if is_p1 else p2_rounds
        opp_rounds = p2_rounds if is_p1 else p1_rounds
        char_id = p1_chara_id if is_p1 else p2_chara_id
        opponent_char_id = p2_chara_id if is_p1 else p1_chara_id
        opponent_name = p2_name if is_p1 else p1_name

        try:
            char = Character.objects.get(chara_id=char_id)
        except Character.DoesNotExist:
            continue

        try:
            opponent_char = Character.objects.get(chara_id=opponent_char_id)
            opponent_char_name = opponent_char.name
        except Character.DoesNotExist:
            opponent_char_name = "Unknown"

        match_objects.append(Match(
            profile=profile,
            battle_at=battle_at,
            battle_type=2,
            character=char,
            opponent_name=opponent_name,
            opponent_character=opponent_char_name,
            rounds_won=user_rounds,
            rounds_lost=opp_rounds,
            winner=(winner == 1 and not is_p1) or (winner == 2 and is_p1)
        ))

    Match.objects.bulk_create(match_objects)
    conn.close()

    messages.success(request, "Your match data has been refreshed.")
    return redirect('matchup_summary')


def match_list(request):
    return render(request, 'analytics/match_list.html')




def matchup_summary(request):
    def add_set_result(score, match):
        return {
            'battle_at': match.battle_at,
            'wins': score,
            'result': 'Win' if score == 2 else 'Loss',
            'your_character': match.character,
            'opponent_character': match.opponent_character
            }

    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to access the matchup summary.")
        return redirect('login')
    
    
    user_profile = request.user.profile
    analysis_format = request.GET.get('analysis_format') #Gets sets/matches html
    selected_user_character = request.GET.get('user_character') #Get the user's character from html
    selected_opponent_character = request.GET.get('opponent_character') #Gets the opponent_character for html
    matches = Match.objects.filter(profile=user_profile).order_by('-battle_at') # Pull all matches from that user
    user_characters = Character.objects.filter(chara_id__in=Match.objects.filter(profile=user_profile).values_list('character__chara_id', flat=True)).distinct() # Filters character selected
    opponent_characters = sorted(set(Match.objects.filter(profile=user_profile).values_list('opponent_character', flat=True))) #Filters opponent selected character

    if selected_user_character:
            selected_character = Character.objects.get(name=selected_user_character)
            matches = matches.filter(character=selected_character)
        
    
    if selected_opponent_character:
        matches = matches.filter(opponent_character=selected_opponent_character)

    sets = []
    buffer = []
    current_opponent = None

    for match in matches:
        if current_opponent is None:
            current_opponent = match.opponent_name

        if match.opponent_name != current_opponent:
            # Opponent changed – evaluate buffer
            # Checks if the buffer (temporary list of matches against the same opponent) contains 2 or more matches 
            if len(buffer) >= 2:
                # Loop through the buffered matches, and for each match that you won (m.winner is True), we increase the wins counter.
                wins = 0
                for m in buffer:
                    if m.winner is False:
                        wins += 1
                losses = len(buffer) - wins
                if wins == 2 or losses == 2:
                    sets.append(add_set_result(wins, buffer[-1]))
            # Reset buffer
            buffer = []
            current_opponent = match.opponent_name

        buffer.append(match)

    # After loop, evaluate final buffer
    if len(buffer) >= 2:
        wins = 0
        for m in buffer:
            if m.winner is False:
                wins += 1
        losses = len(buffer) - wins
        if wins == 2 or losses == 2:
            sets.append(add_set_result(wins, buffer[-1]))



    total = 0
    wins = 0

    if analysis_format == 'Match':
        total = matches.count()
        wins = matches.filter(winner=False).count()  # False means you won

    elif analysis_format == 'Set':
        total = len(sets)
        wins = sum(1 for s in sets if s['result'] == 'Win')

    overall_win_rate = round((wins / total) * 100, 2) if total > 0 else 0



    from collections import Counter

    loss_contribution = []

    if analysis_format == 'Match':
        losses = matches.filter(winner=True)  #Gets all matches that you lost to
        counter = Counter(losses.values_list('opponent_character', flat=True))
        loss_contribution = counter.most_common()
        print("Losses:", losses)
        print("Loss contribution per character:", counter)

    elif analysis_format == 'Set':
        counter = Counter(s['opponent_character'] for s in sets if s['result'] == 'Loss')
        loss_contribution = counter.most_common()





    

    

    ##### PRINT TESTING ###
    # print(f"The current user is {request.user}")
    # print(f"Analysis format is {analysis_format}")
    # print(f"This is the selected characters {selected_user_character}")
    # print(f"These are the matches {matches}")
    # print(f"These are the sets {sets}")
    print(f"The win rate is  {overall_win_rate}")


    

    
    # user_characters = Match.objects.filter(profile=user_profile).values_list('character', flat=True).distinct()



    
    daily_wl_data = defaultdict(lambda: {"wins": 0, "losses": 0})

    if analysis_format == 'Match':
        for match in matches.order_by('battle_at'):
            date = localtime(match.battle_at).date()
            if match.winner is False: 
                daily_wl_data[date]["wins"] += 1
            else:
                daily_wl_data[date]["losses"] += 1

    elif analysis_format == 'Set':
        for set_result in sets:
            date = localtime(set_result['battle_at']).date()
            if set_result['result'] == 'Win':
                daily_wl_data[date]["wins"] += 1
            else:
                daily_wl_data[date]["losses"] += 1

    wl_chart_data = []
    for date in sorted(daily_wl_data.keys()):
        wl_chart_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "wins": daily_wl_data[date]["wins"],
            "losses": daily_wl_data[date]["losses"],
        })

        
    
    
    return render(request, 'analytics/matchups.html', {
        'sets': sets,
        'matches': matches,
        'analysis_format': analysis_format,
        'selected_user_character': selected_user_character,
        'selected_opponent_character': selected_opponent_character,
        'user_characters': user_characters,
        'opponent_characters': opponent_characters,
        'wl_chart_data': wl_chart_data,
        'overall_win_rate': overall_win_rate,
        'loss_contribution': loss_contribution,

    })








