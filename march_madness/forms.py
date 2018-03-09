from django import forms

from .models import UserPrediction, Team


class UserPredictionForm(forms.ModelForm):
    class Meta:
        model = UserPrediction
        fields = ["user", "match", "guess", "team1_score", "team2_score"]
        widgets = {"user": forms.HiddenInput(), "match": forms.HiddenInput()}

    def __init__(self, user, match, *args, **kwargs):
        try:
            if "initial" not in kwargs:
                kwargs["initial"] = {"user": user, "match": match}
            else:
                kwargs["initial"]["user"] = user
                kwargs["initial"]["match"] = match
            if "instance" not in kwargs:
                kwargs["instance"] = UserPrediction.objects.get(user=user, match=match)
        except UserPrediction.DoesNotExist:
            pass

        super(UserPredictionForm, self).__init__(*args, **kwargs)
        self._match = match

        # Change id to work with multiple forms on one page.
        self.fields["team1_score"].widget.attrs["id"] = "id_team1_score_" + str(match.id) + "_" + str(user.id)
        self.fields["team2_score"].widget.attrs["id"] = "id_team2_score_" + str(match.id) + "_" + str(user.id)
        guess_id = "id_guess_" + str(match.id) + "_" + str(user.id)
        self.fields["guess"].widget.attrs["id"] = guess_id

        # Get the team choices and check if the guess widget should be a radio button selection
        self._radio_form = False
        choices = [(t.id, str(t)) for t in match.get_team_choices()]
        if len(choices) == 2:
            # If only 2 choices change to a radio button selection
            self._radio_form = True
            self.fields["guess"].widget = forms.RadioSelect(attrs={"id": guess_id})

        self.fields["guess"].choices = choices

    def get_match(self):
        return self._match

    def is_radio_form(self):
        return self._radio_form

    def is_select_form(self):
        return not self._radio_form
