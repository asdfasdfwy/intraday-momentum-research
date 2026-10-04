from src.download.selectsymbols import daysin2025
from src.backtest.trade import trademinute
from src.backtest import state
import pandas as pd

def tradeday(date):
    df = pd.read_parquet(f"data/minute/{date}.parquet").reorder_levels(["timestamp", "symbol"]).sort_index()
    timestamps = df.index.get_level_values("timestamp").unique()
    symbols = set(df.loc[timestamps[0]].index)
    for time in range(len(timestamps)):
        timestamp = timestamps[time]
        stocks = df.loc[timestamp]
        symbols.intersection_update(stocks.index)
    symbols = sorted(symbols)
    rows = []
    for symbol in symbols:
        rows.append({
            "symbol": symbol,
            "price": df.loc[timestamps[0], symbol].close,
            "prev5": [df.loc[timestamps[0], symbol].close]
        })
    state.minutedf = pd.DataFrame(rows)
    for time in range(len(timestamps)):
        trademinute(time, df)

for day in daysin2025:
    tradeday(day.date())
    print(f"{day.date()}: {state.portval}")