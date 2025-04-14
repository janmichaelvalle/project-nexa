from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('matches/', views.match_list, name='match_list'),
    path('matchups/', views.matchup_summary, name='matchup_summary'),
    path('regenerate/', views.regenerate_matches, name='regenerate_matches'),
]
