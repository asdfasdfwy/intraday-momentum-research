from src.download.selectsymbols import daysin2025
from src.backtest.trade import trademinute
from src.backtest import state
import pandas as pd

def tradeday(date):
    df = pd.read_parquet(f"data/minute/{date}.parquet").reorder_levels(["timestamp", "symbol"]).sort_index()
    for time in range(390):
        trademinute(time, df)

for day in daysin2025:
    tradeday(day.date())
    #print(f"{day.date()}: {state.portval}")