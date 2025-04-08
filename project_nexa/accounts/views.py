import sqlite3
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm


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
            cursor.execute(
                "SELECT 1 FROM matches WHERE p1_polaris_id = ? OR p2_polaris_id = ? LIMIT 1",
                (tekken_id, tekken_id)
            )
            result = cursor.fetchone()
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


