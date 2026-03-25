# german_words/urls.py
from django.urls import path
from . import views

app_name = 'german_words'

urlpatterns = [
    path('', views.home, name='home'),
    path('words/', views.words, name='words'),
]
