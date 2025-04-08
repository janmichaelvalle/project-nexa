from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('matches/', views.match_list, name='match_list'),
    path('test/', views.test_template, name='test'),
]
