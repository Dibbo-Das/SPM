import yfinance as yf
import pandas as pd
import datetime as dt


class YfinanceApi:

    defaultStartDate = dt.date(2000, 1, 1)
    interval = '1d'
    maxDays = 3660

    def __init__(self):
        self.startDate = self.defaultStartDate

    def getHistoricalPrices(self, ticker, startDate, endDate):
        return self._callApi(ticker, startDate, endDate)

    def getStartDate(self):
        return self.startDate

    def getMaxDays(self):
        return self.maxDays

    def _callApi(self, ticker, startDate, endDate):

        dataFrame = yf.download(
            ticker,
            start=startDate,
            end=endDate + dt.timedelta(days=1),
            interval=self.interval,
            auto_adjust=False,
            progress=False,
            multi_level_index=False
        )

        if dataFrame is None or dataFrame.empty:
            return pd.DataFrame()

        dataFrame = dataFrame.reset_index()

        if isinstance(dataFrame.columns, pd.MultiIndex):
            dataFrame.columns = [
                col[0] if isinstance(col, tuple) else col
                for col in dataFrame.columns
            ]

        return dataFrame