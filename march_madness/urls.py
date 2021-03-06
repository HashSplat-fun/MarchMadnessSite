from django.urls import path
from . import views


app_name = "march_madness"

urlpatterns = [
    path('', views.view_group_scores, name="home"),
    path('group_scores/', views.view_group_scores, name="group_scores"),
    path('tournament_standings/', views.tournament_standings, name="tournament_standings"),
    path('round/<int:pk>/', views.view_round, name="round"),
    path('bracket/<str:user>/captain/', views.captain_view_bracket, name="captain_bracket"),
    path('bracket/<str:user>/', views.view_bracket, name="bracket"),
    path('user_prediction/', views.user_prediction, name="user_prediction")
]
