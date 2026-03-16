from django.core.management.base import BaseCommand
from django.db import connection as db
import datetime as dt
import pandas as pd
from importer.yfinance_api import YfinanceApi
from core.db_extra import DbExtra


class Command(BaseCommand):

    help = 'Import historical stock data from yfinance API'
    schema = 'public'
    tickers = ['NVDA']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.dbex = DbExtra(db, self.schema)

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS(f'==> {self.help}'))

        tableName = 'stockPricesNvda'
        self.createTable(tableName)

        self.api = YfinanceApi()

        for ticker in self.tickers:
            self.stdout.write(self.style.WARNING(f'--> processing ticker: {ticker}'))
            self.processTicker(ticker, tableName)

        self.stdout.write(self.style.SUCCESS('==> Done'))

    def processTicker(self, ticker, tableName):

        maxMarketDate = self.dbex.fetchOne(
            f'''
            SELECT MAX(market_date)
            FROM {self.schema}."{tableName}"
            WHERE ticker = %s
            ''',
            (ticker,)
        )

        if maxMarketDate is None:
            startDate = self.api.getStartDate()
        else:
            startDate = maxMarketDate + dt.timedelta(days=1)

        today = dt.date.today()

        while True:
            if startDate > today:
                break

            endDate = min(
                startDate + dt.timedelta(days=self.api.getMaxDays() - 1),
                today
            )

            self.stdout.write(
                f'----> fetching {ticker} from {startDate} to {endDate}'
            )

            dataFrame = self.api.getHistoricalPrices(ticker, startDate, endDate)

            if dataFrame.empty:
                break

            dataFrame['Date'] = pd.to_datetime(dataFrame['Date'])
            rows = []

            for _, row in dataFrame.iterrows():
                adjCloseValue = None
                if 'Adj Close' in dataFrame.columns and pd.notna(row['Adj Close']):
                    adjCloseValue = float(row['Adj Close'])

                rows.append((
                    row['Date'].date(),
                    ticker,
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    adjCloseValue,
                    int(row['Volume'])
                ))

            self.dbex.batchInsert(
                tableName,
                [
                    'market_date',
                    'ticker',
                    'open_price',
                    'high_price',
                    'low_price',
                    'close_price',
                    'adj_close',
                    'volume'
                ],
                rows,
                uniqueIndexColumns=['market_date', 'ticker']
            )

            self.stdout.write(
                self.style.SUCCESS(f'----> inserted {len(rows)} rows for {ticker}')
            )

            startDate = endDate + dt.timedelta(days=1)

    def createTable(self, tableName):
        
        query = f'''
        CREATE TABLE IF NOT EXISTS {self.schema}."{tableName}" (
            market_date DATE NOT NULL,
            ticker VARCHAR(10) NOT NULL,
            open_price DOUBLE PRECISION NOT NULL,
            high_price DOUBLE PRECISION NOT NULL,
            low_price DOUBLE PRECISION NOT NULL,
            close_price DOUBLE PRECISION NOT NULL,
            adj_close DOUBLE PRECISION,
            volume BIGINT NOT NULL,
            PRIMARY KEY (market_date, ticker)
        )
        '''
        db.cursor().execute(query)