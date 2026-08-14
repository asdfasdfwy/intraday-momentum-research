from datetime import date
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
    realdays = []
    for index in range(0,len(days)):
        if index == len(days)-1:
            realdays.append(days[index].close)
        else:
            realdays.append(days[index].open)
    return realdays

daysin2025 = getDays(year)

startday = daysin2025[0]
endday = daysin2025[-1]

bar = dClient.get_stock_bars(StockBarsRequest(
    symbol_or_symbols="AAPL",
    start=startday,
    end=endday,
    timeframe=TimeFrame.Day
))

stocks = tClient.get_all_assets(GetAssetsRequest(
    asset_class=AssetClass.US_EQUITY
))

symbols = [stock.symbol for stock in stocks]

def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

passedsymbols = []

for batch in chunks(symbols, 5000):
    while len(batch) > 0:
        try:
            firstday = dClient.get_stock_bars(StockBarsRequest(
                symbol_or_symbols=batch,
                start=daysin2025[0],
                end=daysin2025[1],
                timeframe=TimeFrame.Day
            ))
            if not firstday.df.empty:
                passedsymbols.extend(firstday.df.index.get_level_values("symbol").unique())
            break
        except APIError as error:
            batch.remove(str(error.message).split(": ")[-1])