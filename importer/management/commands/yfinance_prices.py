from core.command import BaseCommand
from django.db import connection as db
from core.db_extra import DbExtra


class Command(BaseCommand):

    help = 'Import historical stock prices from yfinance'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbex = DbExtra(db, self.schema)

    def handle(self, *args, **options):
        pass
