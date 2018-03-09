from django.urls import path, re_path
from . import views


app_name = "march_madness"

urlpatterns = [
    path('', views.my_bracket, name="home"),
    path('group_scores/', views.view_group_scores, name="group_scores"),
    path('tournament_standings/', views.tournament_standings, name="tournament_standings"),
    path('round/<int:pk>/', views.view_round, name="round"),
    path('bracket/mine/', views.my_bracket, name="my_bracket"),
    path('bracket/', views.view_bracket, name="bracket"),
    path('user_prediction/', views.user_prediction, name="user_prediction")
]
