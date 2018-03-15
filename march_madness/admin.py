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
    list_display = ("round", "match_number", "date", "team1", "team2", "victor")
    list_filter = ['round__tournament__year', 'round__round_number', 'match_number', 'date']
    search_fields = ['team1__name', 'team2__name', 'victor__name']
    ordering = ('round__tournament', 'round__round_number', 'match_number')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if form.initial["team1"] and form.initial["team2"]:
            form.fields["victor"].choices = [()]
        return form


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
