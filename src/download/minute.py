from src.download.selectsymbols import daysin2025, getsymbols, chunks
from src.api import dClient, tClient
from alpaca.data.requests import StockBarsRequest
from datetime import timedelta
from alpaca.data.timeframe import TimeFrame
import pandas as pd
from alpaca.trading.requests import GetCalendarRequest

for index in range(0,len(daysin2025)):
    day = tClient.get_calendar(GetCalendarRequest(
        start=daysin2025[index],
        end=daysin2025[index] + timedelta(days=1)
    ))
    totaldf = getsymbols(daysin2025[index])
    symbols = totaldf.index.get_level_values("symbol").unique().tolist()
    resultdf = []
    for batch in chunks(symbols, 1000):
        bars = dClient.get_stock_bars(StockBarsRequest(
            symbol_or_symbols=batch,
            start=day[0].open,
            end=day[0].close - timedelta(minutes=1),
            timeframe=TimeFrame.Minute
        ))
        if not bars.df.empty:
            resultdf.append(bars.df)
    resultdf = pd.concat(resultdf)
    resultdf.to_parquet(f"data/minute/{daysin2025[index].date()}.parquet")
    print(f"{index+1}/{len(daysin2025)} downloaded")