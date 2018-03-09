import os
import sys

from django.core.management.base import BaseCommand

from march_madness.models import current_year, Tournament
from march_madness.utils import line_up_matches


class Command(BaseCommand):
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("--tournament", "-t", type=str, default=None,
                            help="Tournament name to line up matches for. "
                                 "Not needed if there is one tournament this year.")

        parser.add_argument("--year", "-y", type=int, default=current_year(),
                            help="Year of the tournament to line up matches for. Not needed if tournament is given.")

    @classmethod
    def handle(cls, *args, **options):

        tourney = None
        try:
            if options["tournament"] is not None:
                tourney = Tournament.objects.get(name=options["tournament"])
            if tourney is None:
                tourney = Tournament.objects.get(year=options["year"])
        except Tournament.DoesNotExist:
            pass

        if tourney is None:
            tourney = Tournament.objects.get(year=options["year"])

        line_up_matches(tourney)
