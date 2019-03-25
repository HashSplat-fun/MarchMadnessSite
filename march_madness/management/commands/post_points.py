from django.core.management.base import BaseCommand

from march_madness.models import current_year, Tournament, Match
from march_madness.utils import calculate_points


class Command(BaseCommand):
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("tournament_name", type=str, help="Tournament name with year (EX: 'March Madness 2019')")

    @classmethod
    def handle(cls, *args, **options):
        ROUND_POINTS = {
            1: 2,
            2: 2,
            3: 4,
            4: 6,
            5: 8,
            6: 10
        }

        SEED_POINTS = {
            "16 v 1": 8,
            "15 v 2": 7,
            "14 v 3": 6,
            "13 v 4": 5,
            "12 v 5": 4,
            "11 v 6": 3,
            "10 v 7": 2,
            "9 v 8": 1,
        }

        t = options['tournament_name']
        t, y = t.rsplit(' ', 1)
        tournament = Tournament.objects.get(name=t, year=int(y))

        for m in Match.objects.filter(round__tournament=tournament):
            calculate_points(m, ROUND_POINTS, SEED_POINTS)
