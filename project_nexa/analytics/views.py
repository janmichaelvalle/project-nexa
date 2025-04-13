from django.shortcuts import render, redirect
from .models import Match
from django.db.models import Count, Sum, IntegerField, Q
from django.db.models.functions import Cast
from django.contrib import messages

def index(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'profile'):
        return render(request, 'analytics/match_list.html', {
            'error': 'No profile found or user not logged in.'
        })
    
    user_profile = request.user.profile

    return render(request, 'analytics/match_list.html', {
        'user_profile': user_profile
    })




def match_list(request):
    return render(request, 'analytics/match_list.html')






def matchup_summary(request):
    def add_set_result(score, match):
        return {
            'wins': score,
            'result': 'Win' if score == 2 else 'Loss',
            'your_character': match.character,
            'opponent_character': match.opponent_character
            }

    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to access the matchup summary.")
        return redirect('login')
    
    
    user_profile = request.user.profile
    analysis_format = request.GET.get('analysis_format') #Gets sets/matches for dropdown in html
    selected_user_character = request.GET.get('user_character') #Get the user's character from dropdown in the html
    selected_opponent_character = request.GET.get('opponent_character') #Gets the opponent_character for dropdown in html
    matches = Match.objects.filter(profile=user_profile).order_by('battle_at')
          # Pull all matches from that user

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
                    if m.winner is True:
                        wins += 1
                sets.append(add_set_result(wins, buffer[-1]))
            # Reset buffer
            buffer = []
            current_opponent = match.opponent_name

        buffer.append(match)

    # After loop, evaluate final buffer
    if len(buffer) >= 2:
        wins = 0
        for m in buffer:
            if m.winner is True:
                wins += 1
        sets.append(add_set_result(wins, buffer[-1]))






    # sets = []
    # current_set_score = 0
    # number_of_matches = 0
    # current_opponent = None

    # for match in matches:
    #     if current_opponent is None:
    #         # First match
    #         current_opponent = match.opponent_name
    #         if match.winner is True:
    #             current_set_score += 1
    #         number_of_matches = 1
    #         print(f"This is opening match #{number_of_matches} against {current_opponent} and won {current_set_score} set/s")
    #     elif match.opponent_name == current_opponent:
    #         number_of_matches += 1
    #         print(f"This is match #{number_of_matches} against {current_opponent} and won {current_set_score} set/s")
    #         # Same opponent, add to current set
    #         if match.winner is True:
    #             current_set_score += 1       
    #     else:
    #          # Opponent changed — finalize the last set **before** moving on
    #         if number_of_matches >= 2:
    #             sets.append(add_set_result(current_set_score, previous_match))
    #             # Reset for new opponent
    #             number_of_matches = 0
    #             current_set_score = 0
    #             current_opponent = None
    #     previous_match = match  
    # if number_of_matches >= 2:
    #     sets.append(add_set_result(current_set_score, previous_match))
        

                
     
            

    print(f"The current user is {request.user}")
    print(f"Analysis format is {analysis_format}")
    if analysis_format == 'Set':
        print("Here are the sets:", sets)
    if analysis_format == 'Match':
        print(f"Here are the matches {matches}")
    
    if selected_user_character:
        matches = matches.filter(character=selected_user_character)
    
    if selected_opponent_character:
        matches = matches.filter(opponent_character=selected_opponent_character)
    
    user_characters = Match.objects.filter(profile=user_profile).values_list('character', flat=True).distinct()
    opponent_characters = Match.objects.filter(profile=user_profile).values_list('opponent_character', flat=True).distinct()
    
    
    
    return render(request, 'analytics/matchups.html', {
        'sets': sets,
        'matches': matches,
        'analysis_format': analysis_format,
        'selected_user_character': selected_user_character,
        'selected_opponent_character': selected_opponent_character,
        'user_characters': user_characters,
        'opponent_characters': opponent_characters
    })









    """
    # === MATCHUP ANALYSIS - TEMP DISABLED ===
    
    # Get all matches sorted by battle_at
    all_match_data = list(Match.objects.filter(profile=user_profile).order_by('-battle_at'))
    all_100_matches_qs = Match.objects.filter(
        Q(profile=user_profile) & (Q(rounds_won=2) | Q(rounds_lost=2))
    ).order_by('-battle_at')
    last_100_matches = list(all_100_matches_qs[:100])
    date_100_first = last_100_matches[-1].battle_at.date() if last_100_matches else None
    date_100_last = last_100_matches[0].battle_at.date() if last_100_matches else None
    print(f"Total last 100 matches: {len(last_100_matches)}")
    print("Last 100 Matches:", last_100_matches)

    # Debug prints to check the correctness of last_100_matches
    for match in last_100_matches:
        print(match.battle_at, match.character, match.opponent_character, match.opponent_name, match.rounds_won, match.rounds_lost)

    # Function to compute loss rate per character based on completed sets
    def compute_loss_rate(queryset):
        stats = queryset.values('opponent_character') \
            .annotate(
                total_sets=Count('battle_at'),  # Count occurrences of battle_at
                losses=Sum(Cast(Q(rounds_lost=2), IntegerField()))  # Sum only where player lost
            )
        for stat in stats:
            stat['loss_rate'] = (stat['losses'] / stat['total_sets']) * 100 if stat['total_sets'] > 0 else 0
            stat['win_rate'] = (1 - (stat['losses'] / stat['total_sets'])) * 100 if stat['total_sets'] > 0 else 0
        return {s['opponent_character']: s for s in stats}

    # Compute overall loss rate for all completed sets
    overall_loss_rates = compute_loss_rate(
        Match.objects.filter(Q(profile=user_profile) & (Q(rounds_won=2) | Q(rounds_lost=2)))
    )

    # Compute loss contribution for last 100 sets, summing multiple sets properly
    loss_contributions_100 = {}
    max_total_sets = 0

    for match in last_100_matches:
        char = match.opponent_character
        if char not in loss_contributions_100:
            loss_contributions_100[char] = {'total_sets': 0, 'losses': 0}

        loss_contributions_100[char]['total_sets'] += 1
        if match.rounds_lost == 2:
            loss_contributions_100[char]['losses'] += 1

        if loss_contributions_100[char]['total_sets'] > max_total_sets:
            max_total_sets = loss_contributions_100[char]['total_sets']

    # Calculate total losses to compute contribution percentage
    total_losses_last_100 = sum(data['losses'] for data in loss_contributions_100.values())
    print(f"Total losses in last 100: {total_losses_last_100}")

    loss_contributions_list_100 = []

    for char, data in loss_contributions_100.items():
        adjusted_loss_contribution = (data['losses'] / total_losses_last_100 * (data['total_sets'] / max_total_sets)) * 100 if total_losses_last_100 > 0 else 0
        win_rate = (1 - (data['losses'] / data['total_sets'])) * 100 if data['total_sets'] > 0 else 0
        loss_contributions_list_100.append({
            'opponent_character': char,
            'total_sets': data['total_sets'],
            'losses': data['losses'],
            'adjusted_loss_contribution': adjusted_loss_contribution,
            'win_rate': win_rate
        })

    loss_contributions_list_100 = sorted(loss_contributions_list_100, key=lambda x: x['adjusted_loss_contribution'], reverse=True)
    print("Loss Contributions 100:", loss_contributions_list_100)

    # Compute loss contribution for last 50 sets, summing multiple sets properly
    last_50_matches = Match.objects.filter(
        Q(profile=user_profile) & (Q(rounds_won=2) | Q(rounds_lost=2))
    ).order_by('-battle_at')[:50]
    date_50_first = last_50_matches[len(last_50_matches) - 1].battle_at.date() if last_50_matches else None
    date_50_last = last_50_matches[0].battle_at.date() if last_50_matches else None
    
    loss_contributions_50 = {}
    max_total_sets_50 = 0

    for match in last_50_matches:
        char = match.opponent_character
        if char not in loss_contributions_50:
            loss_contributions_50[char] = {'total_sets': 0, 'losses': 0}

        loss_contributions_50[char]['total_sets'] += 1
        if match.rounds_lost == 2:
            loss_contributions_50[char]['losses'] += 1

        if loss_contributions_50[char]['total_sets'] > max_total_sets_50:
            max_total_sets_50 = loss_contributions_50[char]['total_sets']

    # Calculate total losses to compute contribution percentage
    total_losses_last_50 = sum(data['losses'] for data in loss_contributions_50.values())

    loss_contributions_list_50 = []

    for char, data in loss_contributions_50.items():
        adjusted_loss_contribution = (data['losses'] / total_losses_last_50 * (data['total_sets'] / max_total_sets_50)) * 100 if total_losses_last_50 > 0 else 0
        win_rate = (1 - (data['losses'] / data['total_sets'])) * 100 if data['total_sets'] > 0 else 0
        loss_contributions_list_50.append({
            'opponent_character': char,
            'total_sets': data['total_sets'],
            'losses': data['losses'],
            'adjusted_loss_contribution': adjusted_loss_contribution,
            'win_rate': win_rate
        })

    loss_contributions_list_50 = sorted(loss_contributions_list_50, key=lambda x: x['adjusted_loss_contribution'], reverse=True)

    # Compute loss contribution for last 25 sets, summing multiple sets properly
    last_25_matches = Match.objects.filter(
        Q(profile=user_profile) & (Q(rounds_won=2) | Q(rounds_lost=2))
    ).order_by('-battle_at')[:25]
    date_25_first = last_25_matches[len(last_25_matches) - 1].battle_at.date() if last_25_matches else None
    date_25_last = last_25_matches[0].battle_at.date() if last_25_matches else None
    
    loss_contributions_25 = {}
    max_total_sets_25 = 0

    for match in last_25_matches:
        char = match.opponent_character
        if char not in loss_contributions_25:
            loss_contributions_25[char] = {'total_sets': 0, 'losses': 0}

        loss_contributions_25[char]['total_sets'] += 1
        if match.rounds_lost == 2:
            loss_contributions_25[char]['losses'] += 1

        if loss_contributions_25[char]['total_sets'] > max_total_sets_25:
            max_total_sets_25 = loss_contributions_25[char]['total_sets']

    total_losses_last_25 = sum(data['losses'] for data in loss_contributions_25.values())

    loss_contributions_list_25 = []

    for char, data in loss_contributions_25.items():
        adjusted_loss_contribution = (data['losses'] / total_losses_last_25 * (data['total_sets'] / max_total_sets_25)) * 100 if total_losses_last_25 > 0 else 0
        win_rate = (1 - (data['losses'] / data['total_sets'])) * 100 if data['total_sets'] > 0 else 0
        loss_contributions_list_25.append({
            'opponent_character': char,
            'total_sets': data['total_sets'],
            'losses': data['losses'],
            'adjusted_loss_contribution': adjusted_loss_contribution,
            'win_rate': win_rate
        })

    loss_contributions_list_25 = sorted(loss_contributions_list_25, key=lambda x: x['adjusted_loss_contribution'], reverse=True)

    # Compute the change in loss contribution over time
    loss_contribution_trends = []

    for char in loss_contributions_100:
        last_100 = next((item for item in loss_contributions_list_100 if item['opponent_character'] == char), None)
        last_50 = next((item for item in loss_contributions_list_50 if item['opponent_character'] == char), None)

        loss_100 = last_100['adjusted_loss_contribution'] if last_100 else 0
        loss_50 = last_50['adjusted_loss_contribution'] if last_50 else 0
        change = loss_50 - loss_100  # Negative means improvement

        loss_contribution_trends.append({
            'opponent_character': char,
            'loss_contribution_50': loss_50,
            'loss_contribution_100': loss_100,
            'change': change,
            'total_sets': last_50['total_sets'] if last_50 else 0,
            'losses': last_50['losses'] if last_50 else 0,
            'win_rate': last_50['win_rate'] if last_50 else 0,
        })

    # Sort by highest worsening loss contribution
    loss_contribution_trends = sorted(loss_contribution_trends, key=lambda x: x['change'], reverse=True)

    # Find the last 20 sets per opponent character
    character_match_history = {}
    for match in all_match_data:
        char = match.opponent_character
        if char not in character_match_history:
            character_match_history[char] = []
        character_match_history[char].append(match)

    # Compare last 10 vs. previous 10 sets for each character
    matchup_performance = []
    for char, matches in character_match_history.items():
        completed_sets = [m for m in matches if m.rounds_won == 2 or m.rounds_lost == 2]
        if len(completed_sets) < 20:
            continue  # Skip if there are less than 20 completed sets

        last_20 = completed_sets[:20]
        recent_10 = last_20[:10]
        previous_10 = last_20[10:] if len(last_20) > 10 else []

        recent_loss_rates = compute_loss_rate(Match.objects.filter(profile=user_profile, battle_at__in=[m.battle_at for m in recent_10]))
        
        if previous_10:
            previous_loss_rates = compute_loss_rate(Match.objects.filter(profile=user_profile, battle_at__in=[m.battle_at for m in previous_10]))
            previous = previous_loss_rates.get(char, {'loss_rate': 0, 'win_rate': 0})
        else:
            previous = {'loss_rate': 0, 'win_rate': 0}

        recent = recent_loss_rates.get(char, {'loss_rate': 0, 'win_rate': 0})
        overall = overall_loss_rates.get(char, {'loss_rate': 0, 'win_rate': 0})

        improvement = recent['win_rate'] - previous['win_rate']

        matchup_performance.append({
            'opponent_character': char,
            'total_sets': overall.get('total_sets', 0),
            'losses': overall.get('losses', 0),
            'overall_loss_rate': overall.get('loss_rate', 0),
            'overall_win_rate': overall.get('win_rate', 0),
            'previous_loss_rate': previous['loss_rate'],
            'previous_win_rate': previous['win_rate'],
            'recent_loss_rate': recent['loss_rate'],
            'recent_win_rate': recent['win_rate'],
            'improvement': improvement
        })

    # Sort matchups by improvement (from worst to best)
    matchup_performance = sorted(matchup_performance, key=lambda x: x['improvement'])

    key_matchups = []
    for matchup in matchup_performance:
        key_matchups.append({
            'opponent_character': matchup['opponent_character'],
            'loss_contribution': matchup['overall_loss_rate'],
            'overall_win_rate': matchup['overall_win_rate'],
            'recent_win_rate': 100 - recent['loss_rate'],
            'previous_win_rate': 100 - previous['loss_rate'],
            'change': matchup['improvement']
        })

    return render(request, 'analytics/match_list.html', {
        'all_match_data': all_match_data,
        'matchup_performance': matchup_performance,
        'loss_contributions_100': loss_contributions_list_100,
        'loss_contributions_50': loss_contributions_list_50,
        'loss_contributions_25': loss_contributions_list_25,
        'loss_contribution_trends': loss_contribution_trends,
        'key_matchups': key_matchups,
        'loss_contribution_range': {
            100: {'first_date': date_100_first, 'last_date': date_100_last},
            50: {'first_date': date_50_first, 'last_date': date_50_last},
            25: {'first_date': date_25_first, 'last_date': date_25_last},
        }
    })

def match_list(request):
    return render(request, 'analytics/match_list.html')

"""