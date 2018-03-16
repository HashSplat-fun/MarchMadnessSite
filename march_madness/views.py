from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse

from materialize_nav import NavView, SearchView

from .models import current_year, Tournament, Match, Team
from .forms import UserPredictionForm


class MarchMadnessNav(NavView):
    AppName = "March Madness"
    Title = "March Madness"
    HomeURL = 'march_madness:group_scores'
    FixedSidebar = False
    ContainerOn = False


MarchMadnessNav.add_navigation_header("March Madness")
MarchMadnessNav.add_navigation("march_madness:group_scores", "Group Scores", app="March Madness")


def tournament_standings(request):
    year = request.GET.get("year", current_year())
    tourney = get_object_or_404(Tournament, Q(year=year) | Q(name__iexact=request.GET.get("tournament", None)))

    view = MarchMadnessNav(title=str(tourney), page_title="Tournament Standings")

    nav_items = [view.NavItem(rnd, str(rnd), app="March Madness") for rnd in tourney.rounds.all()]
    if request.user and request.user.is_authenticated:
        url = reverse("march_madness:bracket", kwargs={"user": request.user.username})
        my_bracket = view.NavItem(url, "My Bracket", app="March Madness")
        nav_items = [my_bracket] + nav_items
    context = view.get_context(request, nav_items=nav_items)

    context["tournament"] = tourney
    num_rounds = tourney.rounds.count()
    context["matches"] = {rnd: [get_form_or_match(request, None, mtch, rnd, num_rounds=num_rounds) for mtch in rnd.matches.all()]
                          for rnd in tourney.rounds.all().select_related()}
    return render(request, "march_madness/bracket.html", context)


def view_bracket(request, user=None):
    """View the bracket for the given user."""
    if user is None and not request.user.is_authenticated:
        return redirect("login")
    elif user is None:
        user = request.user

    year = request.GET.get("year", current_year())
    tourney = get_object_or_404(Tournament, Q(year=year) | Q(name__iexact=request.GET.get("tournament", None)))
    if not isinstance(user, get_user_model()):
        user = get_object_or_404(get_user_model(), username__iexact=str(user))

    view = MarchMadnessNav(title=str(tourney), page_title="%s's Bracket" % user.username)

    # Page navigation
    nav_items = [view.NavItem(rnd, str(rnd), app="March Madness") for rnd in tourney.rounds.all()]
    if request.user and request.user.is_authenticated:
        url = reverse("march_madness:bracket", kwargs={"user": request.user.username})
        my_bracket = view.NavItem(url, "My Bracket", app="March Madness")
        nav_items = [my_bracket] + nav_items
    context = view.get_context(request, nav_items=nav_items)

    context["user"] = user
    context["tournament"] = tourney
    num_rounds = tourney.rounds.count()
    context["matches"] = {rnd: [get_form_or_match(request, user, mtch, rnd, num_rounds=num_rounds) for mtch in rnd.matches.all()]
                          for rnd in tourney.rounds.all().select_related()}
    return render(request, "march_madness/bracket.html", context)


def get_form_or_match(request, user, match, rnd, *args, num_rounds=None, **kwargs):
    now = timezone.now().date()

    match.num_rounds = num_rounds

    if user is None:
        return match
    elif match.victor or (user != request.user or not user.is_authenticated) or \
            (rnd and (rnd.start_date and now >= rnd.start_date)):
        match.user_guess = match.prediction(user)

        parent1, parent2 = match.parent_matches()
        if parent1:
            match.parent_team1_guess = parent1.prediction(user)
            if not match.team1 and parent1.victor:
                match.team1 = parent1.victor
                match.save()
        if parent2:
            match.parent_team2_guess = parent2.prediction(user)
            if not match.team2 and parent2.victor:
                match.team2 = parent2.victor
                match.save()

        return match

    form = UserPredictionForm(user, match, *args, **kwargs)
    if match and match.date:
        form.date = match.date
    return form


@login_required
def view_round(request, pk):
    """View the round for the given user."""
    year = request.GET.get("year", current_year())
    tourney = get_object_or_404(Tournament, Q(year=year) | Q(name__iexact=request.GET.get("tournament", None)))
    user = request.user

    rnd = tourney.rounds.get(pk=pk)

    view = MarchMadnessNav(title=str(tourney), page_title=str(rnd))

    # Page navigation
    nav_items = [view.NavItem(rnd, str(rnd), app="March Madness") for rnd in tourney.rounds.all()]
    if request.user and request.user.is_authenticated:
        url = reverse("march_madness:bracket", kwargs={"user": request.user.username})
        my_bracket = view.NavItem(url, "My Bracket", app="March Madness")
        nav_items = [my_bracket] + nav_items
    context = view.get_context(request, nav_items=nav_items)

    context["tournament"] = tourney
    context["rnd"] = rnd
    num_rounds = tourney.rounds.count()
    context["matches"] = [get_form_or_match(request, user, match, rnd, num_rounds=num_rounds) for match in rnd.matches.all()]

    return render(request, "march_madness/round.html", context)


@login_required
def user_prediction(request):
    user = request.user

    if request.method == "GET" or (user is None or not user.is_authenticated):
        return redirect("march_madness:home")

    post_data = {key: request.POST[key] for key in request.POST}
    post_data["user"] = user.id
    match = Match.objects.get(pk=request.POST["match"])
    form = get_form_or_match(request, user, match, None, post_data)
    if form.is_valid():
        instance = form.save()
        if request.is_ajax():
            return JsonResponse({'success': True, 'team': str(instance.guess)})
    elif request.is_ajax():
        try:
            return JsonResponse({'success': False, 'team': str(Team.objects.get(pk=int(form["guess"].value())))})
        except:
            return JsonResponse({'success': False, 'team': ''})

    return redirect("march_madness:home")


def view_group_scores(request):
    year = request.GET.get("year", current_year())
    tourney = get_object_or_404(Tournament, Q(year=year) | Q(name__iexact=request.GET.get("tournament", None)))

    view = MarchMadnessNav(title=str(tourney), page_title="Group Scores")

    # Page navigation
    nav_items = [view.NavItem(rnd, str(rnd), app="March Madness") for rnd in tourney.rounds.all()]
    if request.user and request.user.is_authenticated:
        url = reverse("march_madness:bracket", kwargs={"user": request.user.username})
        my_bracket = view.NavItem(url, "My Bracket", app="March Madness")
        nav_items = [my_bracket] + nav_items
    context = view.get_context(request, nav_items=nav_items)

    def modify_user(mem, tourney):
        mem.score = tourney.get_user_score(mem) or 0
        return mem

    context["tournament"] = tourney
    context["groups"] = [{"name": group.name, "captain": group.captain, "score": 0,
                          "members": [modify_user(mem, tourney)
                                      for mem in group.members.all()]}
                         for group in tourney.groups.all()]

    for group in context["groups"]:
        for user in group["members"]:
            group["score"] += user.score

    return render(request, "march_madness/group_scores.html", context)

