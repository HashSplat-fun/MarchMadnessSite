import collections
from django.db.models import ManyToManyField, DateTimeField

from .models import Round, Match, Team, TeamRank, Tournament


def load_csv(filename):
    """Load a csv file with the first line being the exact tournament name and the next lines be comma separated
    columns of year, team name, seed.

    Note:
        The tournament must exist and must be "<name> <year>" separated by a space.
        The teams and rounds will be created if given.

    Example:
        March Madness 2018

        Year, Round, Match, Team 1, Team 1 Seed, Team 2, Team 2 Seed, Tournament Value
        2018, 1, 1, UMBC Retrievers, 16, Virginia Cavaliers, 1, 1
        2018, 1, 2, Kansas State Wildcats, 9,,,
    """
    tourney = None
    columns = None

    with open(filename) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if i == 0:
                # Tournament must exist
                n, y = [j.strip() for j in line.rsplit(' ', 1)]
                tourney = Tournament.objects.get(name=n, year=int(y))
            elif columns is None:
                if ',' in line:
                    columns = {c.strip(): j for j, c in enumerate(line.split(','))}
            else:
                items = [l.strip() for l in line.split(',')]
                year = int(items[columns['Year']])
                r_num = int(items[columns['Round']])
                m_num = int(items[columns['Match']])
                t_val = int(items[columns.get('Tournament Value', 1)])

                # Create the round and match
                rnd, created = Round.objects.get_or_create(tournament=tourney, round_number=r_num,
                                                           name='Round ' + str(r_num))
                match, created = Match.objects.get_or_create(round=rnd, match_number=m_num)

                # Set the match value
                match.tournament_value = t_val

                # Setup Team 1 if given
                try:
                    t1 = items[columns.get('Team 1', None)]
                    if t1.strip() == '':
                        raise KeyError

                    # Make or get Team 1
                    team1, created = Team.objects.get_or_create(name=t1)
                    match.team1 = team1

                    # Make the team rank
                    t1_seed = int(items[columns.get('Team 1 Seed', None)])
                    team1_r, created = TeamRank.objects.get_or_create(team=team1, year=year, seed=t1_seed)
                except (IndexError, ValueError, TypeError, KeyError, AttributeError):
                    pass

                # Setup Team 2 if given
                try:
                    t2 = items[columns['Team 2']]
                    if t2.strip() == '':
                        raise KeyError

                    # Make or get Team 2
                    team2, created = Team.objects.get_or_create(name=t2)
                    match.team2 = team2

                    # Make the team rank
                    t2_seed = int(items[columns.get('Team 2 Seed', None)])
                    team2_r, created = TeamRank.objects.get_or_create(team=team2, year=year, seed=t2_seed)
                except (IndexError, ValueError, TypeError, KeyError, AttributeError):
                    pass

                # Save the match
                match.save()

    line_up_matches(tourney)


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


def calculate_points(match, round_mapping=None, seed_mapping=None):
    """If Higher Seed wins give multiplier else normal"""
    if round_mapping is None:
        round_mapping = {}

    if seed_mapping is None:
        seed_mapping = {}

    round_value = round_mapping.get(match.round.round_number, 1)
    year = match.round.tournament.year
    team1 = match.victor
    if team1 is None:
        return
    if team1 == match.team1:
        team2 = match.team2
    else:
        team2 = match.team11

    try:
        seed1 = team1.rankings.get(year=year).seed
        seed2 = team2.rankings.get(year=year).seed
        seed_match = "{seed1} v {seed2}".format(seed1=seed1, seed2=seed2)
        seed_value = seed_mapping.get(seed_match, 1)  # Creating Seed Value from documented Seed Details

        match.tournament_value = round_value * seed_value
        match.save()
    except:
        return

