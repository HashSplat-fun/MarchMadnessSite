from django import template
from ..forms import UserPredictionForm
from ..models import UserPrediction

register = template.Library()


@register.inclusion_tag("march_madness/includes/match.html")
def render_match(match):
    return {"match": match}


@register.inclusion_tag("march_madness/includes/match_form_ajax_func.html")
def render_match_form_ajax_func(match, is_key_press=False):
    return {"match": match, "is_key_press": is_key_press}


@register.inclusion_tag("march_madness/includes/radio_match_form.html")
def render_radio_match_form(form):
    return {"form": form, "match": form.get_match()}


@register.inclusion_tag("march_madness/includes/select_match_form.html")
def render_select_match_form(form):
    return {"form": form, "match": form.get_match()}


@register.filter
def get_item(dit, key):
    try:
        return dit[key]
    except:
        return None


@register.filter
def user_guess(match, user):
    return match.prediction(user)
