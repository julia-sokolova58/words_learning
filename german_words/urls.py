from django.urls import path
from . import views

app_name = 'german_words'

urlpatterns = [
    path('', views.home, name='home'),
    path('words/', views.words, name='words'),
    path('grammar/<str:word>/', views.grammar_page, name='grammar'),
    path('synonyms/<str:word>/', views.synonyms_page, name='synonyms'),
]
