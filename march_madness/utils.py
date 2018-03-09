from django.db.models import ManyToManyField, DateTimeField

from .models import Round, Match, Team


def model_to_dict(self):
    opts = self._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, ManyToManyField):
            if self.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(self).values_list('pk', flat=True))
        elif isinstance(f, DateTimeField):
            if f.value_from_object(self) is not None:
                data[f.name] = f.value_from_object(self).timestamp()
            else:
                data[f.name] = None
        else:
            data[f.name] = f.value_from_object(self)
    return data


def line_up_matches(tournament):
    """If the first round is completely filled out. This function will go through the next rounds and make up the
    matches.
    """
    prev_round = tournament.rounds.all()[0]
    round_num = prev_round.round_number
    matches = prev_round.matches.all()
    num_rounds = 1
    num_matches = len(matches)
    while num_matches > 1:
        num_matches = num_matches / 2
        num_rounds += 1

    for r in range(1, num_rounds):
        next_round, created = Round.objects.get_or_create(tournament=tournament, round_number=round_num+r)
        for i in range(0, len(prev_round.matches.all()), 2):
            try:
                match1 = matches[i]
                match2 = matches[i+1]
            except IndexError:
                break

            try:
                next_match = Match.objects.get(round=next_round, match_number=int(i//2)+1)
            except Match.DoesNotExist:
                # Create the match
                next_match = Match.objects.create(round=next_round, match_number=int(i//2)+1)

            # next_match.team1.clear()
            # if match1.victor:
            #     next_match.team1.add(match1.victor)
            # else:
            #     next_match.team1.add(*match1.teams.all())
            #
            # next_match.team2.clear()
            # if match2.victor:
            #     next_match.team2.add(match2.victor)
            # else:
            #     next_match.team2.add(*match2.teams.all())
            # next_match.save()
        prev_round = next_round
