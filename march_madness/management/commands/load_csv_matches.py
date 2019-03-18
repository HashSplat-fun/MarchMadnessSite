from django.core.management.base import BaseCommand

from march_madness.models import current_year, Tournament
from march_madness.utils import load_csv


class Command(BaseCommand):
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("filename", type=str, help=load_csv.__doc__)

    @classmethod
    def handle(cls, *args, **options):
        load_csv(options['filename'])
