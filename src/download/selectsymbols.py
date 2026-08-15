from datetime import date, datetime, timedelta
from src.api import tClient, dClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.requests import GetCalendarRequest, GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.common.exceptions import APIError
import pandas as pd

year = 2025

def getDays(year):
    days = tClient.get_calendar(GetCalendarRequest(
        start=date(year,1,1),
        end=date(year,12,31)
    ))
    return [datetime.combine(day.date, datetime.min.time()) for day in days]

daysin2025 = getDays(year)

stocks = tClient.get_all_assets(GetAssetsRequest(
    asset_class=AssetClass.US_EQUITY
))

symbols = [stock.symbol for stock in stocks]

def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def getsymbols(day):
    dataframe = []

    for batch in chunks(symbols, 5000):
        while len(batch) > 0:
            try:
                firstday = dClient.get_stock_bars(StockBarsRequest(
                    symbol_or_symbols=batch,
                    start=day,
                    end=day + timedelta(days=1),
                    timeframe=TimeFrame.Day,
                    limit=10000
                ))
                if not firstday.df.empty:
                    dataframe.append(firstday.df)
                break
            except APIError as error:
                batch.remove(str(error.message).split(": ")[-1])

    dataframe = pd.concat(dataframe)

    dataframe["trading_value"] = (dataframe["close"] * dataframe["volume"])

    dataframe = dataframe[(dataframe["trading_value"] >= 50000000) & (dataframe["close"] >= 5)]

    return dataframe