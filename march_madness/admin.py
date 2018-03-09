from django.contrib import admin


from .models import Tournament, Round, Match, UserPrediction, Group, Team, TeamRank


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(TeamRank)
class TeamRankAdmin(admin.ModelAdmin):
    list_display = ("id", "team", 'year', 'seed')


class RoundInline(admin.StackedInline):
    model = Round


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", 'year')

    inlines = [RoundInline]


class MatchInline(admin.StackedInline):
    model = Match


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("name", "match_names")

    inlines = [MatchInline]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("round", "match_number", "date", "team1", "team2", "victor")


@admin.register(UserPrediction)
class UserPredictionAdmin(admin.ModelAdmin):
    list_display = ("user", "match", "guess", "team1_score", "team2_score")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("tournament", "name", "captain", "member_names")

    def member_names(self, instance):
        return ", ".join((str(mem.username) for mem in instance.members.all()))
