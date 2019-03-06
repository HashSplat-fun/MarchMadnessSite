from django import forms
from django.contrib import admin


from .models import Tournament, Round, Match, UserPrediction, Group, Team, TeamRank


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_filter = ['name']
    search_fields = ['name']
    ordering = ('name',)


@admin.register(TeamRank)
class TeamRankAdmin(admin.ModelAdmin):
    list_display = ("id", "team", 'year', 'seed')
    list_filter = ['year', 'seed', 'team']
    search_fields = ['name', 'year', 'seed']
    ordering = ('year', 'seed', 'team__name',)


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", 'year')
    list_filter = ['year']
    search_fields = ['name', 'year']
    ordering = ('year', 'name')

    class RoundInline(admin.StackedInline):
        model = Round

    inlines = [RoundInline]


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("tournament", "name", 'round_number', 'start_date', 'end_date', "match_names")
    list_filter = ['tournament__year', 'round_number', 'start_date']
    search_fields = ['name']
    ordering = ('tournament', 'round_number')

    class MatchInline(admin.StackedInline):
        model = Match

    inlines = [MatchInline]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("round", "match_number", "date", "team1", "team2", "victor", "tournament_value")
    list_filter = ['round__tournament__year', 'round__round_number', 'match_number', 'date']
    search_fields = ['team1__name', 'team2__name', 'victor__name']
    ordering = ('round__tournament', 'round__round_number', 'match_number')

    class MatchForm(forms.ModelForm):

        class Meta:
            model = Match
            exclude = ['name']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if self.initial["team1"] and self.initial['team2']:
                team1 = Team.objects.get(pk=self['team1'].value())
                team2 = Team.objects.get(pk=self['team2'].value())
                self.fields['victor'].choices = [(None, self.fields['victor'].empty_label), (team1.id, str(team1)), (team2.id, str(team2))]

    form = MatchForm


@admin.register(UserPrediction)
class UserPredictionAdmin(admin.ModelAdmin):
    list_display = ("user", "match", "guess", "team1_score", "team2_score")
    list_filter = ['match__round__tournament__year', 'match__round__round_number', 'match__match_number']
    search_fields = ['user__first_name', 'user__username', 'guess__name']
    ordering = ('user', 'match__round__round_number', 'match__match_number')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("tournament", "name", "captain", "member_names")
    list_filter = ['tournament__year']
    search_fields = ['name', 'captain__username', 'captain__first_name']
    ordering = ('tournament', 'name',)

    def member_names(self, instance):
        return ", ".join((str(mem.username) for mem in instance.members.all()))
