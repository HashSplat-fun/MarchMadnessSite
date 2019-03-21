from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse, Http404
import urllib.parse

from materialize_nav import NavView, SearchView

from .models import current_year, Tournament, Round, Match, Team
from .forms import UserPredictionForm


class MarchMadnessNav(NavView):
    AppName = "March Madness"
    Title = "March Madness"
    HomeURL = 'march_madness:group_scores'
    FixedSidebar = False
    ContainerOn = False


MarchMadnessNav.add_navigation_header("Tournaments")
MarchMadnessNav.add_navigation_header("March Madness")
MarchMadnessNav.add_navigation("march_madness:group_scores", "Group Scores", app="March Madness")


def reverse_params(view, *args, url_kwargs=None, **kwargs):
    if url_kwargs is None:
        url_kwargs = {}
    if not isinstance(view, str):
        url = view.get_absolute_url()
    else:
        url = reverse(view, args=args, kwargs=url_kwargs)
    return url + '?' + urllib.parse.urlencode(kwargs)


def get_tournament_or_404(request):
    """Return the tournament requested for the given params.

    Args:
        request: Request object containing the get parameters
    """
    try:
        return Tournament.objects.get(Q(name__iexact=request.GET.get("tournament", None)) |
                                      Q(pk=request.GET.get("tournament", None)))
    except Tournament.DoesNotExist:
        pass
    try:
        t = list(Tournament.objects.filter().order_by('-year'))[0]
        return t
    except (IndexError, ValueError, TypeError, KeyError):
        pass
    raise Http404


def get_nav_items(request, view, tourney):
    """Return a context with all of the proper nav items."""
    nav_items = [view.NavItem(reverse_params("march_madness:group_scores", tournament=t.pk), str(t), app="Tournaments")
                 for t in Tournament.objects.all() if t != tourney]

    nav_items.extend([view.NavItem(reverse_params(rnd, tournament=tourney.pk), str(rnd), app="March Madness")
                      for rnd in tourney.rounds.all()])

    if request.user and request.user.is_authenticated:
        url = reverse_params("march_madness:bracket", url_kwargs={"user": request.user.username}, tournament=tourney.pk)
        my_bracket = view.NavItem(url, "My Bracket", app="March Madness")
        nav_items = [my_bracket] + nav_items
    context = view.get_context(request, nav_items=nav_items)
    context['tournament'] = tourney
    return context


def get_form_or_match(request, user, match, rnd, *args, num_rounds=None, check_captain=False, **kwargs):
    now = timezone.now().date()

    match.num_rounds = num_rounds

    is_captain = check_captain and match.get_captain_for_user(user) == request.user
    can_user_vote = request.user.is_authenticated and (user == request.user or is_captain)

    if user is None:
        return match
    elif match.victor or not can_user_vote or (rnd and (rnd.start_date and now >= rnd.start_date)):
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


def tournament_standings(request):
    tourney = get_tournament_or_404(request)

    view = MarchMadnessNav(title=str(tourney), page_title="Tournament Standings")
    context = get_nav_items(request, view, tourney)

    num_rounds = tourney.rounds.count()
    context["matches"] = {rnd: [get_form_or_match(request, None, mtch, rnd, num_rounds=num_rounds)
                                for mtch in rnd.matches.all()]
                          for rnd in tourney.rounds.all().select_related()}
    return render(request, "march_madness/bracket.html", context)


def view_bracket(request, user=None):
    """View the bracket for the given user."""
    if user is None and not request.user.is_authenticated:
        return redirect("login")
    elif user is None:
        user = request.user

    tourney = get_tournament_or_404(request)
    if not isinstance(user, get_user_model()):
        user = get_object_or_404(get_user_model(), username__iexact=str(user))

    view = MarchMadnessNav(title=str(tourney), page_title="%s's Bracket" % user.username)
    context = get_nav_items(request, view, tourney)

    context["user"] = user
    num_rounds = tourney.rounds.count()
    context["matches"] = {rnd: [get_form_or_match(request, user, mtch, rnd, num_rounds=num_rounds) for mtch in rnd.matches.all()]
                          for rnd in tourney.rounds.all().select_related()}
    return render(request, "march_madness/bracket.html", context)


def captain_view_bracket(request, user=None):
    """View the bracket for the given user if Captain."""
    if user is None and not request.user.is_authenticated:
        return redirect("login")
    elif user is None:
        user = request.user

    tourney = get_tournament_or_404(request)
    if not isinstance(user, get_user_model()):
        user = get_object_or_404(get_user_model(), username__iexact=str(user))

    view = MarchMadnessNav(title=str(tourney), page_title="%s's Bracket" % user.username)
    context = get_nav_items(request, view, tourney)

    context["user"] = user
    num_rounds = tourney.rounds.count()
    context["matches"] = {rnd: [get_form_or_match(request, user, mtch, rnd, num_rounds=num_rounds, check_captain=True)
                                for mtch in rnd.matches.all()]
                          for rnd in tourney.rounds.all().select_related()}
    return render(request, "march_madness/bracket.html", context)


@login_required
def view_round(request, pk):
    """View the round for the given user."""
    tourney = get_tournament_or_404(request)
    user = request.user
    rnd = get_object_or_404(Round, tournament=tourney, pk=pk)

    view = MarchMadnessNav(title=str(tourney), page_title=str(rnd))
    context = get_nav_items(request, view, tourney)

    context["rnd"] = rnd
    num_rounds = tourney.rounds.count()
    context["matches"] = [get_form_or_match(request, user, match, rnd, num_rounds=num_rounds) for match in rnd.matches.all()]

    return render(request, "march_madness/round.html", context)


@login_required
def user_prediction(request):
    if request.method == "GET" or (request.user is None or not request.user.is_authenticated):
        return redirect("march_madness:home")

    post_data = {key: request.POST[key] for key in request.POST}
    user = get_object_or_404(get_user_model(), pk=post_data['user'])  # Get the correct user. Captain can vote now
    match = Match.objects.get(pk=request.POST["match"])
    form = get_form_or_match(request, user, match, None, post_data, check_captain=True)
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
    tourney = get_tournament_or_404(request)
    view = MarchMadnessNav(title=str(tourney), page_title="Group Scores")
    context = get_nav_items(request, view, tourney)

    def modify_user(mem, tourney):
        mem.score = tourney.get_user_score(mem) or 0
        return mem

    context["groups"] = [{"name": group.name, "captain": group.captain, "score": 0,
                          "members": [modify_user(mem, tourney)
                                      for mem in group.members.all()]}
                         for group in tourney.groups.all()]

    for group in context["groups"]:
        for user in group["members"]:
            group["score"] += user.score

    return render(request, "march_madness/group_scores.html", context)
