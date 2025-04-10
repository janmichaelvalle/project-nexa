import sqlite3
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            tekken_id = form.cleaned_data.get('tekken_id')

            # Path to your SQLite DB
            db_path = os.path.join(settings.BASE_DIR, 'wavu_data.sqlite3')

            # Check if tekken_id exists in the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT battle_at, p1_polaris_id, p1_name, p1_rank, p2_polaris_id, p2_name, p2_rank
                FROM matches
                WHERE p1_polaris_id = ? OR p2_polaris_id = ?
                ORDER BY battle_at DESC
                LIMIT 1
            """, (tekken_id, tekken_id))
            result = cursor.fetchone()
            if result:
                battle_at, p1_pid, p1_name, p1_rank, p2_pid, p2_name, p2_rank = result

                # Choose which side the user is (p1 or p2)
                if tekken_id == p1_pid:
                    ign = p1_name
                    rank = p1_rank
                else:
                    ign = p2_name
                    rank = p2_rank

                user = form.save(commit=False)
                user.save()

                Profile.objects.create(
                    user=user,
                    in_game_name=ign,
                    polaris_id=tekken_id,
                    rank_id=rank,  # or rank=Rank.objects.get(id=rank) if you're linking via FK to Rank model
                )

            conn.close()

            if not result:
                error_message = form.add_error('tekken_id', 
                'Tekken ID not found')
                print(error_message)
            else:
                form.save()
                messages.success(request, 'Welcome! Your account is created')
                return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'accounts/profile.html', {'profile':profile})

