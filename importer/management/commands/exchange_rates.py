from core.command import BaseCommand
from django.db import connection as db
import os
from contextlib import redirect_stdout, redirect_stderr
import datetime as dt
import pandas as pd
from importer.yfinance_api import YfinanceApi
from core.db_extra import DbExtra


class Command(BaseCommand):

    help = 'Import historical exchange rates from yfinance API'
    schema = 'public'
    
    # Dictionary mapping yfinance Forex tickers to our internal currency symbols
    # Format: [CURRENCY]USD=X (Value of 1 unit of foreign currency in USD)
    tickers = {
        'JPYUSD=X': 'JPY',  
        'CADUSD=X': 'CAD',  
        'GBPUSD=X': 'GBP',  
        'EURUSD=X': 'EUR',  
        'INRUSD=X': 'INR',  
        'CNHUSD=X': 'CNH',  
        'HKDUSD=X': 'HKD',  
        'SGDUSD=X': 'SGD',  
        'AUDUSD=X': 'AUD'   
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbex = DbExtra(db, self.schema)


    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS(f'==> {self.help}'))
        
        self.processMonitorStart('exchange_rates_generation', options)

        db.cursor().execute(f'CREATE SCHEMA IF NOT EXISTS {self.schema}')

        self.api = YfinanceApi()

        for i, (ticker, currency) in enumerate(self.tickers.items()):
            self.stdout.write(self.style.WARNING(f"--> processing currency: {currency} ({i + 1}/{len(self.tickers)})"))
            
            tableName = f'exchangeRate_{currency}'
            self.createTable(tableName)
            self.processTicker(ticker, currency, tableName)

        self.stdout.write(self.style.SUCCESS('==> Done'))
        self.processMonitorFinish()


    def processTicker(self, ticker, currency, tableName):

        maxMarketDate = self.dbex.fetchOne(
            f'SELECT MAX(market_date) FROM {self.schema}."{tableName}"'
        )

        if maxMarketDate is None:
            startDate = self.api.getStartDate()
        else:
            startDate = maxMarketDate + dt.timedelta(days=1)

        today = dt.date.today()
        while startDate <= today:
            endDate = min(startDate + dt.timedelta(days=365), today)

            self.stdout.write(f'\r----> fetching {currency} from {startDate} to {endDate} ... ', ending='')

            with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
                dataFrame = self.api.getHistoricalPrices(ticker, startDate, endDate)

            if dataFrame.empty:
                self.stdout.write(self.style.NOTICE('no data for this chunk       '), ending='')
            else:
                dataFrame['Date'] = pd.to_datetime(dataFrame['Date'])

                rows = [
                    (row['Date'].date(), float(row['Close']))
                    for _, row in dataFrame.iterrows() if pd.notna(row['Close'])
                ]

                if not rows:
                    self.stdout.write(self.style.NOTICE('no valid close data          '), ending='')
                else:
                    cursor = self.dbex.batchInsert(
                        tableName,
                        ['market_date', 'rate'],
                        rows,
                        uniqueIndexColumns=['market_date'],
                        ignoreConflicts=True
                    )

                    if cursor.rowcount == 0:
                        self.stdout.write(self.style.NOTICE('no new data          '), ending='')
                    else:
                        self.stdout.write(self.style.SUCCESS(f'inserted {cursor.rowcount} rows          '), ending='')

            startDate = endDate + dt.timedelta(days=1)

        self.stdout.write('')


    def createTable(self, tableName):

        #db.cursor().execute(f'drop table if exists {self.schema}."{tableName}"')  # DEBUG: uncomment to reset table on each run

        query = f'''
        CREATE TABLE IF NOT EXISTS {self.schema}."{tableName}" (
            market_date DATE NOT NULL PRIMARY KEY,
            rate DOUBLE PRECISION NOT NULL
        )
        '''
        db.cursor().execute(query)
