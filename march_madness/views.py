from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q

from materialize_nav import NavView, SearchView

from .models import current_year, Tournament, Match
from .forms import UserPredictionForm


class MarchMadnessNav(NavView):
    AppName = "March Madness"
    Title = "March Madness"
    HomeURL = 'march_madness:group_scores'


MarchMadnessNav.add_navigation_header("March Madness")
MarchMadnessNav.add_navigation("march_madness:group_scores", "Group Scores", app="March Madness")
MarchMadnessNav.add_navigation("march_madness:my_bracket", "My Bracket", app="March Madness")
try:
    __tourn = Tournament.objects.get(year=current_year())
    for __rnd in __tourn.rounds.all():
        MarchMadnessNav.add_navigation("march_madness:round", str(__rnd), app="March Madness", url_args=(__rnd.id,))
except:
    pass


def tournament_standings(request, user=None):
    year = request.GET.get("year", current_year())
    tournament = request.GET.get("tournament", None)
    user = request.GET.get("user", user)

    if user is None:
        page_title = "Tournament Standings"
    else:
        user = get_object_or_404(get_user_model(), username__iexact=user)
        page_title = "%s Bracket" % user
    context = MarchMadnessNav.get_context(request, page_title=page_title, fixed_sidebar=False, container_on=False)

    tourney = get_object_or_404(Tournament, Q(year=year) | Q(name__iexact=tournament))
    context["tournament"] = tourney

    if user is not None and user == request.user and request.user.is_authenticated:
        now = timezone.now().date()
        context["matches"] = {rnd: [get_form_or_match(user, mtch, rnd) for mtch in rnd.matches.all()]
                              for rnd in tourney.rounds.all()}
    else:
        context["matches"] = {rnd: rnd.matches.all()
                              for rnd in tourney.rounds.all()}
    return render(request, "march_madness/bracket.html", context)


def my_bracket(request):
    """View my bracket"""
    if not request.user.is_authenticated:
        return redirect("march_madness:tournament_standings")
    return tournament_standings(request, request.user)


def view_bracket(request):
    """View the bracket for the given user."""
    return tournament_standings(request)


def get_form_or_match(user, match, rnd, *args, **kwargs):
    now = timezone.now().date()
    if user is None:
        return match
    elif rnd and (rnd.start_date and now >= rnd.start_date):
        match.user_guess = match.prediction(user)
        return match
    return UserPredictionForm(user, match, *args, **kwargs)


def view_round(request, pk):
    """View the round for the given user."""
    year = request.GET.get("year", current_year())
    tournament = request.GET.get("tournament", None)
    user = request.GET.get("user", request.user)

    tourney = get_object_or_404(Tournament, Q(year=year) | Q(name__iexact=tournament))
    rnd = tourney.rounds.get(pk=pk)
    if user:
        user = get_object_or_404(get_user_model(), username__iexact=user)
        page_title = "%s's Bracket" % user
    else:
        page_title = None

    title = "%s - %s" % (str(tourney), str(rnd))
    context = MarchMadnessNav.get_context(request, title=title, page_title=page_title,
                                          fixed_sidebar=False, container_on=False)
    context["tournament"] = tourney
    context["rnd"] = rnd

    if user is not None and user == request.user and user.is_authenticated:
        context["matches"] = [get_form_or_match(user, match, rnd) for match in rnd.matches.all()]
    else:
        context["matches"] = rnd.matches.all()

    return render(request, "march_madness/round.html", context)


@login_required
def user_prediction(request):
    user = request.user

    if request.method == "GET" or (user is None or not user.is_authenticated):
        return redirect("march_madness:home")

    post_data = {key: request.POST[key] for key in request.POST}
    post_data["user"] = user.id
    form = get_form_or_match(user, Match.objects.get(pk=request.POST["match"]), None, post_data)
    if form.is_valid():
        form.save()

    return redirect("march_madness:home")


def view_group_scores(request):
    year = request.GET.get("year", current_year())
    tournament = request.GET.get("tournament", None)

    tourney = get_object_or_404(Tournament, Q(year=year) | Q(name__iexact=tournament))
    page_title = "Group Scores"
    context = MarchMadnessNav.get_context(request, title=str(tourney), page_title=page_title,
                                          fixed_sidebar=False, container_on=False)
    context["tournament"] = tourney
    context["groups"] = [{"name": group.name, "captain": group.captain, "score": 0,
                          "members": [
                              {"username": mem.username, "first_name": mem.first_name, "last_name": mem.last_name,
                               "score": tourney.get_user_score(mem)}
                                      for mem in group.members.all()]}
                         for group in tourney.groups.all()]

    for group in context["groups"]:
        for user in group["members"]:
            group["score"] += user["score"]

    return render(request, "march_madness/group_scores.html", context)

