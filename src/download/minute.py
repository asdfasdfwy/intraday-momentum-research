from src.download.selectsymbols import daysin2025, getsymbols, chunks
from src.api import dClient, tClient

from alpaca.data.requests import StockBarsRequest
from alpaca.data.enums import DataFeed
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.requests import GetCalendarRequest

from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd


NEW_YORK = ZoneInfo("America/New_York")


for index in range(156, len(daysin2025)):

    day = tClient.get_calendar(
        GetCalendarRequest(
            start=daysin2025[index],
            end=daysin2025[index] + timedelta(days=1)
        )
    )

    market_open = (
        day[0].open
        .replace(tzinfo=NEW_YORK)
        .astimezone(timezone.utc)
    )

    market_close = (
        day[0].close
        .replace(tzinfo=NEW_YORK)
        .astimezone(timezone.utc)
    )

    totaldf = getsymbols(daysin2025[index])
    symbols = totaldf.index.get_level_values("symbol").unique().tolist()

    resultdf = []

    for batch in chunks(symbols, 500):

        bars = dClient.get_stock_bars(
            StockBarsRequest(
                symbol_or_symbols=batch,
                start=market_open,
                end=market_close - timedelta(minutes=1),
                timeframe=TimeFrame.Minute,
                feed=DataFeed.SIP
            )
        )

        if not bars.df.empty:
            resultdf.append(bars.df)

    resultdf = pd.concat(resultdf)

    resultdf.to_parquet(
        f"data/minute/{daysin2025[index].date()}.parquet"
    )

    print(f"{index + 1}/{len(daysin2025)} downloaded")